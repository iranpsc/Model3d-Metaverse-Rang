"""Avatar & Humanoid Validator Plugin - Ready Player Me + Mandatory Blendshapes (MR-3D-EXEC-V5.0)."""
import re
from typing import Any, Dict, List


def _normalize_bone(name: str) -> str:
    # Strip common prefixes like mixamorig:, Armature_, RPM_
    n = re.sub(r"^(mixamorig[:_]|armature[:_]|rpm[:_])", "", name, flags=re.IGNORECASE)
    return n.strip().lower()


def validate(
    gltf_data: Dict[str, Any],
    gltf_info: Dict[str, Any],
    issue_spec: Dict[str, str],
    registry_entry: Dict[str, Any],
) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []
    standards = registry_entry.get("standards", {})
    skins = gltf_data.get("skins", [])
    nodes = gltf_data.get("nodes", [])
    meshes = gltf_data.get("meshes", [])

    # 1. Skeleton / Rigging Check
    has_skin = len(skins) > 0
    joint_indices = skins[0].get("joints", []) if has_skin else []
    bone_names_raw = [nodes[idx].get("name", "") for idx in joint_indices if idx < len(nodes)]
    bone_names_norm = {_normalize_bone(b) for b in bone_names_raw}

    checks.append({
        "name": "[Avatar] وجود اسکلت و ریگ (Skin / Rig)",
        "expected": "حداقل ۱ Skin استاندارد",
        "actual": f"{len(skins)} Skin ({len(joint_indices)} Bones)" if has_skin else "یافت نشد",
        "status": "PASS" if has_skin else "FAIL",
        "note": "" if has_skin else "آواتار فاقد ساختار ریگ‌بندی (skins) است.",
    })

    # 2. Ready Player Me / Humanoid Required Bones
    req_bones = standards.get("required_bones", [])
    missing_bones = [b for b in req_bones if _normalize_bone(b) not in bone_names_norm]
    checks.append({
        "name": "[Avatar] انطباق استخوان‌های Ready Player Me (Humanoid)",
        "expected": f"{len(req_bones)} استخوان کلیدی RPM",
        "actual": f"{len(req_bones) - len(missing_bones)}/{len(req_bones)} منطبق",
        "status": "PASS" if (has_skin and not missing_bones) else "FAIL",
        "note": "" if not missing_bones else f"استخوان‌های مفقود: {', '.join(missing_bones[:6])}{'...' if len(missing_bones) > 6 else ''}",
    })

    # 3. Max Bone Count
    max_bones_raw = issue_spec.get("max_bones", "")
    m_b = re.search(r"\d+", max_bones_raw or "")
    max_bones = int(m_b.group(0)) if m_b else int(standards.get("max_bones_default", 75))
    ok_bones = len(joint_indices) <= max_bones if has_skin else False
    checks.append({
        "name": "[Avatar] سقف تعداد استخوان‌ها (Max Bone Count)",
        "expected": f"<= {max_bones} Bones",
        "actual": f"{len(joint_indices)} Bones",
        "status": "PASS" if ok_bones else "FAIL",
        "note": "" if ok_bones else "تعداد استخوان‌ها برای WebGL و Meta Quest 3 بیش از سقف مجاز است.",
    })

    # 4. JOINTS_0 & WEIGHTS_0 Skinning Attributes
    skinned_prims = 0
    total_prims = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            total_prims += 1
            attrs = prim.get("attributes", {})
            if "JOINTS_0" in attrs and "WEIGHTS_0" in attrs:
                skinned_prims += 1
    checks.append({
        "name": "[Avatar] وزن‌دهی مش به اسکلت (JOINTS_0 & WEIGHTS_0)",
        "expected": "حداقل ۱ مش دارای وزن‌دهی کامل",
        "actual": f"{skinned_prims}/{total_prims} Primitives",
        "status": "PASS" if skinned_prims > 0 else "FAIL",
        "note": "" if skinned_prims > 0 else "ویژگی‌های Skinning (JOINTS_0 / WEIGHTS_0) روی مش‌ها یافت نشد.",
    })

    # 5. Mandatory Blendshapes (Morph Targets + Oculus Visemes / ARKit)
    morph_target_count = 0
    target_names: List[str] = []
    for mesh in meshes:
        extras = mesh.get("extras", {})
        if isinstance(extras, dict) and isinstance(extras.get("targetNames"), list):
            target_names.extend([str(t) for t in extras["targetNames"]])
        for prim in mesh.get("primitives", []):
            targets = prim.get("targets", [])
            if targets:
                morph_target_count = max(morph_target_count, len(targets))

    has_blendshapes = morph_target_count > 0
    checks.append({
        "name": "[Avatar] الزام Blendshapes چهره و لب (Morph Targets)",
        "expected": "الزامی (Mandatory - RPM Visemes / ARKit)",
        "actual": f"{morph_target_count} Morph Targets" if has_blendshapes else "یافت نشد (0)",
        "status": "PASS" if has_blendshapes else "FAIL",
        "note": "" if has_blendshapes else "طبق استاندارد V5.0 وجود Blendshapes برای آواتار متارنگ الزامی است.",
    })

    # Check Viseme sample names if targetNames metadata is present
    req_visemes = standards.get("required_visemes_sample", [])
    if has_blendshapes and target_names and req_visemes:
        tn_lower = {t.lower() for t in target_names}
        missing_vis = [v for v in req_visemes if v.lower() not in tn_lower]
        checks.append({
            "name": "[Avatar] کلیدهای Lip-Sync استاندارد (Oculus Visemes)",
            "expected": ", ".join(req_visemes),
            "actual": f"{len(target_names)} Named Targets",
            "status": "PASS" if not missing_vis else "FAIL",
            "note": "" if not missing_vis else f"کلیدهای Viseme یافت نشدند: {', '.join(missing_vis)}",
        })

    return checks
