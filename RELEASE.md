# 🚀 Release Process Guide

This document explains how to use the automated release system for Python Repomix.

## 📋 Overview

The release system consists of:

1. **Interactive Release Wizard**: Foolproof step-by-step release process
2. **Automated Workflows**: GitHub Actions for CI/CD
3. **Version Management**: Scripts for version bumping
4. **Changelog Generation**: AI-assisted release notes with Claude Code
5. **Multi-Platform Publishing**: PyPI and GitHub Releases

## 🎯 Quick Start

### 🧙‍♂️ Interactive Release Wizard (推荐)

For the easiest release experience:

```bash
# Start the interactive release wizard
pdm run release

# The wizard will guide you through:
# 1. Environment checks
# 2. Version selection
# 3. Tests and validation
# 4. Changelog generation with Claude Code
# 5. Automatic publishing
```

### ⚡ Quick Release (高级用户)

For experienced users who want direct control:

```bash
# Patch release (0.3.0 → 0.3.1)
pdm run quick-release patch

# Minor release (0.3.0 → 0.4.0)
pdm run quick-release minor

# Major release (0.3.0 → 1.0.0)
pdm run quick-release major

# Specific version
pdm run quick-release patch --version 0.3.2

# Dry run (preview changes)
pdm run quick-release minor --dry-run
```

## 🔄 Release Workflow

### 1. Automated CI/CD Pipeline

- **CI Workflow** (`.github/workflows/ci.yml`): Runs on every push/PR
  - Tests across Python 3.10, 3.11, 3.12
  - Linting with Ruff
  - Type checking with Pyright
  - Docker image testing

- **Release Workflow** (`.github/workflows/release.yml`): Triggered by version tags
  - Full test suite
  - Package building
  - Automatic changelog generation
  - GitHub Release creation
  - PyPI publishing

### 2. Available Scripts

The project provides multiple release tools:

- **`pdm run release`** - Interactive release wizard (recommended)
- **`pdm run quick-release`** - Direct version bumping for advanced users
- **`pdm run collect-commits`** - Collect commits for changelog generation
- **`pdm run test`** - Run test suite
- **`pdm run lint`** - Run code linting
- **`pdm run typecheck`** - Run type checking

## 🤖 AI-Assisted Changelog Generation

The release wizard integrates with Claude Code for intelligent changelog generation:

### Automatic Commit Collection

```bash
# Collect commits since last release
pdm run collect-commits

# This creates commits-for-changelog.md with structured commit data
```

### Claude Code Integration

The wizard will prompt you to run:

```bash
claude "请分析 @commits-for-changelog.md 中的提交，生成结构化的 CHANGELOG.md 条目，重点突出用户关心的功能改进、新特性和错误修复。请直接写入到 CHANGELOG.md 文件的 [Unreleased] 部分。"
```

Claude Code will automatically:
- Analyze commit messages
- Categorize changes (Added, Fixed, Changed, etc.)
- Generate user-friendly descriptions
- Write directly to CHANGELOG.md

## 📝 Changelog Management

### Two Approaches for Release Notes

