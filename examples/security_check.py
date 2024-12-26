"""
Security Check Example

This example demonstrates how to use the security check feature of repomix to detect potential sensitive information.
"""

from repomix import RepoProcessor, RepomixConfig


def main():
    # Create configuration and enable security check
    config = RepomixConfig()
    config.security.enable_security_check = True
    config.security.exclude_suspicious_files = True

    # Create processor
    processor = RepoProcessor(".", config=config)
    result = processor.process(write_output=False)

    # Check for suspicious files
    if result.suspicious_files_results:
        print("Suspicious files found:")
        for suspicious_file in result.suspicious_files_results:
            print(f"\nFile path: {suspicious_file.file_path}")
            print(f"Reason: {', '.join(suspicious_file.messages)}")
    else:
        print("No suspicious files found!")

    # Print processing results
    print("\nProcessing complete!")
    print(f"Total files: {result.total_files}")
    print(f"Checked files: {len(result.suspicious_files_results)}")


if __name__ == "__main__":
    main()
