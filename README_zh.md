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