1. **CHANGELOG.md (Recommended)**
   - Manually maintained detailed change records
   - Follows [Keep a Changelog](https://keepachangelog.com/) format
   - GitHub Release will **prioritize** content from here
   - Provides structured change categorization (Added, Fixed, Changed, etc.)

2. **Auto-generated from Git History (Fallback)**
   - Automatically enabled when no corresponding version exists in CHANGELOG.md
   - Generated from Git commit messages
   - Includes commit list and contributor information

### Release Page Content Priority

GitHub Release page content **priority** is as follows:

1. **First choice**: Content for the corresponding version in CHANGELOG.md
   ```markdown
   ## [0.3.1] - 2024-12-25
   ### Added
   - Docker support for easy deployment
   ### Fixed  
   - Fixed line numbering in output
   ```

2. **Second choice**: Content from the `[Unreleased]` section in CHANGELOG.md

3. **Fallback**: Auto-generated Git commit history

### How to Write Good Release Notes

**When adding versions in CHANGELOG.md:**

```markdown
## [0.3.1] - 2024-12-25

### Added
- 🐳 Docker support for containerized usage
- 🔄 Automatic changelog generation from CHANGELOG.md
- ✅ Enhanced CI/CD with multi-Python version testing

### Fixed
- 🐛 Fixed line numbering not working with --output-show-line-numbers
- 🔧 Resolved Docker build issues on ARM platforms

### Changed  
- 📝 Improved documentation with clearer examples
- ⚡ Better error messages for invalid configurations

### Developer Experience
- 🛠 Added release automation script
- 📊 Enhanced testing coverage
```

**Best Practices:**
- Use emojis to make content more engaging (optional)
- Sort by impact level (important features first)
- Write about features users care about, not technical details
- Explain **why** this change is important

## 🚀 Step-by-Step Release Process

### Using the Interactive Wizard (Recommended)

The interactive release wizard (`pdm run release`) handles everything automatically:

1. **Environment Checks**
   - Verifies clean git state
   - Checks for required tools
   - Validates current branch

2. **Version Selection**
   - Shows current version (e.g., 0.3.0)
   - Displays next version options:
     - **Patch (0.3.1)**: Bug fixes, small improvements
     - **Minor (0.4.0)**: New features, backward compatible
     - **Major (1.0.0)**: Breaking changes
     - **Custom**: Specify exact version

3. **Quality Assurance**
   - Runs test suite automatically
   - Performs linting checks
   - Validates type checking
   - Shows detailed error messages if anything fails

4. **Changelog Generation**
   - Collects commits since last release
   - Provides Claude Code command for AI-assisted changelog
   - Previews [Unreleased] section
   - Allows manual editing before proceeding

5. **Release Execution**
   - Updates version numbers in files
   - Creates git commit and tag
   - Pushes to GitHub to trigger release workflow
   - Provides monitoring links

### Manual Process (Advanced Users)

If you prefer manual control:

```bash
# 1. Prepare environment
git checkout main && git pull origin main
git status  # Should be clean

# 2. Collect commits and generate changelog
pdm run collect-commits
claude "Generate changelog from @commits-for-changelog.md and write to CHANGELOG.md"

# 3. Edit and commit changelog
vim CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: update changelog for v0.3.1"

# 4. Create release
pdm run quick-release patch  # or minor/major
```

## ✅ Release Verification

After any release method, verify:

- **GitHub Actions**: Check the release workflow status
- **GitHub Releases**: Verify release notes and assets are created
- **PyPI**: Confirm new version is published
- **Installation Test**: `pip install repomix==NEW_VERSION`

Both methods will provide monitoring links and status updates.

## 🔧 Configuration Details

### PyPI Trusted Publishing

The workflow uses PyPI's trusted publishing feature. To set up:

1. Go to [PyPI Trusted Publishers](https://pypi.org/manage/account/publishing/)
2. Add this repository with these settings:
   - Owner: `your-username`
   - Repository: `python-repomix`
   - Workflow: `release.yml`
   - Environment: (leave empty)

### Available Development Commands

All development commands are available through PDM:

```bash
# Release commands
pdm run release          # Interactive release wizard
pdm run quick-release    # Direct version bumping
pdm run collect-commits  # Collect commits for changelog

# Development commands
pdm run test            # Run test suite
pdm run lint            # Run ruff linter
pdm run lint-fix        # Run ruff with auto-fix
pdm run typecheck       # Run pyright type checker
pdm run format          # Format code with ruff
pdm run check           # Run all quality checks
```

## 📊 What Happens During Release

### Version Bump Process
- Updates `pyproject.toml` version
- Updates `src/repomix/__init__.py` version  
- Commits changes with message: "bump: version X.X.X"
- Creates annotated git tag: "vX.X.X"
- Pushes commit and tag to GitHub

### GitHub Release Workflow
1. **Quality Checks**: Full test suite, linting, type checking
2. **Package Building**: Build wheel and source distribution
3. **Changelog Extraction**: From CHANGELOG.md or git history
4. **Publishing**: Creates GitHub Release and publishes to PyPI

## 🛠 Troubleshooting

### Common Issues

**Release Workflow Fails**
```bash
# Delete failed tag and retry
git push --delete origin vX.X.X
pdm run release  # or pdm run quick-release patch
```

**PyPI Publishing Fails**
- Verify trusted publishing setup on PyPI
- Check if version already exists
- Test local build: `pdm build`

**Git Working Directory Not Clean**
```bash
git status                     # Check for uncommitted changes
git stash                     # Stash changes if needed
git checkout main             # Ensure on main branch
```

### Manual Recovery

If automatic release fails:

```bash
# Build and publish manually
pdm build
pdm publish

# Create GitHub release manually
gh release create vX.X.X dist/* \
  --title "Release X.X.X" \
  --notes "Manual release"
```

## 📋 Release Checklist

**Before Release:**
- [ ] All tests passing in CI
- [ ] Documentation updated
- [ ] Clean git working directory
- [ ] On main branch with latest changes

**After Release:**
- [ ] Verify GitHub Release created
- [ ] Verify PyPI package published  
- [ ] Test installation from PyPI
- [ ] Update any dependent projects

## 🎉 Summary

The release system provides two complementary approaches:

1. **`pdm run release`** - Foolproof interactive wizard with AI-assisted changelog
2. **`pdm run quick-release patch`** - Direct version bumping for power users

Both integrate with the same GitHub Actions workflow for consistent, automated publishing.

Happy releasing! 🚀