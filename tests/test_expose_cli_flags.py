"""
Test suite for exposing config-only features as CLI flags (Issue #16)
"""

import pytest

from src.repomix.cli.cli_run import create_parser
from src.repomix.cli.actions.default_action import _build_cli_options_override, _parse_split_output


class TestExposedCLIFlags:
    """Test cases for newly exposed CLI flags"""

    def test_token_count_tree_flag_boolean(self):
        """Test --token-count-tree without value"""
        parser = create_parser()
        args = parser.parse_args(["--token-count-tree"])
        assert args.token_count_tree is True

    def test_token_count_tree_flag_with_threshold(self):
        """Test --token-count-tree with threshold value"""
        parser = create_parser()
        args = parser.parse_args(["--token-count-tree", "100"])
        assert args.token_count_tree == "100"

    def test_token_count_tree_default_none(self):
        """Test --token-count-tree defaults to None"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.token_count_tree is None

    def test_header_text_flag(self):
        """Test --header-text flag"""
        parser = create_parser()
        args = parser.parse_args(["--header-text", "Custom header"])
        assert args.header_text == "Custom header"

    def test_instruction_file_path_flag(self):
        """Test --instruction-file-path flag"""
        parser = create_parser()
        args = parser.parse_args(["--instruction-file-path", "/path/to/instructions.md"])
        assert args.instruction_file_path == "/path/to/instructions.md"

    def test_split_output_flag(self):
        """Test --split-output flag"""
        parser = create_parser()
        args = parser.parse_args(["--split-output", "2mb"])
        assert args.split_output == "2mb"

    def test_include_full_directory_structure_flag(self):
        """Test --include-full-directory-structure flag"""
        parser = create_parser()
        args = parser.parse_args(["--include-full-directory-structure"])
        assert args.include_full_directory_structure is True

    def test_no_git_sort_by_changes_flag(self):
        """Test --no-git-sort-by-changes flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-git-sort-by-changes"])
        assert args.no_git_sort_by_changes is True

    def test_include_logs_flag(self):
        """Test --include-logs flag"""
        parser = create_parser()
        args = parser.parse_args(["--include-logs"])
        assert args.include_logs is True

    def test_include_logs_count_flag(self):
        """Test --include-logs-count flag"""
        parser = create_parser()
        args = parser.parse_args(["--include-logs-count", "25"])
        assert args.include_logs_count == 25

    def test_no_gitignore_flag(self):
        """Test --no-gitignore flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-gitignore"])
        assert args.no_gitignore is True

    def test_no_default_patterns_flag(self):
        """Test --no-default-patterns flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-default-patterns"])
        assert args.no_default_patterns is True

    def test_all_defaults(self):
        """Test all new flags default correctly"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.token_count_tree is None
        assert args.header_text is None
        assert args.instruction_file_path is None
        assert args.split_output is None
        assert args.include_full_directory_structure is False
        assert args.no_git_sort_by_changes is False
        assert args.include_logs is False
        assert args.include_logs_count is None
        assert args.no_gitignore is False
        assert args.no_default_patterns is False


class TestBuildCliOptionsOverride:
    """Test _build_cli_options_override wiring"""

    def test_header_text_override(self):
        """Test header_text is passed through"""
        override = _build_cli_options_override({"header_text": "My header"})
        assert override["output"]["header_text"] == "My header"

    def test_instruction_file_path_override(self):
        """Test instruction_file_path is passed through"""
        override = _build_cli_options_override({"instruction_file_path": "/path/to/file"})
        assert override["output"]["instruction_file_path"] == "/path/to/file"

    def test_no_git_sort_by_changes_override(self):
        """Test --no-git-sort-by-changes sets git.sort_by_changes to False"""
        override = _build_cli_options_override({"no_git_sort_by_changes": True})
        assert override["output"]["git"]["sort_by_changes"] is False

    def test_include_logs_override(self):
        """Test --include-logs sets git.include_logs to True"""
        override = _build_cli_options_override({"include_logs": True})
        assert override["output"]["git"]["include_logs"] is True

    def test_include_logs_count_override(self):
        """Test --include-logs-count sets git.include_logs_count"""
        override = _build_cli_options_override({"include_logs_count": 25})
        assert override["output"]["git"]["include_logs_count"] == 25

    def test_no_gitignore_override(self):
        """Test --no-gitignore sets ignore.use_gitignore to False"""
        override = _build_cli_options_override({"no_gitignore": True})
        assert override["ignore"]["use_gitignore"] is False

    def test_no_default_patterns_override(self):
        """Test --no-default-patterns sets ignore.use_default_ignore to False"""
        override = _build_cli_options_override({"no_default_patterns": True})
        assert override["ignore"]["use_default_ignore"] is False

    def test_token_count_tree_override(self):
        """Test --token-count-tree is passed through"""
        override = _build_cli_options_override({"token_count_tree": True})
        assert override["output"]["token_count_tree"] is True

    def test_include_full_directory_structure_override(self):
        """Test --include-full-directory-structure is passed through"""
        override = _build_cli_options_override({"include_full_directory_structure": True})
        assert override["output"]["include_full_directory_structure"] is True


class TestParseSplitOutput:
    """Test _parse_split_output helper"""

    def test_parse_none(self):
        assert _parse_split_output(None) is None

    def test_parse_kb(self):
        assert _parse_split_output("500kb") == 500 * 1024

    def test_parse_mb(self):
        assert _parse_split_output("2mb") == 2 * 1024 * 1024

    def test_parse_fractional_mb(self):
        assert _parse_split_output("2.5mb") == int(2.5 * 1024 * 1024)

    def test_parse_gb(self):
        assert _parse_split_output("1gb") == 1024 * 1024 * 1024

    def test_parse_plain_bytes(self):
        assert _parse_split_output("1048576") == 1048576

    def test_parse_invalid(self):
        from src.repomix.shared.error_handle import RepomixError
        with pytest.raises(RepomixError):
            _parse_split_output("invalid")
