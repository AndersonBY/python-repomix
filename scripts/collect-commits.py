#!/usr/bin/env python3
"""
Git Commits Collector for Changelog Generation

This script collects all git commits since the last release and formats them
for easy processing by Claude Code to generate CHANGELOG.md entries.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str]) -> Tuple[bool, str]:
    """Run a git command and return success status and output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def get_latest_tag() -> str | None:
    """Get the latest git tag"""
    success, output = run_command(["git", "describe", "--tags", "--abbrev=0"])
    if success and output:
        return output
    return None


def get_commits_since_tag(tag: str | None = None, max_count: int | None = None) -> List[dict]:
    """Get all commits since the specified tag (or all commits if no tag)"""
    if tag:
        cmd = ["git", "log", f"{tag}..HEAD", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]
    else:
        cmd = ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]

    # Add max count limit if specified
    if max_count:
        cmd.extend(["-n", str(max_count)])

    success, output = run_command(cmd)
    if not success:
        print(f"Error getting commits: {output}")
        return []

    commits = []
    for line in output.split("\n"):
        if line.strip():
            parts = line.split("|", 4)
            if len(parts) == 5:
                commits.append(
                    {
                        "hash": parts[0][:8],  # Short hash
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4],
                    }
                )

    return commits


def categorize_commit(message: str) -> str:
    """Categorize commit based on conventional commit patterns"""
    message_lower = message.lower()

    # Conventional commit prefixes
    if message_lower.startswith(("feat:", "feature:")):
        return "Added"
    elif message_lower.startswith("fix:"):
        return "Fixed"
    elif message_lower.startswith(("docs:", "doc:")):
        return "Documentation"
    elif message_lower.startswith(("style:", "fmt:", "format:")):
        return "Style"
    elif message_lower.startswith(("refactor:", "refact:")):
        return "Changed"
    elif message_lower.startswith(("test:", "tests:")):
        return "Tests"
    elif message_lower.startswith(("chore:", "build:", "ci:")):
        return "Maintenance"
    elif message_lower.startswith("perf:"):
        return "Performance"
    elif message_lower.startswith(("security:", "sec:")):
        return "Security"
    elif message_lower.startswith(("break:", "breaking:")):
        return "Breaking Changes"
    elif message_lower.startswith("revert:"):
        return "Reverted"

    # Keyword-based categorization
    elif any(word in message_lower for word in ["add", "new", "create", "implement", "introduce"]):
        return "Added"
    elif any(word in message_lower for word in ["fix", "bug", "resolve", "correct", "patch"]):
        return "Fixed"
    elif any(word in message_lower for word in ["update", "change", "modify", "improve", "enhance"]):
        return "Changed"
    elif any(word in message_lower for word in ["remove", "delete", "drop"]):
        return "Removed"
    elif any(word in message_lower for word in ["deprecate"]):
        return "Deprecated"
    else:
        return "Other"


