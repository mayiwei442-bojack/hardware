#!/bin/sh

# Managed by MacroPad Settings. Remove this line before editing; marked files may be replaced on update.
# Copy to ~/.deepcode/keyboard-notify.sh, make it executable, and set the
# `notify` key in ~/.deepcode/settings.json to that absolute path.
KEYBOARD_BIN="/Applications/MacroPad.app/Contents/MacOS/MacroPad"

case "${STATUS:-}" in
  completed) light_status="success" ;;
  failed) light_status="error" ;;
  *) exit 0 ;;
esac

"$KEYBOARD_BIN" status "$light_status" "deep-code:${TITLE:-default}" >/dev/null 2>&1 || true
