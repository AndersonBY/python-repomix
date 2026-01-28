"""
Test suite for Output Sort functionality
"""

import tempfile
import subprocess
import pytest
from pathlib import Path

from src.repomix.core.output.output_sort import (
    get_file_change_count,
    sort_output_files,
    clear_caches,
    _check_git_availability,
)
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.file.file_types import ProcessedFile


class TestGetFileChangeCount:
    """Test cases for get_file_change_count function"""

    def test_get_file_change_count_with_commits(self):
        """Test get_file_change_count with commits"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"],
                cwd=temp_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"],
                cwd=temp_dir,
                capture_output=True,
            )

            # Create and commit files multiple times
            test_file1 = Path(temp_dir) / "file1.txt"
            test_file2 = Path(temp_dir) / "file2.txt"

            # First commit - both files
            test_file1.write_text("content1")
            test_file2.write_text("content2")
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "first"],
                cwd=temp_dir,
                capture_output=True,
            )

            # Second commit - only file1
            test_file1.write_text("content1 modified")
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "second"],
                cwd=temp_dir,
                capture_output=True,
            )

            result = get_file_change_count(temp_dir, max_commits=10)

            # file1 should have 2 changes, file2 should have 1
            assert result.get("file1.txt", 0) == 2
            assert result.get("file2.txt", 0) == 1

    def test_get_file_change_count_empty_repo(self):
        """Test get_file_change_count with empty repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

            result = get_file_change_count(temp_dir, max_commits=10)
            assert result == {}

    def test_get_file_change_count_non_git_repo(self):
        """Test get_file_change_count with non-git directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_file_change_count(temp_dir, max_commits=10)
            assert result == {}


class TestCheckGitAvailability:
    """Test cases for git availability check"""

    def setup_method(self):
        """Clear caches before each test"""
        clear_caches()

    def test_check_git_availability_with_git_repo(self):
        """Test git availability check with git repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

            result = _check_git_availability(temp_dir)
            assert result is True

    def test_check_git_availability_without_git_repo(self):
        """Test git availability check without git repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = _check_git_availability(temp_dir)
            assert result is False


class TestSortOutputFiles:
    """Test cases for sort_output_files function"""

    def setup_method(self):
        """Clear caches before each test"""
        clear_caches()

    def test_sort_output_files_disabled(self):
        """Test sort_output_files when sorting is disabled"""
        config = RepomixConfig()
        config.output.git.sort_by_changes = False

        files = [
            ProcessedFile(path="file1.txt", content="content1"),
            ProcessedFile(path="file2.txt", content="content2"),
        ]

        result = sort_output_files(files, config)
        assert result == files  # Should return unchanged

    def test_sort_output_files_enabled(self):
        """Test sort_output_files when sorting is enabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"],
                cwd=temp_dir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"],
                cwd=temp_dir,
                capture_output=True,
            )

            # Create files with different change counts
            test_file1 = Path(temp_dir) / "file1.txt"
            test_file2 = Path(temp_dir) / "file2.txt"
            test_file3 = Path(temp_dir) / "file3.txt"

            # First commit - all files
            test_file1.write_text("content1")
            test_file2.write_text("content2")
            test_file3.write_text("content3")
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "first"],
                cwd=temp_dir,
                capture_output=True,
            )

            # Second commit - file1 and file2
            test_file1.write_text("content1 v2")
            test_file2.write_text("content2 v2")
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "second"],
                cwd=temp_dir,
                capture_output=True,
            )

            # Third commit - only file1
            test_file1.write_text("content1 v3")
            subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "third"],
                cwd=temp_dir,
                capture_output=True,
            )

            config = RepomixConfig()
            config.output.git.sort_by_changes = True
            config.cwd = temp_dir

            files = [
                ProcessedFile(path="file1.txt", content="content1"),  # 3 changes
                ProcessedFile(path="file2.txt", content="content2"),  # 2 changes
                ProcessedFile(path="file3.txt", content="content3"),  # 1 change
            ]

            result = sort_output_files(files, config)

            # Files should be sorted by change count (ascending)
            # file3 (1 change) < file2 (2 changes) < file1 (3 changes)
            assert result[0].path == "file3.txt"
            assert result[1].path == "file2.txt"
            assert result[2].path == "file1.txt"

    def test_sort_output_files_non_git_repo(self):
        """Test sort_output_files with non-git directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RepomixConfig()
            config.output.git.sort_by_changes = True
            config.cwd = temp_dir

            files = [
                ProcessedFile(path="file1.txt", content="content1"),
                ProcessedFile(path="file2.txt", content="content2"),
            ]

            result = sort_output_files(files, config)
            assert result == files  # Should return unchanged


if __name__ == "__main__":
    pytest.main([__file__])
