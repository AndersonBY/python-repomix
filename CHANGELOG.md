# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 🔍 **Semantic CLI Suggestions**: Unknown CLI options now suggest the closest valid alternative (e.g., `--exclude` → "Did you mean: `--ignore`?")
- 📂 **Multiple Directories Support**: Process multiple directories in a single command (`repomix src lib tests`), with root-labeled file trees for multi-root output
- 🛠️ **Skill Generation CLI Flags**: New `--skill-generate`, `--skill-output`, and `--force` flags for Claude Agent Skills generation from CLI
- 🔇 **Quiet Mode**: New `--quiet` flag to suppress all console output except errors, with `--quiet`/`--verbose` conflict detection
- 🌿 **Remote Branch Flag**: New `--remote-branch` flag (replaces deprecated `--branch`) for specifying branch, tag, or commit for remote repositories
- 🔢 **Token Count Encoding**: New `--token-count-encoding` flag to specify custom tokenizer encoding (e.g., `o200k_base`, `cl100k_base`)
- 📄 **Ignore File Support**: Added `.repomixignore` and `.ignore` file support alongside `.gitignore`
- 🚫 **Output Control Flags**: New `--no-file-summary`, `--no-directory-structure`, `--no-files`, `--no-gitignore`, `--no-dot-ignore`, `--no-default-patterns` flags for fine-grained output control
- 🧪 **Comprehensive Test Suite**: Added 125 new tests covering all new features (418 → 543 total)

### Changed
- 🔧 **Type Checker Migration**: Replaced pyright with ty (from Astral/Ruff team) for faster, more accurate type checking
- 🧹 **Code Quality**: Applied ruff auto-fixes across codebase (`Optional[X]` → `X | None`), fixed `raise` without `from`, deprecated API usage
- 📦 **Type Safety**: Improved type annotations with `Sequence` for covariant parameters and `cast` for dict unpacking patterns

## [0.4.1] - 2026-01-29

### Fixed
- 🐛 **CLI Style Option**: Added missing `json` choice to `--style` CLI argument
## [0.4.0] - 2026-01-28

### Added
- 🎨 **JSON Output Format**: New `--style json` option for machine-readable structured output, perfect for integration with other tools and scripts
- 📊 **Git Log Integration**: Include recent commit history in output with `--include-logs` option
- 🔀 **Git Sort by Changes**: Sort files by change frequency with `--sort-by-changes` option, showing most frequently modified files first
- 📂 **Output Split**: Split large outputs into multiple files with configurable size limits using `split_output` configuration
- 🌳 **Token Count Tree**: Visualize token distribution across directories with `token_count_tree` option
- 📁 **Full Directory Structure**: Show complete directory tree including ignored files with `include_full_directory_structure` option
- 🔧 **Skill Generation**: Generate Claude Agent Skills from codebase with new skill generation module
- 🤖 **MCP generate_skill Tool**: New MCP tool for generating Claude Agent Skills directly from AI assistants
- 🌐 **Extended Tree-sitter Support**: Added support for 9 additional languages (Rust, Java, C, C++, C#, Ruby, PHP, Swift, CSS) - now supporting 13 languages total

### Changed
- 📝 **Configuration Schema**: Updated with new options for git integration, output splitting, and token tree visualization
- 📚 **Documentation**: Comprehensive updates to README files with new feature documentation
- 🧪 **Examples**: Added 5 new example files demonstrating JSON output, Git integration, output splitting, token tree, and full directory structure

### Fixed
- 🐛 **Test Fixes**: Fixed path comparison issues in test_file_stdin.py and output file path handling in test_core_functionality.py
## [0.3.4] - 2025-09-01

### Fixed
- 🔧 **Configuration Export**: Fixed internal field filtering and ensured style configuration is properly exported as string format, improving configuration reliability
## [0.3.3] - 2025-09-01

### Changed
- 🧹 **Configuration Migration**: Streamlined configuration migration by removing deprecated internal fields, improving startup performance and reducing memory footprint
- 📝 **Changelog Management**: Enhanced changelog formatting with improved version section extraction for better release automation

## [0.3.2] - 2025-08-12

### Added
- 🔄 **Configuration Migration**: Automatic backward compatibility handling for output style configuration changes
- 🚀 **Release Automation**: Automated changelog management that moves unreleased content to version sections during releases

### Changed
- 🧹 **Code Quality**: Improved code readability and maintainability in release management scripts

## [0.3.1] - 2025-01-02

### Added
- 🚀 **Release Management System**: Interactive release wizard with automated changelog generation and multi-step validation
- 🏗️ **Enhanced CI/CD Pipeline**: Comprehensive GitHub Actions workflows with multi-Python version testing (3.10, 3.11, 3.12)
- 🐳 **Docker Support**: Complete containerization with Dockerfile and comprehensive usage instructions for easy deployment
- 📊 **Advanced Output Options**: New CLI formatting options including parsable style, stdout output, and comment removal capabilities
- 🔧 **Standard Input Support**: `--stdin` option enables reading file paths from standard input for pipeline integration
- 🌳 **Tree-sitter Code Compression**: Intelligent AST-based Python code compression with multiple modes (interface, signature, minimal) for optimized LLM token usage and enhanced structural parsing
- 🤖 **MCP Server Integration**: Enhanced Model Context Protocol (MCP) server functionality with new tools and improved AI development workflow integration
- 📋 **Contributing Guidelines**: Added comprehensive contribution documentation for developers

### Changed  
- 📖 **Documentation Improvements**: Updated README with comprehensive Docker usage instructions and `--stdin` option guidance
- 🎯 **Code Quality Standards**: Integrated Ruff linting configuration across codebase for consistent formatting and linting
- 🧪 **Test Infrastructure**: Enhanced test environment with improved logger state management and output handling

### Fixed
- 🐛 **Configuration Validation**: Fixed RepomixConfigOutput style field handling to properly update with enum changes
- 🔧 **CLI Argument Processing**: Improved stdin option parsing and default action handling reliability

### Performance
- ⚡ **Tree-sitter Optimization**: Refined structural compression algorithms for better performance and accuracy

### Developer Experience
- 🤖 **Automated Release Tools**: Added release scripts with interactive prompts and validation
- 🔐 **PyPI Integration**: Streamlined publishing process with trusted publishing support
- 📋 **Comprehensive Testing**: Extended test coverage for advanced CLI options and configuration scenarios

## Previous Versions

For versions prior to 0.3.0, please check the git history or GitHub releases page.

---

## How to Update This Changelog

When preparing a release:

1. Move items from `[Unreleased]` to the new version section
2. Add the release date 
3. Create a new `[Unreleased]` section for future changes
4. Follow the categories: Added, Changed, Deprecated, Removed, Fixed, Security

Example entry:
```markdown
## [1.2.3] - 2024-12-25

### Added
- New awesome feature that users will love

### Fixed  
- Critical bug that was causing issues
```