#!/usr/bin/env bash
# Tailwind CSS Standalone + daisyUI 다운로드 (daisyUI Django 가이드 기반)
# https://daisyui.com/docs/install/django/
# 실행: 프로젝트 루트에서 ./static/css/install-daisyui.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TAILWIND_BASE="https://github.com/tailwindlabs/tailwindcss/releases/latest/download"
DAISYUI_BASE="https://github.com/saadeghi/daisyui/releases/latest/download"

get_os() {
  case "$(uname -s)" in
    Linux*)  echo "linux";;
    Darwin*) echo "macos";;
    *)       echo "unknown";;
  esac
}

get_arch() {
  case "$(uname -m)" in
    x86_64|amd64) echo "x64";;
    aarch64|arm64) echo "arm64";;
    *) echo "unknown";;
  esac
}

get_musl() {
  [ "$(uname -s)" = "Linux" ] && (ldd --version 2>&1 | grep -q musl) && echo "-musl" || echo ""
}

os=$(get_os)
arch=$(get_arch)
suffix=$(get_musl)
filename="tailwindcss-${os}-${arch}${suffix}"

if [ "$os" = "unknown" ] || [ "$arch" = "unknown" ]; then
  echo "❌ Unsupported OS/arch. Install manually from https://daisyui.com/docs/install/django/" >&2
  exit 1
fi

echo "📥 Downloading Tailwind CSS ($os $arch)..."
curl -fsSLo tailwindcss "${TAILWIND_BASE}/${filename}"
chmod +x tailwindcss

echo "📥 Downloading daisyUI..."
curl -fsSLo daisyui.mjs "${DAISYUI_BASE}/daisyui.mjs"
curl -fsSLo daisyui-theme.mjs "${DAISYUI_BASE}/daisyui-theme.mjs"

echo "✅ Done. Generate CSS with:"
echo "   ./static/css/tailwindcss -i static/css/input.css -o static/css/output.css"
echo "   (watch: add --watch)"
