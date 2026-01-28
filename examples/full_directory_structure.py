"""
Full Directory Structure Example

This example demonstrates the full directory structure option:
- Show complete directory tree including ignored files
- Useful for understanding project structure
- Includes files that are excluded from output content
"""

from repomix import RepoProcessor, RepomixConfig


def main():
    # Create configuration with full directory structure
    config = RepomixConfig()

    # Configure output
    config.output.file_path = "full-structure-output.md"
    config.output.style = "markdown"

    # Enable full directory structure
    # When True, shows all files/directories including ignored ones
    config.output.include_full_directory_structure = True

    # Still respect normal filtering for content
    config.ignore.custom_patterns = ["*.log", "*.tmp"]

    # Process the repository
    processor = RepoProcessor(".", config=config)
    result = processor.process()

    print("Full Directory Structure Example Complete!")
    print(f"Output file: {result.config.output.file_path}")
    print(f"Files in content: {result.total_files}")

    print("\nWith include_full_directory_structure=True:")
    print("- Directory tree shows ALL files and folders")
    print("- Includes node_modules/, __pycache__/, .git/, etc.")
    print("- File content section still respects ignore patterns")
    print("- Useful for showing complete project structure to AI")

    print("\nWith include_full_directory_structure=False (default):")
    print("- Directory tree only shows files included in output")
    print("- Matches the content section exactly")


if __name__ == "__main__":
    main()
