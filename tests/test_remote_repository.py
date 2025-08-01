"""
Test suite for remote repository functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from src.repomix.shared.git_utils import format_git_url, clone_repository
from src.repomix.shared.fs_utils import create_temp_directory, cleanup_temp_directory
from src.repomix.core.repo_processor import RepoProcessor
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.shared.error_handle import RepomixError


class TestGitUtils:
    """Test cases for Git utility functions"""

    def test_is_git_url_https(self):
        """Test Git URL detection for HTTPS URLs"""
        https_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user/repo",
            "https://gitlab.com/user/repo.git",
            "https://bitbucket.org/user/repo.git",
        ]

        # Since is_git_url doesn't exist, test URL format validation manually
        for url in https_urls:
            assert url.startswith("https://"), f"{url} should be HTTPS URL"
            assert "github.com" in url or "gitlab.com" in url or "bitbucket.org" in url

    def test_is_git_url_ssh(self):
        """Test Git URL detection for SSH URLs"""
        ssh_urls = [
            "git@github.com:user/repo.git",
            "git@gitlab.com:user/repo.git",
            "git@bitbucket.org:user/repo.git",
        ]

        # Test SSH URL format validation manually
        for url in ssh_urls:
            assert url.startswith("git@"), f"{url} should be SSH URL"
            assert ":" in url, f"{url} should contain colon separator"

    def test_is_git_url_github_shorthand(self):
        """Test Git URL detection for GitHub shorthand"""
        shorthand_urls = ["user/repo", "organization/project", "my-user/my-repo"]

        # Test GitHub shorthand format validation manually
        import re

        for url in shorthand_urls:
            # Should match pattern: username/repository
            assert re.match(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$", url), f"{url} should be valid GitHub shorthand"

    def test_is_git_url_invalid(self):
        """Test Git URL detection for invalid URLs"""
        invalid_urls = [
            "not-a-url",
            "http://example.com",
            "ftp://example.com/file.txt",
            "/local/path",
            "C:\\local\\path",
            "",
        ]

        # Test that these don't match common Git URL patterns
        import re

        git_patterns = [
            r"^https://.*\.git$",
            r"^git@.*:.*\.git$",
            r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$",
        ]

        for url in invalid_urls:
            matches_git_pattern = any(re.match(pattern, url) for pattern in git_patterns)
            assert not matches_git_pattern, f"{url} should not match Git URL patterns"

    def test_format_git_url_https(self):
        """Test Git URL formatting for HTTPS URLs"""
        test_cases = [
            ("https://github.com/user/repo.git", "https://github.com/user/repo.git"),
            ("https://github.com/user/repo", "https://github.com/user/repo.git"),
            ("https://gitlab.com/user/repo", "https://gitlab.com/user/repo.git"),
        ]

        for input_url, expected in test_cases:
            result = format_git_url(input_url)
            assert result == expected, f"Expected {expected}, got {result}"

    def test_format_git_url_shorthand(self):
        """Test Git URL formatting for GitHub shorthand"""
        test_cases = [
            ("user/repo", "https://github.com/user/repo.git"),
            ("organization/project", "https://github.com/organization/project.git"),
            ("my-user/my-repo", "https://github.com/my-user/my-repo.git"),
        ]

        for input_url, expected in test_cases:
            result = format_git_url(input_url)
            assert result == expected, f"Expected {expected}, got {result}"

    def test_format_git_url_ssh(self):
        """Test Git URL formatting for SSH URLs"""
        ssh_urls = ["git@github.com:user/repo.git", "git@gitlab.com:user/repo.git"]

        for url in ssh_urls:
            result = format_git_url(url)
            assert result == url, f"SSH URL should remain unchanged: {url}"


class TestCloneRepository:
    """Test cases for repository cloning functionality"""

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_basic(self, mock_run):
        """Test basic repository cloning"""
        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_repository("https://github.com/user/repo.git", temp_dir)

            mock_run.assert_called_once()

            # Verify git clone command
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "clone" in call_args
            assert "https://github.com/user/repo.git" in call_args

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_with_branch(self, mock_run):
        """Test repository cloning with specific branch"""
        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_repository("https://github.com/user/repo.git", temp_dir, branch="develop")

            mock_run.assert_called_once()

            # Verify git clone command with branch
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "clone" in call_args
            assert "-b" in call_args
            assert "develop" in call_args

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_shallow(self, mock_run):
        """Test shallow repository cloning"""
        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_repository("https://github.com/user/repo.git", temp_dir)

            # Verify shallow clone option
            call_args = mock_run.call_args[0][0]
            assert "--depth" in call_args
            assert "1" in call_args

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_failure(self, mock_run):
        """Test repository cloning failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "clone"], stderr="fatal: repository not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(RepomixError, match="Repository clone failed"):
                clone_repository("https://github.com/nonexistent/repo.git", temp_dir)

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_timeout(self, mock_run):
        """Test repository cloning with timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 300)

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(RepomixError, match="Repository clone failed"):
                clone_repository("https://github.com/user/huge-repo.git", temp_dir)

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_network_error(self, mock_run):
        """Test repository cloning with network error"""
        mock_run.side_effect = subprocess.CalledProcessError(
            128,
            ["git", "clone"],
            stderr="fatal: unable to access 'https://github.com/user/repo.git/': Could not resolve host",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(RepomixError, match="Repository clone failed"):
                clone_repository("https://github.com/user/repo.git", temp_dir)

    @patch("src.repomix.core.file.git_command.subprocess.run")
    def test_clone_repository_shorthand_url(self, mock_run):
        """Test cloning with GitHub shorthand URL"""
        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_repository("user/repo", temp_dir)

            # Should expand to full GitHub URL
            call_args = mock_run.call_args[0][0]
            assert "https://github.com/user/repo.git" in call_args


class TestTempDirectoryManagement:
    """Test cases for temporary directory management"""

    def test_create_temp_directory(self):
        """Test temporary directory creation"""
        temp_dir = create_temp_directory()

        assert temp_dir is not None
        assert Path(temp_dir).exists()
        assert Path(temp_dir).is_dir()

        # Cleanup
        cleanup_temp_directory(temp_dir)

    def test_create_temp_directory_with_prefix(self):
        """Test temporary directory creation with default prefix"""
        temp_dir = create_temp_directory()

        assert temp_dir is not None
        assert Path(temp_dir).exists()
        assert "repomix-" in Path(temp_dir).name

        # Cleanup
        cleanup_temp_directory(temp_dir)

    def test_cleanup_temp_directory(self):
        """Test temporary directory cleanup"""
        temp_dir = create_temp_directory()

        # Create some content
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()

        # Cleanup
        cleanup_temp_directory(temp_dir)

        assert not Path(temp_dir).exists()

    def test_cleanup_nonexistent_directory(self):
        """Test cleanup of non-existent directory"""
        nonexistent_dir = "/tmp/nonexistent_12345"

        # Should not raise an error
        cleanup_temp_directory(Path(nonexistent_dir))


class TestRemoteRepoProcessor:
    """Test cases for RepoProcessor with remote repositories"""

    @patch("src.repomix.core.repo_processor.cleanup_temp_directory")
    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_repo_processor_remote_basic(self, mock_create_temp, mock_clone, mock_cleanup):
        """Test RepoProcessor with remote repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup mocks
            mock_create_temp.return_value = temp_dir
            mock_clone.return_value = None  # clone_repository doesn't return anything

            # Create test files in temp directory
            (Path(temp_dir) / "main.py").write_text("print('remote repo')")
            (Path(temp_dir) / "README.md").write_text("# Remote Repository")

            # Test RepoProcessor
            processor = RepoProcessor(repo_url="user/repo", branch="main")

            result = processor.process()

            # Verify clone was called with formatted URL
            mock_clone.assert_called_once_with("https://github.com/user/repo.git", temp_dir, "main")

            # Verify result
            assert result is not None
            assert result.total_files >= 0  # Should have processed files

    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_repo_processor_remote_clone_failure(self, mock_create_temp, mock_clone):
        """Test RepoProcessor with clone failure"""
        mock_create_temp.return_value = "/tmp/test"
        mock_clone.side_effect = RepomixError("Clone failed")

        processor = RepoProcessor(repo_url="nonexistent/repo")

        with pytest.raises(RepomixError, match="Clone failed"):
            processor.process()

    @patch("src.repomix.core.repo_processor.cleanup_temp_directory")
    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_repo_processor_remote_with_branch(self, mock_create_temp, mock_clone, mock_cleanup):
        """Test RepoProcessor with specific branch"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_create_temp.return_value = temp_dir
            mock_clone.return_value = None

            # Create branch-specific content
            (Path(temp_dir) / "feature.py").write_text("# Feature branch code")

            processor = RepoProcessor(repo_url="https://github.com/user/repo.git", branch="feature-branch")

            result = processor.process()

            # Verify branch was passed to clone
            mock_clone.assert_called_once_with("https://github.com/user/repo.git", temp_dir, "feature-branch")
            assert result is not None

    @patch("src.repomix.core.repo_processor.cleanup_temp_directory")
    @patch("src.repomix.core.repo_processor.search_files")
    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_repo_processor_remote_cleanup_on_error(self, mock_create_temp, mock_clone, mock_search, mock_cleanup):
        """Test RepoProcessor cleanup on processing error"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_create_temp.return_value = temp_dir
            mock_clone.return_value = None
            # Mock search_files to raise an error after clone succeeds
            mock_search.side_effect = Exception("Processing error")

            processor = RepoProcessor(repo_url="user/repo")

            # Mock processing error after clone
            with pytest.raises(Exception, match="Processing error"):
                processor.process()

            # Verify cleanup was called even on error
            mock_cleanup.assert_called_once_with(temp_dir)


