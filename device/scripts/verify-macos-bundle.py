#!/usr/bin/env python3
"""Inspect a packaged MacroPad app without executing the application.

The plist, resource and Mach-O header checks are portable. --native additionally
uses Apple's lipo, otool and codesign on macOS; it does not launch the app, access
a keyboard, install hooks or claim Developer ID/notarization status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import struct
import subprocess
import sys
from pathlib import Path


class InvalidBundle(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidBundle(message)


def read_required(path: Path) -> bytes:
    require(path.is_file(), f"Required file is missing: {path}")
    data = path.read_bytes()
    require(bool(data), f"Required file is empty: {path}")
    return data


def normal_dependencies(metadata: dict) -> set[tuple[str, str]]:
    resolve = metadata.get("resolve") or {}
    root = resolve.get("root")
    require(bool(root), "Cargo metadata must describe one app root")
    nodes = {node["id"]: node for node in resolve.get("nodes", [])}
    packages = {package["id"]: package for package in metadata["packages"]}
    visited: set[str] = set()
    pending = [root]
    while pending:
        package_id = pending.pop()
        if package_id in visited:
            continue
        require(package_id in nodes, f"Missing Cargo resolve node: {package_id}")
        visited.add(package_id)
        for dependency in nodes[package_id].get("deps", []):
            if any(kind.get("kind") in (None, "normal", "build") for kind in dependency["dep_kinds"]):
                pending.append(dependency["pkg"])
    return {
        (packages[package_id]["name"], packages[package_id]["version"])
        for package_id in visited
        if package_id != root
    }


def inspect_licenses(resources: Path, metadata_path: Path | None) -> dict:
    directory = resources / "licenses"
    require(directory.is_dir(), f"License directory is missing: {directory}")
    for name in ("lucide.LICENSE.txt", "NotoSansSC.LICENSE.txt", "simple-icons.LICENSE.md"):
        read_required(directory / name)
    text_files = [path for path in directory.iterdir() if path.is_file() and path.suffix != ".json"]
    upstream_retained = any(
        "Copyright (c) 2026 Tony Huang" in path.read_text(encoding="utf-8", errors="replace")
        and "Permission is hereby granted" in path.read_text(encoding="utf-8", errors="replace")
        for path in text_files
    )
    require(upstream_retained, "The retained upstream MIT copyright/permission notice is missing")
    notices_path = directory / "Rust-dependency-licenses.json"
    notices = json.loads(read_required(notices_path))
    libraries = notices.get("third_party_libraries", [])
    require(bool(libraries), "Rust dependency notices contain no libraries")
    require(not notices.get("unresolved"), "Rust dependency notices still report unresolved source licenses")
    identities: set[tuple[str, str]] = set()
    missing_text: list[str] = []
    for library in libraries:
        identity = (library["package_name"], library["package_version"])
        identities.add(identity)
        licenses = library.get("licenses", [])
        if not licenses or any(
            not license.get("text", "").strip()
            or license["text"].strip() == "NOT FOUND"
            for license in licenses
        ):
            missing_text.append("@".join(identity))
        for license in licenses:
            if license.get("source_sha256"):
                encoding = license.get("source_encoding", "utf-8")
                original = license["text"].encode(encoding)
                require(hashlib.sha256(original).hexdigest() == license["source_sha256"],
                        f"Bundled license text hash mismatch: {'@'.join(identity)} / {license.get('source_path')}")
    require(not missing_text, "License text needs review for: " + ", ".join(sorted(missing_text)))
    require({"gpui", "gpui-component", "hidapi", "libusb1-sys"}.issubset({x[0] for x in identities}),
            "Expected desktop/native dependencies are absent from the Rust notices")
    expected_count = None
    if metadata_path:
        expected = normal_dependencies(json.loads(read_required(metadata_path)))
        missing = expected - identities
        require(not missing, "Mac normal/build dependencies absent from notices: " + ", ".join(
            "@".join(identity) for identity in sorted(missing)))
        expected_count = len(expected)
    return {
        "rust_library_count": len(identities),
        "mac_normal_and_build_dependency_count": expected_count,
        "upstream_notice_retained": upstream_retained,
        "canonical_reference_package_count": notices.get("collection", {}).get("canonical_reference_package_count", 0),
        "attribution_limitations": notices.get("attribution_limitations", []),
        "notes": "Automated source/metadata coverage check; not a manual legal review.",
    }


def native_command(arguments: list[str]) -> str:
    result = subprocess.run(arguments, capture_output=True, text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    require(result.returncode == 0, f"{' '.join(arguments)} failed: {output}")
    return output


def inspect_bundle(bundle: Path, metadata_path: Path | None, native: bool) -> dict:
    require(bundle.name == "MacroPad.app", "Expected a MacroPad.app bundle")
    contents = bundle / "Contents"
    plist = plistlib.loads(read_required(contents / "Info.plist"))
    expected = {
        "CFBundleDisplayName": "MacroPad",
        "CFBundleName": "MacroPad",
        "CFBundleExecutable": "MacroPad",
        "CFBundleIdentifier": "io.macropad.desktop",
        "CFBundlePackageType": "APPL",
    }
    for key, value in expected.items():
        require(plist.get(key) == value, f"Unexpected {key}: {plist.get(key)!r}")
    require(bool(plist.get("CFBundleShortVersionString")), "Missing app version")
    require(not plist.get("SUEnableAutomaticChecks"), "Automatic update checks must be disabled")
    require(not plist.get("SUFeedURL"), "The default bundle must not advertise an update feed")
    resources = contents / "Resources"
    icon_name = plist.get("CFBundleIconFile", "")
    require(bool(icon_name) and Path(icon_name).name == icon_name, "Invalid bundle icon filename")
    icon_path = resources / (icon_name if icon_name.endswith(".icns") else icon_name + ".icns")
    icon_data = read_required(icon_path)
    require(icon_data.startswith(b"icns"), "The bundle icon is not an ICNS resource")
    executable = contents / "MacOS" / "MacroPad"
    data = read_required(executable)
    require(len(data) >= 32 and data[:4] == b"\xcf\xfa\xed\xfe", "Expected a thin little-endian Mach-O64 executable")
    cpu_type = struct.unpack_from("<I", data, 4)[0]
    require(cpu_type == 0x0100000C, f"Expected native ARM64 code, got CPU type 0x{cpu_type:x}")
    require(struct.unpack_from("<I", data, 12)[0] == 2, "Mach-O file is not an executable image")
    require(not (contents / "Frameworks" / "Sparkle.framework").exists(), "Default package must not contain Sparkle")
    firmware = read_required(resources / "firmware" / "keyboard-fw.bin")
    manifest = json.loads(read_required(resources / "firmware" / "manifest.json"))
    firmware_sha = hashlib.sha256(firmware).hexdigest()
    require(manifest.get("sha256") == firmware_sha, "Bundled firmware does not match its manifest SHA-256")
    require(firmware_sha == "18fa7f1ef748a1ece833fd288760e8407cc51d627a75bf27183c5ea2c914c12d",
            "Bundled firmware is not the reviewed fixed 0.10.1 image")
    require(manifest.get("version") == "0.10.1", "Unexpected bundled firmware version")
    report = {
        "bundle": str(bundle.resolve()),
        "app_version": plist["CFBundleShortVersionString"],
        "architecture": "arm64",
        "executable_sha256": hashlib.sha256(data).hexdigest(),
        "firmware_sha256": firmware_sha,
        "licenses": inspect_licenses(resources, metadata_path),
        "application_launched": False,
        "native_signature_verified": False,
        "notarization": "not checked; not provided by this build workflow",
    }
    if native:
        require(sys.platform == "darwin", "--native requires macOS")
        architecture = native_command(["lipo", "-archs", str(executable)])
        require(architecture == "arm64", f"Unexpected lipo architecture: {architecture}")
        dependencies = native_command(["otool", "-L", str(executable)])
        require("Sparkle.framework" not in dependencies, "Executable still links Sparkle")
        verification = native_command(["codesign", "--verify", "--deep", "--strict", "--verbose=2", str(bundle)])
        signature = native_command(["codesign", "--display", "--verbose=4", str(bundle)])
        report["native"] = {"lipo": architecture, "dependencies": dependencies,
                            "codesign_verification": verification, "signature": signature}
        report["native_signature_verified"] = True
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = {"ok": True, **inspect_bundle(args.bundle, args.metadata, args.native)}
    except (InvalidBundle, OSError, ValueError, KeyError, TypeError) as error:
        report = {"ok": False, "error": str(error), "application_launched": False}
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
