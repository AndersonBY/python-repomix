"""
Test suite for CLI functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import argparse
import sys

from src.repomix.cli.cli_run import create_parser, execute_action, run_cli
from src.repomix.cli.actions.init_action import run_init_action
from src.repomix.cli.actions.version_action import run_version_action
from src.repomix.cli.actions.remote_action import run_remote_action
from src.repomix.cli.types import CliOptions, CliResult
from src.repomix.__init__ import __version__


class TestCLIParser:
    """Test cases for CLI argument parsing"""

    def test_create_parser_basic(self):
        """Test basic parser creation"""
        parser = create_parser()

        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.description and "Repomix" in parser.description

    def test_parser_default_arguments(self):
        """Test parser with default arguments"""
        parser = create_parser()
        args = parser.parse_args([])

        assert args.directories == ["."]
        assert args.version is False
        assert args.verbose is False
        assert args.init is False
        assert args.mcp is False
        assert args.stdin is False

    def test_parser_directory_argument(self):
        """Test parser with directory argument"""
        parser = create_parser()
        args = parser.parse_args(["/path/to/project"])

        assert args.directories == ["/path/to/project"]

    def test_parser_version_flag(self):
        """Test parser with version flag"""
        parser = create_parser()
        args = parser.parse_args(["--version"])

        assert args.version is True

    def test_parser_verbose_flag(self):
        """Test parser with verbose flag"""
        parser = create_parser()
        args = parser.parse_args(["--verbose"])

        assert args.verbose is True

    def test_parser_output_option(self):
        """Test parser with output option"""
        parser = create_parser()
        args = parser.parse_args(["--output", "custom-output.md"])

        assert args.output == "custom-output.md"

    def test_parser_style_option(self):
        """Test parser with style option"""
        parser = create_parser()
        args = parser.parse_args(["--style", "xml"])

        assert args.style == "xml"

    def test_parser_style_validation(self):
        """Test parser style validation"""
        parser = create_parser()

        # Valid styles should work
        valid_styles = ["plain", "xml", "markdown"]
        for style in valid_styles:
            args = parser.parse_args(["--style", style])
            assert args.style == style

    def test_parser_include_patterns(self):
        """Test parser with include patterns"""
        parser = create_parser()
        args = parser.parse_args(["--include", "*.py,*.js"])

        assert args.include == "*.py,*.js"

    def test_parser_ignore_patterns(self):
        """Test parser with ignore patterns"""
        parser = create_parser()
        args = parser.parse_args(["--ignore", "node_modules,*.tmp"])

        assert args.ignore == "node_modules,*.tmp"

    def test_parser_config_path(self):
        """Test parser with config path"""
        parser = create_parser()
        args = parser.parse_args(["--config", "/path/to/config.json"])

        assert args.config == "/path/to/config.json"

    def test_parser_copy_flag(self):
        """Test parser with copy flag"""
        parser = create_parser()
        args = parser.parse_args(["--copy"])

        assert args.copy is True

    def test_parser_top_files_len(self):
        """Test parser with top files length"""
        parser = create_parser()
        args = parser.parse_args(["--top-files-len", "5"])

        assert args.top_files_len == 5

    def test_parser_line_numbers_flag(self):
        """Test parser with line numbers flag"""
        parser = create_parser()
        args = parser.parse_args(["--output-show-line-numbers"])

        assert args.output_show_line_numbers is True

    def test_parser_init_flag(self):
        """Test parser with init flag"""
        parser = create_parser()
        args = parser.parse_args(["--init"])

        assert args.init is True

    def test_parser_global_flag(self):
        """Test parser with global flag"""
        parser = create_parser()
        args = parser.parse_args(["--init", "--global"])

        assert args.init is True
        assert args.use_global is True

    def test_parser_remote_url(self):
        """Test parser with remote URL"""
        parser = create_parser()
        args = parser.parse_args(["--remote", "user/repo"])

        assert args.remote == "user/repo"

    def test_parser_branch_option(self):
        """Test parser with branch option"""
        parser = create_parser()
        args = parser.parse_args(["--branch", "develop"])

        assert args.branch == "develop"

    def test_parser_no_security_check(self):
        """Test parser with no security check flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-security-check"])

        assert args.no_security_check is True

    def test_parser_mcp_flag(self):
        """Test parser with MCP flag"""
        parser = create_parser()
        args = parser.parse_args(["--mcp"])

        assert args.mcp is True

    def test_parser_stdin_flag(self):
        """Test parser with stdin flag"""
        parser = create_parser()
        args = parser.parse_args(["--stdin"])

        assert args.stdin is True

    def test_parser_parsable_style_flag(self):
        """Test parser with parsable-style flag"""
        parser = create_parser()
        args = parser.parse_args(["--parsable-style"])

        assert args.parsable_style is True

    def test_parser_stdout_flag(self):
        """Test parser with stdout flag"""
        parser = create_parser()
        args = parser.parse_args(["--stdout"])

        assert args.stdout is True

    def test_parser_remove_comments_flag(self):
        """Test parser with remove-comments flag"""
        parser = create_parser()
        args = parser.parse_args(["--remove-comments"])

        assert args.remove_comments is True

    def test_parser_remove_empty_lines_flag(self):
        """Test parser with remove-empty-lines flag"""
        parser = create_parser()
        args = parser.parse_args(["--remove-empty-lines"])

        assert args.remove_empty_lines is True

    def test_parser_truncate_base64_flag(self):
        """Test parser with truncate-base64 flag"""
        parser = create_parser()
        args = parser.parse_args(["--truncate-base64"])

        assert args.truncate_base64 is True

    def test_parser_include_empty_directories_flag(self):
        """Test parser with include-empty-directories flag"""
        parser = create_parser()
        args = parser.parse_args(["--include-empty-directories"])

        assert args.include_empty_directories is True

    def test_parser_include_diffs_flag(self):
        """Test parser with include-diffs flag"""
        parser = create_parser()
        args = parser.parse_args(["--include-diffs"])

        assert args.include_diffs is True

    def test_parser_combined_options(self):
        """Test parser with multiple combined options"""
        parser = create_parser()
        args = parser.parse_args(
            [
                "my-project",
                "--output",
                "output.xml",
                "--style",
                "xml",
                "--verbose",
                "--copy",
                "--include",
                "*.py,*.js",
                "--ignore",
                "*.tmp",
                "--top-files-len",
                "10",
                "--no-security-check",
            ]
        )

        assert args.directories == ["my-project"]
        assert args.output == "output.xml"
        assert args.style == "xml"
        assert args.verbose is True
        assert args.copy is True
        assert args.include == "*.py,*.js"
        assert args.ignore == "*.tmp"
        assert args.top_files_len == 10
        assert args.no_security_check is True

    def test_parser_advanced_output_options_combined(self):
        """Test parser with multiple advanced output options"""
        parser = create_parser()
        args = parser.parse_args(
            [
                "test-project",
                "--parsable-style",
                "--stdout",
                "--remove-comments",
                "--remove-empty-lines",
                "--truncate-base64",
                "--include-empty-directories",
                "--include-diffs",
                "--style",
                "markdown",
            ]
        )

        assert args.directories == ["test-project"]
        assert args.parsable_style is True
        assert args.stdout is True
        assert args.remove_comments is True
        assert args.remove_empty_lines is True
        assert args.truncate_base64 is True
        assert args.include_empty_directories is True
        assert args.include_diffs is True
        assert args.style == "markdown"


