"""
JSON Output Format Example

This example demonstrates how to use the JSON output format, which provides:
- Structured, machine-readable output
- Easy integration with other tools and scripts
- Complete metadata and statistics in JSON format
"""

import json
from repomix import RepoProcessor, RepomixConfig


def main():
    # Create configuration for JSON output
    config = RepomixConfig()

    # Configure JSON output
    config.output.file_path = "repomix-output.json"
    config.output.style = "json"  # Use JSON format

    # Enable token counting for complete statistics
    config.output.calculate_tokens = True

    # Process the repository
    processor = RepoProcessor(".", config=config)
    result = processor.process()

    print("JSON Output Example Complete!")
    print(f"Output file: {result.config.output.file_path}")
    print(f"Files processed: {result.total_files}")

    # Read and parse the JSON output
    with open(result.config.output.file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Display structure of the JSON output
    print("\nJSON Output Structure:")
    print("- summary: Contains metadata and statistics")
    print("- file_tree: Directory structure as nested object")
    print(f"- files: Array of {len(data.get('files', []))} file objects")

    # Show statistics from JSON
    if "summary" in data:
        summary = data["summary"]
        print("\nStatistics from JSON:")
        print(f"- Total files: {summary.get('total_files', 'N/A')}")
        print(f"- Total characters: {summary.get('total_chars', 'N/A')}")
        print(f"- Total tokens: {summary.get('total_tokens', 'N/A')}")


if __name__ == "__main__":
    main()
