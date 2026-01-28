"""
Test suite for Git Log functionality
"""

import json
import tempfile
import subprocess
import pytest
from pathlib import Path

from src.repomix.core.file.git_command import exec_git_log
from src.repomix.core.file.git_log_handle import (
    GitLogCommit,
    GitLogResult,
    parse_git_log,
    get_git_log,
    get_git_logs,
    GIT_LOG_RECORD_SEPARATOR,
)
from src.repomix.core.output.output_generate import generate_output
from src.repomix.config.config_schema import RepomixConfig, RepomixOutputStyle
from src.repomix.core.file.file_types import ProcessedFile


class TestGitLogCommand:
    """Test cases for git log command functions"""

    def test_exec_git_log_empty_repo(self):
        """Test exec_git_log on empty repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)

            result = exec_git_log(temp_dir, max_commits=10)
            assert result == ""

    def test_exec_git_log_with_commits(self):
        """Test exec_git_log with commits"""
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

            # Create and commit a file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("initial content")
            subprocess.run(["git", "add", "test.txt"], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "initial commit"],
                cwd=temp_dir,
                capture_output=True,
            )

            result = exec_git_log(temp_dir, max_commits=10)
            assert "initial commit" in result


class TestGitLogParsing:
    """Test cases for git log parsing functions"""

    def test_parse_git_log_empty(self):
        """Test parse_git_log with empty input"""
        result = parse_git_log("")
        assert result == []

    def test_parse_git_log_single_commit(self):
        """Test parse_git_log with single commit"""
        raw_log = f"{GIT_LOG_RECORD_SEPARATOR}2024-01-15 10:30:00 +0000|Initial commit\nfile1.txt\nfile2.txt"
        result = parse_git_log(raw_log)

        assert len(result) == 1
        assert result[0].date == "2024-01-15 10:30:00 +0000"
        assert result[0].message == "Initial commit"
        assert result[0].files == ["file1.txt", "file2.txt"]

    def test_parse_git_log_multiple_commits(self):
        """Test parse_git_log with multiple commits"""
        raw_log = (
            f"{GIT_LOG_RECORD_SEPARATOR}2024-01-15 10:30:00 +0000|First commit\nfile1.txt"
            f"{GIT_LOG_RECORD_SEPARATOR}2024-01-14 09:00:00 +0000|Second commit\nfile2.txt\nfile3.txt"
        )
        result = parse_git_log(raw_log)

        assert len(result) == 2
        assert result[0].message == "First commit"
        assert result[1].message == "Second commit"
        assert result[1].files == ["file2.txt", "file3.txt"]

    def test_git_log_commit_dataclass(self):
        """Test GitLogCommit dataclass"""
        commit = GitLogCommit(
            date="2024-01-15",
            message="Test commit",
            files=["file1.txt", "file2.txt"],
        )
        assert commit.date == "2024-01-15"
        assert commit.message == "Test commit"
        assert commit.files == ["file1.txt", "file2.txt"]

    def test_git_log_result_dataclass(self):
        """Test GitLogResult dataclass"""
        commits = [GitLogCommit(date="2024-01-15", message="Test", files=[])]
        result = GitLogResult(log_content="raw log", commits=commits)
        assert result.log_content == "raw log"
        assert len(result.commits) == 1


class TestGitLogHandle:
    """Test cases for git log handle functions"""

    def test_get_git_log_non_git_repo(self):
        """Test get_git_log returns empty string for non-git directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_git_log(temp_dir, max_commits=10)
            assert result == ""

    def test_get_git_logs_disabled(self):
        """Test get_git_logs returns None when disabled"""
        config = RepomixConfig()
        config.output.git.include_logs = False

        result = get_git_logs(["."], config)
        assert result is None

    def test_get_git_logs_enabled(self):
        """Test get_git_logs returns result when enabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo with a commit
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

            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("content")
            subprocess.run(["git", "add", "test.txt"], cwd=temp_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "test commit"],
                cwd=temp_dir,
                capture_output=True,
            )

            config = RepomixConfig()
            config.output.git.include_logs = True
            config.output.git.include_logs_count = 10

            result = get_git_logs([temp_dir], config)
            assert result is not None
            assert isinstance(result, GitLogResult)
            assert len(result.commits) >= 1


class TestOutputWithGitLog:
    """Test cases for output generation with git log"""

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
        self.git_log_result = GitLogResult(
            log_content="raw log content",
            commits=[
                GitLogCommit(
                    date="2024-01-15 10:30:00 +0000",
                    message="Initial commit",
                    files=["file1.txt", "file2.txt"],
                ),
                GitLogCommit(
                    date="2024-01-14 09:00:00 +0000",
                    message="Second commit",
                    files=["file3.txt"],
                ),
            ],
        )

    def test_output_with_git_log_markdown(self):
        """Test markdown output includes git log section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.MARKDOWN
        config.output.git.include_logs = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_log_result=self.git_log_result,
        )

        assert "# Git Logs" in output
        assert "Initial commit" in output
        assert "Second commit" in output
        assert "file1.txt" in output

    def test_output_with_git_log_xml(self):
        """Test XML output includes git log section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.XML
        config.output.git.include_logs = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_log_result=self.git_log_result,
        )

        assert "<git_logs>" in output
        assert "<git_log_commit>" in output
        assert "Initial commit" in output

    def test_output_with_git_log_plain(self):
        """Test plain text output includes git log section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.PLAIN
        config.output.git.include_logs = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_log_result=self.git_log_result,
        )

        assert "Git Logs" in output
        assert "Initial commit" in output

    def test_output_with_git_log_json(self):
        """Test JSON output includes git log section"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.JSON
        config.output.git.include_logs = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_log_result=self.git_log_result,
        )

        parsed = json.loads(output)
        assert "gitLogs" in parsed
        assert len(parsed["gitLogs"]) == 2
        assert parsed["gitLogs"][0]["message"] == "Initial commit"
        assert parsed["gitLogs"][0]["files"] == ["file1.txt", "file2.txt"]

    def test_output_without_git_log(self):
        """Test output without git log when disabled"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.MARKDOWN
        config.output.git.include_logs = False

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
            git_log_result=None,
        )

        assert "# Git Logs" not in output


if __name__ == "__main__":
    pytest.main([__file__])
