"""
Tests for stdin file reading functionality.
"""

import sys
from io import StringIO

import pytest

from pathlib import Path

from repomix.core.file.file_stdin import (
    StdinFileResult,
    filter_valid_lines,
    read_file_paths_from_stdin,
    resolve_and_deduplicate_paths,
    should_ignore_path,
)


class TestFilterValidLines:
    """Test filter_valid_lines function."""

    def test_filters_empty_lines(self):
        """Should filter out empty lines."""
        lines = ["file1.py", "", "file2.py", "   ", "file3.py"]
        result = filter_valid_lines(lines)
        assert result == ["file1.py", "file2.py", "file3.py"]

    def test_filters_comment_lines(self):
        """Should filter out lines starting with #."""
        lines = [
            "file1.py",
            "# this is a comment",
            "file2.py",
            "#another comment",
            "file3.py",
        ]
        result = filter_valid_lines(lines)
        assert result == ["file1.py", "file2.py", "file3.py"]

    def test_strips_whitespace(self):
        """Should strip whitespace from lines."""
        lines = ["  file1.py  ", "\tfile2.py\t", " file3.py "]
        result = filter_valid_lines(lines)
        assert result == ["file1.py", "file2.py", "file3.py"]

    def test_handles_mixed_input(self):
        """Should handle mixed input correctly."""
        lines = [
            "  file1.py  ",
            "",
            "# comment",
            "file2.py",
            "   ",
            "  # another comment  ",
            "file3.py",
        ]
        result = filter_valid_lines(lines)
        assert result == ["file1.py", "file2.py", "file3.py"]


class TestResolveAndDeduplicatePaths:
    """Test resolve_and_deduplicate_paths function."""

    def test_resolves_relative_paths(self, tmp_path):
        """Should resolve relative paths to absolute paths."""
        cwd = tmp_path
        lines = ["file1.py", "subdir/file2.py", "./file3.py"]
        result = resolve_and_deduplicate_paths(lines, cwd)

        expected = [
            str(cwd / "file1.py"),
            str(cwd / "subdir/file2.py"),
            str(cwd / "file3.py"),
        ]
        assert result == expected

    def test_preserves_absolute_paths(self, tmp_path):
        """Should preserve absolute paths."""
        cwd = tmp_path
        abs_path = str(tmp_path / "absolute/path/file.py")
        lines = ["relative.py", abs_path]
        result = resolve_and_deduplicate_paths(lines, cwd)

        expected = [str(cwd / "relative.py"), abs_path]
        assert result == expected

    def test_deduplicates_paths(self, tmp_path):
        """Should remove duplicate paths."""
        cwd = tmp_path
        lines = ["file1.py", "file2.py", "file1.py", "./file1.py", "file2.py"]
        result = resolve_and_deduplicate_paths(lines, cwd)

        expected = [str(cwd / "file1.py"), str(cwd / "file2.py")]
        assert result == expected

    def test_handles_parent_directory_references(self, tmp_path):
        """Should handle parent directory references correctly."""
        cwd = tmp_path / "subdir"
        cwd.mkdir(exist_ok=True)
        lines = ["../file1.py", "file2.py", "../file1.py"]
        result = resolve_and_deduplicate_paths(lines, cwd)

        expected = [str(tmp_path / "file1.py"), str(cwd / "file2.py")]
        assert result == expected


class TestIgnorePatterns:
    """Test ignore pattern functionality."""

    def test_should_ignore_venv_paths(self):
        """Should ignore paths containing .venv directory."""
        assert should_ignore_path(Path("/home/user/.venv/lib/python3.11/site-packages/module.py"))
        assert should_ignore_path(Path("/project/venv/bin/python"))
        assert should_ignore_path(Path("env/lib/site-packages/test.py"))
        assert not should_ignore_path(Path("/home/user/myproject/main.py"))

    def test_should_ignore_node_modules(self):
        """Should ignore paths containing node_modules."""
        assert should_ignore_path(Path("/project/node_modules/package/index.js"))
        assert should_ignore_path(Path("node_modules/lodash/lodash.js"))
        assert not should_ignore_path(Path("/project/src/index.js"))

    def test_should_ignore_pycache(self):
        """Should ignore __pycache__ directories and .pyc files."""
        assert should_ignore_path(Path("/project/__pycache__/module.cpython-311.pyc"))
        assert should_ignore_path(Path("/project/src/__pycache__/test.pyc"))
        assert should_ignore_path(Path("/project/test.pyc"))
        assert not should_ignore_path(Path("/project/test.py"))

    def test_should_ignore_build_directories(self):
        """Should ignore build and dist directories."""
        assert should_ignore_path(Path("/project/build/lib/module.py"))
        assert should_ignore_path(Path("/project/dist/package.whl"))
        assert should_ignore_path(Path("target/classes/Main.class"))
        assert not should_ignore_path(Path("/project/src/build.py"))

    def test_filters_ignored_paths_from_stdin(self, tmp_path):
        """Should filter out ignored paths when resolving."""
        cwd = tmp_path
        lines = [
            "main.py",
            ".venv/lib/python3.11/site-packages/module.py",
            "src/app.py",
            "node_modules/package/index.js",
            "__pycache__/test.pyc",
            "build/output.py",
            "dist/package.whl",
        ]
        result = resolve_and_deduplicate_paths(lines, cwd)

        # Should only include main.py and src/app.py
        assert len(result) == 2
        assert str(cwd / "main.py") in result
        assert str(cwd / "src/app.py") in result
        # Ignored paths should not be in result
        assert not any(".venv" in path for path in result)
        assert not any("node_modules" in path for path in result)
        assert not any("__pycache__" in path for path in result)
        assert not any("build" in path for path in result)
        assert not any("dist" in path for path in result)


