#!/usr/bin/env python3
"""Collect source notices and explicitly identified SPDX references for Cargo.

Input must be metadata produced with --filter-platform aarch64-apple-darwin.
Normal and build dependencies are followed; dev-only dependencies are omitted.
SPDX declarations are copied verbatim from Cargo metadata. Verified upstream
recovery and canonical SPDX references require separate provenance records.
Canonical references are labeled as references, never as recovered upstream
copyright text; the original Cargo manifest and author metadata are retained.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path


LICENSE_NAME = re.compile(r"^(?:licen[cs]e|copying|notice|unlicense|copyright)(?:$|[._-])", re.I)
EXCLUDED_DIRECTORIES = {".git", "target", "node_modules", ".history"}


def dependency_packages(metadata: dict) -> list[dict]:
    resolve = metadata.get("resolve") or {}
    root = resolve.get("root")
    if not root:
        raise ValueError("Cargo metadata must have one package root")
    nodes = {node["id"]: node for node in resolve["nodes"]}
    packages = {package["id"]: package for package in metadata["packages"]}
    seen: set[str] = set()
    pending = [root]
    while pending:
        package_id = pending.pop()
        if package_id in seen:
            continue
        seen.add(package_id)
        if package_id not in nodes:
            raise ValueError(f"Missing dependency resolve node: {package_id}")
        for dep in nodes[package_id].get("deps", []):
            if any(item.get("kind") in (None, "normal", "build") for item in dep.get("dep_kinds", [])):
                pending.append(dep["pkg"])
    return sorted((packages[item] for item in seen if item != root),
                  key=lambda package: (package["name"], package["version"], package["id"]))


def within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def candidates(package: dict) -> list[Path]:
    manifest = Path(package["manifest_path"])
    if not manifest.is_file():
        raise ValueError(f"Cargo source manifest is unavailable: {manifest}")
    root = manifest.parent.resolve()
    found: set[Path] = set()
    declared = package.get("license_file")
    if declared:
        explicit = (root / declared).resolve()
        # A local workspace crate may explicitly share its parent LICENSE.
        allowed_root = root if package.get("source") else root.parent
        if not within(explicit, allowed_root):
            raise ValueError(f"Declared license path escapes the source scope: {explicit}")
        if explicit.is_file():
            found.add(explicit)
    for directory, names, files in os.walk(root, followlinks=False):
        names[:] = [name for name in names if name not in EXCLUDED_DIRECTORIES
                    and not (Path(directory) / name).is_symlink()]
        parent = Path(directory)
        in_license_dir = any(part.lower() in {"licenses", "licences"}
                             for part in parent.relative_to(root).parts)
        for name in files:
            file = parent / name
            if file.is_symlink():
                continue
            if LICENSE_NAME.match(name) or (in_license_dir and file.suffix.lower() in {"", ".txt", ".md", ".rst"}):
                found.add(file.resolve())
    return sorted(found, key=str)


def text_record(path: Path, package: dict) -> dict:
    raw = path.read_bytes()
    if not raw.strip():
        raise ValueError(f"Empty license source: {path}")
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError(f"License source exceeds 8 MiB; review manually: {path}")
    if raw.startswith(b"\xff\xfe"):
        encoding = "utf-16-le"
    elif raw.startswith(b"\xfe\xff"):
        encoding = "utf-16-be"
    else:
        try:
            raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "latin-1"
    text = raw.decode(encoding)
    root = Path(package["manifest_path"]).parent.resolve()
    return {
        "license": package.get("license") or "LicenseRef-Declared-License-File",
        "text": text,
        "source_path": str(path),
        "source_relative_path": os.path.relpath(path, root).replace("\\", "/"),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "source_encoding": encoding,
        "spdx_assignment": "Package declaration copied from Cargo metadata; no per-file inference",
    }


def source_overrides(package: dict, directory: Path) -> list[dict]:
    package_directory = directory / f"{package['name']}-{package['version']}"
    provenance_path = package_directory / "PROVENANCE.json"
    if not provenance_path.is_file():
        return []
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("package_name") != package["name"] or provenance.get("package_version") != package["version"]:
        raise ValueError(f"Notice provenance package/version mismatch: {provenance_path}")
    canonical = provenance.get("acquisition") == "canonical-spdx-reference"
    commit = provenance.get("source_commit") or ""
    if not re.fullmatch(r"[a-fA-F0-9]{40}", commit) and not (canonical and not commit):
        raise ValueError(f"Notice provenance must pin a full source commit: {provenance_path}")
    license_commit = provenance.get("license_source_commit") or commit
    if not re.fullmatch(r"[a-fA-F0-9]{40}", license_commit):
        raise ValueError(f"Notice provenance must pin the actual license source commit: {provenance_path}")
    if canonical and not provenance.get("upstream_notice_status"):
        raise ValueError(f"Canonical SPDX reference must explicitly describe the missing upstream notice: {provenance_path}")
    vcs_path = Path(package["manifest_path"]).parent / ".cargo_vcs_info.json"
    if vcs_path.is_file():
        crate_commit = json.loads(vcs_path.read_text(encoding="utf-8")).get("git", {}).get("sha1")
        if crate_commit and commit.lower() != crate_commit.lower():
            raise ValueError(f"Notice source commit does not match packaged .cargo_vcs_info: {provenance_path}")
    records = []
    for item in provenance.get("files", []):
        path = (package_directory / item["file"]).resolve()
        if not within(path, package_directory.resolve()) or path.is_symlink():
            raise ValueError(f"Unsafe notice override path: {path}")
        source_url = item.get("source_url", "")
        archive_source = item.get("origin") == "crate-archive"
        if not archive_source and (not source_url.startswith("https://") or license_commit.lower() not in source_url.lower()):
            raise ValueError(f"Notice URL must point to the pinned HTTPS source commit: {path}")
        record = text_record(path, package)
        if record["source_sha256"] != item.get("sha256", "").lower():
            raise ValueError(f"Notice override SHA-256 mismatch: {path}")
        if archive_source:
            root = Path(package["manifest_path"]).parent.resolve()
            original = (root / item.get("crate_source_path", item["file"])).resolve()
            if not within(original, root) or not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != record["source_sha256"]:
                raise ValueError(f"Archived declaration does not match the actual crate source: {path}")
            record["origin"] = "crate-archive"
            record["original_crate_source_path"] = str(original)
        record.update({"source_url": source_url, "source_commit": commit,
                       "license_source_commit": license_commit,
                       "source_provenance_path": str(provenance_path),
                       "source_provenance_sha256": hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
                       "acquisition": ("canonical-spdx-reference" if canonical else
                                       "Original version-pinned upstream source file omitted from crate archive")})
        if canonical:
            record["upstream_notice_status"] = provenance["upstream_notice_status"]
            record["attribution_note"] = provenance.get("attribution_note", "Upstream package declares its license but ships no standalone license text. Canonical SPDX text is included for reference, not represented as recovered upstream text. Attribution is copied from the original Cargo manifest.")
            record["upstream_authors"] = package.get("authors", [])
        if license_commit.lower() != commit.lower() and not canonical:
            record["source_recovery_limitations"] = {key: value for key, value in provenance.items()
                if key in {"source_equivalence", "source_commit_unavailable", "historical_license_basis", "notes", "limitations"}}
        records.append(record)
    if canonical:
        declaration = text_record(Path(package["manifest_path"]), package)
        declaration["acquisition"] = "Original crate Cargo manifest; declared license and authors, not a standalone license text"
        records.append(declaration)
    if not records:
        raise ValueError(f"Notice provenance contains no source files: {provenance_path}")
    return records


def collect(metadata_path: Path, overrides: Path) -> dict:
    raw_metadata = metadata_path.read_bytes()
    metadata = json.loads(raw_metadata)
    libraries: list[dict] = []
    unresolved: list[dict] = []
    for package in dependency_packages(metadata):
        entry = {
            "package_name": package["name"],
            "package_version": package["version"],
            "repository": package.get("repository") or "",
            "authors": package.get("authors", []),
            "license": package.get("license"),
            "source": package.get("source"),
            "manifest_path": package["manifest_path"],
            "licenses": [],
        }
        try:
            files = candidates(package)
            entry["licenses"] = [text_record(file, package) for file in files]
            if not files:
                entry["licenses"] = source_overrides(package, overrides)
            if not entry["licenses"]:
                raise ValueError("No license source was shipped in the crate, and no verified version-pinned upstream notice override is available")
        except (OSError, ValueError) as error:
            unresolved.append({"package_name": package["name"], "package_version": package["version"],
                               "license": package.get("license"), "manifest_path": package["manifest_path"],
                               "repository": package.get("repository"), "reason": str(error)})
        libraries.append(entry)
    root_id = metadata["resolve"]["root"]
    root = next(package for package in metadata["packages"] if package["id"] == root_id)
    canonical_libraries = [library for library in libraries if any(
        license.get("acquisition") == "canonical-spdx-reference" for license in library["licenses"])]
    limitations = []
    for library in libraries:
        notes = [license.get("attribution_note") or license.get("source_recovery_limitations")
                 for license in library["licenses"]
                 if license.get("attribution_note") or license.get("source_recovery_limitations")]
        if notes:
            unique = list({json.dumps(note, sort_keys=True): note for note in notes}.values())
            limitations.append({"package_name": library["package_name"],
                                "package_version": library["package_version"], "notes": unique})
    return {
        "root_name": root["name"],
        "schema": "macropad-source-license-inventory-v1",
        "collection": {
            "method": "Original source notices, version-pinned upstream recoveries, and explicitly labeled canonical SPDX reference fallbacks; no invented upstream copyright statements",
            "dependency_scope": "Reachable normal and build dependencies, excluding dev-only edges",
            "platform_scope": "Caller-provided Cargo metadata platform filter",
            "metadata_sha256": hashlib.sha256(raw_metadata).hexdigest(),
            "package_count": len(libraries),
            "license_file_count": sum(len(library["licenses"]) for library in libraries),
            "canonical_reference_package_count": len(canonical_libraries),
            "historical_license_recovery_package_count": sum(any(
                license.get("source_recovery_limitations") for license in library["licenses"])
                for library in libraries),
        },
        "third_party_libraries": libraries,
        "attribution_limitations": limitations,
        "unresolved": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--notice-overrides", type=Path,
                        default=Path(__file__).resolve().parents[1] / "app/resources/dependency-notices")
    args = parser.parse_args()
    try:
        result = collect(args.metadata, args.notice_overrides)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Collected {result['collection']['license_file_count']} source notice/declaration/reference records for "
              f"{result['collection']['package_count']} dependencies; "
              f"{result['collection']['canonical_reference_package_count']} packages use explicitly labeled canonical SPDX references")
        if result["unresolved"]:
            for item in result["unresolved"]:
                print(f"UNRESOLVED {item['package_name']}@{item['package_version']}: {item['reason']}", file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"License collection failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
