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