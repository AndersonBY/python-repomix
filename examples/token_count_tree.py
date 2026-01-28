"""
Token Count Tree Example

This example demonstrates the token count tree feature:
- Visualize token distribution across directories
- Identify which parts of your codebase consume the most tokens
- Useful for optimizing AI context usage
"""

from repomix import RepoProcessor, RepomixConfig


def main():
    # Create configuration with token count tree enabled
    config = RepomixConfig()

    # Configure output
    config.output.file_path = "token-tree-output.md"
    config.output.style = "markdown"

    # Enable token counting (required for token tree)
    config.output.calculate_tokens = True

    # Enable token count tree
    # Can be True (default depth), an integer (custom depth), or "full"
    config.output.token_count_tree = True  # Use default depth

    # Alternative configurations:
    # config.output.token_count_tree = 3  # Show 3 levels deep
    # config.output.token_count_tree = "full"  # Show all levels

    # Process the repository
    processor = RepoProcessor(".", config=config)
    result = processor.process()

    print("Token Count Tree Example Complete!")
    print(f"Output file: {result.config.output.file_path}")
    print(f"Files processed: {result.total_files}")
    print(f"Total tokens: {result.total_tokens}")

    print("\nToken Count Tree shows:")
    print("- Token count per directory")
    print("- Percentage of total tokens")
    print("- Hierarchical view of token distribution")
    print("\nExample tree output:")
    print("├── src/ (5000 tokens, 50%)")
    print("│   ├── core/ (3000 tokens, 30%)")
    print("│   └── utils/ (2000 tokens, 20%)")
    print("└── tests/ (2000 tokens, 20%)")


if __name__ == "__main__":
    main()