def generate_commit_summary(commits: List[dict], latest_tag: str | None, max_count: int | None = None) -> str:
    """Generate a markdown summary of commits for Claude to process"""

    if not commits:
        return "No commits found since the last release."

    # Group commits by category
    categorized = {}
    contributors = set()

    for commit in commits:
        category = categorize_commit(commit["message"])
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(commit)
        contributors.add(commit["author"])

    # Generate markdown
    md_content = []
    md_content.append("# Git Commits Summary for Changelog Generation")
    md_content.append("")
    md_content.append(f"**Collection Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if latest_tag:
        md_content.append(f"**Since Tag**: {latest_tag}")
    else:
        md_content.append("**Since**: Repository start (no previous tags)")

    if max_count:
        md_content.append(f"**Limit**: Last {max_count} commits")

    md_content.append(f"**Total Commits**: {len(commits)}")
    md_content.append(f"**Contributors**: {len(contributors)}")
    md_content.append("")

    # Add instructions for Claude
    md_content.append("## Instructions for Claude Code")
    md_content.append("")
    md_content.append("Please help me convert these git commits into a proper CHANGELOG.md entry following these guidelines:")
    md_content.append("")
    md_content.append("1. **Format**: Use [Keep a Changelog](https://keepachangelog.com/) format")
    md_content.append("2. **Categories**: Group changes into Added, Changed, Fixed, Deprecated, Removed, Security")
    md_content.append("3. **User Focus**: Write descriptions from a user's perspective, not technical implementation details")
    md_content.append("4. **Combine Similar**: Merge related commits into single, clear bullet points")
    md_content.append("5. **Skip Internal**: Ignore purely internal changes like formatting, minor refactoring unless they impact users")
    md_content.append("6. **Highlight Important**: Emphasize breaking changes, major new features, and important bug fixes")
    md_content.append("")
    md_content.append("Expected output format:")
    md_content.append("```markdown")
    md_content.append("## [X.X.X] - YYYY-MM-DD")
    md_content.append("")
    md_content.append("### Added")
    md_content.append("- New feature description")
    md_content.append("")
    md_content.append("### Fixed")
    md_content.append("- Bug fix description")
    md_content.append("```")
    md_content.append("")

    # Add commits by category
    md_content.append("## Commits by Category")
    md_content.append("")

    # Define category order
    category_order = [
        "Breaking Changes",
        "Added",
        "Changed",
        "Fixed",
        "Security",
        "Performance",
        "Deprecated",
        "Removed",
        "Documentation",
        "Tests",
        "Style",
        "Maintenance",
        "Reverted",
        "Other",
    ]

    for category in category_order:
        if category in categorized:
            md_content.append(f"### {category}")
            md_content.append("")
            for commit in categorized[category]:
                md_content.append(f"- **{commit['hash']}** ({commit['author']}): {commit['message']}")
                md_content.append(f"  *Date: {commit['date'][:10]}*")
            md_content.append("")

    # Add all commits chronologically
    md_content.append("## All Commits (Chronological)")
    md_content.append("")
    for commit in commits:
        md_content.append(f"- **{commit['date'][:10]}** `{commit['hash']}` - {commit['message']} ({commit['author']})")
    md_content.append("")

    # Add contributors
    md_content.append("## Contributors")
    md_content.append("")
    for contributor in sorted(contributors):
        md_content.append(f"- {contributor}")
    md_content.append("")

    # Add raw data for reference
    md_content.append("## Raw Commit Data")
    md_content.append("")
    md_content.append("```json")
    md_content.append("[")
    for i, commit in enumerate(commits):
        md_content.append("  {")
        md_content.append(f'    "hash": "{commit["hash"]}",')
        md_content.append(f'    "author": "{commit["author"]}",')
        md_content.append(f'    "date": "{commit["date"]}",')
        md_content.append(f'    "message": "{commit["message"]}"')
        md_content.append("  }" + ("," if i < len(commits) - 1 else ""))
    md_content.append("]")
    md_content.append("```")

    return "\n".join(md_content)


def main():
    parser = argparse.ArgumentParser(description="Collect git commits for changelog generation")
    parser.add_argument("--since-tag", help="Collect commits since this specific tag (default: latest tag)")
    parser.add_argument("--all", action="store_true", help="Collect all commits (ignore tags)")
    parser.add_argument("--count", "-n", type=int, help="Limit to the last N commits (can be combined with --since-tag)")
    parser.add_argument("--output", "-o", default="commits-for-changelog.md", help="Output file name (default: commits-for-changelog.md)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected without writing file")

    args = parser.parse_args()

    # Check if we're in a git repository
    success, _ = run_command(["git", "rev-parse", "--git-dir"])
    if not success:
        print("Error: Not in a git repository")
        sys.exit(1)

    # Determine which commits to collect
    if args.all:
        tag = None
        if args.count:
            print(f"Collecting last {args.count} commits...")
        else:
            print("Collecting all commits...")
    elif args.since_tag:
        tag = args.since_tag
        if args.count:
            print(f"Collecting last {args.count} commits since tag: {tag}")
        else:
            print(f"Collecting commits since tag: {tag}")
    else:
        tag = get_latest_tag()
        if tag:
            if args.count:
                print(f"Collecting last {args.count} commits since latest tag: {tag}")
            else:
                print(f"Collecting commits since latest tag: {tag}")
        else:
            if args.count:
                print(f"No tags found, collecting last {args.count} commits...")
            else:
                print("No tags found, collecting all commits...")

    # Get commits
    commits = get_commits_since_tag(tag, args.count)

    if not commits:
        print("No commits found!")
        sys.exit(0)

    print(f"Found {len(commits)} commits")

    # Generate summary
    summary = generate_commit_summary(commits, tag, args.count)

    if args.dry_run:
        print("\n" + "=" * 50)
        print("DRY RUN - Would write to:", args.output)
        print("=" * 50)
        print(summary[:1000] + "..." if len(summary) > 1000 else summary)
    else:
        # Write to file
        output_path = Path(args.output)
        output_path.write_text(summary, encoding="utf-8")
        print(f"✅ Commits summary written to: {output_path}")
        print("📝 Next step: Use Claude Code to convert this into CHANGELOG.md entries")
        print(f"💡 Command: claude code '{output_path}' 'Help me convert these commits into CHANGELOG.md format'")


if __name__ == "__main__":
    main()
