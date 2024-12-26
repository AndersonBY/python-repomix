# Repomix Usage Examples

This directory contains example code for using Repomix as a Python library. Each example demonstrates different use cases and functionalities.

## Example File Descriptions

1. `basic_usage.py` - Basic Usage Example
   - Demonstrates the most basic usage of Repomix
   - Includes repository processing and obtaining basic statistics
   - Outputs basic information such as file count, character count, and token count

2. `custom_config.py` - Custom Configuration Example
   - Demonstrates how to create and use custom configurations
   - Supports custom output formats (e.g., XML) and paths
   - Configurable file include/exclude rules
   - Supports security check option settings
   - Supports integration of gitignore rules

3. `security_check.py` - Security Check Example
   - Demonstrates how to enable and use the security check feature
   - Detects potential sensitive information
   - Provides detailed reports of suspicious files
   - Supports automatic exclusion of suspicious files

4. `file_statistics.py` - File Statistics Example
   - Provides detailed file statistics
   - Supports character and token count statistics at the file level
   - Visualizes the repository file tree structure
   - Outputs a complete statistical report

5. `remote_repo_usage.py` - Remote Repository Handling Example
   - Demonstrates how to handle remote Git repositories
   - Supports automatic cloning and temporary directory management
   - Provides complete analysis functionality for remote repositories

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
   ```

## Notes

- Ensure to run the examples in a valid code repository
- Configuration parameters can be adjusted according to actual needs
- It is recommended to read the comments in the example code to understand specific functionalities
- Remote repository handling requires a stable network connection
- The security check feature may take a longer processing time

## Configuration Description

All examples support custom configuration through `RepomixConfig`, with key configuration items including:

- Output options: file path, format, whether to show line numbers, etc.
- File filtering: include/exclude rules, gitignore support
- Security checks: sensitive information detection, suspicious file handling
- Statistical options: whether to count comments, handle empty lines, etc.

For detailed configuration, please refer to the `custom_config.py` example. 