#!/usr/bin/env bash
set -euo pipefail

fail() { printf 'MacroPad packaging: %s\n' "$*" >&2; exit 1; }
[[ "$(uname -s)" == "Darwin" ]] || fail "run this script on macOS to build a real Mac application."
for tool in cargo rustc jq python3 plutil codesign lipo hdiutil ditto shasum file otool; do
    command -v "$tool" >/dev/null 2>&1 || fail "required command is unavailable: $tool"
done
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
OUTPUT_ARGUMENT="${1:-$REPO_ROOT/dist}"
FIRMWARE_BIN="${2:-}"
[[ -n "$OUTPUT_ARGUMENT" ]] || fail "output directory must not be empty."
OUTPUT_DIR="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$OUTPUT_ARGUMENT")"
case "$OUTPUT_DIR" in / | "$REPO_ROOT" | "$REPO_ROOT/app") fail "unsafe output directory: $OUTPUT_DIR" ;; esac
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd -P)"

# Resolve before recursive cleanup; reject a staging symlink even if its
# destination happens to be inside the output directory.
require_output_child() {
    local resolved
    resolved="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$1")"
    case "$resolved" in "$OUTPUT_DIR"/*) ;; *) fail "output target escapes $OUTPUT_DIR: $resolved" ;; esac
    [[ ! -L "$1" ]] || fail "refusing a symlink output target: $1"
}
REQUESTED_ARCH="${MACROPAD_MACOS_ARCH:-${KEYBOARD_MACOS_ARCH:-arm64}}"
case "$REQUESTED_ARCH" in
    arm64 | aarch64) ARCH=aarch64; LIPO_ARCH=arm64; RUST_TARGET=aarch64-apple-darwin ;;
    x86_64) ARCH=x86_64; LIPO_ARCH=x86_64; RUST_TARGET=x86_64-apple-darwin ;;
    *) fail "unsupported macOS architecture: $REQUESTED_ARCH" ;;
esac
APP_METADATA="$(cargo metadata --manifest-path "$REPO_ROOT/app/Cargo.toml" --locked --no-deps --format-version 1)"
APP_VERSION="$(printf '%s' "$APP_METADATA" | jq -er '.packages[] | select(.name == "keyboard-app") | .version')"
TARGET_DIR="$(printf '%s' "$APP_METADATA" | jq -er '.target_directory')"
FW_VERSION="$(cargo metadata --manifest-path "$REPO_ROOT/fw/Cargo.toml" --locked --no-deps --format-version 1 |
    jq -er '.packages[] | select(.name == "keyboard-fw") | .version')"
[[ "$APP_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([+-][0-9A-Za-z.+-]+)?$ ]] || fail "invalid version: $APP_VERSION"
BASE_VERSION="${APP_VERSION%%[-+]*}"
BUILD_VERSION="${MACROPAD_BUILD_NUMBER:-$BASE_VERSION}"
[[ "$BUILD_VERSION" =~ ^[0-9]+(\.[0-9]+){0,2}$ ]] || fail "build number must contain one to three numeric components."
ICON="$REPO_ROOT/app/macos/MacroPad.icns"
[[ -f "$ICON" ]] || fail "missing icon: $ICON"
[[ -f "$REPO_ROOT/LICENSE" ]] || fail "missing source license."
LICENSES_FILE="${MACROPAD_DEPENDENCY_LICENSES_FILE:-$OUTPUT_DIR/licenses/Rust-dependency-licenses.json}"
LICENSES_FILE="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$LICENSES_FILE")"
[[ -f "$LICENSES_FILE" ]] || fail "set MACROPAD_DEPENDENCY_LICENSES_FILE to the dependency license JSON from this build."
python3 - "$LICENSES_FILE" <<'PY'
import json, pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text()
data = json.loads(text)
if not isinstance(data, dict) or not isinstance(data.get("third_party_libraries"), list) or not data["third_party_libraries"]:
    sys.exit("Dependency license inventory must contain third_party_libraries.")
if "NOT FOUND" in text:
    sys.exit("Dependency license inventory contains unresolved license text.")
for library in data["third_party_libraries"]:
    notices=library.get("licenses") if isinstance(library,dict) else None
    if not isinstance(notices,list) or not notices or any(not isinstance(item,dict) or not isinstance(item.get("text"),str) or not item["text"].strip() for item in notices):
        sys.exit("Every dependency must have nonempty licenses.text notices.")
PY
if [[ -n "$FIRMWARE_BIN" ]]; then
    FIRMWARE_BIN="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$FIRMWARE_BIN")"
    [[ -f "$FIRMWARE_BIN" ]] || fail "missing firmware image: $FIRMWARE_BIN"
fi
SIGN_IDENTITY="${MACROPAD_MACOS_SIGN_IDENTITY:-${MACOS_SIGN_IDENTITY:-}}"
if [[ "${REQUIRE_SIGNING:-0}" == "1" ]]; then
    [[ -n "$SIGN_IDENTITY" ]] || fail "Developer ID signing was required but no identity is configured."
fi
if [[ -n "$SIGN_IDENTITY" ]]; then
    security find-identity -v -p codesigning | python3 -c '
import re,sys
requested=sys.argv[1]
for line in sys.stdin:
    found=re.search(r"([0-9A-Fa-f]{40})\s+\"([^\"]+)\"", line)
    if found and found[2].startswith("Developer ID Application:") and (requested==found[2] or requested.lower()==found[1].lower()):
        sys.exit(0)
sys.exit("Select an available Developer ID Application identity, by exact name or certificate hash.")
' "$SIGN_IDENTITY"
fi
SPARKLE_FEED="${MACROPAD_SPARKLE_FEED_URL:-}"
SPARKLE_KEY="${MACROPAD_SPARKLE_PUBLIC_ED_KEY:-}"
SPARKLE_ROOT="${MACROPAD_SPARKLE_ROOT:-${KEYBOARD_SPARKLE_ROOT:-$REPO_ROOT/app/target/sparkle/2.9.6}}"
SPARKLE_MODE="${MACROPAD_ENABLE_SPARKLE:-auto}"
case "$SPARKLE_MODE" in
    0) SPARKLE_FEED=""; SPARKLE_KEY="" ;;
    1 | auto) ;;
    *) fail "MACROPAD_ENABLE_SPARKLE must be 0, 1, or auto." ;;
esac
SPARKLE_ENABLED=0
if [[ "$SPARKLE_MODE" == "1" || -n "$SPARKLE_FEED" || -n "$SPARKLE_KEY" ]]; then
    [[ -n "$SIGN_IDENTITY" && -n "$SPARKLE_FEED" && -n "$SPARKLE_KEY" ]] ||
        fail "Sparkle needs Developer ID signing and both MACROPAD_SPARKLE_FEED_URL / MACROPAD_SPARKLE_PUBLIC_ED_KEY."
    python3 - "$SPARKLE_FEED" "$SPARKLE_KEY" "$REPO_ROOT/app/macos/sparkle-public-key.txt" <<'PY'
import base64, pathlib, sys, urllib.parse
url=urllib.parse.urlsplit(sys.argv[1])
if url.scheme != "https" or not url.hostname or url.username is not None or url.password is not None or url.fragment:
    sys.exit("Sparkle feed must be HTTPS, without embedded credentials or a fragment.")
try:
    key=base64.b64decode(sys.argv[2], validate=True)
except (ValueError, base64.binascii.Error):
    sys.exit("Sparkle public key is not valid base64.")
if len(key) != 32:
    sys.exit("Sparkle public key must decode to 32 bytes.")
old=pathlib.Path(sys.argv[3])
if old.is_file() and old.read_text().strip() == sys.argv[2]:
    sys.exit("The upstream Sparkle public key cannot be reused; configure your own key.")
PY
    SPARKLE_ROOT="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$SPARKLE_ROOT")"
    for member in Sparkle.framework/Headers/Sparkle.h Sparkle.framework/Versions/B/Sparkle LICENSE; do
        [[ -f "$SPARKLE_ROOT/$member" ]] || fail "prepared Sparkle distribution is incomplete: $member"
    done
    SPARKLE_ENABLED=1
fi

STAGE="$OUTPUT_DIR/macos-$ARCH"
APP_BUNDLE="$STAGE/MacroPad.app"
CONTENTS="$APP_BUNDLE/Contents"
RESOURCES="$CONTENTS/Resources"
FRAMEWORKS="$CONTENTS/Frameworks"
DMG_ROOT="$STAGE/dmg-root"
DMG="$OUTPUT_DIR/MacroPad-$APP_VERSION-macos-$ARCH.dmg"
APP_ZIP="$OUTPUT_DIR/MacroPad-$APP_VERSION-macos-$ARCH.app.zip"
for target in "$STAGE" "$DMG" "$APP_ZIP"; do require_output_child "$target"; done
for input in "$LICENSES_FILE" "$FIRMWARE_BIN"; do
    case "$input" in "$STAGE"/*) fail "inputs must be outside the staging directory: $input" ;; esac
done
if [[ -e "$STAGE" ]]; then
    # STAGE was resolved and checked above against the canonical OUTPUT_DIR.
    rm -rf -- "$STAGE"
fi
mkdir -p "$CONTENTS/MacOS" "$RESOURCES/licenses" "$DMG_ROOT"
(
    cd "$REPO_ROOT/app"
    unset MACROPAD_SPARKLE_FRAMEWORK_DIR KEYBOARD_SPARKLE_FRAMEWORK_DIR
    if [[ "$SPARKLE_ENABLED" == "1" ]]; then
        export MACROPAD_SPARKLE_FRAMEWORK_DIR="$SPARKLE_ROOT"
    fi
    export MACOSX_DEPLOYMENT_TARGET=11.0
    export KEYBOARD_FIRMWARE_VERSION="$FW_VERSION"
    cargo build --release --locked --target "$RUST_TARGET" --bin keyboard-app
)
cp "$TARGET_DIR/$RUST_TARGET/release/keyboard-app" "$CONTENTS/MacOS/MacroPad"
chmod 755 "$CONTENTS/MacOS/MacroPad"
cp "$ICON" "$RESOURCES/MacroPad.icns"
cp "$REPO_ROOT/LICENSE" "$RESOURCES/licenses/Upstream-MIT-LICENSE.txt"
cp "$LICENSES_FILE" "$RESOURCES/licenses/Rust-dependency-licenses.json"
python3 - "$REPO_ROOT/app/resources" "$RESOURCES/licenses" <<'PY'
import pathlib,re,shutil,sys
source,destination=map(pathlib.Path,sys.argv[1:])
for item in source.iterdir():
    if item.is_file() and re.search(r"LICENSE|NOTICE|OFL",item.name,re.I):
        shutil.copy2(item,destination/item.name)
PY
if [[ "$SPARKLE_ENABLED" == "1" ]]; then
    mkdir -p "$FRAMEWORKS"
    ditto "$SPARKLE_ROOT/Sparkle.framework" "$FRAMEWORKS/Sparkle.framework"
    cp "$SPARKLE_ROOT/LICENSE" "$RESOURCES/licenses/Sparkle-LICENSE.txt"
fi
python3 - "$REPO_ROOT/app/macos/Info.plist.in" "$CONTENTS/Info.plist" "$BASE_VERSION" "$BUILD_VERSION" "$SPARKLE_ENABLED" "$SPARKLE_FEED" "$SPARKLE_KEY" <<'PY'
import plistlib,sys
with open(sys.argv[1],"rb") as source: info=plistlib.load(source)
info["CFBundleShortVersionString"]=sys.argv[3]
info["CFBundleVersion"]=sys.argv[4]
enabled=sys.argv[5]=="1"
info["MacroPadAutomaticUpdates"]=enabled
if enabled:
    info.update(SUFeedURL=sys.argv[6],SUPublicEDKey=sys.argv[7],SUEnableAutomaticChecks=False,
                SURequireSignedFeed=True,SUVerifyUpdateBeforeExtraction=True)
with open(sys.argv[2],"wb") as target: plistlib.dump(info,target,sort_keys=False)
PY
printf 'APPL????' > "$CONTENTS/PkgInfo"
if [[ -n "$FIRMWARE_BIN" ]]; then
    mkdir -p "$RESOURCES/firmware"
    cp "$FIRMWARE_BIN" "$RESOURCES/firmware/keyboard-fw.bin"
    FW_SHA256="$(shasum -a 256 "$FIRMWARE_BIN" | awk '{print $1}')"
    jq -n --arg version "$FW_VERSION" --arg sha256 "$FW_SHA256" '{version:$version,sha256:$sha256}' > "$RESOURCES/firmware/manifest.json"
fi
plutil -lint "$CONTENTS/Info.plist"
file "$CONTENTS/MacOS/MacroPad"
lipo "$CONTENTS/MacOS/MacroPad" -verify_arch "$LIPO_ARCH"
[[ "$(lipo -archs "$CONTENTS/MacOS/MacroPad")" == "$LIPO_ARCH" ]] || fail "executable architecture does not match $LIPO_ARCH."
if [[ "$SPARKLE_ENABLED" == "1" ]]; then
    otool -L "$CONTENTS/MacOS/MacroPad" | grep -F '@rpath/Sparkle.framework/Versions/B/Sparkle' >/dev/null ||
        fail "the enabled Sparkle framework is not linked."
else
    if otool -L "$CONTENTS/MacOS/MacroPad" | grep -F 'Sparkle.framework' >/dev/null; then
        fail "an updater-disabled build unexpectedly links Sparkle."
    fi
fi
if [[ -n "$SIGN_IDENTITY" ]]; then
    if [[ "$SPARKLE_ENABLED" == "1" ]]; then
        SPARKLE_FRAMEWORK="$FRAMEWORKS/Sparkle.framework"
        for member in Versions/B/XPCServices/Installer.xpc Versions/B/XPCServices/Downloader.xpc Versions/B/Autoupdate Versions/B/Updater.app; do
            [[ -e "$SPARKLE_FRAMEWORK/$member" ]] || fail "missing Sparkle signing member: $member"
            if [[ "$member" == *Downloader.xpc ]]; then
                codesign --force --options runtime --timestamp --preserve-metadata=entitlements --sign "$SIGN_IDENTITY" "$SPARKLE_FRAMEWORK/$member"
            else
                codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$SPARKLE_FRAMEWORK/$member"
            fi
        done
        codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$SPARKLE_FRAMEWORK"
        codesign --verify --deep --strict --verbose=2 "$SPARKLE_FRAMEWORK"
    fi
    codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$APP_BUNDLE"
else
    printf '%s\n' "MacroPad: ad-hoc signed local package; this is not a notarized distribution." >&2
    codesign --force --sign - "$APP_BUNDLE"
fi
codesign --verify --deep --strict --verbose=2 "$APP_BUNDLE"

# Notarization is opt-in and uses an existing keychain profile. No credentials
# are imported, generated, or assumed by this packaging script.
NOTARY_PROFILE="${MACROPAD_NOTARY_PROFILE:-}"
if [[ -n "$NOTARY_PROFILE" ]]; then
    [[ -n "$SIGN_IDENTITY" ]] || fail "notarization requires Developer ID signing."
    command -v xcrun >/dev/null 2>&1 || fail "xcrun is needed for notarization."
    ditto -c -k --sequesterRsrc --keepParent "$APP_BUNDLE" "$STAGE/notarize-app.zip"
    xcrun notarytool submit "$STAGE/notarize-app.zip" --keychain-profile "$NOTARY_PROFILE" --wait --output-format json > "$STAGE/notary-app.json"
    [[ "$(jq -r '.status' "$STAGE/notary-app.json")" == Accepted ]] || fail "app notarization was not accepted."
    xcrun stapler staple "$APP_BUNDLE"
    xcrun stapler validate "$APP_BUNDLE"
fi
ditto "$APP_BUNDLE" "$DMG_ROOT/MacroPad.app"
ln -s /Applications "$DMG_ROOT/Applications"
hdiutil create -volname MacroPad -srcfolder "$DMG_ROOT" -format UDZO -ov "$DMG"
if [[ -n "$SIGN_IDENTITY" ]]; then
    codesign --force --timestamp --sign "$SIGN_IDENTITY" "$DMG"
    codesign --verify --strict --verbose=2 "$DMG"
fi
if [[ -n "$NOTARY_PROFILE" ]]; then
    xcrun notarytool submit "$DMG" --keychain-profile "$NOTARY_PROFILE" --wait --output-format json > "$STAGE/notary-dmg.json"
    [[ "$(jq -r '.status' "$STAGE/notary-dmg.json")" == Accepted ]] || fail "DMG notarization was not accepted."
    xcrun stapler staple "$DMG"
    xcrun stapler validate "$DMG"
fi
hdiutil verify "$DMG"
if [[ "${MACROPAD_CREATE_APP_ZIP:-0}" == "1" ]]; then
    ditto -c -k --sequesterRsrc --keepParent "$APP_BUNDLE" "$APP_ZIP"
    shasum -a 256 "$APP_ZIP"
    printf 'APP ZIP: %s\n' "$APP_ZIP"
fi
shasum -a 256 "$DMG"
printf 'APP: %s\nDMG: %s\n' "$APP_BUNDLE" "$DMG"
