"""
Test suite for configuration schema functionality
"""

import json
import pytest
from src.repomix.config.config_schema import (
    RepomixConfig,
    RepomixConfigOutput,
    RepomixOutputStyle,
)


class TestRepomixConfigOutput:
    """Test cases for RepomixConfigOutput class"""

    def test_style_property_setter(self):
        """Test setting style through property"""
        test_output = RepomixConfigOutput()

        # Setting style_enum should work and update the style field
        test_output.style_enum = "xml"

        assert test_output.style == "xml"  # style field updated to match enum
        assert test_output.style_enum == RepomixOutputStyle.XML

    def test_style_property_with_enum(self):
        """Test setting style with enum value"""
        test_output = RepomixConfigOutput()

        # Set the style using enum via style_enum property
        test_output.style_enum = RepomixOutputStyle.PLAIN

        assert test_output.style == "plain"  # style field updated to match enum
        assert test_output.style_enum == RepomixOutputStyle.PLAIN

    def test_invalid_style_value(self):
        """Test setting invalid style value"""
        # Test invalid style during initialization
        # Current implementation defaults to MARKDOWN for invalid values, doesn't raise
        test_output = RepomixConfigOutput(style="invalid_style")
        assert test_output.style_enum == RepomixOutputStyle.MARKDOWN

    def test_invalid_style_type(self):
        """Test setting style with invalid type"""
        # Test invalid style during initialization
        # Current implementation defaults to MARKDOWN for invalid types
        test_output = RepomixConfigOutput(style=123)  # type: ignore[arg-type]
        assert test_output.style_enum == RepomixOutputStyle.MARKDOWN

    def test_default_values(self):
        """Test default configuration values"""
        output = RepomixConfigOutput()

        assert output.file_path == "repomix-output.md"
        assert output.style == RepomixOutputStyle.MARKDOWN
        assert output.header_text == ""
        assert output.instruction_file_path == ""
        assert output.remove_comments is False
        assert output.remove_empty_lines is False
        assert output.top_files_length == 5
        assert output.show_line_numbers is False
        assert output.copy_to_clipboard is False
        assert output.include_empty_directories is False
        assert output.calculate_tokens is False
        assert output.show_file_stats is False
        assert output.show_directory_structure is True


class TestRepomixConfig:
    """Test cases for RepomixConfig class"""

    def test_nested_config_initialization(self):
        """Test nested config initialization with dictionary"""
        # Define output configuration as a dictionary
        output_dict = {
            "file_path": "test-output.xml",
            "style": "xml",  # This will be handled by __post_init__
            "calculate_tokens": True,
        }

        # Create full config with nested output dictionary
        full_config_dict = {"output": output_dict, "include": ["*"]}

        # Initialize the complete config
        full_config = RepomixConfig(**full_config_dict)

        # Verify the config structure
        assert isinstance(full_config.output, RepomixConfigOutput)
        assert full_config.output.style == "xml"
        assert full_config.output.style_enum == RepomixOutputStyle.XML
        assert full_config.output.calculate_tokens is True
        assert full_config.include == ["*"]

    def test_json_config_loading(self):
        """Test loading configuration from JSON-like structure"""
        # Create a complete config similar to repomix.config.json
        complete_config = {
            "output": {
                "file_path": "instructor-repo.xml",
                "style": "xml",
                "header_text": "",
                "instruction_file_path": "",
                "remove_comments": False,
                "remove_empty_lines": False,
                "top_files_length": 5,
                "show_line_numbers": False,
                "copy_to_clipboard": False,
                "include_empty_directories": False,
                "calculate_tokens": True,
            },
            "include": ["*"],
        }

        # Convert to JSON and back to simulate file loading
        json_str = json.dumps(complete_config)
        loaded_dict = json.loads(json_str)
        loaded_config = RepomixConfig(**loaded_dict)

        # Verify loaded configuration
        assert isinstance(loaded_config.output, RepomixConfigOutput)
        assert loaded_config.output.style == "xml"
        assert loaded_config.output.style_enum == RepomixOutputStyle.XML
        assert loaded_config.output.calculate_tokens is True
        assert loaded_config.output.file_path == "instructor-repo.xml"
        assert loaded_config.include == ["*"]

    def test_default_config_creation(self):
        """Test creating config with default values"""
        config = RepomixConfig()

        assert isinstance(config.output, RepomixConfigOutput)
        assert isinstance(config.security, type(config.security))
        assert isinstance(config.ignore, type(config.ignore))
        assert isinstance(config.compression, type(config.compression))
        assert config.include == []

    def test_compression_config_defaults(self):
        """Test compression configuration defaults"""
        config = RepomixConfig()

        assert config.compression.enabled is False
        assert config.compression.keep_signatures is True
        assert config.compression.keep_docstrings is True
        assert config.compression.keep_interfaces is True

    def test_security_config_defaults(self):
        """Test security configuration defaults"""
        config = RepomixConfig()

        assert config.security.enable_security_check is True
        assert config.security.exclude_suspicious_files is True

    def test_ignore_config_defaults(self):
        """Test ignore configuration defaults"""
        config = RepomixConfig()

        assert config.ignore.custom_patterns == []
        assert config.ignore.use_gitignore is True
        assert config.ignore.use_default_ignore is True

    def test_partial_config_initialization(self):
        """Test initialization with partial configuration"""
        partial_config = {
            "output": {"style": "plain", "show_line_numbers": True},
            "compression": {"enabled": True, "keep_signatures": False},
        }

        config = RepomixConfig(**partial_config)

        # Check that specified values are set
        assert config.output.style == RepomixOutputStyle.PLAIN
        assert config.output.show_line_numbers is True
        assert config.compression.enabled is True
        assert config.compression.keep_signatures is False

        # Check that unspecified values use defaults
        assert config.output.file_path == "repomix-output.md"  # default
        assert config.compression.keep_docstrings is True  # default

    def test_all_style_options(self):
        """Test all available style options"""
        styles = ["plain", "xml", "markdown"]

        for style_str in styles:
            config = RepomixConfig(output=RepomixConfigOutput(style=style_str))

            expected_enum = RepomixOutputStyle(style_str.lower())
            assert config.output.style_enum == expected_enum
            assert config.output.style == style_str

    def test_config_with_all_sections(self):
        """Test configuration with all sections specified"""
        full_config_dict = {
            "output": {
                "file_path": "custom-output.xml",
                "style": "xml",
                "show_line_numbers": True,
                "calculate_tokens": True,
            },
            "security": {
                "enable_security_check": False,
                "exclude_suspicious_files": False,
            },
            "ignore": {"custom_patterns": ["*.tmp", "*.log"], "use_gitignore": False},
            "compression": {
                "enabled": True,
                "keep_signatures": True,
                "keep_docstrings": False,
                "keep_interfaces": True,
            },
            "include": ["src/**", "tests/**"],
        }

        config = RepomixConfig(**full_config_dict)

        # Verify all sections
        assert config.output.file_path == "custom-output.xml"
        assert config.output.style == RepomixOutputStyle.XML
        assert config.output.show_line_numbers is True
        assert config.output.calculate_tokens is True

        assert config.security.enable_security_check is False
        assert config.security.exclude_suspicious_files is False

        assert config.ignore.custom_patterns == ["*.tmp", "*.log"]
        assert config.ignore.use_gitignore is False

        assert config.compression.enabled is True
        assert config.compression.keep_signatures is True
        assert config.compression.keep_docstrings is False
        assert config.compression.keep_interfaces is True

        assert config.include == ["src/**", "tests/**"]


