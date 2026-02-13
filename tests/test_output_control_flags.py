"""
Test suite for --no-file-summary, --no-directory-structure, --no-files CLI flags (Issue #10)
"""


from src.repomix.cli.cli_run import create_parser
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.output.output_generate import generate_output
from src.repomix.core.file.file_types import ProcessedFile


class TestOutputControlFlags:
    """Test cases for output control CLI flags"""

    def test_parser_no_file_summary_flag(self):
        """Test parser recognizes --no-file-summary flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-file-summary"])
        assert args.no_file_summary is True

    def test_parser_no_directory_structure_flag(self):
        """Test parser recognizes --no-directory-structure flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-directory-structure"])
        assert args.no_directory_structure is True

    def test_parser_no_files_flag(self):
        """Test parser recognizes --no-files flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-files"])
        assert args.no_files is True

    def test_parser_defaults_false(self):
        """Test all flags default to False"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.no_file_summary is False
        assert args.no_directory_structure is False
        assert args.no_files is False

    def test_config_file_summary_default_true(self):
        """Test file_summary defaults to True in config"""
        config = RepomixConfig()
        assert config.output.file_summary is True

    def test_config_directory_structure_default_true(self):
        """Test directory_structure defaults to True in config"""
        config = RepomixConfig()
        assert config.output.directory_structure is True

    def test_config_files_default_true(self):
        """Test files defaults to True in config"""
        config = RepomixConfig()
        assert config.output.files is True


class TestOutputControlGeneration:
    """Test output generation respects control flags"""

    def _make_config(self, **output_overrides):
        config = RepomixConfig()
        for k, v in output_overrides.items():
            setattr(config.output, k, v)
        return config

    def _make_files(self):
        return [ProcessedFile(path="test.py", content="print('hello')")]

    def _make_counts(self):
        return {"test.py": 15}, {"test.py": 3}

    def _make_tree(self):
        return {"test.py": ""}

    def test_no_file_summary_omits_header(self):
        """Test --no-file-summary omits the file summary section"""
        config = self._make_config(file_summary=False, style="markdown")
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        assert "File Summary" not in output

    def test_file_summary_enabled_includes_header(self):
        """Test file summary is included by default"""
        config = self._make_config(file_summary=True, style="markdown")
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        assert "File Summary" in output

    def test_no_directory_structure_omits_tree(self):
        """Test --no-directory-structure omits the directory tree"""
        config = self._make_config(directory_structure=False, style="markdown")
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        # The tree section header should not appear as a standalone section
        assert "\n# Repository Structure\n" not in output

    def test_directory_structure_enabled_includes_tree(self):
        """Test directory structure is included by default"""
        config = self._make_config(directory_structure=True, style="markdown")
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        assert "\n# Repository Structure\n" in output

    def test_no_files_omits_file_contents(self):
        """Test --no-files omits file contents"""
        config = self._make_config(files=False, style="markdown")
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        assert "print('hello')" not in output
        assert "Repository Files" not in output

    def test_files_enabled_includes_contents(self):
        """Test file contents are included by default"""
        config = self._make_config(files=True, style="markdown")
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        assert "print('hello')" in output

    def test_all_disabled_metadata_only(self):
        """Test all three flags disabled produces metadata-only output"""
        config = self._make_config(
            file_summary=False,
            directory_structure=False,
            files=False,
            style="markdown",
        )
        files = self._make_files()
        char_counts, token_counts = self._make_counts()
        tree = self._make_tree()

        output = generate_output(files, config, char_counts, token_counts, tree)
        assert "File Summary" not in output
        assert "Repository Structure" not in output
        assert "print('hello')" not in output
        # Statistics should still be present
        assert "Statistics" in output
