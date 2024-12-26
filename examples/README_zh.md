# Repomix 使用示例

这个目录包含了一些使用 Repomix 作为 Python 库的示例代码。每个示例都展示了不同的使用场景和功能。

## 示例文件说明

1. `basic_usage.py` - 基本使用示例
   - 展示了最基本的 Repomix 使用方法
   - 包含仓库处理和基本统计信息的获取
   - 输出文件数量、字符数和Token数等基础信息

2. `custom_config.py` - 自定义配置示例
   - 展示如何创建和使用自定义配置
   - 支持自定义输出格式（如XML）和路径
   - 可配置文件包含/排除规则
   - 支持安全检查选项设置
   - 支持 gitignore 规则集成

3. `security_check.py` - 安全检查示例
   - 展示如何启用和使用安全检查功能
   - 检测潜在的敏感信息
   - 提供可疑文件的详细报告
   - 支持自动排除可疑文件

4. `file_statistics.py` - 文件统计示例
   - 提供详细的文件统计信息
   - 支持单文件级别的字符数和Token数统计
   - 可视化展示仓库文件树结构
   - 输出完整的统计报告

5. `remote_repo_usage.py` - 远程仓库处理示例
   - 展示如何处理远程 Git 仓库
   - 支持自动克隆和临时目录管理
   - 提供远程仓库的完整分析功能

## 运行示例

1. 确保已安装 Repomix：
   ```bash
   pip install repomix
   ```

2. 进入示例目录：
   ```bash
   cd examples
   ```

3. 运行任意示例：
   ```bash
   python basic_usage.py
   python custom_config.py
   python security_check.py
   python file_statistics.py
   python remote_repo_usage.py
   ```

## 注意事项

- 运行示例前请确保在有效的代码仓库中执行
- 可根据实际需求调整配置参数
- 建议先阅读示例代码的注释，了解具体功能
- 远程仓库处理需要确保网络连接正常
- 安全检查功能可能需要较长处理时间

## 配置说明

所有示例都支持通过 `RepomixConfig` 进行自定义配置，主要配置项包括：

- 输出选项：文件路径、格式、是否显示行号等
- 文件过滤：包含/排除规则、gitignore 支持
- 安全检查：敏感信息检测、可疑文件处理
- 统计选项：是否统计注释、空行处理等

详细配置请参考 `custom_config.py` 示例。 