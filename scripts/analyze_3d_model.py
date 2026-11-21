#!/usr/bin/env python3
"""
MetaRang 3D Model Analyzer & Plugin-Based Contract Validator (MR-3D-EXEC-V5.0)
Supports Dual-Track Development:
  - Track 1 (Issue-Backed): Official v1/v2/v3 orders validated against GitHub Issue Form.
  - Track 2 (Self-Initiated): Citizen derivatives without Issue, validated via `derivative-config.json`.
Single Source of Truth for:
  1. GitHub Action (pre-merge-3d-analysis) - Zero-Override CI Gate
  2. Local CLI (Pre-Push Validation)
  3. Standalone Desktop GUI App (MetaRang-3D-Tester.exe)
"""

import argparse
import json
import math
import os
import re
import struct
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Ensure validators subpackage is importable
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validators import avatar as avatar_validator
from validators import building as building_validator
from validators import generic as generic_validator
from validators import vehicle as vehicle_validator

PERSIAN_ARABIC_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
RES_MAP = {"1K": 1024, "2K": 2048, "4K": 4096, "8K": 8192}
TOLERANCE_PCT = 0.02
COLOR_DELTA_E_THRESHOLD = 24.0


def load_category_registry(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    candidates = []
    if repo_root:
        candidates.append(repo_root / "schemas" / "category-registry.json")
    candidates.append(SCRIPT_DIR.parent / "schemas" / "category-registry.json")
    candidates.append(Path("schemas/category-registry.json"))
    for p in candidates:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {"categories": {}, "core_rules": {"max_package_size_mb": 100.0, "min_render_images": 2}}


def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    s = text.translate(PERSIAN_ARABIC_DIGITS).strip()
    if s.lower() in {"_no response_", "none", "n/a", "-", "not specified"}:
        return ""
    return s


def parse_numeric_spec(raw: str) -> Optional[Tuple[float, float]]:
    s = normalize_text(raw)
    if not s:
        return None
    s = re.sub(r"(مترمربع|متر|sqm|m2|m|px|تا|to)", " ", s, flags=re.IGNORECASE)
    s = s.replace(",", "").replace("–", "-").replace("—", "-")
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if not nums:
        return None
    if len(nums) == 1:
        v = float(nums[0])
        return (v, v)
    v1, v2 = float(nums[0]), float(nums[1])
    return (min(v1, v2), max(v1, v2))


def parse_single_int(raw: str) -> Optional[int]:
    s = normalize_text(raw)
    if not s:
        return None
    s = s.replace(",", "").replace("_", "")
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else None


def parse_hex_list(raw: str) -> List[str]:
    s = normalize_text(raw)
    if not s:
        return []
    found = re.findall(r"#?[0-9a-fA-F]{6}", s)
    return [("#" + c.lstrip("#").upper()) for c in found]


def parse_texture_specs(raw: str) -> Dict[str, Any]:
    s = normalize_text(raw)
    if not s:
        return {}
    specs: Dict[str, Any] = {}
    m_cnt = re.search(r"max_count\s*=\s*(\d+)", s, flags=re.IGNORECASE)
    if m_cnt:
        specs["max_count"] = int(m_cnt.group(1))
    m_res = re.search(r"max_res\s*=\s*([0-9]+K|\d+)", s, flags=re.IGNORECASE)
    if m_res:
        val = m_res.group(1).upper()
        specs["max_res_label"] = val
        specs["max_res_px"] = RES_MAP.get(val, int(re.sub(r"\D", "", val) or 4096))
    m_fmt = re.search(r"formats\s*=\s*([a-zA-Z0-9|,_]+)", s, flags=re.IGNORECASE)
    if m_fmt:
        specs["formats"] = [x.strip().lower() for x in re.split(r"[|,]", m_fmt.group(1)) if x.strip()]
    return specs


def fetch_github_issue(issue_url: str, token: Optional[str] = None) -> Dict[str, Any]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", issue_url)
    if not m:
        raise ValueError(f"Invalid GitHub Issue URL: {issue_url}")
    owner, repo, number = m.group(1), m.group(2), m.group(3)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "MetaRang-3D-Analyzer/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API error {e.code} fetching {api_url}: {e.reason}")


