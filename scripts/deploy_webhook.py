#!/usr/bin/env python3
"""
MetaRang 3D Auto-Deploy Webhook Dispatcher (MR-3D-EXEC-V5.0)
Sends finalized `product-detail.json` to the Laravel backend (`3DMeta-Shop-Object-3D`)
with:
  - HMAC-SHA256 signature (`X-MetaRang-Signature-256`)
  - Idempotency key (`X-MetaRang-Idempotency-Key` = commit_sha)
  - Automatic 3x exponential backoff retry for resilience
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def send_webhook(webhook_url: str, secret: str, payload: dict, commit_sha: str, max_retries: int = 3) -> None:
    body_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "User-Agent": "MetaRang-3D-DeployBot/5.0",
        "X-MetaRang-Signature-256": f"sha256={signature}",
        "X-MetaRang-Idempotency-Key": commit_sha,
        "X-MetaRang-Schema-Version": "5.0.0",
    }

    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(webhook_url, data=body_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                resp_body = resp.read().decode("utf-8", errors="replace")
                print(f"[SUCCESS] Attempt {attempt}/{max_retries}: HTTP {resp.status} -> {resp_body}")
                return
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"[WARN] Attempt {attempt}/{max_retries} failed with HTTP {e.code}: {err_body}", file=sys.stderr)
            if 400 <= e.code < 500 and e.code != 429:
                # Client/signature error - do not retry
                sys.exit(1)
        except Exception as exc:
            print(f"[WARN] Attempt {attempt}/{max_retries} network error: {exc}", file=sys.stderr)

        if attempt < max_retries:
            sleep_sec = 2 ** attempt
            print(f"Retrying in {sleep_sec} seconds...", file=sys.stderr)
            time.sleep(sleep_sec)

    print(f"[FATAL] Webhook delivery failed after {max_retries} attempts.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="MetaRang 3D Auto-Deploy Webhook Dispatcher (V5.0)")
    parser.add_argument("--model-dir", required=True, help="Relative path to versioned model directory")
    parser.add_argument("--commit-sha", required=True, help="Git commit SHA for idempotency")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "iranpsc/Model3d-Metaverse-Rang"))
    args = parser.parse_args()

    webhook_url = os.environ.get("THREEDMETA_WEBHOOK_URL", "").strip()
    webhook_secret = os.environ.get("THREEDMETA_WEBHOOK_SECRET", "").strip()

    if not webhook_url or not webhook_secret:
        print("[SKIP] THREEDMETA_WEBHOOK_URL or THREEDMETA_WEBHOOK_SECRET is not configured yet. Skipping live dispatch.")
        sys.exit(0)

    model_dir = Path(args.model_dir)
    detail_file = model_dir / "product-detail.json"
    if not detail_file.exists():
        print(f"[ERROR] product-detail.json not found in {model_dir}", file=sys.stderr)
        sys.exit(1)

    detail = json.loads(detail_file.read_text(encoding="utf-8"))
    payload = {
        "event": "model.published",
        "repository": args.repo,
        "branch": "main",
        "commit_sha": args.commit_sha,
        "model_path": model_dir.as_posix().strip("/"),
        "product_detail": detail,
    }

    send_webhook(webhook_url, webhook_secret, payload, args.commit_sha, max_retries=3)


if __name__ == "__main__":
    main()
