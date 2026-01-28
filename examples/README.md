# Repomix Usage Examples

This directory contains example code for using Repomix as a Python library. Each example demonstrates different use cases and functionalities.

## Example File Descriptions

### Basic Examples

1. **`basic_usage.py`** - Basic Usage Example
   - Demonstrates the most basic usage of Repomix
   - Includes repository processing and obtaining basic statistics
   - Outputs basic information such as file count, character count, and token count

2. **`custom_config.py`** - Custom Configuration Example
   - Demonstrates how to create and use custom configurations
   - Supports custom output formats (e.g., XML) and paths
   - Configurable file include/exclude rules
   - Supports security check option settings

3. **`security_check.py`** - Security Check Example
   - Demonstrates how to enable and use the security check feature
   - Detects potential sensitive information
   - Provides detailed reports of suspicious files

4. **`file_statistics.py`** - File Statistics Example
   - Provides detailed file statistics
   - Supports character and token count statistics at the file level
   - Visualizes the repository file tree structure

5. **`remote_repo_usage.py`** - Remote Repository Handling Example
   - Demonstrates how to handle remote Git repositories
   - Supports automatic cloning and temporary directory management
   - Provides complete analysis functionality for remote repositories

### Advanced Examples

6. **`json_output.py`** - JSON Output Format Example *(New)*
   - Demonstrates JSON output format for machine-readable results
   - Shows how to parse and use the structured JSON output
   - Useful for integration with other tools and scripts

7. **`git_integration.py`** - Git Integration Example *(New)*
   - Demonstrates Git diff and log integration
   - Shows how to include staged/unstaged changes in output
   - Enables sorting files by git change frequency

8. **`output_split.py`** - Output Split Example *(New)*
   - Demonstrates splitting large outputs into multiple files
   - Useful for very large codebases exceeding context limits
   - Files are intelligently grouped by directory structure

9. **`token_count_tree.py`** - Token Count Tree Example *(New)*
   - Visualize token distribution across directories
   - Identify which parts consume the most tokens
   - Useful for optimizing AI context usage

10. **`full_directory_structure.py`** - Full Directory Structure Example *(New)*
    - Show complete directory tree including ignored files
    - Useful for understanding full project structure
    - Distinguishes between structure display and content inclusion

11. **`tree_sitter_compression.py`** - Tree-sitter Compression Demonstration
    - Shows the difference between normal and tree-sitter compressed output
    - Demonstrates compression effects on real code files
    - Now supports 13 languages: Python, JavaScript, TypeScript, Go, Java, C, C++, C#, Rust, Ruby, PHP, Swift, CSS

## Running Examples

1. Ensure Repomix is installed:
   ```bash
   pip install repomix
   ```

2. Navigate to the examples directory:
   ```bash
   cd examples
   ```

3. Run any example:
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

## Notes

- Ensure to run the examples in a valid code repository
- Git integration features require a Git repository with history
- Configuration parameters can be adjusted according to actual needs
- It is recommended to read the comments in the example code to understand specific functionalities
- Remote repository handling requires a stable network connection
- The security check feature may take a longer processing time

## Configuration Description

All examples support custom configuration through `RepomixConfig`, with key configuration items including:

### Output Options
- `file_path`: Output file path
- `style`: Output format (`plain`, `markdown`, `xml`, `json`)
- `show_line_numbers`: Add line numbers to code blocks
- `calculate_tokens`: Enable token counting
- `split_output`: Maximum bytes per output file (for splitting)
- `token_count_tree`: Enable token distribution visualization
- `include_full_directory_structure`: Show complete directory tree

### Git Integration
- `git.include_diffs`: Include staged and unstaged changes
- `git.include_logs`: Include recent commit history
- `git.include_logs_count`: Number of commits to include
- `git.sort_by_changes`: Sort files by change frequency
- `git.sort_by_changes_max_commits`: Commits to analyze for sorting

### File Filtering
- `include`: Patterns for files to include
- `ignore.custom_patterns`: Additional ignore patterns
- `ignore.use_gitignore`: Respect .gitignore rules
- `ignore.use_default_ignore`: Use built-in ignore patterns

### Security
- `security.enable_security_check`: Enable sensitive data detection
- `security.exclude_suspicious_files`: Auto-exclude suspicious files

### Compression
- `compression.enabled`: Enable code compression
- `compression.keep_signatures`: Preserve function signatures
- `compression.keep_docstrings`: Preserve documentation
- `compression.keep_interfaces`: Interface-only mode

For detailed configuration, please refer to the individual example files.
