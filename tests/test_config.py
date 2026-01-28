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
from src.repomix.config.config_load import migrate_config_format


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
                "style": "xml",
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
                "copy_to_clipboard": True,
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


class TestConfigMigration:
    """Test cases for configuration migration functionality"""

    def test_style_migration_from_underscore_style(self):
        """Test that _style is properly migrated to style"""
        old_config = {
            "output": {"file_path": "repomix-output.md", "_style": "markdown", "header_text": "", "remove_comments": False},
            "security": {"enable_security_check": True},
        }

        migrated = migrate_config_format(old_config)

        # Check that _style was converted to style
        assert "_style" not in migrated["output"]
        assert migrated["output"]["style"] == "markdown"

        # Verify we can create RepomixConfig with migrated data
        config_obj = RepomixConfig(**migrated)
        assert config_obj.output.style == "markdown"
        assert config_obj.output.style_enum == RepomixOutputStyle.MARKDOWN

    def test_style_migration_with_both_style_and_underscore_style(self):
        """Test that _style is removed when both _style and style are present"""
        config_with_both = {"output": {"_style": "xml", "style": "markdown"}}

        migrated = migrate_config_format(config_with_both)
        assert "_style" not in migrated["output"]
        assert migrated["output"]["style"] == "markdown"

    def test_migration_preserves_new_format(self):
        """Test that new config format without _style is unchanged"""
        new_config = {"output": {"style": "xml", "file_path": "output.xml"}}

        migrated = migrate_config_format(new_config)
        assert migrated["output"]["style"] == "xml"
        assert "_style" not in migrated["output"]

    def test_migration_with_real_user_config(self):
        """Test with the actual problematic config from user"""
        user_config = {
            "output": {
                "file_path": "repomix-output.md",
                "_style": "markdown",
                "header_text": "",
                "instruction_file_path": "",
                "remove_comments": False,
                "remove_empty_lines": False,
                "top_files_length": 5,
                "show_line_numbers": False,
                "copy_to_clipboard": False,
                "include_empty_directories": False,
                "calculate_tokens": False,
                "show_file_stats": False,
                "show_directory_structure": True,
            },
            "security": {"enable_security_check": True, "exclude_suspicious_files": True},
            "ignore": {"custom_patterns": [], "use_gitignore": True, "use_default_ignore": True},
            "include": [],
        }

        migrated = migrate_config_format(user_config)

        # Verify migration
        assert "_style" not in migrated["output"]
        assert migrated["output"]["style"] == "markdown"

        # Test that we can create RepomixConfig with migrated data
        config_obj = RepomixConfig(**migrated)
        assert config_obj.output.style == "markdown"
        assert config_obj.output.style_enum == RepomixOutputStyle.MARKDOWN
        assert config_obj.output.top_files_length == 5
        assert config_obj.security.enable_security_check is True


