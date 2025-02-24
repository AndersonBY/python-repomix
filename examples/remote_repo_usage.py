"""
Remote Repository Usage Example

This example demonstrates how to use repomix to process a remote Git repository.
"""

from repomix import RepoProcessor, RepomixConfig, RepomixConfigOutput


def main():
    # Create a processor instance with a remote repository URL
    remote_url = "https://github.com/AndersonBY/python-repomix.git"
    config = RepomixConfig(output=RepomixConfigOutput(file_path="/tmp/repomix-output.md"))
    processor = RepoProcessor(repo_url=remote_url, config=config)

    # Process the repository
    # By default, it will clone to a temporary directory
    result = processor.process()

    # Print processing results
    print("Remote repository processing complete!")
    print(f"Repository URL: {remote_url}")
    print(f"Total files: {result.total_files}")
    print(f"Total characters: {result.total_chars}")
    print(f"Total tokens: {result.total_tokens}")
    print(f"Output saved to: {result.config.output.file_path}")


if __name__ == "__main__":
    main()