class TestCLIActions:
    """Test cases for CLI actions"""

    def test_version_action(self):
        """Test version action"""
        with patch("builtins.print") as mock_print:
            run_version_action()

            # Version should be printed (exact call may vary)
            mock_print.assert_called_once()
            args, _kwargs = mock_print.call_args
            assert args[0] == __version__

    def test_init_action_local(self):
        """Test init action for local config"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("src.repomix.cli.actions.init_action.RepomixConfig") as mock_config:
                with patch("builtins.open", mock_open()) as mock_file:
                    with patch("json.dump") as mock_json_dump:
                        run_init_action(temp_dir, use_global=False)

                        # Should create RepomixConfig instance
                        mock_config.assert_called_once()
                        # Should open config file for writing
                        mock_file.assert_called()
                        # Should write JSON config
                        mock_json_dump.assert_called_once()

    @patch("src.repomix.cli.actions.init_action.get_global_directory")
    def test_init_action_global(self, mock_get_global_dir):
        """Test init action for global config"""
        mock_get_global_dir.return_value = "/global/config"

        with patch("src.repomix.cli.actions.init_action.RepomixConfig") as mock_config:
            with patch("builtins.open", mock_open()):
                with patch("json.dump") as mock_json_dump:
                    with patch("pathlib.Path.mkdir") as mock_mkdir:
                        run_init_action(Path.cwd(), use_global=True)

                        # Should create RepomixConfig instance
                        mock_config.assert_called_once()
                        # Should create global directory
                        mock_mkdir.assert_called()
                        # Should write JSON config
                        mock_json_dump.assert_called_once()

    @patch("src.repomix.cli.actions.remote_action.run_default_action")
    @patch("src.repomix.cli.actions.remote_action.clone_repository")
    @patch("src.repomix.cli.actions.remote_action.is_git_installed")
    @patch("src.repomix.cli.actions.remote_action.create_temp_directory")
    @patch("src.repomix.cli.actions.remote_action.cleanup_temp_directory")
    def test_remote_action(
        self,
        mock_cleanup,
        mock_create_temp,
        mock_git_installed,
        mock_clone,
        mock_run_default,
    ):
        """Test remote action"""
        mock_git_installed.return_value = True
        mock_create_temp.return_value = "/tmp/test"
        mock_result = Mock()
        mock_result.config.output.file_path = "output.md"
        mock_run_default.return_value = mock_result

        options = {"branch": "main", "output": "remote-output.md"}

        with patch("src.repomix.cli.actions.remote_action.copy_output_to_current_directory"):
            run_remote_action("user/repo", options)

            mock_git_installed.assert_called_once()
            mock_create_temp.assert_called_once()
            mock_clone.assert_called_once_with("user/repo", "/tmp/test", "main")
            mock_run_default.assert_called_once()
            mock_cleanup.assert_called_once_with("/tmp/test")

    @patch("src.repomix.cli.cli_run.run_default_action")
    def test_execute_action_default(self, mock_run_default):
        """Test execute_action with default action"""
        mock_run_default.return_value = Mock()

        options = argparse.Namespace(
            version=False,
            init=False,
            mcp=False,
            remote=None,
            verbose=False,
            output=None,
            style="xml",
            include=None,
            ignore=None,
            copy=False,
            top_files_len=None,
            output_show_line_numbers=False,
            config=None,
            no_security_check=False,
            branch=None,
        )

        execute_action(".", Path.cwd(), options)

        mock_run_default.assert_called_once()

    @patch("src.repomix.cli.cli_run.run_version_action")
    def test_execute_action_version(self, mock_version):
        """Test execute_action with version flag"""
        options = argparse.Namespace(version=True, verbose=False)

        execute_action(".", Path.cwd(), options)

        mock_version.assert_called_once()

    @patch("src.repomix.cli.cli_run.run_init_action")
    def test_execute_action_init(self, mock_init):
        """Test execute_action with init flag"""
        options = argparse.Namespace(version=False, init=True, use_global=False, verbose=False)

        execute_action(".", Path.cwd(), options)

        mock_init.assert_called_once_with(Path.cwd(), False)

    @patch("src.repomix.cli.cli_run.run_remote_action")
    def test_execute_action_remote(self, mock_remote):
        """Test execute_action with remote flag"""
        options = argparse.Namespace(version=False, init=False, mcp=False, remote="user/repo", verbose=False)

        execute_action(".", Path.cwd(), options)

        mock_remote.assert_called_once_with("user/repo", vars(options))

    @patch("asyncio.run")
    @patch("src.repomix.mcp.mcp_server.run_mcp_server")
    def test_execute_action_mcp(self, mock_run_mcp, mock_asyncio_run):
        """Test execute_action with MCP flag"""
        options = argparse.Namespace(version=False, init=False, mcp=True, verbose=False)

        execute_action(".", Path.cwd(), options)

        # Should call asyncio.run
        mock_asyncio_run.assert_called_once()


class TestCLITypes:
    """Test cases for CLI types"""

    def test_cli_options_creation(self):
        """Test CliOptions creation"""
        options = CliOptions(
            compress=True,
            include="*.py",
            ignore="*.tmp",
            output="output.md",
            style="markdown",
            security_check=True,
            top_files_len=5,
            quiet=False,
        )

        assert options.compress is True
        assert options.include == "*.py"
        assert options.ignore == "*.tmp"
        assert options.output == "output.md"
        assert options.style == "markdown"
        assert options.security_check is True
        assert options.top_files_len == 5
        assert options.quiet is False

    def test_cli_result_creation(self):
        """Test CliResult creation"""
        mock_pack_result = Mock()

        result = CliResult(pack_result=mock_pack_result)

        assert result.pack_result == mock_pack_result


class TestRunCLIFunction:
    """Test cases for run_cli function"""

    @pytest.mark.asyncio
    @patch("src.repomix.cli.cli_run.run_default_action")
    @patch("src.repomix.cli.cli_run.logger.set_verbose")
    @patch("src.repomix.cli.cli_run.logger.is_verbose")
    async def test_run_cli_basic(self, mock_is_verbose, mock_set_verbose, mock_run_default):
        """Test basic run_cli functionality"""
        mock_is_verbose.return_value = False
        mock_result = Mock()
        mock_result.pack_result = Mock()
        mock_run_default.return_value = mock_result

        cli_options = CliOptions(
            compress=False,
            include=None,
            ignore=None,
            output=None,
            style="xml",
            security_check=True,
            top_files_len=10,
            quiet=True,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file so the directory isn't empty
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('test')")

            result = await run_cli([temp_dir], temp_dir, cli_options)

            assert result is not None
            assert result.pack_result == mock_result.pack_result
            mock_set_verbose.assert_called()
            mock_run_default.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.repomix.cli.cli_run.run_default_action")
    @patch("src.repomix.cli.cli_run.logger.set_verbose")
    @patch("src.repomix.cli.cli_run.logger.is_verbose")
    async def test_run_cli_with_options(self, mock_is_verbose, mock_set_verbose, mock_run_default):
        """Test run_cli with various options"""
        mock_is_verbose.return_value = True
        mock_result = Mock()
        mock_result.pack_result = Mock()
        mock_run_default.return_value = mock_result

        cli_options = CliOptions(
            compress=True,
            include="*.py,*.js",
            ignore="*.tmp,node_modules",
            output="custom-output.xml",
            style="xml",
            security_check=False,
            top_files_len=15,
            quiet=False,
        )

        result = await run_cli(["custom-dir"], "/custom/cwd", cli_options)

        assert result is not None
        mock_run_default.assert_called_once()

        # Verify options were passed correctly
        args, _kwargs = mock_run_default.call_args
        options_dict = args[2]  # Third argument is options dict

        assert options_dict["include"] == "*.py,*.js"
        assert options_dict["ignore"] == "*.tmp,node_modules"
        assert options_dict["output"] == "custom-output.xml"
        assert options_dict["style"] == "xml"
        assert options_dict["no_security_check"] is True

    @pytest.mark.asyncio
    @patch("src.repomix.cli.cli_run.run_default_action")
    @patch("src.repomix.cli.cli_run.logger.set_verbose")
    @patch("src.repomix.cli.cli_run.logger.is_verbose")
    async def test_run_cli_error_handling(self, mock_is_verbose, mock_set_verbose, mock_run_default):
        """Test run_cli error handling"""
        mock_is_verbose.return_value = False
        mock_run_default.side_effect = Exception("Test error")

        cli_options = CliOptions(
            compress=False,
            include=None,
            ignore=None,
            output=None,
            style="xml",
            security_check=True,
            top_files_len=10,
            quiet=True,
        )

        with patch("src.repomix.cli.cli_run.logger.error") as mock_log_error:
            result = await run_cli(["test-dir"], "/test/cwd", cli_options)

            assert result is None
            mock_log_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_cli_empty_directories(self):
        """Test run_cli with empty directories list"""
        cli_options = CliOptions(
            compress=False,
            include=None,
            ignore=None,
            output=None,
            style="xml",
            security_check=True,
            top_files_len=10,
            quiet=True,
        )

        with patch("src.repomix.cli.cli_run.run_default_action") as mock_run_default:
            mock_result = Mock()
            mock_result.pack_result = Mock()
            mock_run_default.return_value = mock_result

            await run_cli([], "/test/cwd", cli_options)

            # Should default to current directory ["."]
            args, _kwargs = mock_run_default.call_args
            assert args[0] == ["."]


class TestStdinFunctionality:
    """Test cases for stdin functionality"""

    @patch("src.repomix.cli.actions.default_action.asyncio.run")
    @patch("src.repomix.cli.actions.default_action.RepoProcessor")
    @patch("src.repomix.cli.cli_run.run_default_action")
    def test_execute_action_with_stdin(self, mock_run_default, mock_repo_processor, mock_asyncio_run):
        """Test execute_action with stdin flag"""
        from src.repomix.core.file.file_stdin import StdinFileResult

        # Setup mock stdin result
        mock_stdin_result = StdinFileResult(file_paths=["/path/to/file1.py", "/path/to/file2.py"], empty_dir_paths=[])
        mock_asyncio_run.return_value = mock_stdin_result

        # Setup mock processor
        mock_processor_instance = Mock()
        mock_processor_instance.process.return_value = Mock(
            total_files=2,
            total_chars=1000,
            total_tokens=200,
            file_char_counts={},
            file_token_counts={},
            config=Mock(output=Mock(file_path="output.md", top_files_length=10)),
            suspicious_files_results=[],
            output_content="test content",
        )
        mock_repo_processor.return_value = mock_processor_instance

        options = argparse.Namespace(version=False, init=False, mcp=False, stdin=True, verbose=False, remote=None)

        # This should call run_default_action with stdin handling
        execute_action(".", Path.cwd(), options)

        mock_run_default.assert_called_once()

    @patch("src.repomix.cli.actions.default_action._handle_stdin_processing")
    def test_default_action_stdin_mode(self, mock_handle_stdin):
        """Test default action routes to stdin handler"""
        from src.repomix.cli.actions.default_action import run_default_action

        mock_handle_stdin.return_value = Mock()

        options = {"stdin": True}
        run_default_action(".", Path.cwd(), options)

        mock_handle_stdin.assert_called_once_with(Path.cwd(), options)

    def test_stdin_with_directory_argument_raises_error(self):
        """Test stdin mode raises error when directory is specified"""
        from src.repomix.cli.actions.default_action import run_default_action
        from src.repomix.shared.error_handle import RepomixError

        options = {"stdin": True}

        with pytest.raises(RepomixError, match="When using --stdin"):
            run_default_action("/some/directory", Path.cwd(), options)


class TestCLIIntegration:
    """Integration tests for CLI functionality"""

    def test_cli_workflow_integration(self):
        """Test complete CLI workflow integration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('CLI integration test')")

            # Test complete workflow
            parser = create_parser()
            args = parser.parse_args(
                [
                    temp_dir,
                    "--output",
                    "integration-test.md",
                    "--style",
                    "markdown",
                    "--verbose",
                ]
            )

            with patch("src.repomix.cli.cli_run.run_default_action") as mock_run_default:
                mock_result = Mock()
                mock_run_default.return_value = mock_result

                with patch("src.repomix.cli.cli_run.logger.set_verbose"):
                    execute_action(args.directories, Path.cwd(), args)

                mock_run_default.assert_called_once()

                # Verify correct arguments passed
                call_args = mock_run_default.call_args[0]
                call_options = mock_run_default.call_args[0][2]

                assert call_args[0] == [temp_dir]
                assert call_options["output"] == "integration-test.md"
                assert call_options["style"] == "markdown"

    def test_cli_error_handling_integration(self):
        """Test CLI error handling integration"""
        with patch(
            "src.repomix.cli.cli_run.execute_action",
            side_effect=Exception("Integration error"),
        ):
            with patch("src.repomix.cli.cli_run.handle_error") as mock_handle_error:
                from src.repomix.cli.cli_run import run

                # Mock sys.argv to avoid actual command line parsing
                with patch.object(sys, "argv", ["repomix", "test-dir"]):
                    run()

                mock_handle_error.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
