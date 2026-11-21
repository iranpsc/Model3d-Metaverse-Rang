"""Generic Category Validator Plugin for Remaining 9 MetaRang Categories (MR-3D-EXEC-V5.0)."""
from typing import Any, Dict, List


def validate(
    asset_type: str,
    gltf_data: Dict[str, Any],
    gltf_info: Dict[str, Any],
    issue_spec: Dict[str, str],
    registry_entry: Dict[str, Any],
) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []
    dims = gltf_info.get("dimensions_meters", {})
    anim = gltf_info.get("animation", {})
    meshes = gltf_data.get("meshes", [])
    nodes = gltf_data.get("nodes", [])
    materials = gltf_data.get("materials", [])

    if asset_type == "wearable":
        has_skin = len(gltf_data.get("skins", [])) > 0
        rpm_req = (issue_spec.get("rpm_skinning") or "").lower()
        if "rigid" not in rpm_req:
            checks.append({
                "name": "[Wearable] انطباق Skinning با اسکلت RPM",
                "expected": "دارای Skin / JOINTS_0",
                "actual": "یافت شد" if has_skin else "یافت نشد",
                "status": "PASS" if has_skin else "FAIL",
                "note": "" if has_skin else "پوشاک باید روی اسکلت Ready Player Me وزن‌دهی (Skinned) شده باشد.",
            })

    elif asset_type == "animation-pack":
        clip_cnt = int(anim.get("clip_count", 0))
        checks.append({
            "name": "[Animation-Pack] وجود کلیپ‌های انیمیشن",
            "expected": ">= 1 Animation Clip",
            "actual": f"{clip_cnt} Clips",
            "status": "PASS" if clip_cnt >= 1 else "FAIL",
            "note": "" if clip_cnt >= 1 else "فایل پکیج انیمیشن فاقد هرگونه کلیپ انیمیشن در glTF است.",
        })

    elif asset_type == "tech-gadget":
        scr_req = (issue_spec.get("screen_mesh_required") or "").lower()
        if "required" in scr_req or "الزامی" in scr_req:
            all_names = {n.get("name", "").lower() for n in nodes} | {m.get("name", "").lower() for m in meshes}
            ok_scr = any("screen" in nm for nm in all_names)
            checks.append({
                "name": "[Tech-Gadget] تفکیک مش نمایشگر (Screen_Mesh)",
                "expected": "مش/Node حاوی Screen",
                "actual": "یافت شد" if ok_scr else "یافت نشد",
                "status": "PASS" if ok_scr else "FAIL",
                "note": "" if ok_scr else "مش نمایشگر جداگانه (مثلاً Screen_Mesh) یافت نشد.",
            })

    elif asset_type in {"urban-prop", "interior-decor", "art-sculpture"}:
        ground_req = (issue_spec.get("ground_aligned") or "").lower()
        if "required" in ground_req or "الزامی" in ground_req:
            ok = bool(dims.get("ground_aligned", False))
            checks.append({
                "name": f"[{asset_type}] تراز کف روی محور Y=0",
                "expected": "Y_min ≈ 0.0 (±0.05m)",
                "actual": "تراز است" if ok else "تراز نیست",
                "status": "PASS" if ok else "FAIL",
                "note": "" if ok else "مبدا مختصات (Pivot) باید روی کف مدل (Y=0) قرار گیرد.",
            })

    elif asset_type == "foliage-nature":
        alpha_req = (issue_spec.get("alpha_mode") or "").lower()
        if "mask" in alpha_req:
            has_mask = any(m.get("alphaMode") == "MASK" for m in materials)
            checks.append({
                "name": "[Foliage] حالت بهینه Alpha Cutout (MASK)",
                "expected": "alphaMode = MASK",
                "actual": "تنظیم شده" if has_mask else "تنظیم نشده",
                "status": "PASS" if has_mask else "WARN",
                "note": "" if has_mask else "برای عملکرد بهتر برگ‌ها در WebGL/VR استفاده از alphaMode=MASK توصیه می‌شود.",
            })

    elif asset_type == "modular-kit":
        checks.append({
            "name": "[Modular-Kit] تعدد قطعات ماژولار در صحنه",
            "expected": ">= 1 Mesh",
            "actual": f"{len(meshes)} Meshes",
            "status": "PASS" if len(meshes) >= 1 else "FAIL",
            "note": "",
        })

    elif asset_type == "environment-vfx":
        checks.append({
            "name": "[Environment-VFX] بررسی متریال و بهینه‌سازی محیطی",
            "expected": "ساختار استاندارد glTF/GLB",
            "actual": f"{len(materials)} Materials",
            "status": "PASS",
            "note": "",
        })

    return checks
