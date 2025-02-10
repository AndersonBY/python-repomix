# 📦 Repomix (Python Version)

English | [简体中文](README_zh.md)

## 🎯 1. Introduction

Repomix is a powerful tool that packs your entire repository into a single, AI-friendly file. It's perfect for when you need to feed your codebase to Large Language Models (LLMs) or other AI tools like Claude, ChatGPT, and Gemini.

The original [Repomix](https://github.com/yamadashy/repomix) is written in JavaScript, and this is the ported Python version.

## ⭐ 2. Features

-   **AI-Optimized**: Formats your codebase in a way that's easy for AI to understand and process.
-   **Token Counting**: Provides token counts for each file and the entire repository using tiktoken.
-   **Simple to Use**: Pack your entire repository with just one command.
-   **Customizable**: Easily configure what to include or exclude.
-   **Git-Aware**: Automatically respects your .gitignore files.
-   **Security-Focused**: Built-in security checks to detect and prevent the inclusion of sensitive information.

## 🚀 3. Quick Start

You can install Repomix using pip:

```bash
pip install repomix
```

Then run in any project directory:

```bash
python -m repomix
```

That's it! Repomix will generate a `repomix-output.md` file in your current directory, containing your entire repository in an AI-friendly format.

## 📖 4. Usage

### 4.1 Command Line Usage

To pack your entire repository:

```bash
python -m repomix
```

To pack a specific directory:

```bash
python -m repomix path/to/directory
```

To pack a remote repository:

```bash
python -m repomix --remote https://github.com/username/repo
```

To initialize a new configuration file:

```bash
python -m repomix --init
```

### 4.2 Configuration Options

Create a `repomix.config.json` file in your project root for custom configurations:

```json
{
  "output": {
    "file_path": "repomix-output.md",
    "style": "markdown",
    "header_text": "",
    "instruction_file_path": "",
    "remove_comments": false,
    "remove_empty_lines": false,
    "top_files_length": 5,
    "show_line_numbers": false,
    "copy_to_clipboard": false,
    "include_empty_directories": false,
    "calculate_tokens": false
  },
  "security": {
    "enable_security_check": true,
    "exclude_suspicious_files": true
  },
  "ignore": {
    "custom_patterns": [],
    "use_gitignore": true,
    "use_default_ignore": true
  },
  "include": []
}
```

**Command Line Options**

-   `-v, --version`: Show version
-   `-o, --output <file>`: Specify output file name
-   `--style <style>`: Specify output style (plain, xml, markdown)
-   `--remote <url>`: Process a remote Git repository
-   `--init`: Initialize configuration file
-   `--no-security-check`: Disable security check
-   `--verbose`: Enable verbose logging

### 4.3 Security Check

Repomix includes built-in security checks to detect potentially sensitive information in your files. This helps prevent accidental exposure of secrets when sharing your codebase.

The security check is powered by the [detect-secrets](https://github.com/Yelp/detect-secrets) library, which can identify various types of secrets including:

- API keys
- AWS access keys
- Database credentials
- Private keys
- Authentication tokens
- And more...

You can disable security checks using:

```bash
python -m repomix --no-security-check
```

### 4.4 Ignore Patterns

Repomix provides multiple methods to set ignore patterns for excluding specific files or directories during the packing process:

#### Priority Order

Ignore patterns are applied in the following priority order (from highest to lowest):

1. Custom patterns in configuration file (`ignore.custom_patterns`)
2. `.repomixignore` file
3. `.gitignore` file (if `ignore.use_gitignore` is true)
4. Default patterns (if `ignore.use_default_ignore` is true)

#### Ignore Methods

##### .gitignore
By default, Repomix uses patterns listed in your project's `.gitignore` file. This behavior can be controlled with the `ignore.use_gitignore` option in the configuration file:

```json
{
  "ignore": {
    "use_gitignore": true
  }
}
```

##### Default Patterns
Repomix includes a default list of commonly excluded files and directories (e.g., `__pycache__`, `.git`, binary files). This feature can be controlled with the `ignore.use_default_ignore` option:

```json
{
  "ignore": {
    "use_default_ignore": true
  }
}
```

The complete list of default ignore patterns can be found in [default_ignore.py](src/repomix/config/default_ignore.py).

##### .repomixignore
You can create a `.repomixignore` file in your project root to define Repomix-specific ignore patterns. This file follows the same format as `.gitignore`.

##### Custom Patterns
Additional ignore patterns can be specified using the `ignore.custom_patterns` option in the configuration file:

```json
{
  "ignore": {
    "custom_patterns": [
      "*.log",
      "*.tmp",
      "tests/**/*.pyc"
    ]
  }
}
```

#### Notes

- Binary files are not included in the packed output by default, but their paths are listed in the "Repository Structure" section of the output file. This provides a complete overview of the repository structure while keeping the packed file efficient and text-based.
- Ignore patterns help optimize the size of the generated pack file by ensuring the exclusion of security-sensitive files and large binary files, while preventing the leakage of confidential information.
- All ignore patterns use glob pattern syntax similar to `.gitignore`.

## 🔒 5. Output File Format

Repomix generates a single file with clear separators between different parts of your codebase. To enhance AI comprehension, the output file begins with an AI-oriented explanation, making it easier for AI models to understand the context and structure of the packed repository.

### 5.1 Plain Text Format (default)

```text
This file is a merged representation of the entire codebase, combining all repository files into a single document.

================================================================
File Summary
================================================================
(Metadata and usage AI instructions)

================================================================
Repository Structure
================================================================
src/
  cli/
    cliOutput.py
    index.py
  config/
    configLoader.py

(...remaining directories)

================================================================
Repository Files
================================================================

================
File: src/index.py
================
# File contents here

================
File: src/utils.py
================
# File contents here

(...remaining files)

================================================================
Statistics
================================================================
(File statistics and metadata)
```

### 5.2 Markdown Format

To generate output in Markdown format, use the `--style markdown` option:

```bash
python -m repomix --style markdown
```

The Markdown format structures the content in a readable manner:

`````markdown
# File Summary
(Metadata and usage AI instructions)

# Repository Structure
```
src/
  cli/
    cliOutput.py
    index.py
```

# Repository Files

## File: src/index.py
```python
# File contents here
```

## File: src/utils.py
```python
# File contents here
```

# Statistics
- Total Files: 19
- Total Characters: 37377
- Total Tokens: 11195
`````

### 5.3 XML Format

To generate output in XML format, use the `--style xml` option:

```bash
python -m repomix --style xml
```

The XML format structures the content in a hierarchical manner:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<repository>
<repository_structure>
(Directory and file structure)
</repository_structure>

<repository_files>
<file>
  <path>src/index.py</path>
  <stats>
    <chars>1234</chars>
    <tokens>567</tokens>
  </stats>
  <content>
    # File contents here
  </content>
</file>
(...remaining files)
</repository_files>

<statistics>
  <total_files>19</total_files>
  <total_chars>37377</total_chars>
  <total_tokens>11195</total_tokens>
</statistics>
</repository>
```

## 🛠️ 6. Advanced Usage

### 6.1 Library Usage

You can use Repomix as a Python library in your projects. Here's a basic example:

```python
from repomix import RepoProcessor

# Basic usage
processor = RepoProcessor(".")
result = processor.process()

# Access processing results
print(f"Total files: {result.total_files}")
print(f"Total characters: {result.total_chars}")
print(f"Total tokens: {result.total_tokens}")
print(f"Output saved to: {result.config.output.file_path}")
```

### 6.2 Advanced Configuration

```python
from repomix import RepoProcessor, RepomixConfig

# Create custom configuration
config = RepomixConfig()

# Output settings
config.output.file_path = "custom-output.md"
config.output.style = "markdown"  # supports "plain", "markdown", and "xml"
config.output.show_line_numbers = True

# Security settings
config.security.enable_security_check = True
config.security.exclude_suspicious_files = True

# Include/Ignore patterns
config.include = ["src/**/*", "tests/**/*"]
config.ignore.custom_patterns = ["*.log", "*.tmp"]
config.ignore.use_gitignore = True

# Process repository with custom config
processor = RepoProcessor(".", config=config)
result = processor.process()
```

For more example code, check out the `examples` directory:

-   `basic_usage.py`: Basic usage examples
-   `custom_config.py`: Custom configuration examples
-   `security_check.py`: Security check feature examples
-   `file_statistics.py`: File statistics examples
-   `remote_repo_usage.py`: Remote repository processing examples

## 🤖 7. AI Usage Guide

### 7.1 Prompt Examples

Once you have generated the packed file with Repomix, you can use it with AI tools like Claude, ChatGPT, and Gemini. Here are some example prompts to get you started:

#### Code Review and Refactoring

For a comprehensive code review and refactoring suggestions:

```
This file contains my entire codebase. Please review the overall structure and suggest any improvements or refactoring opportunities, focusing on maintainability and scalability.
```

#### Documentation Generation

To generate project documentation:

```
Based on the codebase in this file, please generate a detailed README.md that includes an overview of the project, its main features, setup instructions, and usage examples.
```

#### Test Case Generation

For generating test cases:

```
Analyze the code in this file and suggest a comprehensive set of unit tests for the main functions and classes. Include edge cases and potential error scenarios.
```

#### Code Quality Assessment
Evaluate code quality and adherence to best practices:

```
Review the codebase for adherence to coding best practices and industry standards. Identify areas where the code could be improved in terms of readability, maintainability, and efficiency. Suggest specific changes to align the code with best practices.
```

#### Library Overview
Get a high-level understanding of the library

```
This file contains the entire codebase of library. Please provide a comprehensive overview of the library, including its main purpose, key features, and overall architecture.
```

Feel free to modify these prompts based on your specific needs and the capabilities of the AI tool you're using.

### 7.2 Best Practices

*   **Be Specific:** When prompting the AI, be as specific as possible about what you want. The more context you provide, the better the results will be.
*   **Iterate:** Don't be afraid to iterate on your prompts. If you don't get the results you want on the first try, refine your prompt and try again.
*   **Combine with Manual Review:** While AI can be a powerful tool, it's not perfect. Always combine AI-generated output with manual review and editing.
*   **Security First:** Always be mindful of security when working with your codebase. Use Repomix's built-in security checks and avoid sharing sensitive information with AI tools.

## 📄 8. License

This project is licensed under the MIT License.

---

For more detailed information about usage and configuration options, please visit the [documentation](https://github.com/andersonby/python-repomix).