class TestReadFilePathsFromStdin:
    """Test read_file_paths_from_stdin function."""

    @pytest.mark.asyncio
    async def test_reads_file_paths_successfully(self, tmp_path, monkeypatch):
        """Should read file paths from stdin successfully."""
        # Mock stdin with file paths
        stdin_content = "file1.py\nfile2.py\nsubdir/file3.py\n"
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        result = await read_file_paths_from_stdin(tmp_path)

        assert isinstance(result, StdinFileResult)
        assert len(result.file_paths) == 3
        assert str(tmp_path / "file1.py") in result.file_paths
        assert str(tmp_path / "file2.py") in result.file_paths
        assert str(tmp_path / "subdir/file3.py") in result.file_paths
        assert result.empty_dir_paths == []

    @pytest.mark.asyncio
    async def test_filters_comments_and_empty_lines(self, tmp_path, monkeypatch):
        """Should filter out comments and empty lines."""
        stdin_content = """file1.py
# This is a comment
file2.py

# Another comment
file3.py

"""
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        result = await read_file_paths_from_stdin(tmp_path)

        assert len(result.file_paths) == 3
        assert all("file" in path for path in result.file_paths)

    @pytest.mark.asyncio
    async def test_deduplicates_paths(self, tmp_path, monkeypatch):
        """Should deduplicate file paths."""
        stdin_content = """file1.py
file2.py
file1.py
./file1.py
file2.py"""
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        result = await read_file_paths_from_stdin(tmp_path)

        assert len(result.file_paths) == 2
        assert str(tmp_path / "file1.py") in result.file_paths
        assert str(tmp_path / "file2.py") in result.file_paths

    @pytest.mark.asyncio
    async def test_handles_absolute_paths(self, tmp_path, monkeypatch):
        """Should handle absolute paths correctly."""
        abs_path = str(tmp_path / "absolute/file.py")
        stdin_content = f"relative.py\n{abs_path}\n"
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        result = await read_file_paths_from_stdin(tmp_path)

        assert len(result.file_paths) == 2
        assert str(tmp_path / "relative.py") in result.file_paths
        assert abs_path in result.file_paths

    @pytest.mark.asyncio
    async def test_raises_error_for_tty(self, tmp_path, monkeypatch):
        """Should raise error when stdin is a TTY."""
        # Mock stdin as a TTY
        mock_stdin = StringIO()
        mock_stdin.isatty = lambda: True
        monkeypatch.setattr(sys, "stdin", mock_stdin)

        with pytest.raises(ValueError, match="No data provided via stdin"):
            await read_file_paths_from_stdin(tmp_path)

    @pytest.mark.asyncio
    async def test_raises_error_for_empty_input(self, tmp_path, monkeypatch):
        """Should raise error when no valid paths are found."""
        stdin_content = "# Only comments\n\n# More comments\n   \n"
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        with pytest.raises(ValueError, match="No valid file paths found"):
            await read_file_paths_from_stdin(tmp_path)

    @pytest.mark.asyncio
    async def test_handles_paths_with_spaces(self, tmp_path, monkeypatch):
        """Should handle file paths with spaces correctly."""
        stdin_content = '"file with spaces.py"\nregular_file.py\n"another file with spaces.py"'
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        result = await read_file_paths_from_stdin(tmp_path)

        assert len(result.file_paths) == 3
        # Note: The current implementation doesn't handle quoted paths specially
        # This test documents the current behavior

    @pytest.mark.asyncio
    async def test_filters_ignored_paths(self, tmp_path, monkeypatch):
        """Should filter out ignored paths from stdin."""
        stdin_content = """main.py
.venv/lib/python3.11/site-packages/module.py
src/app.py
node_modules/package/index.js
__pycache__/test.pyc
tests/test_app.py
build/output.py
.git/config
"""
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_content))

        result = await read_file_paths_from_stdin(tmp_path)

        # Should only include main.py, src/app.py, and tests/test_app.py
        paths = [Path(path) for path in result.file_paths]
        assert len(paths) == 3
        assert tmp_path / "main.py" in paths
        assert tmp_path / "src" / "app.py" in paths
        assert tmp_path / "tests" / "test_app.py" in paths
        # Ignored paths should not be present
        assert not any(".venv" in path.parts for path in paths)
        assert not any("node_modules" in path.parts for path in paths)
        assert not any("__pycache__" in path.parts for path in paths)
        assert not any("build" in path.parts for path in paths)
        assert not any(".git" in path.parts for path in paths)
