#!/usr/bin/env bash
# Builds the ZIP you upload to claude.ai (Settings > Capabilities > Skills > Upload skill).
# The ZIP contains one top-level folder named exactly like the skill, with SKILL.md inside.
set -euo pipefail
cd "$(dirname "$0")"
SKILL_DIR="plugins/full-stack-ai-engineer/skills/full-stack-ai-engineer"
mkdir -p dist
rm -f dist/full-stack-ai-engineer.zip
# Zip from the parent folder so the archive's top-level entry is "full-stack-ai-engineer/"
( cd "$(dirname "$SKILL_DIR")" && zip -qr "$OLDPWD/dist/full-stack-ai-engineer.zip" full-stack-ai-engineer -x "*/__pycache__/*" )
echo "Built dist/full-stack-ai-engineer.zip"
unzip -l dist/full-stack-ai-engineer.zip | sed -n '1,6p'