class TestNewConfigOptions:
    """Test cases for new configuration options added from TypeScript version"""

    def test_json_output_style(self):
        """Test JSON output style option"""
        config = RepomixConfig(output={"style": "json"})
        assert config.output.style == "json"
        assert config.output.style_enum == RepomixOutputStyle.JSON

    def test_git_config_defaults(self):
        """Test git configuration defaults"""
        from src.repomix.config.config_schema import RepomixConfigGit

        config = RepomixConfig()
        assert isinstance(config.output.git, RepomixConfigGit)
        assert config.output.git.sort_by_changes is True
        assert config.output.git.sort_by_changes_max_commits == 100
        assert config.output.git.include_diffs is False
        assert config.output.git.include_logs is False
        assert config.output.git.include_logs_count == 50

    def test_git_config_from_dict(self):
        """Test git configuration from dictionary"""
        config_dict = {
            "output": {
                "git": {
                    "sort_by_changes": False,
                    "sort_by_changes_max_commits": 50,
                    "include_diffs": True,
                    "include_logs": True,
                    "include_logs_count": 100,
                }
            }
        }
        config = RepomixConfig(**config_dict)
        assert config.output.git.sort_by_changes is False
        assert config.output.git.sort_by_changes_max_commits == 50
        assert config.output.git.include_diffs is True
        assert config.output.git.include_logs is True
        assert config.output.git.include_logs_count == 100

    def test_input_config_defaults(self):
        """Test input configuration defaults"""
        from src.repomix.config.config_schema import RepomixConfigInput

        config = RepomixConfig()
        assert isinstance(config.input, RepomixConfigInput)
        assert config.input.max_file_size == 50 * 1024 * 1024  # 50MB

    def test_input_config_from_dict(self):
        """Test input configuration from dictionary"""
        config_dict = {"input": {"max_file_size": 10 * 1024 * 1024}}  # 10MB
        config = RepomixConfig(**config_dict)
        assert config.input.max_file_size == 10 * 1024 * 1024

    def test_output_new_options_defaults(self):
        """Test new output options defaults"""
        config = RepomixConfig()
        assert config.output.include_full_directory_structure is False
        assert config.output.split_output is None
        assert config.output.token_count_tree is False
        assert config.output.compress is False

    def test_output_new_options_configuration(self):
        """Test configuring new output options"""
        config_dict = {
            "output": {
                "include_full_directory_structure": True,
                "split_output": 1024 * 1024,  # 1MB
                "token_count_tree": True,
                "compress": True,
            }
        }
        config = RepomixConfig(**config_dict)
        assert config.output.include_full_directory_structure is True
        assert config.output.split_output == 1024 * 1024
        assert config.output.token_count_tree is True
        assert config.output.compress is True

    def test_token_count_tree_variants(self):
        """Test token_count_tree with different value types"""
        # Boolean
        config1 = RepomixConfig(output={"token_count_tree": True})
        assert config1.output.token_count_tree is True

        # Integer (depth limit)
        config2 = RepomixConfig(output={"token_count_tree": 3})
        assert config2.output.token_count_tree == 3

        # String (custom format)
        config3 = RepomixConfig(output={"token_count_tree": "detailed"})
        assert config3.output.token_count_tree == "detailed"

    def test_skill_generate_defaults(self):
        """Test skill_generate configuration defaults"""
        config = RepomixConfig()
        assert config.skill_generate is False

    def test_skill_generate_with_bool(self):
        """Test skill_generate with boolean value"""
        config = RepomixConfig(skill_generate=True)
        assert config.skill_generate is True

    def test_skill_generate_with_string(self):
        """Test skill_generate with string value (skill name)"""
        config = RepomixConfig(skill_generate="my-skill")
        assert config.skill_generate == "my-skill"

    def test_legacy_include_diffs_migration(self):
        """Test that legacy include_diffs is migrated to git.include_diffs"""
        config_dict = {"output": {"include_diffs": True}}
        config = RepomixConfig(**config_dict)
        # Legacy field should migrate to git.include_diffs
        assert config.output.git.include_diffs is True

    def test_all_style_options_including_json(self):
        """Test all available style options including JSON"""
        styles = ["plain", "xml", "markdown", "json"]

        for style_str in styles:
            config = RepomixConfig(output={"style": style_str})
            expected_enum = RepomixOutputStyle(style_str.lower())
            assert config.output.style_enum == expected_enum
            assert config.output.style == style_str

    def test_complete_new_config(self):
        """Test complete configuration with all new options"""
        complete_config = {
            "input": {"max_file_size": 25 * 1024 * 1024},
            "output": {
                "style": "json",
                "include_full_directory_structure": True,
                "split_output": 2 * 1024 * 1024,
                "token_count_tree": 5,
                "compress": True,
                "git": {
                    "sort_by_changes": True,
                    "sort_by_changes_max_commits": 200,
                    "include_diffs": True,
                    "include_logs": True,
                    "include_logs_count": 25,
                },
            },
            "skill_generate": "test-skill",
        }

        config = RepomixConfig(**complete_config)

        # Verify input
        assert config.input.max_file_size == 25 * 1024 * 1024

        # Verify output
        assert config.output.style == "json"
        assert config.output.include_full_directory_structure is True
        assert config.output.split_output == 2 * 1024 * 1024
        assert config.output.token_count_tree == 5
        assert config.output.compress is True

        # Verify git
        assert config.output.git.sort_by_changes is True
        assert config.output.git.sort_by_changes_max_commits == 200
        assert config.output.git.include_diffs is True
        assert config.output.git.include_logs is True
        assert config.output.git.include_logs_count == 25

        # Verify skill_generate
        assert config.skill_generate == "test-skill"


if __name__ == "__main__":
    pytest.main([__file__])
