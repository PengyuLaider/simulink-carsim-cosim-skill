#!/usr/bin/env python3
"""Hash an explicit source inventory and detect local drift. Not a signature service."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

SCHEMA = "cosim-source-manifest/v1"


def relative_name(value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value or ":" in value:
        raise ValueError("Selections must be nonempty relative paths.")
    value = value.replace("\\", "/")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value in (".", "./"):
        raise ValueError("Absolute, root and parent-traversal selections are not allowed.")
    if not path.parts:
        raise ValueError("Empty selection.")
    return path.as_posix()


def checked_path(root: Path, name: str) -> Path:
    candidate = root
    for component in PurePosixPath(relative_name(name)).parts:
        candidate = candidate / component
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        if stat.S_ISLNK(info.st_mode) or reparse:
            raise ValueError("Symlink/reparse-point selections are not supported: " + name)
    if not candidate.resolve().is_relative_to(root):
        raise ValueError("Selection escapes the project root.")
    return candidate


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def signature(payload: dict) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path, includes: list[str], *, allow_missing: bool = False) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory.")
    names = sorted({relative_name(name) for name in includes})
    if not names:
        raise ValueError("Select at least one source file or directory.")
    selected: set[Path] = set()
    for name in names:
        entry = checked_path(root, name)
        if not entry.exists():
            if allow_missing:
                continue
            raise ValueError("Missing selected input: " + name)
        if entry.is_file():
            selected.add(entry)
            continue
        if not entry.is_dir():
            raise ValueError("Selected input is not a regular file/directory: " + name)
        count = 0
        def walk_error(error):
            raise error
        for base, dirs, files in os.walk(entry, followlinks=False, onerror=walk_error):
            for child in sorted(dirs + files):
                rel = (Path(base) / child).relative_to(root).as_posix()
                resolved = checked_path(root, rel)
                if resolved.is_file():
                    selected.add(resolved)
                    count += 1
                elif not resolved.is_dir():
                    raise ValueError("Unsupported selected file: " + rel)
        if count == 0 and not allow_missing:
            raise ValueError("Empty selected directory: " + name)
    rows = []
    folded = {}
    for path in sorted(selected, key=lambda item: item.relative_to(root).as_posix()):
        name = path.relative_to(root).as_posix()
        old = folded.setdefault(name.casefold(), name)
        if old != name:
            raise ValueError("Case-colliding paths are not portable: " + name)
        rows.append({"path": name, "sha256": digest(path), "size_bytes": path.stat().st_size})
    if not rows and not allow_missing:
        raise ValueError("Source inventory is empty.")
    payload = {"schema": SCHEMA, "includes": names, "files": rows}
    return {**payload, "signature": signature(payload)}


def read_manifest(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict) or set(value) != {"schema", "includes", "files", "signature"}:
        raise ValueError("Invalid manifest fields.")
    if value["schema"] != SCHEMA or not isinstance(value["includes"], list) or not value["includes"]:
        raise ValueError("Invalid manifest schema/selections.")
    names = value["includes"]
    if names != sorted({relative_name(name) for name in names}):
        raise ValueError("Manifest selections are not canonical.")
    rows = value["files"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Manifest must contain source files.")
    paths = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "sha256", "size_bytes"}:
            raise ValueError("Invalid file record.")
        name = relative_name(row["path"])
        if name != row["path"] or not any(name == inc or name.startswith(inc + "/") for inc in names):
            raise ValueError("File is outside manifest selections.")
        if not isinstance(row["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None:
            raise ValueError("Invalid SHA256.")
        if type(row["size_bytes"]) is not int or row["size_bytes"] < 0:
            raise ValueError("Invalid file size.")
        paths.append(name)
    if paths != sorted(set(paths)) or len({p.casefold() for p in paths}) != len(paths):
        raise ValueError("Duplicate, unsorted or case-colliding records.")
    payload = {key: value[key] for key in ("schema", "includes", "files")}
    if value["signature"] != signature(payload):
        raise ValueError("Manifest checksum is invalid.")
    return value


def differences(before: dict, after: dict) -> dict:
    old = {row["path"]: row for row in before["files"]}
    new = {row["path"]: row for row in after["files"]}
    return {"added": sorted(new.keys() - old.keys()),
            "removed": sorted(old.keys() - new.keys()),
            "modified": sorted(name for name in old.keys() & new.keys() if old[name] != new[name])}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("snapshot")
    create.add_argument("--root", type=Path, required=True)
    create.add_argument("--include", action="append", required=True)
    create.add_argument("--out", type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("--root", type=Path, required=True)
    check.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            result = snapshot(args.root, args.include)
            output = args.out.resolve()
            for name in result["includes"]:
                selected = checked_path(args.root.resolve(), name)
                if output == selected or (selected.is_dir() and output.is_relative_to(selected)):
                    raise ValueError("Store the manifest outside selected source inputs.")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(json.dumps({"status": "SNAPSHOT_CREATED", "files": len(result["files"]),
                              "signature": result["signature"]}))
            return 0
        before = read_manifest(args.manifest)
        after = snapshot(args.root, before["includes"], allow_missing=True)
        changes = differences(before, after)
        same = not any(changes.values())
        print(json.dumps({"status": "MATCH" if same else "DRIFT", **changes,
                          "signature": after["signature"]}, ensure_ascii=False))
        return 0 if same else 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"status": "INVALID", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
