# 📦 Repomix (Python 版本)

English | [简体中文](README_zh.md)

## 🎯 1. 简介

Repomix 是一个强大的工具，可以将你的整个仓库打包成一个单一的、对 AI 友好的文件。当你需要将你的代码库输入到大型语言模型 (LLM) 或其他 AI 工具（如 Claude、ChatGPT 和 Gemini）时，它非常完美。

最初的 [Repomix](https://github.com/yamadashy/repomix) 是用 JavaScript 编写的，这是移植的 Python 版本。


## ⭐ 2. 功能特性

-   **AI 优化**: 以一种易于人工智能理解和处理的方式格式化你的代码库。
-   **Token 计数**: 使用 tiktoken 为每个文件和整个仓库提供 token 计数。
-   **简单易用**: 只需一个命令即可打包整个仓库。
-   **可定制**: 轻松配置要包含或排除的内容。
-   **Git 感知**: 自动遵守你的 .gitignore 文件。
-   **安全至上**: 内置安全检查，以检测并防止包含敏感信息。

## 🚀 3. 快速开始

你可以使用 pip 安装 Repomix：

```bash
pip install repomix
```

然后在任何项目目录下运行：

```bash
python -m repomix
```

就这样！Repomix 将会在你当前目录下生成一个 `repomix-output.md` 文件，其中包含你整个仓库的 AI 友好格式。


## 📖 4. 用法

### 4.1 命令行用法

要打包你的整个仓库：

```bash
python -m repomix
```

要打包特定目录：

```bash
python -m repomix path/to/directory
```

要打包一个远程仓库：

```bash
python -m repomix --remote https://github.com/username/repo
```

要初始化一个新的配置文件：

```bash
python -m repomix --init
```

### 4.2 配置选项

在你的项目根目录创建一个 `repomix.config.json` 文件来进行自定义配置：

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
    "include_empty_directories": false
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

**命令行选项**

-   `-v, --version`: 显示版本
-   `-o, --output <file>`: 指定输出文件名
-   `--style <style>`: 指定输出样式 (plain, xml, markdown)
-   `--remote <url>`: 处理远程 Git 仓库
-   `--init`: 初始化配置文件
-   `--no-security-check`: 禁用安全检查
-   `--verbose`: 启用详细日志


### 4.3 安全检查

Repomix 包含内置的安全检查，用于检测文件中潜在的敏感信息。这有助于防止在共享代码库时意外暴露秘密。

安全检查使用 [detect-secrets](https://github.com/Yelp/detect-secrets) 库，可以识别各种类型的秘密，包括：

- API 密钥
- AWS 访问密钥
- 数据库凭据
- 私钥
- 认证令牌

您可以使用以下命令禁用安全检查：

```bash
python -m repomix --no-security-check
```

### 4.4 忽略模式

Repomix 提供了多种方法来设置忽略模式，以便在打包过程中排除特定的文件或目录：

#### 优先级顺序

忽略模式按照以下优先级顺序应用（从高到低）：

1. 配置文件中的自定义模式 (`ignore.custom_patterns`)
2. `.repomixignore` 文件
3. `.gitignore` 文件（如果 `ignore.use_gitignore` 为 true）
4. 默认模式（如果 `ignore.use_default_ignore` 为 true）


#### 忽略方法

##### .gitignore
默认情况下，Repomix 使用项目 `.gitignore` 文件中列出的模式。此行为可以通过配置文件中的 `ignore.use_gitignore` 选项来控制：


```json
{
  "ignore": {
    "use_gitignore": true
  }
}
```

##### 默认模式
Repomix 包含一个默认的常用排除文件和目录列表（例如，`__pycache__`，`.git`，二进制文件）。此功能可以通过 `ignore.use_default_ignore` 选项进行控制：


```json
{
  "ignore": {
    "use_default_ignore": true
  }
}
```

完整的默认忽略模式列表可以在 [default_ignore.py](src/repomix/config/default_ignore.py) 中找到。


##### .repomixignore
你可以在你的项目根目录下创建一个 `.repomixignore` 文件来定义 Repomix 特有的忽略模式。这个文件的格式与 `.gitignore` 相同。

##### 自定义模式
可以使用配置文件中的 `ignore.custom_patterns` 选项来指定额外的忽略模式：


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

#### 注释

- 二进制文件默认不包含在打包输出中，但它们的路径会列在输出文件的“仓库结构”部分。这提供了仓库结构的完整概览，同时保持打包文件的高效性和基于文本的特性。
- 忽略模式通过确保排除安全敏感文件和大型二进制文件来帮助优化生成的打包文件的大小，同时防止泄露机密信息。
- 所有忽略模式都使用类似于 `.gitignore` 的 glob 模式语法。


## 🔒 5. 输出文件格式

Repomix 生成一个单独的文件，其中不同代码部分之间有清晰的分隔符。为了增强 AI 的理解能力，输出文件以面向 AI 的解释开头，使 AI 模型更容易理解打包存储库的上下文和结构。

### 5.1 纯文本格式（默认）

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

### 5.2 Markdown 格式

要生成 Markdown 格式的输出，请使用 `--style markdown` 选项：

```bash
python -m repomix --style markdown
```

Markdown 格式以可读的方式构建内容：

```markdown
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
```

### 5.3 XML 格式

要生成 XML 格式的输出，请使用 `--style xml` 选项：


```bash
python -m repomix --style xml
```

XML格式以分层方式组织内容：


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

## 🛠️ 6. 高级用法

### 6.1 库的使用

你可以在你的项目中使用 Repomix 作为 Python 库。这是一个基本示例：

```python
from repomix import RepoProcessor

# 基本用法
processor = RepoProcessor(".")
result = processor.process()

# 访问处理结果
print(f"总文件数: {result.total_files}")
print(f"总字符数: {result.total_chars}")
print(f"总标记数: {result.total_tokens}")
print(f"输出保存至: {result.config.output.file_path}")
```

### 6.2 高级配置

```python
from repomix import RepoProcessor, RepomixConfig

# 创建自定义配置
config = RepomixConfig()

# 输出设置
config.output.file_path = "custom-output.md"
config.output.style = "markdown"  # 支持 "plain", "markdown" 和 "xml"
config.output.show_line_numbers = True

# 安全设置
config.security.enable_security_check = True
config.security.exclude_suspicious_files = True

# 包含/忽略模式
config.include = ["src/**/*", "tests/**/*"]
config.ignore.custom_patterns = ["*.log", "*.tmp"]
config.ignore.use_gitignore = True

# 使用自定义配置处理仓库
processor = RepoProcessor(".", config=config)
result = processor.process()
```

更多示例代码，请查看 `examples` 目录：

- `basic_usage.py`: 基本用法示例
- `custom_config.py`: 自定义配置示例
- `security_check.py`: 安全检查功能示例
- `file_statistics.py`: 文件统计示例
- `remote_repo_usage.py`: 远程仓库处理示例

## 🤖 7. AI 使用指南

### 7.1 提示示例

一旦你使用 Repomix 生成了打包文件，你就可以将其与 Claude、ChatGPT 和 Gemini 等 AI 工具一起使用。以下是一些提示示例，可帮助你入门：

#### 代码审查和重构

对于全面的代码审查和重构建议：

```
这个文件包含了我的全部代码库。请审查整体结构，并提出任何改进或重构的机会，重点关注可维护性和可扩展性。
```

#### 文档生成

生成项目文档：

```
基于此文件中的代码库，请生成一个详细的README.md，其中包含项目概述、主要功能、设置说明和使用示例。
```

#### 测试用例生成

用于生成测试用例：

```
分析此文件中的代码，并为主要函数和类提出一套全面的单元测试。包括边缘情况和潜在的错误场景。
```

#### 代码质量评估

评估代码质量和对最佳实践的遵循情况：

```
审查代码库，检查其是否符合编码最佳实践和行业标准。找出在可读性、可维护性和效率方面可以改进的代码区域。提出具体的修改建议，使代码与最佳实践保持一致。
```

#### 库概述

对库进行高层次的理解

```
这个文件包含了库的整个代码库。请提供该库的全面概述，包括其主要目的、关键特性和整体架构。
```

### 7.2 最佳实践

*   **具体明确：** 在提示 AI 时，尽可能具体地说明你想要什么。你提供的上下文越多，结果就越好。
*   **迭代：** 不要害怕迭代你的提示。如果你第一次没有得到想要的结果，请改进你的提示并再次尝试。
*   **结合人工审查：** 虽然 AI 是一个强大的工具，但它并非完美。始终将 AI 生成的输出与人工审查和编辑相结合。
*   **安全第一：** 在使用代码库时，始终注意安全。使用 Repomix 的内置安全检查，并避免与 AI 工具共享敏感信息。

## 📄 8. 许可证

本项目根据 MIT 许可证获得许可。

有关用法和配置选项的更多详细信息，请访问[文档](https://github.com/andersonby/python-repomix)。
