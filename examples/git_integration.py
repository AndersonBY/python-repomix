"""
Git Integration Example

This example demonstrates how to use Git integration features, including:
- Git diff output (staged and unstaged changes)
- Git log output (recent commit history)
- Sorting files by git change frequency
"""

from repomix import RepoProcessor, RepomixConfig


def main():
    # Create configuration with Git features enabled
    config = RepomixConfig()

    # Configure output
    config.output.file_path = "git-integration-output.md"
    config.output.style = "markdown"

    # Enable Git diff integration
    # Shows both staged and unstaged changes in the output
    config.output.git.include_diffs = True

    # Enable Git log integration
    # Includes recent commit history in the output
    config.output.git.include_logs = True
    config.output.git.include_logs_count = 20  # Number of recent commits to include

    # Enable sorting by git changes
    # Files that change frequently appear first in the output
    config.output.git.sort_by_changes = True
    config.output.git.sort_by_changes_max_commits = 100  # Commits to analyze for sorting

    # Process the repository
    processor = RepoProcessor(".", config=config)
    result = processor.process()

    print("Git Integration Example Complete!")
    print(f"Output file: {result.config.output.file_path}")
    print(f"Files processed: {result.total_files}")
    print("\nThe output includes:")
    print("- Git diff section with staged and unstaged changes")
    print("- Git log section with recent commit history")
    print("- Files sorted by change frequency (most changed first)")


if __name__ == "__main__":
    main()
