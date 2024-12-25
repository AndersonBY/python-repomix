# 📦 Repomix (Python 版本)

[English](README.md) | 简体中文

Repomix 是一个强大的工具，可以将您的整个存储库打包成一个单一的、对 AI 友好的文件。当您需要将代码库提供给大型语言模型（LLM）或其他 AI 工具（如 Claude、ChatGPT 和 Gemini）时，它是理想的选择。

## 🌟 功能

- **AI 优化**: 以一种易于 AI 理解和处理的方式格式化您的代码库
- **Token 计数**: 使用 tiktoken 提供每个文件和整个存储库的 token 计数
- **简单易用**: 只需一个命令即可打包您的整个存储库
- **可定制**: 轻松配置要包含或排除的内容
- **Git 感知**: 自动遵守您的 .gitignore 文件
- **安全至上**: 内置安全检查，以检测和防止包含敏感信息


## 🚀 快速开始

你可以使用 pip 安装 Repomix：

```bash
pip install repomix
```


然后在任何项目目录下运行：

```bash
python -m repomix
```


就这样！Repomix 将在您当前目录下生成一个 `repomix-output.md` 文件，其中包含您整个仓库的 AI 友好格式。

## 📊 用法

分析您的整个仓库：


```bash
python -m repomix
```

要打包一个特定的目录：


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

一旦你生成了打包文件，你就可以将其与 Claude、ChatGPT 和 Gemini 等生成式 AI 工具一起使用。

### 提示示例
一旦你使用 Repomix 生成了打包文件，你就可以将其与 Claude、ChatGPT 和 Gemini 等 AI 工具一起使用。以下是一些入门示例提示：


#### 代码审查和重构
进行全面的代码审查和重构建议：

```
这个文件包含我所有的代码。请审查整体结构，并提出任何改进或重构的机会，重点关注可维护性和可扩展性。
```


#### 文档生成
要生成项目文档：

```
基于此文件中的代码库，请生成一个详细的README.md，其中包括项目概述、主要功能、设置说明和使用示例。
```


#### 测试用例生成
用于生成测试用例：

```
分析此文件中的代码，并为主要函数和类建议一组全面的单元测试。包括边缘情况和潜在的错误场景。
```


#### 代码质量评估
评估代码质量和对最佳实践的遵循程度：

```
审查代码库，检查其是否符合编码最佳实践和行业标准。找出在可读性、可维护性和效率方面可以改进的地方。提出具体的修改建议，使代码与最佳实践保持一致。
```


#### 库概述
获取库的高级理解

```
此文件包含库的整个代码库。请提供该库的全面概述，包括其主要目的、关键特性和整体架构。
```


随意根据您的具体需求和您正在使用的 AI 工具的功能修改这些提示。

### 输出文件格式

Repomix 生成一个单一文件，其中代码库的不同部分之间有清晰的分隔符。为了增强 AI 的理解能力，输出文件以面向 AI 的解释开始，使 AI 模型更容易理解打包存储库的上下文和结构。


#### 纯文本格式 (默认)

```text
This file is a merged representation of the entire codebase, combining all repository files into a single document.

================================================================
File Summary
================================================================
(元数据和使用 AI 指令)

================================================================
Repository Structure
================================================================
src/
  cli/
    cliOutput.py
    index.py
  config/
    configLoader.py

(...剩余目录)

================================================================
Repository Files
================================================================

================
File: src/index.py
================
# 文件内容在这里

================
File: src/utils.py
================
# 文件内容在这里

(...剩余文件)

================================================================
Statistics
================================================================
(文件统计和元数据)
```


#### XML格式
要生成XML格式的输出，请使用 --style xml 选项：

```bash
python -m repomix --style xml
```


XML格式以分层方式构建内容：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<repository>
<repository_structure>
(目录和文件结构)
</repository_structure>

<repository_files>
<file>
  <path>src/index.py</path>
  <stats>
    <chars>1234</chars>
    <tokens>567</tokens>
  </stats>
  <content>
    # 这里是文件内容
  </content>
</file>
(...剩余文件)
</repository_files>

<statistics>
  <total_files>19</total_files>
  <total_chars>37377</total_chars>
  <total_tokens>11195</total_tokens>
</statistics>
</repository>
```


#### `Markdown 格式
要生成 Markdown 格式的输出，请使用 --style markdown 选项：

```bash
python -m repomix --style markdown
```

`````markdown
# File Summary
(元数据和使用 AI 指令)

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
# 文件内容在此
```

## File: src/utils.py
```python
# 文件内容在此
```

# 统计
- 文件总数: 19
- 字符总数: 37377
- 令牌总数: 11195
`````

## ⚙️ 配置

在你的项目根目录创建一个 `repomix.config.json` 文件来进行自定义配置：


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

### 输出格式

Repomix支持三种输出格式：

- **纯文本** (默认)
- **Markdown**
- **XML**

要指定输出格式：


```bash
python -m repomix --style markdown
```

### 命令行选项

- `-v, --version`: 显示版本
- `-o, --output <file>`: 指定输出文件名
- `--style <style>`: 指定输出样式 (plain, xml, markdown)
- `--remote <url>`: 处理远程 Git 仓库
- `--init`: 初始化配置文件
- `--no-security-check`: 禁用安全检查
- `--verbose`: 启用详细日志


## 🔍 安全检查

Repomix 包含内置的安全检查，以检测您文件中潜在的敏感信息。这有助于防止在共享代码库时意外暴露秘密。

您可以使用以下命令禁用安全检查：

```bash
python -m repomix --no-security-check
```


## 📜 许可证

本项目基于 MIT 许可证授权。

有关使用和配置选项的更多详细信息，请访问[文档](https://github.com/andersonby/python-repomix)。