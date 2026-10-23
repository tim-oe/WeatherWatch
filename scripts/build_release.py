#!/usr/bin/env python3
"""Build a WeatherWatch deployment archive.

Reads the version from pyproject.toml and packs the runtime tree into
build/release/weatherwatch-<version>.tar.gz. The archive extracts to a
WeatherWatch/ directory that can be placed at /opt/WeatherWatch.
"""

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ARCHIVE_ROOT = "WeatherWatch"
RUNTIME_DIRS = (
    "weatherwatch",
    "config",
    "systemd",
    "sql",
    "scripts",
    "static",
    "assets",
)
RUNTIME_FILES = (
    "pyproject.toml",
    "poetry.lock",
    "poetry.toml",
    "setup.py",
    "README.md",
    ".pyway.conf",
)


def get_version() -> str:
    """Return the package version from [tool.poetry]."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found", file=sys.stderr)
        sys.exit(1)

    with pyproject_path.open("rb") as handle:
        pyproject = tomllib.load(handle)

    version = pyproject.get("tool", {}).get("poetry", {}).get("version")
    if not version:
        print("Error: version not found in pyproject.toml [tool.poetry]", file=sys.stderr)
        sys.exit(1)
    return version


def build_release(version: str | None = None) -> int:
    """Assemble the release directory and tar it."""
    if version is None:
        version = get_version()

    archive_name = f"weatherwatch-{version}.tar.gz"
    build_dir = Path("build/release")
    release_dir = build_dir / ARCHIVE_ROOT
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.log")

    print("=== Building WeatherWatch Release Package ===")
    print(f"Version: {version} (from pyproject.toml)")
    print(f"Archive: {archive_name}")
    print()

    print("[1/4] Cleaning previous builds...")
    if build_dir.parent.exists():
        shutil.rmtree(build_dir.parent)
    release_dir.mkdir(parents=True)

    print("[2/4] Copying runtime files...")
    for directory in RUNTIME_DIRS:
        print(f"  - {directory}/")
        shutil.copytree(directory, release_dir / directory, ignore=ignore)

    for filename in RUNTIME_FILES:
        print(f"  - {filename}")
        shutil.copy(filename, release_dir / filename)

    print("[3/4] Cleaning Python cache files...")
    for pattern in ("__pycache__", "*.pyc", "*.pyo"):
        for path in release_dir.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    print("[4/4] Creating release archive...")
    subprocess.run(
        ["tar", "-czf", archive_name, ARCHIVE_ROOT],
        cwd=build_dir,
        check=True,
    )

    archive_path = build_dir / archive_name
    size_bytes = archive_path.stat().st_size
    size_kb = size_bytes / 1024
    size = f"{size_kb:.0f}K" if size_kb < 1024 else f"{size_kb / 1024:.1f}M"

    print()
    print("=== Release Package Created ===")
    print(f"Package: {archive_path}")
    print(f"Size: {size}")
    print()
    print("Archive structure:")
    print("  WeatherWatch/")
    print("  ├── weatherwatch/   (application)")
    print("  ├── config/")
    print("  ├── systemd/")
    print("  ├── sql/")
    print("  ├── pyproject.toml")
    print("  └── poetry.lock")
    print()
    print("Build complete!")
    return 0


def usage() -> None:
    """Print the command syntax."""
    print(
        "Usage: ./scripts/build_release.py\n"
        "\n"
        "Pack the runtime tree into build/release/weatherwatch-<version>.tar.gz.\n"
        "The version is read from pyproject.toml. This script takes no arguments."
    )


def main() -> int:
    """Entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1:] == ["-h"] or sys.argv[1:] == ["--help"]:
            usage()
            return 0
        usage()
        return 1
    return build_release(get_version())


if __name__ == "__main__":
    sys.exit(main())
