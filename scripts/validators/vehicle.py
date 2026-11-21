"""Vehicles Validator Plugin - 10 Unity 6 Subtypes (MR-3D-EXEC-V5.0)."""
import re
from typing import Any, Dict, List


def _extract_subtype(raw_val: str, valid_subtypes: Dict[str, Any]) -> str:
    if not raw_val:
        return ""
    s = raw_val.strip().lower()
    # Handle format like "car (خودرو سواری)" or "helicopter"
    m = re.match(r"^([a-z0-9_]+)", s)
    if m and m.group(1) in valid_subtypes:
        return m.group(1)
    for key in valid_subtypes:
        if key in s:
            return key
    return ""


def validate(
    gltf_data: Dict[str, Any],
    gltf_info: Dict[str, Any],
    issue_spec: Dict[str, str],
    registry_entry: Dict[str, Any],
) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []
    subtypes = registry_entry.get("subtypes", {})
    raw_sub = issue_spec.get("vehicle_subtype", "")
    subtype = _extract_subtype(raw_sub, subtypes)

    if not subtype:
        checks.append({
            "name": "[Vehicle] زیرنوع وسیله نقلیه (Unity 6 Subtype)",
            "expected": ", ".join(subtypes.keys()),
            "actual": raw_sub or "مشخص نشده",
            "status": "FAIL",
            "note": "زیرنوع وسیله نقلیه (car, helicopter, boat, ...) در ایشو یا derivative-config.json مشخص نشده است.",
        })
        return checks

    sub_cfg = subtypes[subtype]
    req_nodes = sub_cfg.get("required_nodes", [])

    # Collect all node and mesh names in glTF (case-insensitive matching)
    found_names = set()
    for n in gltf_data.get("nodes", []):
        if n.get("name"):
            found_names.add(n["name"].strip().lower())
    for m in gltf_data.get("meshes", []):
        if m.get("name"):
            found_names.add(m["name"].strip().lower())

    missing_nodes = [rn for rn in req_nodes if rn.lower() not in found_names]
    checks.append({
        "name": f"[Vehicle:{subtype}] مش‌ها و Nodeهای الزامی Unity 6",
        "expected": ", ".join(req_nodes),
        "actual": f"{len(req_nodes) - len(missing_nodes)}/{len(req_nodes)} منطبق",
        "status": "PASS" if not missing_nodes else "FAIL",
        "note": "" if not missing_nodes else f"مش‌های تفکیک‌نشده/مفقود: {', '.join(missing_nodes)}",
    })

    # Optional Emissive Lights Check
    lights_req = (issue_spec.get("emissive_lights") or "").lower()
    if "required" in lights_req or "الزامی" in lights_req:
        materials = gltf_data.get("materials", [])
        has_emissive = any(
            ("emissiveTexture" in m) or (any(v > 0 for v in m.get("emissiveFactor", [0, 0, 0])))
            for m in materials
        )
        checks.append({
            "name": f"[Vehicle:{subtype}] چراغ‌ها و متریال Emissive",
            "expected": "حداقل یک متریال Emissive",
            "actual": "یافت شد" if has_emissive else "یافت نشد",
            "status": "PASS" if has_emissive else "FAIL",
            "note": "" if has_emissive else "متریال Emissive برای چراغ‌های وسیله نقلیه یافت نشد.",
        })

    return checks
