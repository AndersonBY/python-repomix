#!/usr/bin/env python3
"""
Release automation script for repomix.

This script helps automate the release process by:
1. Updating version numbers
2. Creating git tags
3. Pushing to trigger the release workflow
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("Error: Version not found in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml and __init__.py"""
    # Update pyproject.toml
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    # Only update the project version in the [project] section
    content = re.sub(r'(\[project\][\s\S]*?)version = "[^"]+"', f'\\1version = "{new_version}"', content)
    pyproject_path.write_text(content)
    print(f"Updated pyproject.toml version to {new_version}")

    # Update __init__.py
    init_path = Path("src/repomix/__init__.py")
    if init_path.exists():
        content = init_path.read_text()
        content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
        init_path.write_text(content)
        print(f"Updated __init__.py version to {new_version}")


def update_changelog(new_version: str) -> None:
    """Move Unreleased content to new version section in CHANGELOG.md"""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("Warning: CHANGELOG.md not found, skipping changelog update")
        return

    content = changelog_path.read_text(encoding="utf-8")

    # Check if version already exists
    if f"## [{new_version}]" in content:
        print(f"Version {new_version} already exists in CHANGELOG.md")
        return

    # Find Unreleased section
    import re

    unreleased_match = re.search(r"(## \[Unreleased\])(.*?)(?=\n## \[|$)", content, re.DOTALL)

    if not unreleased_match:
        print("Warning: [Unreleased] section not found in CHANGELOG.md")
        return

    unreleased_content = unreleased_match.group(2).strip()

    if not unreleased_content:
        print("Warning: [Unreleased] section is empty")
        return

    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")

    # Create new version section
    new_section = f"\n\n## [{new_version}] - {today}\n\n{unreleased_content}"

    # Replace content: keep Unreleased header but empty its content
    new_content = content.replace(unreleased_match.group(0), f"## [Unreleased]{new_section}")

    changelog_path.write_text(new_content, encoding="utf-8")
    print(f"Updated CHANGELOG.md: moved Unreleased content to [{new_version}]")


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semantic version string"""
    try:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError("Version must have 3 parts")
        return tuple(int(part) for part in parts)
    except ValueError as e:
        print(f"Error parsing version '{version}': {e}")
        sys.exit(1)


def increment_version(current: str, bump_type: str) -> str:
    """Increment version based on bump type"""
    major, minor, patch = parse_version(current)

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        print(f"Error: Invalid bump type '{bump_type}'. Use patch, minor, or major.")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"Command failed: {result.stderr}")
        sys.exit(1)

    return result


def check_git_status() -> None:
    """Check if git working directory is clean"""
    result = run_command(["git", "status", "--porcelain"])
    if result.stdout.strip():
        print("Error: Git working directory is not clean. Please commit or stash changes.")
        sys.exit(1)


def create_and_push_tag(version: str, dry_run: bool = False) -> None:
    """Create and push git tag"""
    tag_name = f"v{version}"

    if not dry_run:
        # Commit version changes
        run_command(["git", "add", "pyproject.toml", "src/repomix/__init__.py", "CHANGELOG.md"])
        run_command(["git", "commit", "-m", f"bump: version {version}"])

        # Create tag
        run_command(["git", "tag", "-a", tag_name, "-m", f"Release {version}"])

        # Push changes and tag
        run_command(["git", "push"])
        run_command(["git", "push", "origin", tag_name])

        print(f"✅ Created and pushed tag {tag_name}")
        print("🚀 Release workflow should start automatically!")
    else:
        print(f"[DRY RUN] Would create tag: {tag_name}")


def main():
    parser = argparse.ArgumentParser(description="Release automation for repomix")
    parser.add_argument("bump_type", choices=["patch", "minor", "major"], help="Type of version bump")
    parser.add_argument("--version", help="Specific version to set (overrides bump_type)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    # Check git status
    if not args.dry_run:
        check_git_status()

    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    # Determine new version
    if args.version:
        new_version = args.version
        # Validate version format
        parse_version(new_version)
    else:
        new_version = increment_version(current_version, args.bump_type)

    print(f"New version: {new_version}")

    if not args.dry_run:
        # Confirm release
        if not args.yes:
            response = input(f"Release version {new_version}? (y/N): ")
            if response.lower() != "y":
                print("Release cancelled")
                sys.exit(0)

        # Update version files
        update_version(new_version)

        # Update CHANGELOG
        update_changelog(new_version)
    else:
        print("[DRY RUN] Would update version files and CHANGELOG")

    # Create and push tag
    create_and_push_tag(new_version, args.dry_run)


if __name__ == "__main__":
    main()
