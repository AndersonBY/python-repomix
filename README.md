# 📦 Repomix (Python Version)

English | [简体中文](README_zh.md)

Repomix is a powerful tool that packs your entire repository into a single, AI-friendly file. It is perfect for when you need to feed your codebase to Large Language Models (LLMs) or other AI tools like Claude, ChatGPT, and Gemini.

## 🌟 Features

- **AI-Optimized**: Formats your codebase in a way that's easy for AI to understand and process
- **Token Counting**: Provides token counts for each file and the entire repository using tiktoken
- **Simple to Use**: Pack your entire repository with just one command
- **Customizable**: Easily configure what to include or exclude
- **Git-Aware**: Automatically respects your .gitignore files
- **Security-Focused**: Built-in security checks to detect and prevent inclusion of sensitive information

## 🚀 Quick Start

You can install Repomix using pip:

```bash
pip install repomix
```

Then run in any project directory:

```bash
python -m repomix
```

That's it! Repomix will generate a `repomix-output.md` file in your current directory, containing your entire repository in an AI-friendly format.

## 📊 Usage

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

Once you have generated the packed file, you can use it with Generative AI tools like Claude, ChatGPT, and Gemini.

### Prompt Examples
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


### Output File Format

Repomix generates a single file with clear separators between different parts of your codebase. To enhance AI comprehension, the output file begins with an AI-oriented explanation, making it easier for AI models to understand the context and structure of the packed repository.

#### Plain Text Format (default)

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

#### XML Format
To generate output in XML format, use the --style xml option:

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

#### `Markdown Format
To generate output in Markdown format, use the --style markdown option:

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

## ⚙️ Configuration

Create a `repomix.config.json` file in your project root for custom configurations:

```json
{
  "output": {
    "filePath": "repomix-output.md",
    "style": "markdown",
    "showLineNumbers": false,
    "copyToClipboard": false,
    "topFilesLength": 5
  },
  "include": ["**/*"],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": []
  },
  "security": {
    "enableSecurityCheck": true
  }
}
```

### Output Formats

Repomix supports three output formats:

- **Plain Text** (default)
- **Markdown**
- **XML**

To specify the output format:
```bash
python -m repomix --style markdown
```

### Command Line Options

- `-v, --version`: Show version
- `-o, --output <file>`: Specify output file name
- `--style <style>`: Specify output style (plain, xml, markdown)
- `--remote <url>`: Process a remote Git repository
- `--init`: Initialize configuration file
- `--no-security-check`: Disable security check
- `--verbose`: Enable verbose logging

## 🔍 Security Check

Repomix includes built-in security checks to detect potentially sensitive information in your files. This helps prevent accidental exposure of secrets when sharing your codebase.

You can disable security checks using:
```bash
python -m repomix --no-security-check
```

## 📜 License

This project is licensed under the MIT License.

---
For more detailed information about usage and configuration options, please visit the [documentation](https://github.com/andersonby/python-repomix).