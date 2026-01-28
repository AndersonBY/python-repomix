"""
Output Split Example

This example demonstrates how to split large outputs into multiple files:
- Useful for very large codebases that exceed context limits
- Each part stays within the specified size limit
- Files are grouped intelligently by directory structure
"""

from repomix import RepoProcessor, RepomixConfig


def main():
    # Create configuration with output splitting
    config = RepomixConfig()

    # Configure output
    config.output.file_path = "split-output.md"
    config.output.style = "markdown"

    # Enable output splitting
    # Split output into parts of maximum 500KB each
    config.output.split_output = 500 * 1024  # 500KB per file

    # Process the repository
    processor = RepoProcessor(".", config=config)
    result = processor.process()

    print("Output Split Example Complete!")
    print(f"Base output file: {result.config.output.file_path}")
    print(f"Files processed: {result.total_files}")
    print("\nWhen split_output is enabled:")
    print("- Output is split into multiple files if it exceeds the limit")
    print("- Files are named: split-output.md, split-output-part2.md, etc.")
    print("- Each part contains complete file entries (no partial files)")
    print("- Files are grouped by root directory when possible")


if __name__ == "__main__":
    main()
