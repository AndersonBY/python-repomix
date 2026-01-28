"""
Test suite for Git Diff functionality
"""

import json
import tempfile
import pytest
from pathlib import Path

from src.repomix.core.file.git_command import (
    is_git_repository,
    exec_git_diff,
)
from src.repomix.core.file.git_diff_handle import (
    GitDiffResult,
    get_work_tree_diff,
    get_staged_diff,
    get_git_diffs,
)
from src.repomix.core.output.output_generate import generate_output
from src.repomix.config.config_schema import RepomixConfig, RepomixOutputStyle
from src.repomix.core.file.file_types import ProcessedFile


class TestGitCommand:
    """Test cases for git command functions"""

    def test_is_git_repository_with_git_repo(self):
        """Test is_git_repository returns True for git repositories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize a git repository
            import subprocess

            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

            result = is_git_repository(temp_dir)
            assert result is True

    def test_is_git_repository_without_git_repo(self):
        """Test is_git_repository returns False for non-git directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = is_git_repository(temp_dir)
            assert result is False

    def test_exec_git_diff_empty_repo(self):
        """Test exec_git_diff on empty repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

            result = exec_git_diff(temp_dir)
            assert result == ""

    def test_exec_git_diff_with_changes(self):
        """Test exec_git_diff with uncommitted changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

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

            # Create and commit a file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("initial content")
            subprocess.run(["git", "add", "test.txt"], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=temp_dir,
                capture_output=True,
            )

            # Modify the file
            test_file.write_text("modified content")

            result = exec_git_diff(temp_dir)
            assert "modified content" in result or "initial content" in result


class TestGitDiffHandle:
    """Test cases for git diff handle functions"""

    def test_git_diff_result_dataclass(self):
        """Test GitDiffResult dataclass"""
        result = GitDiffResult(
            work_tree_diff_content="work tree diff",
            staged_diff_content="staged diff",
        )
        assert result.work_tree_diff_content == "work tree diff"
        assert result.staged_diff_content == "staged diff"

    def test_get_work_tree_diff_non_git_repo(self):
        """Test get_work_tree_diff returns empty string for non-git directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_work_tree_diff(temp_dir)
            assert result == ""

    def test_get_staged_diff_non_git_repo(self):
        """Test get_staged_diff returns empty string for non-git directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_staged_diff(temp_dir)
            assert result == ""

    def test_get_git_diffs_disabled(self):
        """Test get_git_diffs returns None when disabled"""
        config = RepomixConfig()
        config.output.git.include_diffs = False

        result = get_git_diffs(["."], config)
        assert result is None

    def test_get_git_diffs_enabled(self):
        """Test get_git_diffs returns result when enabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

            config = RepomixConfig()
            config.output.git.include_diffs = True

            result = get_git_diffs([temp_dir], config)
            assert result is not None
            assert isinstance(result, GitDiffResult)


class TestOutputWithGitDiff:
    """Test cases for output generation with git diff"""

    def setup_method(self):
        """Set up test data"""
        self.processed_files = [
            ProcessedFile(
                path="src/main.py",
                content="def main():\n    print('Hello')",
            ),
        ]
        self.file_char_counts = {"src/main.py": 30}
        self.file_token_counts = {"src/main.py": 8}
        self.file_tree = {"src": {"main.py": ""}}

    def test_output_with_git_diff_markdown(self):
        """Test markdown output includes git diff section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.MARKDOWN
        config.output.git.include_diffs = True

        git_diff_result = GitDiffResult(
            work_tree_diff_content="diff --git a/test.txt\n+new line",
            staged_diff_content="diff --git a/staged.txt\n+staged change",
        )

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_diff_result=git_diff_result,
        )

        assert "# Git Diffs" in output
        assert "Git Diffs Working Tree" in output
        assert "Git Diffs Staged" in output
        assert "+new line" in output
        assert "+staged change" in output

    def test_output_with_git_diff_xml(self):
        """Test XML output includes git diff section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.XML
        config.output.git.include_diffs = True

        git_diff_result = GitDiffResult(
            work_tree_diff_content="work tree changes",
            staged_diff_content="staged changes",
        )

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_diff_result=git_diff_result,
        )

        assert "<git_diffs>" in output
        assert "<git_diff_work_tree>" in output
        assert "<git_diff_staged>" in output
        assert "work tree changes" in output
        assert "staged changes" in output

    def test_output_with_git_diff_json(self):
        """Test JSON output includes git diff section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.JSON
        config.output.git.include_diffs = True

        git_diff_result = GitDiffResult(
            work_tree_diff_content="json work tree diff",
            staged_diff_content="json staged diff",
        )

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_diff_result=git_diff_result,
        )

        parsed = json.loads(output)
        assert "gitDiffs" in parsed
        assert parsed["gitDiffs"]["workTree"] == "json work tree diff"
        assert parsed["gitDiffs"]["staged"] == "json staged diff"

    def test_output_without_git_diff(self):
        """Test output without git diff when disabled"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.MARKDOWN
        config.output.git.include_diffs = False

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_diff_result=None,
        )

        assert "# Git Diffs" not in output


if __name__ == "__main__":
    pytest.main([__file__])