class TestRepomixOutputStyle:
    """Test cases for RepomixOutputStyle enum"""

    def test_enum_values(self):
        """Test that all enum values are correct"""
        assert RepomixOutputStyle.PLAIN == "plain"
        assert RepomixOutputStyle.XML == "xml"
        assert RepomixOutputStyle.MARKDOWN == "markdown"

    def test_enum_from_string(self):
        """Test creating enum from string values"""
        assert RepomixOutputStyle("plain") == RepomixOutputStyle.PLAIN
        assert RepomixOutputStyle("xml") == RepomixOutputStyle.XML
        assert RepomixOutputStyle("markdown") == RepomixOutputStyle.MARKDOWN

    def test_invalid_enum_value(self):
        """Test that invalid enum values raise ValueError"""
        with pytest.raises(ValueError):
            RepomixOutputStyle("invalid")


class TestAdvancedOutputOptions:
    """Test cases for advanced output options in configuration"""

    def test_advanced_output_options_defaults(self):
        """Test that advanced output options have correct default values"""
        config = RepomixConfig()

        assert config.output.parsable_style is False
        assert config.output.stdout is False
        assert config.output.remove_comments is False
        assert config.output.remove_empty_lines is False
        assert config.output.truncate_base64 is False
        assert config.output.include_empty_directories is False
        assert config.output.include_diffs is False

    def test_advanced_output_options_configuration(self):
        """Test configuring advanced output options"""
        config_dict = {
            "output": {
                "parsable_style": True,
                "stdout": True,
                "remove_comments": True,
                "remove_empty_lines": True,
                "truncate_base64": True,
                "include_empty_directories": True,
                "include_diffs": True,
                "style": "xml"
            }
        }

        config = RepomixConfig(**config_dict)  # type: ignore[arg-type]

        assert config.output.parsable_style is True
        assert config.output.stdout is True
        assert config.output.remove_comments is True
        assert config.output.remove_empty_lines is True
        assert config.output.truncate_base64 is True
        assert config.output.include_empty_directories is True
        assert config.output.include_diffs is True
        assert config.output.style == RepomixOutputStyle.XML

    def test_advanced_output_options_json_serialization(self):
        """Test that advanced output options can be serialized to/from JSON"""
        original_config = {
            "output": {
                "file_path": "test-output.md",
                "style": "markdown",
                "parsable_style": True,
                "stdout": False,
                "remove_comments": True,
                "remove_empty_lines": False,
                "truncate_base64": True,
                "include_empty_directories": False,
                "include_diffs": True,
                "copy_to_clipboard": True
            }
        }

        # Convert to JSON and back to simulate config file loading
        import json
        json_str = json.dumps(original_config)
        loaded_dict = json.loads(json_str)
        config = RepomixConfig(**loaded_dict)

        # Verify all options are preserved
        assert config.output.file_path == "test-output.md"
        assert config.output.style == RepomixOutputStyle.MARKDOWN
        assert config.output.parsable_style is True
        assert config.output.stdout is False
        assert config.output.remove_comments is True
        assert config.output.remove_empty_lines is False
        assert config.output.truncate_base64 is True
        assert config.output.include_empty_directories is False
        assert config.output.include_diffs is True
        assert config.output.copy_to_clipboard is True


if __name__ == "__main__":
    pytest.main([__file__])
