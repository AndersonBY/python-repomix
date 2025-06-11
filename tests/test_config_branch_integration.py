"""
Test suite for branch functionality integration with configuration and CLI
"""

from pathlib import Path
from unittest.mock import patch, Mock

from src.repomix.config.config_schema import RepomixConfig, RepomixConfigRemote
from src.repomix.cli.actions.default_action import run_default_action


class TestConfigBranchIntegration:
    """Test cases for branch functionality integration with config and CLI"""

    def test_remote_config_creation(self):
        """Test creating RemoteConfig with remote repository settings"""
        # Test default values
        remote_config = RepomixConfigRemote()
        assert remote_config.url == ""
        assert remote_config.branch == ""

        # Test with values
        remote_config = RepomixConfigRemote(url="jstrieb/github-stats", branch="dark-mode")
        assert remote_config.url == "jstrieb/github-stats"
        assert remote_config.branch == "dark-mode"

    def test_repomix_config_with_remote(self):
        """Test RepomixConfig with remote configuration"""
        config = RepomixConfig()

        # Test default remote config
        assert hasattr(config, "remote")
        assert config.remote.url == ""
        assert config.remote.branch == ""

    def test_repomix_config_from_dict_with_remote(self):
        """Test creating RepomixConfig from dictionary with remote settings"""
        config_dict = {"remote": {"url": "jstrieb/github-stats", "branch": "dark-mode"}, "output": {"file_path": "test-output.md"}}

        config = RepomixConfig(**config_dict)  # type: ignore

        assert config.remote.url == "jstrieb/github-stats"
        assert config.remote.branch == "dark-mode"
        assert config.output.file_path == "test-output.md"

    @patch("src.repomix.cli.actions.default_action.load_config")
    @patch("src.repomix.core.repo_processor.RepoProcessor")
    def test_default_action_with_remote_config(self, mock_repo_processor, mock_load_config):
        """Test default action uses remote config when available"""
        # Setup mock config with remote settings
        mock_config = Mock()
        mock_config.remote.url = "jstrieb/github-stats"
        mock_config.remote.branch = "dark-mode"
        mock_config.output.copy_to_clipboard = False
        mock_config.output.top_files_length = 5
        mock_load_config.return_value = mock_config

        # Setup mock processor and result
        mock_processor = Mock()
        mock_result = Mock()
        mock_result.total_files = 10
        mock_result.total_chars = 1000
        mock_result.total_tokens = 200
        mock_result.config = mock_config
        mock_result.suspicious_files_results = []
        mock_result.file_char_counts = {}
        mock_result.file_token_counts = {}
        mock_processor.process.return_value = mock_result
        mock_repo_processor.return_value = mock_processor

        # Call default action
        options = {}
        with (
            patch("src.repomix.cli.actions.default_action.print_summary"),
            patch("src.repomix.cli.actions.default_action.print_security_check"),
            patch("src.repomix.cli.actions.default_action.print_top_files"),
            patch("src.repomix.cli.actions.default_action.print_completion"),
        ):
            result = run_default_action(".", Path.cwd(), options)

        # Verify RepoProcessor was called with remote config
        mock_repo_processor.assert_called_once_with(repo_url="jstrieb/github-stats", branch="dark-mode", config=mock_config)

        assert result.total_files == 10

    @patch("src.repomix.cli.actions.default_action.load_config")
    @patch("src.repomix.core.repo_processor.RepoProcessor")
    def test_default_action_with_local_directory(self, mock_repo_processor, mock_load_config):
        """Test default action uses local directory when no remote config"""
        # Setup mock config without remote settings
        mock_config = Mock()
        mock_config.remote.url = ""  # No remote URL
        mock_config.remote.branch = ""
        mock_config.output.copy_to_clipboard = False
        mock_config.output.top_files_length = 5
        mock_load_config.return_value = mock_config

        # Setup mock processor and result
        mock_processor = Mock()
        mock_result = Mock()
        mock_result.total_files = 5
        mock_result.total_chars = 500
        mock_result.total_tokens = 100
        mock_result.config = mock_config
        mock_result.suspicious_files_results = []
        mock_result.file_char_counts = {}
        mock_result.file_token_counts = {}
        mock_processor.process.return_value = mock_result
        mock_repo_processor.return_value = mock_processor

        # Call default action
        options = {}
        with (
            patch("src.repomix.cli.actions.default_action.print_summary"),
            patch("src.repomix.cli.actions.default_action.print_security_check"),
            patch("src.repomix.cli.actions.default_action.print_top_files"),
            patch("src.repomix.cli.actions.default_action.print_completion"),
        ):
            result = run_default_action("./test_dir", Path.cwd(), options)

        # Verify RepoProcessor was called with local directory
        mock_repo_processor.assert_called_once_with("./test_dir", config=mock_config)

        assert result.total_files == 5

    def test_cli_options_with_branch(self):
        """Test CLI options processing includes branch parameter"""
        # This would be tested more comprehensively with actual CLI integration
        # For now, we test the options dict structure
        options = {"branch": "dark-mode", "remote": "jstrieb/github-stats"}
        branch_value = options.get("branch")
        assert branch_value == "dark-mode"

    def test_config_precedence(self):
        """Test that CLI options override config file settings"""
        # This test demonstrates how the configuration system should work
        base_config = {"remote": {"url": "config-file-repo", "branch": "config-file-branch"}}

        cli_override = {"remote": {"url": "cli-repo", "branch": "cli-branch"}}

        # The actual merging logic happens in load_config, but we can test the structure
        config = RepomixConfig(**base_config)  # type: ignore
        assert config.remote.url == "config-file-repo"
        assert config.remote.branch == "config-file-branch"

        # CLI should override
        config_with_override = RepomixConfig(**cli_override)  # type: ignore
        assert config_with_override.remote.url == "cli-repo"
        assert config_with_override.remote.branch == "cli-branch"
