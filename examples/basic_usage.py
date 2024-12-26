"""
Basic Usage Example

This example demonstrates how to use the basic features of repomix to process a code repository.
"""

from repomix import RepoProcessor


def main():
    # Create a processor instance pointing to current directory
    processor = RepoProcessor(".")

    # Process the repository
    result = processor.process()

    # Print processing results
    print("Processing complete!")
    print(f"Total files: {result.total_files}")
    print(f"Total characters: {result.total_chars}")
    print(f"Total tokens: {result.total_tokens}")
    print(f"Output saved to: {result.config.output.file_path}")


if __name__ == "__main__":
    main()
