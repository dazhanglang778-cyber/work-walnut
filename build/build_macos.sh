#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_ROOT="$PROJECT_ROOT/build-output"
DIST_ROOT="$OUTPUT_ROOT/dist"
WORK_ROOT="$OUTPUT_ROOT/work-macos"
RELEASE_ROOT="$OUTPUT_ROOT/release"
ARCH="$(uname -m)"

if [[ "$ARCH" == "arm64" ]]; then
  RELEASE_ARCH="arm64"
else
  RELEASE_ARCH="x64"
fi

ARTIFACT_NAME="工作坚果-macOS-${RELEASE_ARCH}-v1.0.0"
ARTIFACT_PATH="$RELEASE_ROOT/${ARTIFACT_NAME}.zip"

mkdir -p "$OUTPUT_ROOT" "$RELEASE_ROOT"

python3 -m PyInstaller \
  --clean \
  --noconfirm \
  --distpath "$DIST_ROOT" \
  --workpath "$WORK_ROOT" \
  "$PROJECT_ROOT/build/WorkWalnut.spec"

if [[ ! -d "$DIST_ROOT/工作坚果.app" ]]; then
  echo "macOS app bundle was not created" >&2
  exit 1
fi

rm -f "$ARTIFACT_PATH"
ditto -c -k --sequesterRsrc --keepParent \
  "$DIST_ROOT/工作坚果.app" \
  "$ARTIFACT_PATH"

shasum -a 256 "$ARTIFACT_PATH" \
  | sed "s#  .*#  ${ARTIFACT_NAME}.zip#" \
  > "$RELEASE_ROOT/SHA256SUMS-macOS-${RELEASE_ARCH}.txt"

echo "$ARTIFACT_PATH"
