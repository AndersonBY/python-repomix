"""
Test suite for semantic CLI suggestions for unknown options (Issue #19)
"""

import pytest

from src.repomix.cli.cli_run import (
    create_parser,
    SEMANTIC_SUGGESTION_MAP,
    RepomixArgumentParser,
)


class TestSemanticSuggestionMap:
    """Test the semantic suggestion map contents"""

    def test_map_has_ignore_synonyms(self):
        """Synonyms for --ignore should be mapped"""
        for key in ["exclude", "reject", "omit", "skip", "blacklist"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--ignore" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_output_synonyms(self):
        """Synonyms for --output should be mapped"""
        for key in ["save", "export", "out", "file"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--output" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_style_synonyms(self):
        """Synonyms for --style should be mapped"""
        for key in ["format", "type", "syntax"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--style" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_verbose_synonyms(self):
        """Synonyms for --verbose should be mapped"""
        for key in ["debug", "detailed"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--verbose" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_quiet_synonyms(self):
        """Synonyms for --quiet should be mapped"""
        for key in ["silent", "mute"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--quiet" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_include_synonyms(self):
        """Synonyms for --include should be mapped"""
        for key in ["add", "with", "whitelist"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--include" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_remote_synonyms(self):
        """Synonyms for --remote should be mapped"""
        for key in ["clone", "git"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--remote" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_compress_synonyms(self):
        """Synonyms for --compress should be mapped"""
        for key in ["minimize", "reduce"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--compress" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_stdout_synonyms(self):
        """Synonyms for --stdout should be mapped"""
        for key in ["print", "console", "terminal"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--stdout" in SEMANTIC_SUGGESTION_MAP[key]

    def test_map_has_stdin_synonym(self):
        """Synonym for --stdin should be mapped"""
        assert "pipe" in SEMANTIC_SUGGESTION_MAP
        assert "--stdin" in SEMANTIC_SUGGESTION_MAP["pipe"]

    def test_map_has_remove_comments_synonyms(self):
        """Synonyms for --remove-comments should be mapped"""
        for key in ["strip-comments", "no-comments"]:
            assert key in SEMANTIC_SUGGESTION_MAP
            assert "--remove-comments" in SEMANTIC_SUGGESTION_MAP[key]


class TestRepomixArgumentParser:
    """Test the custom argument parser with semantic suggestions"""

    def test_parser_is_custom_class(self):
        """create_parser should return RepomixArgumentParser"""
        parser = create_parser()
        assert isinstance(parser, RepomixArgumentParser)

    def test_known_option_works_normally(self):
        """Known options should parse without error"""
        parser = create_parser()
        args = parser.parse_args(["--verbose"])
        assert args.verbose is True

    def test_unknown_option_with_semantic_match_exits(self):
        """Unknown option with semantic match should exit with suggestion"""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--exclude", "*.log"])
        assert exc_info.value.code == 2

    def test_unknown_option_without_semantic_match_exits(self):
        """Unknown option without semantic match should exit with default error"""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--totally-unknown-xyz"])
        assert exc_info.value.code == 2

    def test_semantic_suggestion_message(self, capsys):
        """Semantic suggestion should include 'Did you mean' message"""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--exclude", "*.log"])
        captured = capsys.readouterr()
        assert "Did you mean" in captured.err
        assert "--ignore" in captured.err

    def test_semantic_suggestion_for_format(self, capsys):
        """--format should suggest --style"""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--format", "xml"])
        captured = capsys.readouterr()
        assert "--style" in captured.err

    def test_semantic_suggestion_for_silent(self, capsys):
        """--silent should suggest --quiet"""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--silent"])
        captured = capsys.readouterr()
        assert "--quiet" in captured.err

    def test_semantic_suggestion_for_clone(self, capsys):
        """--clone should suggest --remote"""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--clone", "https://github.com/test/repo"])
        captured = capsys.readouterr()
        assert "--remote" in captured.err
