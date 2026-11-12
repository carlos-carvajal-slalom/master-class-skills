#!/usr/bin/env bash
# One-time setup for master-class-render (macOS, Apple Silicon). Safe to re-run.
set -euo pipefail
export PATH=/opt/homebrew/bin:$PATH
DIR="$(cd "$(dirname "$0")" && pwd)"
MODELS="$HOME/.cache/kokoro"

command -v brew >/dev/null || { echo "Homebrew is required: https://brew.sh"; exit 1; }
command -v d2 >/dev/null || brew install d2
command -v ffmpeg >/dev/null || brew install ffmpeg
command -v uv >/dev/null || brew install uv

if [ ! -x "$DIR/.venv/bin/python" ]; then
  uv venv -q --python 3.12 "$DIR/.venv"
fi
uv pip install -q --python "$DIR/.venv/bin/python" kokoro-onnx soundfile playwright
"$DIR/.venv/bin/python" -m playwright install chromium >/dev/null

mkdir -p "$MODELS"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$MODELS/$f" ] || curl -sSL -o "$MODELS/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
echo "master-class-render ready: d2 $(d2 --version), $(ffmpeg -version | head -1 | cut -d' ' -f1-3), venv at $DIR/.venv"
