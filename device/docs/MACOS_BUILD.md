# MacroPad for Apple Silicon

The Mac build uses the same MacroPad UI and device code as the Windows build,
with native `aarch64-apple-darwin` output. The user-facing name is MacroPad and
the bundle identifier is `io.macropad.desktop`. Theme names and upstream branding
are not added to the interface. Required license notices stay inside the app's
`Contents/Resources/licenses` directory.

## Reviewable GitHub Actions workflow

The workflow is at the repository root:
`.github/workflows/macropad-macos.yml`. A workflow under
`device/.github/workflows/` is not discovered when this project is checked out as
the `device` subdirectory of the hardware repository.

The prepared workflow:

1. Runs only on the `codex/macropad-macos` branch, by push or a manual dispatch
   selecting that branch.
2. Uses GitHub's `macos-15` standard ARM64 runner and checks `uname -m` is `arm64`.
3. Installs Rust 1.99.1 with the `aarch64-apple-darwin` target. It uses the existing
   app lockfile, records tool/Xcode/SDK versions, and limits parallel compilation
   to two jobs for the standard runner's memory budget.
4. Downloads the fixed upstream firmware 0.10.1 from the v0.15.0 release and
   checks SHA-256
   `18fa7f1ef748a1ece833fd288760e8407cc51d627a75bf27183c5ea2c914c12d`.
   It only bundles this image; it does not flash a connected keyboard.
5. Generates Rust dependency notices from the dependency sources on the Mac
   runner with pinned `cargo-bundle-licenses` 4.2.0. It also records target-filtered
   Cargo metadata so the bundle verifier can compare normal dependencies with
   the notice inventory. A missing license text stops package verification for
   review; a Windows notice inventory is not substituted.
6. Builds the release app, packages `MacroPad.app`, and produces an ARM64 DMG and
   an app ZIP. Sparkle and automatic update feeds are disabled by default.
7. Checks the plist, ARM64 Mach-O header, app icon, firmware digest and license
   resources. On the Mac runner it also uses `lipo`, `otool`, `codesign`, and
   `hdiutil` to verify the generated files. This step does not launch the app.
8. Uploads packages, SHA-256 sums and separate build records as Actions artifacts
   with 14-day retention. It does not create a GitHub Release, update the default
   branch, publish a website, use signing secrets, install agent hooks or run a
   test suite.

The workflow uses immutable commits for the official checkout and artifact
actions. The `GITHUB_TOKEN` has `contents: read`. The job is configured to stop
after 90 minutes.

## Run on a local Apple Silicon Mac

Install Rust and the Xcode command-line tools, then run from the `device`
directory:

```bash
rustup toolchain install 1.99.1 --profile minimal --target aarch64-apple-darwin
rustup override set 1.99.1
mkdir -p dist/inputs dist/licenses dist/logs
curl --fail --location \
  https://github.com/conol-ai/openmicrokbd/releases/download/v0.15.0/openmicro-fw-0.10.1.bin \
  --output dist/inputs/keyboard-fw-0.10.1.bin
printf '%s  %s\n' \
  18fa7f1ef748a1ece833fd288760e8407cc51d627a75bf27183c5ea2c914c12d \
  dist/inputs/keyboard-fw-0.10.1.bin | shasum -a 256 --check
cargo install cargo-bundle-licenses --version 4.2.0 --locked
(
  cd app
  cargo bundle-licenses --format json --prefer MIT,Apache-2.0 \
    --output ../dist/licenses/Rust-dependency-licenses.json
  cargo metadata --locked --format-version 1 --filter-platform aarch64-apple-darwin \
    > ../dist/logs/cargo-macos-metadata.json
)
MACROPAD_MACOS_ARCH=arm64 \
MACROPAD_CREATE_APP_ZIP=1 \
MACROPAD_ENABLE_SPARKLE=0 \
MACROPAD_DEPENDENCY_LICENSES_FILE="$PWD/dist/licenses/Rust-dependency-licenses.json" \
  bash scripts/package-macos.sh "$PWD/dist" "$PWD/dist/inputs/keyboard-fw-0.10.1.bin"
python3 scripts/verify-macos-bundle.py \
  --bundle dist/macos-aarch64/MacroPad.app \
  --metadata dist/logs/cargo-macos-metadata.json --native \
  --report dist/logs/bundle-verification.json
```

The repository retains its upstream MIT notice. Dependency notice generation is
an automated aid; the verifier rejects empty/`NOT FOUND` license text and missing
normal dependencies. These checks do not constitute a manual licensing review.

## Signature and validation limits

Without a configured Apple Developer signing identity, the prepared package uses
an ad-hoc signature. That can be verified for bundle integrity but is not a
Developer ID signature or Apple notarization. No notarization has been requested
or claimed. A downloaded ad-hoc app can still be blocked by Gatekeeper; Mac
distribution policy and user approval are separate from successful compilation.

The current Windows host can inspect the Python source and workflow syntax, and
can inspect a future app's plist, resource files and ARM64 header. It cannot
establish macOS compilation, native signatures, GUI behavior, accessibility
permissions or real keyboard behavior. The first Mac run must supply that
evidence before the package is described as verified on macOS.

## Remote operation requiring approval

No workflow run is started by preparing these files. To obtain a native Mac
build, the pending remote operation is to push the reviewed local commit to
`origin` as `refs/heads/codex/macropad-macos` in
`mayiwei442-bojack/hardware`. That push uploads the included source to the public
repository and triggers this workflow on a GitHub-hosted Mac. The intended
result is an Actions artifact; no Release is published. The branch, exact commit
and included diff must be shown before that push is approved. A later manual
retry would dispatch `macropad-macos.yml` against that same branch only.

## Sources checked for this workflow

- [GitHub-hosted runner labels and architecture](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Official checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
- [Official upload-artifact v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2)
- [cargo-bundle-licenses 4.2.0 CLI source](https://github.com/sstadick/cargo-bundle-licenses/blob/v4.2.0/src/main.rs)
- [License inventory dependency traversal](https://github.com/sstadick/cargo-bundle-licenses/blob/v4.2.0/src/package_loader.rs)
