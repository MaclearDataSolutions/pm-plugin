#!/usr/bin/env python3
"""Archive processed project update source files safely.

This script is intentionally conservative. It prefers files listed in
update_sources_manifest.json, falls back to a known Updates folder, never deletes
files permanently, and writes a human-readable archive log.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

KNOWN_UPDATE_FOLDERS = [
    "Updates",
    "updates",
    "Project_Updates",
    "project_updates",
    "Change_Requests",
    "change_requests",
]

GENERATED_NAMES = {
    "update.md",
    "update_conflict_log.md",
    "update_sources_manifest.json",
    "plan_update_request.md",
    "plan_change_impact.md",
    "plan_change_manifest.json",
    "project_plan.md",
    "gantt_tasks.csv",
    "gantt_chart.md",
    "artifact_update_report.md",
    "update_archive_log.md",
}

GENERATED_SUFFIXES = {".pptx", ".xlsx", ".xlsm"}
PROTECTED_DIRS = {".git", ".claude", "Archive", "archive"}


def load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not parse manifest JSON: {path} ({exc})")


def find_update_folder(project_root: Path, manifest: Any | None, explicit: str | None) -> Path | None:
    if explicit:
        return (project_root / explicit).resolve()

    keys = {
        "selected_update_folder",
        "selected_updates_folder",
        "updates_folder",
        "update_folder",
        "source_folder",
        "chosen_update_folder",
        "input_folder",
    }

    def walk(obj: Any) -> Path | None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in keys and isinstance(value, str):
                    candidate = (project_root / value).resolve()
                    if candidate.exists() and candidate.is_dir():
                        return candidate
            for value in obj.values():
                found = walk(value)
                if found:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = walk(item)
                if found:
                    return found
        return None

    found = walk(manifest) if manifest is not None else None
    if found:
        return found

    for name in KNOWN_UPDATE_FOLDERS:
        candidate = (project_root / name).resolve()
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def collect_manifest_paths(project_root: Path, update_folder: Path | None, manifest: Any | None) -> list[Path]:
    if manifest is None:
        return []

    path_keys = {
        "path",
        "file",
        "file_path",
        "source",
        "source_file",
        "filename",
        "name",
        "relative_path",
    }
    results: list[Path] = []

    def maybe_path(value: str) -> Path | None:
        text = value.strip()
        if not text or text in GENERATED_NAMES:
            return None
        # Ignore obvious non-path prose.
        if len(text) > 260 or "\n" in text:
            return None
        candidates = []
        p = Path(text)
        if p.is_absolute():
            candidates.append(p)
        else:
            candidates.append(project_root / p)
            if update_folder is not None:
                candidates.append(update_folder / p)
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate.resolve()
        return None

    def walk(obj: Any, key_hint: str | None = None) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and key in path_keys:
                    found = maybe_path(value)
                    if found:
                        results.append(found)
                else:
                    walk(value, key)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, key_hint)
        elif isinstance(obj, str) and key_hint in path_keys:
            found = maybe_path(obj)
            if found:
                results.append(found)

    walk(manifest)

    # De-duplicate while preserving order.
    deduped: list[Path] = []
    seen = set()
    for path in results:
        if path not in seen:
            deduped.append(path)
            seen.add(path)
    return deduped


def is_safe_source(path: Path, project_root: Path, update_folder: Path | None) -> bool:
    try:
        rel_to_project = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return False
    if any(part in PROTECTED_DIRS for part in rel_to_project.parts):
        return False
    if path.name in GENERATED_NAMES:
        return False
    if path.suffix.lower() in GENERATED_SUFFIXES:
        return False
    if update_folder is not None:
        try:
            path.resolve().relative_to(update_folder.resolve())
        except ValueError:
            return False
    return path.is_file()


def collect_folder_files(update_folder: Path, project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in update_folder.rglob("*"):
        if path.is_file() and is_safe_source(path, project_root, update_folder):
            files.append(path.resolve())
    return sorted(files)


def unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def write_log(
    log_path: Path,
    timestamp: str,
    update_folder: Path | None,
    archive_destination: Path,
    moved: list[tuple[Path, Path]],
    skipped: list[str],
    missing: list[str],
    dry_run: bool,
) -> None:
    mode = "Dry run" if dry_run else "Archive run"
    lines = [
        f"# Update Archive Log",
        "",
        f"## {mode}: {timestamp}",
        "",
        f"- Source folder: `{update_folder if update_folder else 'Not identified'}`",
        f"- Archive destination: `{archive_destination}`",
        "",
        "## Files moved" if not dry_run else "## Files that would be moved",
        "",
    ]
    if moved:
        for src, dst in moved:
            lines.append(f"- `{src}` -> `{dst}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Files skipped", ""])
    if skipped:
        for item in skipped:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Files missing", ""])
    if missing:
        for item in missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Restore instructions",
        "",
        "To restore archived files, move the listed files from the archive destination back to the source folder, preserving the relative paths shown above.",
        "",
    ])
    previous = ""
    if log_path.exists():
        previous = log_path.read_text(encoding="utf-8") + "\n\n---\n\n"
    log_path.write_text(previous + "\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive processed project update files safely.")
    parser.add_argument("--manifest", default="update_sources_manifest.json", help="Path to update source manifest JSON.")
    parser.add_argument("--updates-folder", help="Updates folder to archive from when no manifest is available.")
    parser.add_argument("--archive-root", default="Archive", help="Archive root folder.")
    parser.add_argument("--log", default="update_archive_log.md", help="Archive log path.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would move without moving files.")
    parser.add_argument("--copy-only", action="store_true", help="Copy files instead of moving them.")
    args = parser.parse_args()

    project_root = Path.cwd().resolve()
    manifest_path = (project_root / args.manifest).resolve()
    manifest = load_json(manifest_path)
    update_folder = find_update_folder(project_root, manifest, args.updates_folder)

    if update_folder is None or not update_folder.exists():
        raise SystemExit("No Updates folder found. Provide --updates-folder or create update_sources_manifest.json.")

    files = collect_manifest_paths(project_root, update_folder, manifest)
    if not files:
        files = collect_folder_files(update_folder, project_root)

    safe_files: list[Path] = []
    skipped: list[str] = []
    missing: list[str] = []

    for path in files:
        if not path.exists():
            missing.append(str(path))
        elif is_safe_source(path, project_root, update_folder):
            safe_files.append(path.resolve())
        else:
            skipped.append(f"`{path}` was outside the selected update folder, generated output, or protected.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_destination = (project_root / args.archive_root / "updates" / timestamp).resolve()
    moved: list[tuple[Path, Path]] = []

    for src in safe_files:
        rel = src.relative_to(update_folder.resolve())
        dst = unique_destination(archive_destination / rel)
        moved.append((src, dst))
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if args.copy_only:
                shutil.copy2(src, dst)
            else:
                shutil.move(str(src), str(dst))

    write_log(
        (project_root / args.log).resolve(),
        timestamp,
        update_folder,
        archive_destination,
        moved,
        skipped,
        missing,
        args.dry_run,
    )

    action = "would archive" if args.dry_run else ("copied" if args.copy_only else "archived")
    print(f"{action}: {len(moved)} file(s)")
    print(f"archive_destination: {archive_destination}")
    print(f"log: {(project_root / args.log).resolve()}")
    if skipped:
        print(f"skipped: {len(skipped)}")
    if missing:
        print(f"missing: {len(missing)}")


if __name__ == "__main__":
    main()
