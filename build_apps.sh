#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
OUT_DIR="$ROOT_DIR/ios_offline_apps"

build_one() {
  local src_html="$1"
  local app_dir="$2"
  local app_title="$3"
  local app_icon="$4"

  mkdir -p "$app_dir"
  cp "$src_html" "$app_dir/index.html"

  perl -0pi -e "s#</head>#  <link rel=\"manifest\" href=\"./manifest.webmanifest\" />\\n  <link rel=\"stylesheet\" href=\"./mobile-overrides.css\" />\\n  <meta name=\"apple-mobile-web-app-capable\" content=\"yes\" />\\n  <meta name=\"apple-mobile-web-app-status-bar-style\" content=\"default\" />\\n  <meta name=\"apple-mobile-web-app-title\" content=\"${app_title}\" />\\n  <link rel=\"apple-touch-icon\" href=\"./${app_icon}\" />\\n</head>#s" "$app_dir/index.html"

  perl -0pi -e 's#</body>#<script>\\nif ("serviceWorker" in navigator) {\\n  window.addEventListener("load", function () {\\n    navigator.serviceWorker.register("./sw.js").catch(function (err) {\\n      console.warn("Service Worker 註冊失敗:", err);\\n    });\\n  });\\n}\\n</script>\\n</body>#s' "$app_dir/index.html"
}

build_one "$ROOT_DIR/Gas_Detector_Lookup_Portable_CLPXfinal.html" "$OUT_DIR/gas-detector-app" "氣體偵測器" "detector-icon.png"
build_one "$ROOT_DIR/氣體洩漏應變.html" "$OUT_DIR/gas-leak-response-app" "氣體洩漏應變" "leak-response-icon.png"

echo "Done: rebuilt iOS offline app bundles in $OUT_DIR"
