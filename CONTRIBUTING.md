# Contributing to Repomix (Python Version)

Thank you for your interest in contributing to Repomix! This document provides guidelines and information to help you contribute effectively to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Guidelines](#code-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Contributions](#submitting-contributions)
- [Project Structure](#project-structure)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [PDM (Python Dependency Manager)](https://pdm.fming.dev/) - Recommended
- Git

### First Time Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/AndersonBY/python-repomix.git
   cd python-repomix
   ```

3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/AndersonBY/python-repomix.git
   ```

## Development Setup

### Using PDM (Recommended)

```bash
# Install PDM if you haven't already
pip install pdm

# Install project dependencies
pdm install --dev
```

### Using pip (Alternative)

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install pytest pytest-asyncio ruff pyright
```

### Verify Installation

```bash
# Test the CLI
pdm run python -m repomix --help

# Run tests
pdm run python -m pytest

# Run code quality checks
pdm run ruff check .
pdm run pyright
```

## Development Workflow

### Branch Management

1. **Create a feature branch** from `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Work on your changes** with regular commits:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

3. **Keep your branch updated**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or modifying tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

Examples:
```
feat: add remote repository support with branch selection
fix: handle edge case in file encoding detection
docs: update installation instructions
test: add comprehensive MCP server tests
```

## Code Guidelines

### Code Style

We use **Ruff** for linting and **Pyright** for type checking:

```bash
# Run linter (with auto-fix)
pdm run ruff check --fix .

# Run type checker
pdm run pyright
```

### Code Quality Standards

1. **Type Annotations**: All new code must include type annotations
2. **Documentation**: Public functions and classes must have docstrings
3. **Error Handling**: Use appropriate exception handling and validation
4. **Security**: Never commit secrets or sensitive information
5. **Performance**: Consider performance implications for large repositories

### Architecture Principles

- **Modular Design**: Keep components loosely coupled
- **Single Responsibility**: Each class/function should have one clear purpose
- **Configuration-Driven**: Use the configuration system for customizable behavior
- **Error Recovery**: Handle edge cases gracefully
- **Testability**: Write code that's easy to test

## Testing

### Running Tests

```bash
# Run all tests
pdm run python -m pytest

# Run specific test file
pdm run python -m pytest tests/test_core_functionality.py

# Run tests with coverage
pdm run python -m pytest --cov=src/repomix --cov-report=html

# Run MCP-specific tests
pdm run python -m pytest tests/test_mcp*.py
```

### Test Guidelines

1. **Write Tests First**: Consider TDD for new features
2. **Test Coverage**: Aim for high test coverage, especially for core functionality
3. **Unit Tests**: Test individual components in isolation
4. **Integration Tests**: Test component interactions
5. **Edge Cases**: Test error conditions and boundary cases

### Test Structure

```python
class TestFeatureName:
    """Test suite for FeatureName functionality"""
    
    def setup_method(self):
        """Setup before each test method"""
        pass
    
    def test_basic_functionality(self):
        """Test basic feature behavior"""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        pass
```

## Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings for all public functions
- **Type Hints**: Include comprehensive type annotations
- **Comments**: Explain complex logic, not obvious code

Example:
```python
def process_repository(
    config: RepomixConfig,
    directory: Path
) -> ProcessResult:
    """Process a repository and generate output.
    
    Args:
        config: Configuration object with processing options
        directory: Path to the repository directory
        
    Returns:
        ProcessResult containing output and metadata
        
    Raises:
        RepositoryError: If repository cannot be processed
        ConfigurationError: If configuration is invalid
    """
```

### User Documentation

- Update README.md for user-facing changes
- Add examples for new features
- Update CLI help text when adding options

## Submitting Contributions

### Before Submitting

1. **Run all quality checks**:
   ```bash
   pdm run ruff check .
   pdm run pyright
   pdm run python -m pytest
   ```

2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Update CHANGELOG.md** with your changes

### Pull Request Process

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Use a descriptive title
   - Fill out the PR template
   - Link related issues
   - Add screenshots for UI changes

3. **Address review feedback**:
   - Make requested changes
   - Push updates to the same branch
   - Respond to comments

4. **Merge requirements**:
   - All CI checks must pass
   - At least one maintainer approval
   - No conflicts with main branch

## Project Structure

```
python-repomix/
├── src/repomix/           # Main source code
│   ├── cli/              # Command-line interface
│   ├── config/           # Configuration management
│   ├── core/             # Core processing logic
│   │   ├── file/         # File processing pipeline
│   │   ├── output/       # Output generation
│   │   └── security/     # Security scanning
│   ├── mcp/              # MCP (Model Context Protocol) server
│   └── shared/           # Shared utilities
├── tests/                # Test suite
├── docs/                 # Documentation (if any)
├── CLAUDE.md            # Claude Code instructions
├── pyproject.toml       # Project configuration
└── README.md            # Project documentation
```

### Key Components

- **RepoProcessor**: Main orchestrator for repository processing
- **Configuration System**: Hierarchical config loading and validation
- **File Pipeline**: Modular file collection, filtering, and processing
- **Output Generators**: Multiple output formats (markdown, XML, plain text)
- **MCP Server**: Model Context Protocol integration for AI tools
- **Security Layer**: Integration with detect-secrets for sensitive data detection

## Release Process

### Version Management

We use semantic versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Publish to PyPI (maintainers only)

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Code Reviews**: PR discussions and feedback

### Development Resources

- **Python Documentation**: [docs.python.org](https://docs.python.org/)
- **PDM Documentation**: [pdm.fming.dev](https://pdm.fming.dev/)
- **Type Hints**: [PEP 484](https://peps.python.org/pep-0484/)
- **Testing with pytest**: [pytest.org](https://pytest.org/)

### Common Issues

**Import Errors**: Make sure you've installed in development mode
```bash
pdm install --dev
```

**Type Check Failures**: Install and run pyright
```bash
pdm install --dev
pdm run pyright
```

**Test Failures**: Run tests individually to debug
```bash
pdm run python -m pytest tests/test_specific.py -v
```

## Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for all contributors. Please be respectful, inclusive, and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Recognition

Contributors are recognized in several ways:
- Listed in project documentation
- Mentioned in release notes
- GitHub contributor statistics
- Community appreciation

Thank you for contributing to Repomix! Your efforts help make this tool better for everyone in the AI and development community.