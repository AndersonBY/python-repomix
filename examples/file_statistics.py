"""
File Statistics Example

This example demonstrates how to use repomix to obtain detailed statistics of a code repository, including:
- File count statistics
- Character count statistics
- Token count statistics
- File tree structure
"""

from repomix import RepoProcessor


def print_tree(tree, indent=0):
    """Print file tree structure"""
    for name, content in tree.items():
        print("  " * indent + name)
        if isinstance(content, dict):
            print_tree(content, indent + 1)


def main():
    # Create processor
    processor = RepoProcessor(".")
    result = processor.process(write_output=False)

    # Print basic statistics
    print("Basic Statistics:")
    print(f"Total files: {result.total_files}")
    print(f"Total characters: {result.total_chars}")
    print(f"Total tokens: {result.total_tokens}")

    # Print detailed statistics for each file
    print("\nDetailed Statistics for Each File:")
    for file_path, char_count in result.file_char_counts.items():
        token_count = result.file_token_counts[file_path]
        print(f"\nFile: {file_path}")
        print(f"Character count: {char_count}")
        print(f"Token count: {token_count}")

    # Print file tree structure
    print("\nRepository File Structure:")
    print_tree(result.file_tree)


if __name__ == "__main__":
    main()
