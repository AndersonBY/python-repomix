"""
Test suite for Token Count Tree functionality
"""

import pytest

from src.repomix.core.tokenCount.token_count_tree import (
    FileTokenInfo,
    FileWithTokens,
    TreeNode,
    build_token_count_tree,
    format_token_count_tree,
    report_token_count_tree,
)
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.file.file_types import ProcessedFile


class TestFileTokenInfo:
    """Test cases for FileTokenInfo dataclass"""

    def test_file_token_info_creation(self):
        """Test FileTokenInfo creation"""
        info = FileTokenInfo(name="test.py", tokens=100)
        assert info.name == "test.py"
        assert info.tokens == 100


class TestFileWithTokens:
    """Test cases for FileWithTokens dataclass"""

    def test_file_with_tokens_creation(self):
        """Test FileWithTokens creation"""
        file = FileWithTokens(path="src/main.py", tokens=500)
        assert file.path == "src/main.py"
        assert file.tokens == 500


class TestTreeNode:
    """Test cases for TreeNode class"""

    def test_tree_node_creation(self):
        """Test TreeNode creation"""
        node = TreeNode()
        assert node.files == []
        assert node.token_sum == 0
        assert node.children == {}


class TestBuildTokenCountTree:
    """Test cases for build_token_count_tree function"""

    def test_build_tree_single_file(self):
        """Test building tree with single file"""
        files = [FileWithTokens(path="main.py", tokens=100)]
        tree = build_token_count_tree(files)

        assert len(tree.files) == 1
        assert tree.files[0].name == "main.py"
        assert tree.files[0].tokens == 100
        assert tree.token_sum == 100

    def test_build_tree_nested_files(self):
        """Test building tree with nested files"""
        files = [
            FileWithTokens(path="src/main.py", tokens=100),
            FileWithTokens(path="src/utils.py", tokens=50),
            FileWithTokens(path="tests/test_main.py", tokens=75),
        ]
        tree = build_token_count_tree(files)

        # Check src directory
        assert "src" in tree.children
        src_node = tree.children["src"]
        assert len(src_node.files) == 2
        assert src_node.token_sum == 150

        # Check tests directory
        assert "tests" in tree.children
        tests_node = tree.children["tests"]
        assert len(tests_node.files) == 1
        assert tests_node.token_sum == 75

        # Check total
        assert tree.token_sum == 225

    def test_build_tree_deeply_nested(self):
        """Test building tree with deeply nested files"""
        files = [
            FileWithTokens(path="src/core/utils/helper.py", tokens=200),
        ]
        tree = build_token_count_tree(files)

        assert "src" in tree.children
        assert "core" in tree.children["src"].children
        assert "utils" in tree.children["src"].children["core"].children
        assert tree.token_sum == 200

    def test_build_tree_empty_list(self):
        """Test building tree with empty list"""
        tree = build_token_count_tree([])
        assert tree.files == []
        assert tree.children == {}
        assert tree.token_sum == 0


class TestFormatTokenCountTree:
    """Test cases for format_token_count_tree function"""

    def test_format_single_file(self):
        """Test formatting tree with single file"""
        files = [FileWithTokens(path="main.py", tokens=100)]
        tree = build_token_count_tree(files)
        output = format_token_count_tree(tree)

        assert "main.py" in output
        assert "100" in output
        assert "tokens" in output

    def test_format_with_directories(self):
        """Test formatting tree with directories"""
        files = [
            FileWithTokens(path="src/main.py", tokens=100),
            FileWithTokens(path="tests/test.py", tokens=50),
        ]
        tree = build_token_count_tree(files)
        output = format_token_count_tree(tree)

        assert "src/" in output
        assert "tests/" in output
        assert "100" in output
        assert "50" in output

    def test_format_with_min_token_count(self):
        """Test formatting with minimum token count filter"""
        files = [
            FileWithTokens(path="big.py", tokens=1000),
            FileWithTokens(path="small.py", tokens=10),
        ]
        tree = build_token_count_tree(files)
        output = format_token_count_tree(tree, min_token_count=100)

        assert "big.py" in output
        assert "small.py" not in output

    def test_format_empty_tree(self):
        """Test formatting empty tree"""
        tree = TreeNode()
        output = format_token_count_tree(tree)

        assert "No files found" in output


class TestReportTokenCountTree:
    """Test cases for report_token_count_tree function"""

    def test_report_basic(self):
        """Test basic report generation"""
        files = [
            ProcessedFile(path="src/main.py", content="print('hello')"),
        ]
        token_counts = {"src/main.py": 100}
        config = RepomixConfig()
        config.output.token_count_tree = True

        output = report_token_count_tree(files, token_counts, config)

        assert "Token Count Tree" in output
        assert "src/" in output
        assert "100" in output

    def test_report_with_threshold(self):
        """Test report with token threshold"""
        files = [
            ProcessedFile(path="big.py", content="x" * 1000),
            ProcessedFile(path="small.py", content="x"),
        ]
        token_counts = {"big.py": 500, "small.py": 10}
        config = RepomixConfig()
        config.output.token_count_tree = 100  # Minimum 100 tokens

        output = report_token_count_tree(files, token_counts, config)

        assert "big.py" in output
        assert "small.py" not in output
        assert "100+" in output


if __name__ == "__main__":
    pytest.main([__file__])
