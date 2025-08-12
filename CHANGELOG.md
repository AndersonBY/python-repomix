# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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