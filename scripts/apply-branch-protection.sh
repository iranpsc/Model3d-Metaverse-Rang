#!/usr/bin/env bash
set -euo pipefail

OWNER="iranpsc"
REPO="Model3d-Metaverse-Rang"
BRANCH="main"

echo "Applying Zero-Override Branch Protection on ${OWNER}/${REPO} (${BRANCH})..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["pre-merge-3d-analysis"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
JSON

echo "Success! Branch '${BRANCH}' is now locked with enforce_admins=true (Zero-Override)."
