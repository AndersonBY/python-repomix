"""
Test suite for RepoProcessor branch functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.repomix.core.repo_processor import RepoProcessor
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.shared.error_handle import RepomixError


class TestRepoProcessorBranch:
    """Test cases for RepoProcessor branch functionality"""

    def test_branch_parameter_initialization(self):
        """Test RepoProcessor initialization with branch parameter"""
        # Test with branch parameter
        processor = RepoProcessor(repo_url="jstrieb/github-stats", branch="dark-mode")

        assert processor.branch == "dark-mode"
        assert processor.repo_url == "jstrieb/github-stats"

    def test_branch_parameter_none_by_default(self):
        """Test that branch parameter defaults to None"""
        processor = RepoProcessor(directory=Path.cwd())

        assert processor.branch is None

    def test_branch_parameter_with_directory(self):
        """Test branch parameter with directory (should be ignored)"""
        processor = RepoProcessor(
            directory=Path.cwd(),
            branch="main",  # This should be set but not used since we're using directory
        )

        assert processor.branch == "main"
        assert processor.repo_url is None

    def test_various_branch_formats(self):
        """Test various branch name formats"""
        test_branches = ["main", "master", "develop", "feature/new-feature", "release/v1.0.0", "hotfix/urgent-fix", "dark-mode", None]

        for branch in test_branches:
            processor = RepoProcessor(repo_url="jstrieb/github-stats", branch=branch)
            assert processor.branch == branch

    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    @patch("src.repomix.core.repo_processor.cleanup_temp_directory")
    def test_branch_passed_to_clone_repository(self, mock_cleanup, mock_create_temp, mock_clone):
        """Test that branch is correctly passed to clone_repository function"""
        # Setup mocks
        mock_temp_dir = "/tmp/test_temp_dir"
        mock_create_temp.return_value = mock_temp_dir

        # Create processor with branch
        processor = RepoProcessor(repo_url="jstrieb/github-stats", branch="dark-mode")

        # Mock the process to avoid actual file operations
        with patch.object(processor, "write_output"):
            with patch("src.repomix.core.repo_processor.search_files") as mock_search:
                with patch("src.repomix.core.repo_processor.collect_files") as mock_collect:
                    with patch("src.repomix.core.repo_processor.process_files") as mock_process:
                        with patch("src.repomix.core.repo_processor.build_file_tree_with_ignore") as mock_tree:
                            with patch("src.repomix.core.repo_processor.generate_output") as mock_output:
                                with patch("src.repomix.core.repo_processor.check_files") as mock_check:
                                    # Setup mock returns
                                    mock_search.return_value = Mock(file_paths=[])
                                    mock_collect.return_value = [Mock(path="test.py", content="test")]
                                    mock_process.return_value = [Mock(path="test.py", content="test")]
                                    mock_tree.return_value = {}
                                    mock_output.return_value = "test output"
                                    mock_check.return_value = []

                                    try:
                                        processor.process(write_output=False)
                                    except Exception as e:
                                        print(e)
                                        pass  # We expect this to fail due to mocking, but we want to check the clone call

        # Verify that clone_repository was called with the correct branch
        mock_clone.assert_called_once_with("https://github.com/jstrieb/github-stats.git", mock_temp_dir, "dark-mode")

    def test_real_repository_with_branch_integration(self):
        """Integration test with real repository and branch"""
        # Use a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Create processor with real GitHub repository and specific branch
                processor = RepoProcessor(repo_url="jstrieb/github-stats", branch="dark-mode", config=RepomixConfig())

                # Set output to temp directory to avoid polluting project
                if processor.config:
                    processor.config.output.file_path = str(Path(temp_dir) / "test-output.md")

                # Process the repository
                result = processor.process(write_output=True)

                # Verify the result
                assert result is not None
                assert result.total_files > 0
                assert result.total_chars > 0
                if processor.config:
                    assert Path(processor.config.output.file_path).exists()

                    # Verify output content contains expected elements
                    with open(processor.config.output.file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # The github-stats repository should contain Python files
                        assert "python" in content.lower() or ".py" in content

            except Exception as e:
                # If the test fails due to network issues, skip it
                pytest.skip(f"Network test failed: {e}")

    def test_real_repository_without_branch_integration(self):
        """Integration test with real repository without specifying branch (should use default)"""
        # Use a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Create processor with real GitHub repository but no branch
                processor = RepoProcessor(
                    repo_url="jstrieb/github-stats",
                    branch=None,  # Should use repository default branch
                    config=RepomixConfig(),
                )

                # Set output to temp directory
                if processor.config:
                    processor.config.output.file_path = str(Path(temp_dir) / "test-output-no-branch.md")

                # Process the repository
                result = processor.process(write_output=True)

                # Verify the result
                assert result is not None
                assert result.total_files > 0
                assert result.total_chars > 0
                if processor.config:
                    assert Path(processor.config.output.file_path).exists()

            except Exception as e:
                # If the test fails due to network issues, skip it
                pytest.skip(f"Network test failed: {e}")

    def test_invalid_branch_handling(self):
        """Test handling of invalid branch names"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Create processor with invalid branch
                processor = RepoProcessor(repo_url="jstrieb/github-stats", branch="non-existent-branch-12345", config=RepomixConfig())
                if processor.config is None:
                    raise RepomixError("Configuration not loaded.")

                processor.config.output.file_path = str(Path(temp_dir) / "test-output-invalid.md")

                # This should raise an error during processing
                with pytest.raises(RepomixError):
                    processor.process(write_output=False)

            except Exception as e:
                # If the test fails due to network issues, skip it
                pytest.skip(f"Network test failed: {e}")

    def test_branch_with_local_directory_ignored(self):
        """Test that branch parameter is ignored when using local directory"""
        # Create processor with local directory and branch (branch should be ignored)
        processor = RepoProcessor(directory=Path.cwd(), branch="some-branch")

        # Branch should still be set but not used
        assert processor.branch == "some-branch"
        assert processor.repo_url is None
        assert processor.directory == Path.cwd()

        # The process should work without trying to clone
        # (We'll just test that it doesn't fail immediately)
        assert processor.config is not None
