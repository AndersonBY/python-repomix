"""
Test suite for --quiet CLI flag (Issue #9)
"""

import pytest
from unittest.mock import patch, MagicMock

from src.repomix.cli.cli_run import create_parser, execute_action
from src.repomix.shared.logger import logger, LogLevel


class TestQuietFlag:
    """Test cases for --quiet CLI flag"""

    def test_parser_quiet_flag(self):
        """Test parser recognizes --quiet flag"""
        parser = create_parser()
        args = parser.parse_args(["--quiet"])
        assert args.quiet is True

    def test_parser_quiet_default_false(self):
        """Test --quiet defaults to False"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.quiet is False

    def test_quiet_sets_silent_log_level(self):
        """Test --quiet sets log level to SILENT"""
        parser = create_parser()
        args = parser.parse_args(["--quiet"])

        original_level = logger.get_log_level()
        try:
            with patch("src.repomix.cli.cli_run.run_default_action") as mock_action:
                mock_action.return_value = MagicMock()
                execute_action(".", ".", args)
                assert logger.get_log_level() == LogLevel.SILENT
        finally:
            logger.set_log_level(original_level)

    def test_quiet_and_verbose_conflict(self):
        """Test --quiet and --verbose cannot be used together"""
        parser = create_parser()
        args = parser.parse_args(["--quiet", "--verbose"])

        from src.repomix.shared.error_handle import RepomixError

        with pytest.raises(RepomixError, match="--quiet and --verbose cannot be used together"):
            execute_action(".", ".", args)

    def test_quiet_suppresses_log_output(self, capsys):
        """Test --quiet suppresses info/warn/success messages"""
        original_level = logger.get_log_level()
        try:
            logger.set_log_level(LogLevel.SILENT)
            logger.info("should not appear")
            logger.warn("should not appear")
            logger.success("should not appear")
            logger.debug("should not appear")
            logger.trace("should not appear")
            captured = capsys.readouterr()
            assert "should not appear" not in captured.out
            assert "should not appear" not in captured.err
        finally:
            logger.set_log_level(original_level)

    def test_quiet_in_cli_options_type(self):
        """Test quiet field exists in CliOptions"""
        from src.repomix.cli.types import CliOptions

        opts = CliOptions(quiet=True)
        assert opts.quiet is True

        opts_default = CliOptions()
        assert opts_default.quiet is False
