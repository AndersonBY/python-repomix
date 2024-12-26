"""
Custom Configuration Example

This example demonstrates how to use custom configuration to process code repositories, including:
- Custom output format and path
- Setting include and exclude rules
- Configuring security check options
"""

from repomix import RepoProcessor, RepomixConfig


def main():
    # Create custom configuration
    config = RepomixConfig()

    # Configure output options
    config.output.file_path = "custom-output.xml"
    config.output.style = "xml"
    config.output.show_line_numbers = True
    config.output.copy_to_clipboard = True
    config.output.remove_comments = False
    config.output.remove_empty_lines = False
    config.output.top_files_length = 10

    # Configure include and exclude rules
    config.include = ["src/**/*", "tests/**/*"]
    config.ignore.custom_patterns = ["*.log", "*.tmp", "**/__pycache__/**"]
    config.ignore.use_gitignore = True
    config.ignore.use_default_ignore = True

    # Configure security checks
    config.security.enable_security_check = True
    config.security.exclude_suspicious_files = True

    # Create processor with custom configuration
    processor = RepoProcessor(".", config=config)
    result = processor.process()

    # Print results
    print("Processing completed with custom configuration!")
    print(f"Output file: {result.config.output.file_path}")
    print(f"Files processed: {result.total_files}")


if __name__ == "__main__":
    main()