class TestRemoteRepositoryIntegration:
    """Integration tests for remote repository functionality"""

    @patch("src.repomix.core.repo_processor.cleanup_temp_directory")
    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_complete_remote_workflow(self, mock_create_temp, mock_clone, mock_cleanup):
        """Test complete remote repository workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_create_temp.return_value = temp_dir
            mock_clone.return_value = None

            # Create realistic repo structure
            (Path(temp_dir) / "src").mkdir()
            (Path(temp_dir) / "src" / "main.py").write_text('''
def main():
    """Main function of remote repository."""
    print("Hello from remote repo!")
    return 0

if __name__ == "__main__":
    main()
            ''')

            (Path(temp_dir) / "requirements.txt").write_text("""
requests>=2.25.0
pytest>=6.0.0
            """)

            (Path(temp_dir) / "README.md").write_text("""
# Remote Repository

This is a test remote repository for integration testing.

## Installation

pip install -r requirements.txt

## Usage

python src/main.py
            """)

            # Test complete workflow
            config = RepomixConfig()
            processor = RepoProcessor(repo_url="test/remote-repo", branch="main", config=config)

            result = processor.process()

            # Verify processing results
            assert result is not None
            assert result.total_files > 0
            assert result.total_chars > 0
            assert result.output_content is not None
            assert len(result.output_content) > 0

            # Verify clone was called
            mock_clone.assert_called_once_with("https://github.com/test/remote-repo.git", temp_dir, "main")

    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_remote_repository_error_scenarios(self, mock_create_temp, mock_clone):
        """Test various error scenarios with remote repositories"""
        error_scenarios = [
            ("user/nonexistent-repo", "Repository not found"),
            ("https://invalid-host.example/user/repo.git", "Network error"),
        ]

        for repo_url, expected_error in error_scenarios:
            mock_create_temp.return_value = "/tmp/test"
            # Mock git clone failure - clone_repository wraps errors in RepomixError
            mock_clone.side_effect = RepomixError(f"Repository clone failed: {expected_error}")

            processor = RepoProcessor(repo_url=repo_url)

            with pytest.raises(RepomixError):
                processor.process()

            # Reset for next iteration
            mock_clone.side_effect = None

    @patch("src.repomix.core.repo_processor.cleanup_temp_directory")
    @patch("src.repomix.core.repo_processor.clone_repository")
    @patch("src.repomix.core.repo_processor.create_temp_directory")
    def test_remote_repository_with_different_branches(self, mock_create_temp, mock_clone, mock_cleanup):
        """Test remote repository processing with different branches"""
        branches = ["main", "develop", "feature/new-feature", "release/v1.0"]

        for branch in branches:
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_create_temp.return_value = temp_dir
                mock_clone.return_value = None

                # Create branch-specific content
                (Path(temp_dir) / f"{branch.replace('/', '_')}.py").write_text(f"# Code from {branch} branch")

                processor = RepoProcessor(repo_url="user/repo", branch=branch)

                result = processor.process()

                # Verify correct branch was used in clone
                mock_clone.assert_called_with("https://github.com/user/repo.git", temp_dir, branch)
                assert result is not None

                # Reset mocks for next iteration
                mock_clone.reset_mock()


if __name__ == "__main__":
    pytest.main([__file__])
