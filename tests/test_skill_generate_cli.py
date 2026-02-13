"""
Test suite for --skill-generate, --skill-output, --force CLI flags (Issue #18)
"""

import pytest

from src.repomix.cli.cli_run import create_parser
from src.repomix.cli.actions.default_action import (
    _validate_skill_options,
    _validate_option_conflicts,
    _build_cli_options_override,
)
from src.repomix.shared.error_handle import RepomixError


class TestSkillGenerateParser:
    """Test CLI parser for skill generation flags"""

    def test_skill_generate_flag_without_name(self):
        """--skill-generate without name sets True"""
        parser = create_parser()
        args = parser.parse_args(["--skill-generate"])
        assert args.skill_generate is True

    def test_skill_generate_flag_with_name(self):
        """--skill-generate with name sets the name string"""
        parser = create_parser()
        args = parser.parse_args(["--skill-generate", "my-skill"])
        assert args.skill_generate == "my-skill"

    def test_skill_generate_default_none(self):
        """--skill-generate defaults to None"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.skill_generate is None

    def test_skill_output_flag(self):
        """--skill-output sets the path"""
        parser = create_parser()
        args = parser.parse_args(["--skill-output", "/tmp/skills"])
        assert args.skill_output == "/tmp/skills"

    def test_force_flag(self):
        """-f/--force sets True"""
        parser = create_parser()
        args = parser.parse_args(["--force"])
        assert args.force is True

    def test_force_short_flag(self):
        """-f sets force to True"""
        parser = create_parser()
        args = parser.parse_args(["-f"])
        assert args.force is True

    def test_force_default_false(self):
        """--force defaults to False"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.force is False


class TestSkillOptionValidation:
    """Test validation of skill-related option dependencies"""

    def test_skill_output_without_skill_generate_raises(self):
        """--skill-output without --skill-generate should raise"""
        options = {"skill_output": "/tmp/skills", "skill_generate": None}
        with pytest.raises(RepomixError, match="--skill-output can only be used with --skill-generate"):
            _validate_skill_options(options)

    def test_force_without_skill_generate_raises(self):
        """--force without --skill-generate should raise"""
        options = {"force": True, "skill_generate": None}
        with pytest.raises(RepomixError, match="--force can only be used with --skill-generate"):
            _validate_skill_options(options)

    def test_skill_output_empty_string_raises(self):
        """--skill-output with empty string should raise"""
        options = {"skill_output": "", "skill_generate": True}
        with pytest.raises(RepomixError, match="--skill-output path cannot be empty"):
            _validate_skill_options(options)

    def test_skill_output_whitespace_only_raises(self):
        """--skill-output with whitespace-only string should raise"""
        options = {"skill_output": "   ", "skill_generate": True}
        with pytest.raises(RepomixError, match="--skill-output path cannot be empty"):
            _validate_skill_options(options)

    def test_skill_output_with_skill_generate_ok(self):
        """--skill-output with --skill-generate should not raise"""
        options = {"skill_output": "/tmp/skills", "skill_generate": True}
        _validate_skill_options(options)  # Should not raise

    def test_force_with_skill_generate_ok(self):
        """--force with --skill-generate should not raise"""
        options = {"force": True, "skill_generate": "my-skill"}
        _validate_skill_options(options)  # Should not raise

    def test_no_skill_options_ok(self):
        """No skill options should not raise"""
        options = {}
        _validate_skill_options(options)  # Should not raise


class TestOptionConflicts:
    """Test conflicting option validation"""

    def test_skill_generate_with_stdout_raises(self):
        options = {"skill_generate": True, "stdout": True}
        with pytest.raises(RepomixError, match="--skill-generate cannot be used with --stdout"):
            _validate_option_conflicts(options)

    def test_skill_generate_with_copy_raises(self):
        options = {"skill_generate": True, "copy": True}
        with pytest.raises(RepomixError, match="--skill-generate cannot be used with --copy"):
            _validate_option_conflicts(options)

    def test_split_output_with_stdout_raises(self):
        options = {"split_output": "500kb", "stdout": True}
        with pytest.raises(RepomixError, match="--split-output cannot be used with --stdout"):
            _validate_option_conflicts(options)

    def test_split_output_with_skill_generate_raises(self):
        options = {"split_output": "500kb", "skill_generate": True}
        with pytest.raises(RepomixError, match="--split-output cannot be used with --skill-generate"):
            _validate_option_conflicts(options)

    def test_split_output_with_copy_raises(self):
        options = {"split_output": "500kb", "copy": True}
        with pytest.raises(RepomixError, match="--split-output cannot be used with --copy"):
            _validate_option_conflicts(options)

    def test_no_conflicts_ok(self):
        options = {"skill_generate": True, "output": "out.md"}
        _validate_option_conflicts(options)  # Should not raise


class TestSkillGenerateConfigOverride:
    """Test skill_generate wiring through config override"""

    def test_skill_generate_string_in_override(self):
        """skill_generate string name should appear in override"""
        options = {"skill_generate": "my-skill"}
        result = _build_cli_options_override(options)
        assert result.get("skill_generate") == "my-skill"

    def test_skill_generate_true_in_override(self):
        """skill_generate True should appear in override"""
        options = {"skill_generate": True}
        result = _build_cli_options_override(options)
        assert result.get("skill_generate") is True

    def test_skill_generate_none_not_in_override(self):
        """skill_generate None should not appear in override"""
        options = {"skill_generate": None}
        result = _build_cli_options_override(options)
        assert "skill_generate" not in result
