#!/usr/bin/env python3
"""
Tree-sitter Compression Example - Demonstrates code compression using tree-sitter

This example shows the difference between normal output and tree-sitter compressed output
using the python-repomix repository itself as a demonstration.
"""

import os
import sys

# Add the parent directory to sys.path to import repomix
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from repomix.config.config_schema import RepomixConfig
from repomix.core.repo_processor import RepoProcessor


def demonstrate_compression_comparison():
    """Demonstrate the difference between normal and compressed output."""

    print("🔬 Tree-sitter Compression Demonstration")
    print("=" * 50)
    print("Repository: https://github.com/AndersonBY/python-repomix.git")
    print()

    # Get the current repository directory (assuming we're running from examples/)
    repo_path = os.path.join(os.path.dirname(__file__), "..")

    # Create two configurations: one normal, one with compression
    normal_config = RepomixConfig()
    normal_config.output.file_path = "normal_output.md"
    normal_config.compression.enabled = False
    normal_config.output.show_line_numbers = False
    # Include multiple Python files to show better compression effect
    normal_config.include = ["src/repomix/core/repo_processor.py", "src/repomix/core/file/file_process.py", "src/repomix/config/config_schema.py"]

    compressed_config = RepomixConfig()
    compressed_config.output.file_path = "compressed_output.md"
    compressed_config.compression.enabled = True
    compressed_config.output.show_line_numbers = False
    # Same files for comparison
    compressed_config.include = ["src/repomix/core/repo_processor.py", "src/repomix/core/file/file_process.py", "src/repomix/config/config_schema.py"]

    print("📄 Processing sample files:")
    print("   • src/repomix/core/repo_processor.py")
    print("   • src/repomix/core/file/file_process.py")
    print("   • src/repomix/config/config_schema.py")
    print()

    # Process with normal configuration
    print("🔄 Processing without compression...")
    try:
        processor_normal = RepoProcessor(repo_path, config=normal_config)
        result_normal = processor_normal.process()

        normal_chars = len(result_normal.output_content)
        normal_files = result_normal.total_files

        print(f"   ✅ Normal output: {normal_chars:,} characters, {normal_files} files")

    except Exception as e:
        print(f"   ❌ Error processing normal output: {e}")
        return

    # Process with compression
    print("🔄 Processing with tree-sitter compression...")
    try:
        processor_compressed = RepoProcessor(repo_path, config=compressed_config)
        result_compressed = processor_compressed.process()

        compressed_chars = len(result_compressed.output_content)
        compressed_files = result_compressed.total_files

        print(f"   ✅ Compressed output: {compressed_chars:,} characters, {compressed_files} files")

    except Exception as e:
        print(f"   ❌ Error processing compressed output: {e}")
        return

    # Calculate compression ratio
    if normal_chars > 0:
        compression_ratio = (1 - compressed_chars / normal_chars) * 100
        print()
        print("📊 Compression Results:")
        print(f"   • Original size: {normal_chars:,} characters")
        print(f"   • Compressed size: {compressed_chars:,} characters")
        if compression_ratio > 0:
            print(f"   • Compression ratio: {compression_ratio:.1f}% (smaller)")
            print(f"   • Size reduction: {normal_chars - compressed_chars:,} characters")
        else:
            print(f"   • Size increase: {abs(compression_ratio):.1f}% (larger)")
            print(f"   • Size increase: {compressed_chars - normal_chars:,} characters")

        print()
        print("📋 Understanding the Results:")
        if compression_ratio < 0:
            print("   • Tree-sitter compression adds metadata and separators")
            print("   • For small files, overhead may exceed compression benefits")
            print("   • Benefits become apparent with larger codebases")
            print("   • Main advantage: structured extraction for AI processing")
        else:
            print("   • Tree-sitter successfully reduced file size")
            print("   • Removed implementation details while preserving structure")
            print("   • Better token efficiency for LLM processing")

    print()
    print("📋 Output Analysis:")

    # Show sample content from both outputs
    print("\n🔍 Normal Output Preview (first 500 characters):")
    print("-" * 50)
    normal_content = extract_file_content(result_normal.output_content)
    print(normal_content[:500] + "..." if len(normal_content) > 500 else normal_content)

    print("\n🔍 Compressed Output Preview (first 500 characters):")
    print("-" * 50)
    compressed_content = extract_file_content(result_compressed.output_content)
    print(compressed_content[:500] + "..." if len(compressed_content) > 500 else compressed_content)

    print()
    print("💡 Key Benefits of Tree-sitter Compression:")
    print("   • Extracts only essential code elements (functions, classes, imports)")
    print("   • Removes implementation details while preserving structure")
    print("   • Uses ⋮---- separators to organize extracted elements")
    print("   • Significantly reduces token usage for LLM processing")
    print("   • Maintains code comprehension for AI analysis")

    print()
    print("🎯 Use Cases for Compression:")
    print("   • Code review and analysis by AI models")
    print("   • Large codebase summarization")
    print("   • API documentation generation")
    print("   • Code structure analysis")
    print("   • Token budget management for LLMs")


