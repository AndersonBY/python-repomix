# 📋 使用 Commit 收集脚本生成 CHANGELOG

这个文档说明如何使用 `collect-commits.py` 脚本配合 Claude Code 来生成专业的 CHANGELOG.md 条目。

## 🚀 快速开始

### 1. 收集提交信息

```bash
# 收集自上次发布以来的所有提交
pdm run collect-commits

# 或者直接运行脚本
python scripts/collect-commits.py

# 收集最近 10 次提交
pdm run collect-commits -- --count 10

# 收集自特定标签以来的提交
pdm run collect-commits -- --since-tag v0.2.0

# 收集最近 5 次提交（不考虑标签）
pdm run collect-commits -- --all --count 5

# 预览会收集什么（不写入文件）
pdm run collect-commits -- --dry-run
```

### 2. 使用 Claude Code 生成 CHANGELOG

脚本运行后会提示：

```bash
✅ Commits summary written to: commits-for-changelog.md
📝 Next step: Use Claude Code to convert this into CHANGELOG.md entries
💡 Command: claude 'Help me convert these commits into CHANGELOG.md format and write the result to CHANGELOG.md file' 或启动交互模式: claude
```

## 📖 使用场景

### 场景 1: 准备新版本发布

```bash
# 1. 收集自上次发布的所有提交
pdm run collect-commits

# 2. 让 Claude Code 生成 CHANGELOG 条目
claude "请将 @commits-for-changelog.md 内的提交转换为 CHANGELOG.md 格式，重点突出用户关心的功能"

# 3. 编辑并更新 CHANGELOG.md
vim CHANGELOG.md

# 4. 提交并发布
git add CHANGELOG.md
git commit -m "docs: update changelog for v0.3.1"
pdm run quick-release patch
```

### 场景 2: 快速回顾最近的工作

```bash
# 收集最近 20 次提交进行回顾
pdm run collect-commits -- --count 20 --output recent-work.md

# 让 Claude 帮助总结
claude "@recent-work.md 请总结最近的工作进展，按功能分类"
```

### 场景 3: 特定时间段的变更

```bash
# 收集从特定版本到现在的所有变更
pdm run collect-commits -- --since-tag v0.2.0 --output v0.2.0-to-now.md

# 生成发布说明
claude "@v0.2.0-to-now.md 请生成从 v0.2.0 到现在的详细发布说明"
```

## 🎯 脚本功能详解

### 参数说明

- `--since-tag TAG`: 收集从指定标签以来的提交
- `--all`: 忽略标签，收集所有提交（或配合 --count 使用）
- `--count N` / `-n N`: 限制收集最近的 N 次提交
- `--output FILE` / `-o FILE`: 指定输出文件名
- `--dry-run`: 预览模式，显示会收集什么但不写入文件

### 智能分类

脚本会自动将提交按以下类别分类：

- **Added**: feat:, add, new, create, implement
- **Fixed**: fix:, bug, resolve, correct, patch  
- **Changed**: update, change, modify, improve, enhance
- **Security**: security:, sec:
- **Performance**: perf:
- **Documentation**: docs:, doc:
- **Tests**: test:, tests:
- **Maintenance**: chore:, build:, ci:

### 输出格式

生成的 markdown 文件包含：

1. **Claude Code 指令**: 详细的转换指导
2. **按类别分组的提交**: 便于理解变更类型
3. **时间顺序的提交列表**: 完整的变更历史
4. **贡献者列表**: 参与开发的人员
5. **原始数据**: JSON 格式的详细信息

## 💡 与 Claude Code 配合的最佳实践

### 提示词示例

```bash
# 生成用户友好的 CHANGELOG 并写入文件
claude "请查看 commits-for-changelog.md 并将这些 git 提交转换为专业的 CHANGELOG.md 条目：

1. 使用 Keep a Changelog 格式
2. 重点突出用户价值，而不是技术实现
3. 合并相关的提交为单个条目
4. 忽略纯内部的重构和格式化
5. 为重要功能添加简短说明

请将生成的内容添加到 CHANGELOG.md 文件的 [Unreleased] 部分下方。

输出格式：
## [0.3.1] - 2024-12-25
### Added
- 功能描述
"

# 生成技术发布说明
claude "请查看 commits-for-changelog.md 并基于这些提交生成技术发布说明，包括：
1. 主要新功能
2. 重要修复  
3. API 变更
4. 性能改进
5. 依赖更新

请将结果写入到 CHANGELOG.md 文件中。
"

# 生成简洁版本  
claude "请查看 commits-for-changelog.md 并生成简洁的发布摘要，每个类别最多 3 个要点，突出最重要的变更。请将结果写入到 CHANGELOG.md 文件中。"
```

## 🔄 完整工作流程

```bash
#!/bin/bash
# release-workflow.sh - 完整的发布工作流程

echo "🚀 开始发布流程..."

# 1. 检查工作目录状态
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 工作目录不干净，请先提交或储藏更改"
    exit 1
fi

# 2. 收集提交信息
echo "📝 收集提交信息..."
pdm run collect-commits

# 3. 提示使用 Claude Code
echo "✨ 请使用 Claude Code 生成 CHANGELOG:"
echo "claude '请查看 commits-for-changelog.md 并将这些提交转换为 CHANGELOG.md 格式，然后写入到 CHANGELOG.md 文件'"
echo ""
echo "然后："
echo "1. 编辑 CHANGELOG.md"  
echo "2. 运行: git add CHANGELOG.md && git commit -m 'docs: update changelog'"
echo "3. 运行: pdm run quick-release patch"
```

## 🎉 优势

- **省时间**: 自动收集和分类提交
- **一致性**: 标准化的 CHANGELOG 格式
- **智能化**: Claude Code 理解上下文并生成用户友好的描述
- **灵活性**: 多种收集模式适应不同需求
- **可追溯**: 保留原始提交信息以供参考

这个工作流程让您从繁琐的手动整理工作中解放出来，专注于编写高质量的发布说明！