def detect_asset_type_from_labels(labels: List[Any], title: str = "") -> str:
    for lb in labels or []:
        name = lb.get("name", "") if isinstance(lb, dict) else str(lb)
        if name.startswith("type:"):
            return name.split("type:", 1)[1].strip().lower()
    m = re.match(r"^\[([A-Z0-9-]+)\]", title or "")
    if m:
        tag = m.group(1).lower()
        mapping = {
            "building": "building", "avatar": "avatar", "vehicle": "vehicle",
            "wearable": "wearable", "urban-prop": "urban-prop", "interior": "interior-decor",
            "foliage": "foliage-nature", "tech": "tech-gadget", "art": "art-sculpture",
            "modular": "modular-kit", "animation": "animation-pack", "env-vfx": "environment-vfx",
        }
        return mapping.get(tag, "")
    return ""


def parse_issue_body(body: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    for part in re.split(r"^###\s+", body or "", flags=re.MULTILINE)[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        sections[lines[0].strip()] = normalize_text("\n".join(lines[1:]).strip())

    def find(*keywords: str) -> str:
        for h, v in sections.items():
            hl = h.lower()
            if any(k.lower() in hl for k in keywords):
                return v
        return ""

    return {
        "operation_type": find("operation type", "نوع عملیات"),
        "asset_classification": find("asset classification", "طبقه دایرکتوری"),
        "primary_owner_id": find("primary owner id", "شناسه مالک اصلی"),
        "model_slug": find("model slug", "نام استاندارد مدل"),
        "version": find("target version", "نسخه هدف"),
        "zone": find("zone / project", "محدوده مکانی"),
        "parent_model_ref": find("parent model ref", "مدل مرجع"),
        "requester_citizen_id": find("citizen id", "شناسه شهروندی"),
        "footprint_sqm": find("footprint", "متراژ"),
        "length_m": find("length", "طول مدل"),
        "width_m": find("width", "عرض مدل"),
        "height_m": find("height", "ارتفاع مدل"),
        "max_polygons": find("max polygons", "پالیگان"),
        "max_points": find("max points", "پوینت", "vertices"),
        "required_colors": find("required colors", "رنگ‌های"),
        "animation_status": find("animation status", "وضعیت انیمیشن"),
        "texture_specs": find("texture specs", "وضعیت و محدودیت تکسچر"),
        # Category-specific fields
        "ground_aligned": find("ground aligned", "تراز دقیق کف", "تراز کف"),
        "night_emissive": find("night emissive", "نورپردازی شب"),
        "max_bones": find("max bone count", "تعداد استخوان"),
        "vehicle_subtype": find("vehicle subtype", "زیرنوع وسیله نقلیه"),
        "emissive_lights": find("emissive lights", "چراغ‌های"),
        "rpm_skinning": find("rpm", "skinning"),
        "screen_mesh_required": find("screen_mesh", "مش نمایشگر"),
        "alpha_mode": find("alpha / cutout", "حالت رندر برگ"),
    }


def load_gltf_json(model_file: Path) -> Dict[str, Any]:
    ext = model_file.suffix.lower()
    if ext == ".gltf":
        return json.loads(model_file.read_text(encoding="utf-8"))
    if ext == ".glb":
        raw = model_file.read_bytes()
        if len(raw) < 20 or raw[:4] != b"glTF":
            raise ValueError(f"Invalid GLB header in {model_file.name}")
        chunk_length, chunk_type = struct.unpack("<II", raw[12:20])
        if chunk_type != 0x4E4F534A:
            raise ValueError(f"First GLB chunk is not JSON in {model_file.name}")
        return json.loads(raw[20:20 + chunk_length].decode("utf-8"))
    raise ValueError(f"Unsupported 3D model format: {ext}")


def inspect_gltf(data: Dict[str, Any]) -> Dict[str, Any]:
    accessors = data.get("accessors", [])
    meshes = data.get("meshes", [])
    materials = data.get("materials", [])
    animations = data.get("animations", [])
    skins = data.get("skins", [])
    nodes = data.get("nodes", [])

    mesh_scales: Dict[int, Tuple[float, float, float]] = {}
    for node in nodes:
        if "mesh" in node:
            sc = node.get("scale", [1.0, 1.0, 1.0])
            mesh_scales[node["mesh"]] = (abs(float(sc[0])), abs(float(sc[1])), abs(float(sc[2])))

    total_triangles = 0
    total_vertices = 0
    has_uv = False
    min_xyz = [float("inf"), float("inf"), float("inf")]
    max_xyz = [float("-inf"), float("-inf"), float("-inf")]

    for m_idx, mesh in enumerate(meshes):
        sx, sy, sz = mesh_scales.get(m_idx, (1.0, 1.0, 1.0))
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            if "TEXCOORD_0" in attrs:
                has_uv = True
            if "POSITION" in attrs:
                pos_acc = accessors[attrs["POSITION"]]
                v_cnt = int(pos_acc.get("count", 0))
                total_vertices += v_cnt
                if "min" in pos_acc and "max" in pos_acc:
                    pmin, pmax = pos_acc["min"], pos_acc["max"]
                    min_xyz[0] = min(min_xyz[0], float(pmin[0]) * sx)
                    min_xyz[1] = min(min_xyz[1], float(pmin[1]) * sy)
                    min_xyz[2] = min(min_xyz[2], float(pmin[2]) * sz)
                    max_xyz[0] = max(max_xyz[0], float(pmax[0]) * sx)
                    max_xyz[1] = max(max_xyz[1], float(pmax[1]) * sy)
                    max_xyz[2] = max(max_xyz[2], float(pmax[2]) * sz)
                if "indices" in prim:
                    idx_acc = accessors[prim["indices"]]
                    total_triangles += int(idx_acc.get("count", 0)) // 3
                else:
                    total_triangles += v_cnt // 3

    if min_xyz[0] == float("inf"):
        length_m = height_m = width_m = footprint_sqm = 0.0
        ground_aligned = False
    else:
        length_m = round(max_xyz[0] - min_xyz[0], 3)
        height_m = round(max_xyz[1] - min_xyz[1], 3)
        width_m = round(max_xyz[2] - min_xyz[2], 3)
        footprint_sqm = round(length_m * width_m, 2)
        ground_aligned = abs(min_xyz[1]) <= 0.05

    clip_list = [{"name": a.get("name", f"clip_{i+1}"), "channels": len(a.get("channels", []))} for i, a in enumerate(animations)]
    anim_status = "skeletal_rigged" if (skins and animations) else "baked_clips" if animations else "none"

    return {
        "dimensions_meters": {
            "height_m": height_m, "length_m": length_m, "width_m": width_m,
            "footprint_sqm": footprint_sqm, "ground_aligned": ground_aligned,
        },
        "animation": {
            "has_animation": len(animations) > 0, "animation_status": anim_status,
            "clip_count": len(animations), "clips": clip_list,
        },
        "analysis_standards": {
            "triangle_count": total_triangles, "vertex_count": total_vertices,
            "mesh_count": len(meshes), "material_count": len(materials),
            "has_uv": has_uv, "bone_count": len(skins[0].get("joints", [])) if skins else 0,
        },
    }


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    h = hex_code.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    def lin(c: float) -> float:
        c = c / 255.0
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    r, g, b = lin(rgb[0]), lin(rgb[1]), lin(rgb[2])
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + (16 / 116)

    fx, fy, fz = f(x), f(y), f(z)
    return ((116 * fy) - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(hex1: str, hex2: str) -> float:
    l1, a1, b1 = rgb_to_lab(hex_to_rgb(hex1))
    l2, a2, b2 = rgb_to_lab(hex_to_rgb(hex2))
    return math.sqrt((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def extract_colors_from_renders(render_files: List[Path], top_k: int = 8) -> Dict[str, Any]:
    if not HAS_PIL or not render_files:
        return {"dominant_hex": [], "color_distribution_pct": {}}
    color_counts: Dict[Tuple[int, int, int], int] = {}
    total_pixels = 0
    for rf in render_files:
        try:
            with Image.open(rf) as img:
                img = img.convert("RGB").resize((120, 120))
                quant = img.quantize(colors=12, method=Image.Quantize.MEDIANCUT).convert("RGB")
                for count, rgb in quant.getcolors(maxcolors=256) or []:
                    color_counts[rgb] = color_counts.get(rgb, 0) + count
                    total_pixels += count
        except Exception:
            continue
    if not total_pixels:
        return {"dominant_hex": [], "color_distribution_pct": {}}
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:top_k]
    dominant_hex = [f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}" for rgb, _ in sorted_colors]
    dist = {f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}": round((cnt / total_pixels) * 100, 1) for rgb, cnt in sorted_colors}
    return {"dominant_hex": dominant_hex, "color_distribution_pct": dist}


def inspect_textures(tex_dir: Path) -> Dict[str, Any]:
    valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".ktx2", ".exr", ".hdr"}
    if not tex_dir.exists():
        return {"texture_count": 0, "max_resolution_px": 0, "max_resolution": "0px", "formats": []}
    files = [f for f in tex_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
    formats = sorted({f.suffix.lower().lstrip(".") for f in files})
    max_dim = 0
    if HAS_PIL:
        for f in files:
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                try:
                    with Image.open(f) as im:
                        max_dim = max(max_dim, im.width, im.height)
                except Exception:
                    pass
    res_label = "8K" if max_dim > 4096 else "4K" if max_dim > 2048 else "2K" if max_dim > 1024 else "1K" if max_dim > 0 else "N/A"
    return {"texture_count": len(files), "max_resolution_px": max_dim, "max_resolution": res_label, "formats": formats}


def resolve_citizen_identity(github_user: str, fallback_citizen_id: str) -> Tuple[str, str]:
    api_url = os.environ.get("METARANG_IDENTITY_API_URL", "").strip()
    if api_url and github_user:
        try:
            req = urllib.request.Request(
                f"{api_url.rstrip('/')}/api/v1/citizens/by-github/{github_user}",
                headers={"User-Agent": "MetaRang-3D-Analyzer/5.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                cid = json.loads(resp.read().decode("utf-8")).get("citizen_id")
                if cid:
                    return cid, "metarang-go-microservice"
        except Exception:
            pass
    return fallback_citizen_id or "HM-PENDING", "fallback-pr-issue"


def check_with_tolerance(actual: float, spec_range: Tuple[float, float], tol: float = TOLERANCE_PCT) -> bool:
    return (spec_range[0] * (1.0 - tol)) <= actual <= (spec_range[1] * (1.0 + tol))


def analyze_model_directory(
    model_dir: Path,
    issue_spec: Dict[str, str],
    asset_type: str = "",
    track: str = "issue-backed",
    issue_number: Optional[int] = None,
    pr_number: Optional[int] = None,
    github_actor: str = "local-developer",
    repo_root: Optional[Path] = None,
) -> Tuple[bool, List[Dict[str, str]], Dict[str, Any]]:
    registry = load_category_registry(repo_root)
    checks: List[Dict[str, str]] = []

    def add_check(name: str, expected: str, actual: str, status: str, note: str = ""):
        checks.append({"name": name, "expected": expected, "actual": actual, "status": status, "note": note})

    # Detect Track 2 (Self-Initiated Derivative via derivative-config.json)
    deriv_cfg: Dict[str, Any] = {}
    deriv_path = model_dir / "derivative-config.json"
    if track == "self-initiated" or (issue_number is None and deriv_path.exists()):
        track = "self-initiated"
        if not deriv_path.exists():
            add_check("فایل derivative-config.json (مسیر توسعه شخصی)", "الزامی در PR بدون ایشو", "یافت نشد", "FAIL")
            return False, checks, {}
        try:
            deriv_cfg = json.loads(deriv_path.read_text(encoding="utf-8"))
        except Exception as e:
            add_check("اعتبارسنجی JSON فایل derivative-config.json", "JSON معتبر", f"خطا: {e}", "FAIL")
            return False, checks, {}

        req_keys = ["asset_type", "parent_model_ref", "creator_citizen_id", "custom_variant_name", "custom_pricing"]
        missing_keys = [k for k in req_keys if not deriv_cfg.get(k)]
        add_check(
            "ساختار derivative-config.json (توسعه شخصی)",
            ", ".join(req_keys),
            "کامل است" if not missing_keys else f"ناقص: {', '.join(missing_keys)}",
            "PASS" if not missing_keys else "FAIL",
        )
        asset_type = deriv_cfg.get("asset_type") or asset_type
        if deriv_cfg.get("vehicle_subtype"):
            issue_spec["vehicle_subtype"] = deriv_cfg["vehicle_subtype"]
        if deriv_cfg.get("parent_model_ref"):
            issue_spec["parent_model_ref"] = deriv_cfg["parent_model_ref"]
        if deriv_cfg.get("creator_citizen_id"):
            issue_spec["requester_citizen_id"] = deriv_cfg["creator_citizen_id"]

    # 1. Version / Directory Naming Rule (Dual-Track)
    parts = model_dir.as_posix().strip("/").split("/")
    version_name = parts[-1] if parts else ""
    if track == "issue-backed":
        valid_ver = bool(re.match(r"^v\d+$", version_name))
        add_check("ساختار پوشه نسخه رسمی (Track 1)", "v1, v2, v3, ...", version_name, "PASS" if valid_ver else "FAIL",
                  "" if valid_ver else "در سفارش رسمی روی ایشو، پوشه نسخه باید با پیشوند v (مثل v1 یا v2) باشد.")
    else:
        valid_custom = bool(re.match(r"^[a-z0-9][a-z0-9-]{1,60}$", version_name))
        add_check("نام دایرکتوری دلخواه توسعه شخصی (Track 2)", "kebab-case معتبر", version_name, "PASS" if valid_custom else "FAIL")

    # 2. 100MB Git LFS Package Cap
    total_mb = round(sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file()) / (1024 * 1024), 2)
    add_check("سقف حجم بسته (Git LFS Cap)", "<= 100 MB", f"{total_mb} MB", "PASS" if total_mb <= 100.0 else "FAIL")

    # 3. 3D Model File (.glb / .gltf)
    model_files = sorted([f for f in model_dir.iterdir() if f.is_file() and f.suffix.lower() in {".glb", ".gltf"}])
    if not model_files:
        add_check("فایل اصلی مدل سه‌بعدی", ".glb / .gltf", "یافت نشد", "FAIL")
        return False, checks, {}

    model_file = model_files[0]
    add_check("فایل اصلی مدل سه‌بعدی", ".glb / .gltf", model_file.name, "PASS")

    gltf_data = load_gltf_json(model_file)
    gltf_info = inspect_gltf(gltf_data)
    dims, anim, stats = gltf_info["dimensions_meters"], gltf_info["animation"], gltf_info["analysis_standards"]

    # 4. Renders (>= 2)
    renders_dir = model_dir / "renders"
    render_files = sorted([f for f in renders_dir.iterdir() if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]) if renders_dir.exists() else []
    add_check("تصاویر رندر (renders/)", ">= 2 تصویر", f"{len(render_files)} تصویر", "PASS" if len(render_files) >= 2 else "FAIL")

    # 5. Textures & Colors
    tex_info = inspect_textures(model_dir / "textures")
    color_info = extract_colors_from_renders(render_files)

    # 6. Core Issue-Driven Contract Checks (Skipped if empty)
    for label, key, actual_val, unit in [
        ("متراژ / زیربنا (مترمربع)", "footprint_sqm", dims["footprint_sqm"], "m²"),
        ("طول مدل (متر)", "length_m", dims["length_m"], "m"),
        ("عرض مدل (متر)", "width_m", dims["width_m"], "m"),
        ("ارتفاع مدل (متر)", "height_m", dims["height_m"], "m"),
    ]:
        parsed = parse_numeric_spec(issue_spec.get(key, ""))
        if not parsed:
            add_check(label, "ثبت نشده", f"{actual_val} {unit}", "SKIPPED")
        else:
            ok = check_with_tolerance(actual_val, parsed, TOLERANCE_PCT)
            exp_str = f"{parsed[0]}–{parsed[1]} {unit} (±2%)" if parsed[0] != parsed[1] else f"{parsed[0]} {unit} (±2%)"
            add_check(label, exp_str, f"{actual_val} {unit}", "PASS" if ok else "FAIL", "" if ok else "خارج از بازه مجاز ±۲٪")

    max_poly = parse_single_int(issue_spec.get("max_polygons", ""))
    if max_poly is None:
        add_check("حداکثر پالیگان (Triangles)", "ثبت نشده", f"{stats['triangle_count']:,}", "SKIPPED")
    else:
        add_check("حداکثر پالیگان (Triangles)", f"<= {max_poly:,}", f"{stats['triangle_count']:,}", "PASS" if stats["triangle_count"] <= max_poly else "FAIL")

    max_pts = parse_single_int(issue_spec.get("max_points", ""))
    if max_pts is None:
        add_check("حداکثر پوینت (Vertices)", "ثبت نشده", f"{stats['vertex_count']:,}", "SKIPPED")
    else:
        add_check("حداکثر پوینت (Vertices)", f"<= {max_pts:,}", f"{stats['vertex_count']:,}", "PASS" if stats["vertex_count"] <= max_pts else "FAIL")

    req_anim = normalize_text(issue_spec.get("animation_status", "")).lower()
    if not req_anim:
        add_check("وضعیت انیمیشن", "ثبت نشده", anim["animation_status"], "SKIPPED")
    else:
        exp_a = "none" if ("none" in req_anim or "static" in req_anim) else req_anim
        add_check("وضعیت انیمیشن", exp_a, f"{anim['animation_status']} ({anim['clip_count']} clips)", "PASS" if anim["animation_status"] == exp_a else "FAIL")

    tex_spec = parse_texture_specs(issue_spec.get("texture_specs", ""))
    if not tex_spec:
        add_check("وضعیت تکسچرها", "ثبت نشده", f"count={tex_info['texture_count']}, max_res={tex_info['max_resolution']}", "SKIPPED")
    else:
        errs = []
        if "max_count" in tex_spec and tex_info["texture_count"] > tex_spec["max_count"]:
            errs.append(f"count>{tex_spec['max_count']}")
        if "max_res_px" in tex_spec and tex_info["max_resolution_px"] > tex_spec["max_res_px"]:
            errs.append(f"res>{tex_spec['max_res_label']}")
        if "formats" in tex_spec:
            bad = [fm for fm in tex_info["formats"] if fm not in tex_spec["formats"]]
            if bad:
                errs.append(f"bad_format:{','.join(bad)}")
        add_check("وضعیت تکسچرها", issue_spec.get("texture_specs", ""), f"count={tex_info['texture_count']}, max_res={tex_info['max_resolution']}", "PASS" if not errs else "FAIL", " | ".join(errs))

    req_colors = parse_hex_list(issue_spec.get("required_colors", ""))
    if not req_colors:
        add_check("رنگ‌های الزامی مدیر (HEX)", "ثبت نشده", ", ".join(color_info["dominant_hex"][:4]) or "N/A", "SKIPPED")
    else:
        extracted = color_info["dominant_hex"]
        missing_c = [rc for rc in req_colors if not extracted or min(delta_e(rc, ec) for ec in extracted) > COLOR_DELTA_E_THRESHOLD]
        add_check("رنگ‌های الزامی مدیر (HEX - Strict)", ", ".join(req_colors), ", ".join(extracted[:5]) or "N/A",
                  "PASS" if not missing_c else "FAIL", f"رنگ‌های نامنطبق: {', '.join(missing_c)}" if missing_c else "تطبیق کامل")

    # 7. Category Plugin Dispatch (12 Specialized Categories)
    asset_type = (asset_type or "building").strip().lower()
    cat_entry = registry.get("categories", {}).get(asset_type, {})
    plugin_checks: List[Dict[str, str]] = []
    if asset_type == "building":
        plugin_checks = building_validator.validate(gltf_data, gltf_info, issue_spec, cat_entry)
    elif asset_type == "avatar":
        plugin_checks = avatar_validator.validate(gltf_data, gltf_info, issue_spec, cat_entry)
    elif asset_type == "vehicle":
        plugin_checks = vehicle_validator.validate(gltf_data, gltf_info, issue_spec, cat_entry)
    else:
        plugin_checks = generic_validator.validate(asset_type, gltf_data, gltf_info, issue_spec, cat_entry)
    checks.extend(plugin_checks)

    # 8. Build product-detail.json (V5.0)
    citizen_id, id_source = resolve_citizen_identity(github_actor, issue_spec.get("requester_citizen_id", ""))
    product_detail = {
        "schema_version": "5.0.0",
        "asset_type": asset_type,
        "development_track": track,
        "asset_classification": issue_spec.get("asset_classification") or (parts[-4] if len(parts) >= 4 else ""),
        "primary_owner_id": issue_spec.get("primary_owner_id") or (parts[-3] if len(parts) >= 3 else ""),
        "model_slug": issue_spec.get("model_slug") or (parts[-2] if len(parts) >= 2 else ""),
        "version": version_name,
        "pr_metadata": {
            "pr_number": pr_number,
            "issue_number": issue_number,
            "creator_github": github_actor,
            "creator_citizen_id": citizen_id,
            "identity_source": id_source,
        },
        "license": {
            "public_dev_license": "CC-BY-NC-SA-4.0",
            "commercial_license": "METARANG_COMMERCIAL_3DMETA_ONLY",
            "integrity_clause": True,
            "parent_model_ref": issue_spec.get("parent_model_ref") or None,
        },
        "custom_pricing": deriv_cfg.get("custom_pricing") if deriv_cfg else None,
        "dimensions_meters": dims,
        "textures": tex_info,
        "animation": anim,
        "colors": color_info,
        "analysis_standards": stats,
        "preview_images": [f"renders/{f.name}" for f in render_files],
        "zone": issue_spec.get("zone") or "",
    }

    all_passed = all(c["status"] != "FAIL" for c in checks)
    return all_passed, checks, product_detail


def render_markdown_report(passed: bool, checks: List[Dict[str, str]], product_detail: Dict[str, Any], model_dir: Path, ref: str) -> str:
    badge = "✅ **PASS — آماده بررسی و تایید مدیر برای Merge**" if passed else "❌ **FAIL — Merge مسدود شد (Zero-Override)**"
    lines = [
        "## 📊 گزارش تحلیل پلاگین‌محور مدل سه‌بعدی (`MR-3D-EXEC-V5.0`)",
        "",
        f"**وضعیت نهایی:** {badge}",
        f"**دسته تخصصی (`asset_type`):** `{product_detail.get('asset_type', 'unknown')}` | **مسیر توسعه:** `{product_detail.get('development_track', 'unknown')}`",
        f"**دایرکتوری مدل:** `{model_dir.as_posix()}` | **مرجع:** `{ref}`",
        "",
        "### ۱. لیست تحلیل (Core + Category Plugin Checklist)",
        "| معیار بررسی | مقدار استاندارد / ایشو | مقدار واقعی استخراج‌شده | وضعیت | توضیحات |",
        "| :--- | :--- | :--- | :---: | :--- |",
    ]
    icons = {"PASS": "✅ PASS", "FAIL": "❌ FAIL", "SKIPPED": "⏭️ SKIPPED", "WARN": "⚠️ WARN"}
    for c in checks:
        lines.append(f"| **{c['name']}** | `{c['expected']}` | `{c['actual']}` | {icons.get(c['status'], c['status'])} | {c['note']} |")
    lines.extend([
        "",
        "### ۲. پیش‌نمایش `product-detail.json` (آماده ارسال به Webhook بکند Laravel)",
        "<details><summary>مشاهده JSON کامل</summary>",
        "",
        "```json",
        json.dumps(product_detail, ensure_ascii=False, indent=2),
        "```",
        "</details>",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="MetaRang 3D Plugin Analyzer (MR-3D-EXEC-V5.0)")
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--issue-url", default="")
    parser.add_argument("--asset-type", default="")
    parser.add_argument("--track", choices=["issue-backed", "self-initiated"], default="issue-backed")
    parser.add_argument("--pr-number", type=int, default=None)
    parser.add_argument("--github-actor", default=os.environ.get("GITHUB_ACTOR", "local-developer"))
    parser.add_argument("--write-json", action="store_true")
    parser.add_argument("--report-out", default="")
    args = parser.parse_args()

    model_dir = Path(args.model_dir)
    if not model_dir.is_dir():
        print(f"ERROR: Model directory not found: {model_dir}", file=sys.stderr)
        sys.exit(1)

    issue_spec: Dict[str, str] = {}
    issue_num = None
    asset_type = args.asset_type
    ref = "Track 2 (Self-Initiated derivative-config.json)"

    if args.issue_url:
        issue_data = fetch_github_issue(args.issue_url, token=os.environ.get("GITHUB_TOKEN"))
        issue_spec = parse_issue_body(issue_data.get("body", ""))
        issue_num = issue_data.get("number")
        if not asset_type:
            asset_type = detect_asset_type_from_labels(issue_data.get("labels", []), issue_data.get("title", ""))
        ref = args.issue_url

    passed, checks, detail = analyze_model_directory(
        model_dir=model_dir,
        issue_spec=issue_spec,
        asset_type=asset_type,
        track=args.track,
        issue_number=issue_num,
        pr_number=args.pr_number,
        github_actor=args.github_actor,
    )

    if args.write_json and detail:
        (model_dir / "product-detail.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = render_markdown_report(passed, checks, detail, model_dir, ref)
    if args.report_out:
        Path(args.report_out).write_text(report, encoding="utf-8")

    print(report)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