def extract_file_content(full_output: str) -> str:
    """Extract the actual file content from the repomix output."""
    # Find all python code blocks and extract the first one
    lines = full_output.split("\n")
    in_code_block = False
    content_lines: list[str] = []

    for line in lines:
        if line.strip().startswith("```python"):
            in_code_block = True
            continue
        elif line.strip() == "```" and in_code_block:
            # Found end of first code block, return what we have
            if content_lines:
                break
            continue
        elif in_code_block:
            content_lines.append(line)

    content = "\n".join(content_lines)
    # If no content found in code blocks, look for content after "## " headers
    if not content.strip():
        in_file_section = False
        for line in lines:
            if line.startswith("## ") and line.endswith(".py"):
                in_file_section = True
                continue
            elif line.startswith("## ") and in_file_section:
                # New section started, stop
                break
            elif in_file_section and not line.startswith("```"):
                content_lines.append(line)
        content = "\n".join(content_lines)

    return content.strip()


def demonstrate_supported_languages():
    """Show which languages are supported by tree-sitter compression."""
    print("\n🌐 Supported Languages for Tree-sitter Compression:")
    print("=" * 50)

    try:
        from repomix.core.tree_sitter.parse_file import get_supported_extensions

        extensions = get_supported_extensions()

        if extensions:
            print("✅ Currently supported file extensions:")
            for i, ext in enumerate(sorted(extensions), 1):
                print(f"   {i:2d}. .{ext}")
        else:
            print("⚠️  No supported extensions found (tree-sitter packages may not be installed)")

    except ImportError:
        print("❌ Tree-sitter compression module not available")

    print()
    print("📦 To add support for more languages, install additional tree-sitter packages:")
    print("   pip install tree-sitter-go tree-sitter-rust tree-sitter-java")


def demonstrate_full_project_compression():
    """Demonstrate compression on the entire src/repomix directory."""
    print("\n🗂️  Full Project Compression Analysis")
    print("=" * 50)

    repo_path = os.path.join(os.path.dirname(__file__), "..")

    # Create configurations for full src/repomix directory
    normal_config = RepomixConfig()
    normal_config.compression.enabled = False
    normal_config.include = ["src/repomix/**/*.py"]

    compressed_config = RepomixConfig()
    compressed_config.compression.enabled = True
    compressed_config.include = ["src/repomix/**/*.py"]

    print("📁 Processing entire src/repomix directory...")
    print()

    try:
        # Process normal
        print("🔄 Processing without compression...")
        processor_normal = RepoProcessor(repo_path, config=normal_config)
        result_normal = processor_normal.process()

        normal_chars = len(result_normal.output_content)
        normal_files = result_normal.total_files

        # Process compressed
        print("🔄 Processing with compression...")
        processor_compressed = RepoProcessor(repo_path, config=compressed_config)
        result_compressed = processor_compressed.process()

        compressed_chars = len(result_compressed.output_content)

        # Results
        compression_ratio = (1 - compressed_chars / normal_chars) * 100 if normal_chars > 0 else 0

        print()
        print("📊 Full Project Results:")
        print(f"   • Files processed: {normal_files}")
        print(f"   • Original size: {normal_chars:,} characters")
        print(f"   • Compressed size: {compressed_chars:,} characters")

        if compression_ratio > 0:
            print(f"   • Compression achieved: {compression_ratio:.1f}%")
            print(f"   • Characters saved: {normal_chars - compressed_chars:,}")
        else:
            print(f"   • Size increase: {abs(compression_ratio):.1f}%")
            print(f"   • Additional characters: {compressed_chars - normal_chars:,}")

        print()
        print("🎯 Key Insights:")
        print("   • Tree-sitter extracts function signatures, class definitions, imports")
        print("   • Removes function bodies, detailed implementations")
        print("   • Preserves code structure and interface information")
        print("   • Ideal for code analysis, documentation, and AI processing")

    except Exception as e:
        print(f"❌ Error during full project analysis: {e}")


def main():
    """Main function to run the demonstration."""
    try:
        demonstrate_compression_comparison()
        demonstrate_full_project_compression()
        demonstrate_supported_languages()

        print()
        print("🎉 Tree-sitter compression demonstration completed!")
        print()
        print("🚀 Try it yourself:")
        print("   repomix . --compress --output compressed_demo.md")
        print("   repomix . --output normal_demo.md")
        print()
        print("📖 Compare the outputs to see the compression effect!")

    except KeyboardInterrupt:
        print("\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("   Make sure you're running this from the python-repomix repository root")
        sys.exit(1)


if __name__ == "__main__":
    main()
