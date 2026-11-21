#!/usr/bin/env python3
"""
MetaRang 3D Live Catalog Generator (MR-3D-EXEC-V5.0)
Scans all 5 central root directories on `main` and builds:
  - catalog/catalog.json  (machine-readable index for Issue Auto-Linker & Desktop Tester)
  - catalog/CATALOG.md    (searchable Markdown table with direct GitHub & sparse-checkout links)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "iranpsc")
REPO_FULL = os.environ.get("GITHUB_REPOSITORY", "iranpsc/Model3d-Metaverse-Rang")
BRANCH = "main"

ROOT_CATEGORIES = [
    "01-investors-assets",
    "02-companies-holdings",
    "03-citizen-creations",
    "04-metarang-core-assets",
    "05-forked-developments",
]


def load_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def scan_repository(repo_root: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []

    for root_cat in ROOT_CATEGORIES:
        root_path = repo_root / root_cat
        if not root_path.exists() or not root_path.is_dir():
            continue

        # Expected structure: <root_cat>/<owner_id>/<model_slug>/<version_or_variant>/
        for owner_dir in sorted(p for p in root_path.iterdir() if p.is_dir() and not p.name.startswith(".")):
            for model_dir in sorted(p for p in owner_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
                for ver_dir in sorted(p for p in model_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
                    rel_path = ver_dir.relative_to(repo_root).as_posix()

                    detail = load_json_safe(ver_dir / "product-detail.json")
                    owners = load_json_safe(ver_dir / "owners.json")
                    deriv = load_json_safe(ver_dir / "derivative-config.json")

                    model_files = sorted(
                        f.name for f in ver_dir.iterdir()
                        if f.is_file() and f.suffix.lower() in {".glb", ".gltf"}
                    )

                    dims = detail.get("dimensions_meters", {})
                    stats = detail.get("analysis_standards", {})
                    anim = detail.get("animation", {})
                    pr_meta = detail.get("pr_metadata", {})

                    asset_type = (
                        detail.get("asset_type")
                        or deriv.get("asset_type")
                        or "unspecified"
                    )
                    parent_ref = (
                        detail.get("license", {}).get("parent_model_ref")
                        or deriv.get("parent_model_ref")
                        or None
                    )
                    track = "self-initiated" if deriv else "issue-backed"
                    status = "published" if model_files else "placeholder"

                    entries.append({
                        "model_path": rel_path,
                        "asset_classification": root_cat,
                        "primary_owner_id": owner_dir.name,
                        "model_slug": model_dir.name,
                        "version": ver_dir.name,
                        "asset_type": asset_type,
                        "track": track,
                        "status": status,
                        "model_files": model_files,
                        "zone": detail.get("zone", ""),
                        "creator_citizen_id": pr_meta.get("creator_citizen_id") or deriv.get("creator_citizen_id") or "",
                        "parent_model_ref": parent_ref,
                        "total_owners": owners.get("total_owners", 0),
                        "dimensions_meters": dims,
                        "triangle_count": stats.get("triangle_count"),
                        "vertex_count": stats.get("vertex_count"),
                        "animation_status": anim.get("animation_status", ""),
                        "github_tree_url": f"https://github.com/{REPO_FULL}/tree/{BRANCH}/{rel_path}",
                    })

    return entries


def build_catalog_markdown(entries: List[Dict[str, Any]], generated_at: str) -> str:
    published_cnt = sum(1 for e in entries if e["status"] == "published")
    placeholder_cnt = sum(1 for e in entries if e["status"] == "placeholder")

    lines = [
        "# 📚 Live 3D Model Catalog (`main`) | کاتالوگ زنده مدل‌های سه‌بعدی متارنگ",
        "",
        f"> **Auto-generated on:** `{generated_at}` | **Total Directories:** `{len(entries)}` (**Published:** `{published_cnt}` | **Placeholders:** `{placeholder_cnt}`)",
        "> **How to use:** Press `Ctrl+F` to find any model, copy its **Model Path** into the `Parent Model Ref` field of a New Issue, and the **Issue Auto-Linker Bot** will automatically post direct download links and technical specs.",
        "",
        "---",
        "",
        "| Model Path (Copy for Issue) | Owner | Category (`asset_type`) | Version | Status | Polygons | Owners | Direct Link |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    if not entries:
        lines.append("| *(No model directories found yet)* | - | - | - | - | - | - | - |")
    else:
        for e in entries:
            status_badge = "✅ Published" if e["status"] == "published" else "📁 Ready (Empty)"
            poly_str = f"{e['triangle_count']:,}" if isinstance(e["triangle_count"], int) else "-"
            lines.append(
                f"| `{e['model_path']}` | `{e['primary_owner_id']}` | `{e['asset_type']}` | `{e['version']}` | {status_badge} | {poly_str} | {e['total_owners']} | [Open Folder]({e['github_tree_url']}) |"
            )

    lines.extend([
        "",
        "---",
        "",
        "<div dir=\"rtl\">",
        "",
        "### راهنمای سریع دانلود یک پوشه مشخص بدون کلون کل مخزن (`git sparse-checkout`)",
        "برای دانلود سریع فقط یک مدل (مثلاً `01-investors-assets/BN-1000/lighthouse/v1`) در **Git Bash** یا **PowerShell**:",
        "",
        "</div>",
        "",
        "```bash",
        f"git clone --filter=blob:none --sparse https://github.com/{REPO_FULL}.git",
        "cd Model3d-Metaverse-Rang",
        "git sparse-checkout set 01-investors-assets/BN-1000/lighthouse/v1",
        "git lfs pull",
        "```",
        "",
    ])
    return "\n".join(lines)


def main():
    repo_root = Path(".").resolve()
    catalog_dir = repo_root / "catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = scan_repository(repo_root)

    catalog_json = {
        "schema_version": "5.0.0",
        "repository": REPO_FULL,
        "branch": BRANCH,
        "generated_at": generated_at,
        "total_models": len(entries),
        "models": entries,
    }

    (catalog_dir / "catalog.json").write_text(
        json.dumps(catalog_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (catalog_dir / "CATALOG.md").write_text(
        build_catalog_markdown(entries, generated_at),
        encoding="utf-8",
    )
    print(f"Catalog updated: {len(entries)} entries written to catalog/catalog.json and catalog/CATALOG.md")


if __name__ == "__main__":
    main()
