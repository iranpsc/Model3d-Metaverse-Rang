"""Building & Architecture Validator Plugin (MR-3D-EXEC-V5.0)."""
from typing import Any, Dict, List


def validate(
    gltf_data: Dict[str, Any],
    gltf_info: Dict[str, Any],
    issue_spec: Dict[str, str],
    registry_entry: Dict[str, Any],
) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []
    dims = gltf_info.get("dimensions_meters", {})

    # 1. Ground Alignment (Y=0)
    ground_req = (issue_spec.get("ground_aligned") or "").lower()
    if "required" in ground_req or "الزامی" in ground_req or not ground_req:
        ok = bool(dims.get("ground_aligned", False))
        checks.append({
            "name": "[Building] تراز کف روی محور Y=0 (Ground Aligned)",
            "expected": "Y_min ≈ 0.0 (±0.05m)",
            "actual": "تراز است (True)" if ok else "تراز نیست (False)",
            "status": "PASS" if ok else "FAIL",
            "note": "" if ok else "نقطه Pivot کف سازه باید دقیقاً روی محور Y=0 قرار گیرد.",
        })

    # 2. Night Emissive Check (if required in Issue)
    emissive_req = (issue_spec.get("night_emissive") or "").lower()
    if "required" in emissive_req or "الزامی" in emissive_req:
        materials = gltf_data.get("materials", [])
        has_emissive = any(
            ("emissiveTexture" in m) or (any(v > 0 for v in m.get("emissiveFactor", [0, 0, 0])))
            for m in materials
        )
        checks.append({
            "name": "[Building] نورپردازی شب (Emissive Material)",
            "expected": "حداقل یک متریال Emissive",
            "actual": "یافت شد" if has_emissive else "یافت نشد",
            "status": "PASS" if has_emissive else "FAIL",
            "note": "" if has_emissive else "در ایشو نورپردازی شب الزامی شده ولی متریال Emissive وجود ندارد.",
        })

    return checks
