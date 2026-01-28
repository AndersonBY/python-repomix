# Repomix 使用示例

本目录包含使用 Repomix 作为 Python 库的示例代码。每个示例演示不同的用例和功能。

## 示例文件说明

### 基础示例

1. **`basic_usage.py`** - 基本使用示例
   - 演示 Repomix 最基本的使用方法
   - 包括仓库处理和获取基本统计信息
   - 输出文件数量、字符数、token 数等基本信息

2. **`custom_config.py`** - 自定义配置示例
   - 演示如何创建和使用自定义配置
   - 支持自定义输出格式（如 XML）和路径
   - 可配置文件包含/排除规则
   - 支持安全检查选项设置

3. **`security_check.py`** - 安全检查示例
   - 演示如何启用和使用安全检查功能
   - 检测潜在的敏感信息
   - 提供可疑文件的详细报告

4. **`file_statistics.py`** - 文件统计示例
   - 提供详细的文件统计信息
   - 支持文件级别的字符和 token 计数统计
   - 可视化仓库文件树结构

5. **`remote_repo_usage.py`** - 远程仓库处理示例
   - 演示如何处理远程 Git 仓库
   - 支持自动克隆和临时目录管理
   - 提供远程仓库的完整分析功能

### 高级示例

6. **`json_output.py`** - JSON 输出格式示例 *(新增)*
   - 演示 JSON 输出格式，用于机器可读的结果
   - 展示如何解析和使用结构化 JSON 输出
   - 适用于与其他工具和脚本集成

7. **`git_integration.py`** - Git 集成示例 *(新增)*
   - 演示 Git diff 和 log 集成
   - 展示如何在输出中包含暂存和未暂存的更改
   - 启用按 git 变更频率排序文件

8. **`output_split.py`** - 输出分割示例 *(新增)*
   - 演示将大型输出分割成多个文件
   - 适用于超出上下文限制的大型代码库
   - 文件按目录结构智能分组

9. **`token_count_tree.py`** - Token 计数树示例 *(新增)*
   - 可视化目录间的 token 分布
   - 识别哪些部分消耗最多 token
   - 用于优化 AI 上下文使用

10. **`full_directory_structure.py`** - 完整目录结构示例 *(新增)*
    - 显示完整的目录树，包括被忽略的文件
    - 用于了解完整的项目结构
    - 区分结构显示和内容包含

11. **`tree_sitter_compression.py`** - Tree-sitter 压缩演示
    - 展示普通输出和 tree-sitter 压缩输出的区别
    - 演示真实代码文件的压缩效果
    - 现支持 13 种语言：Python、JavaScript、TypeScript、Go、Java、C、C++、C#、Rust、Ruby、PHP、Swift、CSS

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
   python json_output.py
   python git_integration.py
   python output_split.py
   python token_count_tree.py
   python full_directory_structure.py
   python tree_sitter_compression.py
   ```

## 注意事项

- 确保在有效的代码仓库中运行示例
- Git 集成功能需要带有历史记录的 Git 仓库
- 配置参数可根据实际需求调整
- 建议阅读示例代码中的注释以了解具体功能
- 远程仓库处理需要稳定的网络连接
- 安全检查功能可能需要较长的处理时间

## 配置说明

所有示例都支持通过 `RepomixConfig` 进行自定义配置，主要配置项包括：

### 输出选项
- `file_path`：输出文件路径
- `style`：输出格式（`plain`、`markdown`、`xml`、`json`）
- `show_line_numbers`：在代码块中添加行号
- `calculate_tokens`：启用 token 计数
- `split_output`：每个输出文件的最大字节数（用于分割）
- `token_count_tree`：启用 token 分布可视化
- `include_full_directory_structure`：显示完整目录树

### Git 集成
- `git.include_diffs`：包含暂存和未暂存的更改
- `git.include_logs`：包含最近的提交历史
- `git.include_logs_count`：包含的提交数量
- `git.sort_by_changes`：按变更频率排序文件
- `git.sort_by_changes_max_commits`：分析排序的提交数量

### 文件过滤
- `include`：要包含的文件模式
- `ignore.custom_patterns`：额外的忽略模式
- `ignore.use_gitignore`：遵循 .gitignore 规则
- `ignore.use_default_ignore`：使用内置忽略模式

### 安全
- `security.enable_security_check`：启用敏感数据检测
- `security.exclude_suspicious_files`：自动排除可疑文件

### 压缩
- `compression.enabled`：启用代码压缩
- `compression.keep_signatures`：保留函数签名
- `compression.keep_docstrings`：保留文档
- `compression.keep_interfaces`：仅接口模式

详细配置请参考各个示例文件。
