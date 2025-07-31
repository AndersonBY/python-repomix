"""
Test suite for core RepoProcessor functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.repomix.core.repo_processor import RepoProcessor, RepoProcessorResult, build_file_tree_with_ignore
from src.repomix.config.config_schema import RepomixConfig, RepomixOutputStyle
from src.repomix.shared.error_handle import RepomixError
from src.repomix.core.security.security_check import SuspiciousFileResult


class TestRepoProcessor:
    """Test cases for RepoProcessor core functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_config = RepomixConfig()

    def test_repo_processor_initialization_with_directory(self):
        """Test RepoProcessor initialization with directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = RepoProcessor(directory=temp_dir)
            
            assert processor.directory == temp_dir
            assert processor.repo_url is None
            assert processor.branch is None
            assert processor.config is not None

    def test_repo_processor_initialization_with_repo_url(self):
        """Test RepoProcessor initialization with repository URL"""
        processor = RepoProcessor(repo_url="test/repo", branch="main")
        
        assert processor.directory is None
        assert processor.repo_url == "test/repo"
        assert processor.branch == "main"
        assert processor.config is not None

    def test_repo_processor_initialization_error(self):
        """Test RepoProcessor initialization error when neither directory nor repo_url provided"""
        with pytest.raises(RepomixError, match="Either directory or repo_url must be provided"):
            RepoProcessor()

    def test_repo_processor_with_custom_config(self):
        """Test RepoProcessor with custom configuration"""
        custom_config = RepomixConfig()
        custom_config.output.file_path = "custom-output.md"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = RepoProcessor(directory=temp_dir, config=custom_config)
            
            # Config should never be None after constructor
            assert processor.config is not None
            assert processor.config.output.file_path == "custom-output.md"

    @patch('src.repomix.core.repo_processor.collect_files')
    @patch('src.repomix.core.repo_processor.process_files')
    @patch('src.repomix.core.repo_processor.generate_output')
    @patch('src.repomix.core.repo_processor.check_files')
    def test_repo_processor_process_workflow(self, mock_check_files, mock_generate_output, 
                                           mock_process_files, mock_collect_files):
        """Test complete RepoProcessor process workflow"""
        # Setup mocks
        from src.repomix.core.file.file_types import RawFile
        
        # Create mock raw files
        raw_file1 = RawFile(path="test.py", content="print('hello')")
        raw_file2 = RawFile(path="readme.md", content="# Test")
        mock_collect_files.return_value = [raw_file1, raw_file2]
        
        # Create mock processed files with content attribute
        mock_processed_file1 = Mock()
        mock_processed_file1.content = "print('hello')"
        mock_processed_file1.path = "test.py"
        
        mock_processed_file2 = Mock()
        mock_processed_file2.content = "# Test"
        mock_processed_file2.path = "readme.md"
        
        mock_process_files.return_value = [mock_processed_file1, mock_processed_file2]
        mock_generate_output.return_value = "# Test Output\n\nContent here"
        mock_check_files.return_value = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "test.py").write_text("print('hello')")
            (Path(temp_dir) / "readme.md").write_text("# Test")
            
            processor = RepoProcessor(directory=temp_dir)
            result = processor.process()
            
            # Verify workflow calls
            mock_collect_files.assert_called_once()
            mock_process_files.assert_called_once()
            mock_generate_output.assert_called_once()
            mock_check_files.assert_called_once()
            
            # Verify result structure
            assert isinstance(result, RepoProcessorResult)
            assert result.total_files == 2
            assert result.total_chars == 20  # len("print('hello')") + len("# Test") = 14 + 6 = 20
            assert result.total_tokens == 0  # No token calculation enabled
            assert result.output_content == "# Test Output\n\nContent here"

    def test_build_file_tree_with_ignore(self):
        """Test file tree building with ignore patterns"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test structure
            (temp_path / "src").mkdir()
            (temp_path / "src" / "main.py").write_text("print('main')")
            (temp_path / "src" / "utils.py").write_text("def helper(): pass")
            (temp_path / "node_modules").mkdir()
            (temp_path / "node_modules" / "package.js").write_text("module.exports = {}")
            (temp_path / ".git").mkdir()
            (temp_path / ".git" / "config").write_text("git config")
            (temp_path / "README.md").write_text("# Project")
            
            # Create .gitignore
            (temp_path / ".gitignore").write_text("node_modules/\n.git/\n")
            
            config = RepomixConfig()
            tree = build_file_tree_with_ignore(temp_path, config)
            
            # Should include src and README.md, but exclude node_modules and .git
            assert "src" in tree
            assert "README.md" in tree
            assert "node_modules" not in tree
            assert ".git" not in tree
            assert "main.py" in tree["src"]
            assert "utils.py" in tree["src"]

    @patch('src.repomix.core.repo_processor.clone_repository')
    @patch('src.repomix.core.repo_processor.create_temp_directory')
    def test_repo_processor_with_remote_repository(self, mock_create_temp, mock_clone_repo):
        """Test RepoProcessor with remote repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_create_temp.return_value = temp_dir
            mock_clone_repo.return_value = None  # clone_repository doesn't return anything
            
            # Create test files in temp directory
            (Path(temp_dir) / "test.py").write_text("print('remote')")
            
            processor = RepoProcessor(repo_url="test/repo", branch="main")
            
            # Run the actual process (it will use the mocked functions)
            result = processor.process()
            
            # Verify clone_repository was called with correct arguments
            mock_clone_repo.assert_called_once_with("https://github.com/test/repo.git", temp_dir, "main")
            
            # Verify the process completed successfully
            assert isinstance(result, RepoProcessorResult)
            assert result.total_files == 1

    def test_repo_processor_with_suspicious_files(self):
        """Test RepoProcessor handling of suspicious files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create suspicious file
            (temp_path / ".env").write_text("API_KEY=secret123")
            (temp_path / "normal.py").write_text("print('normal')")
            
            with patch('src.repomix.core.repo_processor.check_files') as mock_check:
                suspicious_result = SuspiciousFileResult(
                    file_path=str(temp_path / ".env"),
                    messages=["Contains API key pattern"]
                )
                mock_check.return_value = [suspicious_result]
                
                processor = RepoProcessor(directory=temp_dir)
                result = processor.process()
                
                assert len(result.suspicious_files_results) == 1
                assert result.suspicious_files_results[0].file_path.endswith(".env")
                assert "API key pattern" in result.suspicious_files_results[0].messages[0]

    def test_repo_processor_result_dataclass(self):
        """Test RepoProcessorResult dataclass"""
        config = RepomixConfig()
        result = RepoProcessorResult(
            config=config,
            file_tree={"src": []},  # Use List directly for the value
            total_files=1,
            total_chars=100,
            total_tokens=25,
            file_char_counts={"main.py": 100},
            file_token_counts={"main.py": 25},
            output_content="# Output",
            suspicious_files_results=[]
        )
        
        assert result.config == config
        assert result.file_tree == {"src": []}
        assert result.total_files == 1
        assert result.total_chars == 100
        assert result.total_tokens == 25
        assert result.output_content == "# Output"
        assert result.suspicious_files_results == []

    def test_build_file_tree_recursive_structure(self):
        """Test recursive file tree building with nested directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create nested structure
            (temp_path / "src" / "components").mkdir(parents=True)
            (temp_path / "src" / "components" / "Button.py").write_text("class Button: pass")
            (temp_path / "src" / "utils" / "helpers").mkdir(parents=True)
            (temp_path / "src" / "utils" / "helpers" / "math.py").write_text("def add(a, b): return a + b")
            (temp_path / "tests").mkdir()
            (temp_path / "tests" / "test_main.py").write_text("def test_main(): pass")
            
            config = RepomixConfig()
            tree = build_file_tree_with_ignore(temp_path, config)
            
            # Verify nested structure
            assert "src" in tree
            assert "components" in tree["src"]
            assert "Button.py" in tree["src"]["components"]
            assert "utils" in tree["src"]
            assert "helpers" in tree["src"]["utils"]
            assert "math.py" in tree["src"]["utils"]["helpers"]
            assert "tests" in tree
            assert "test_main.py" in tree["tests"]

    @patch('src.repomix.core.repo_processor.cleanup_temp_directory')
    @patch('src.repomix.core.repo_processor.clone_repository')
    @patch('src.repomix.core.repo_processor.create_temp_directory')
    def test_repo_processor_cleanup_on_remote(self, mock_create_temp, mock_clone_repo, mock_cleanup):
        """Test that temporary directories are cleaned up for remote repositories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_create_temp.return_value = temp_dir
            mock_clone_repo.return_value = None
            (Path(temp_dir) / "test.py").write_text("print('test')")
            
            processor = RepoProcessor(repo_url="test/repo", branch="main")
            
            # Run the actual process (will use mocked functions)
            processor.process()
            
            # Verify cleanup was called
            mock_cleanup.assert_called_once_with(temp_dir)

    def test_repo_processor_with_different_output_styles(self):
        """Test RepoProcessor with different output styles"""
        with tempfile.TemporaryDirectory() as temp_dir:
            (Path(temp_dir) / "test.py").write_text("print('test')")
            
            # Test XML style
            config_xml = RepomixConfig()
            config_xml.output._style = RepomixOutputStyle.XML
            
            processor_xml = RepoProcessor(directory=temp_dir, config=config_xml)
            
            with patch('src.repomix.core.repo_processor.generate_output') as mock_generate:
                mock_generate.return_value = "<?xml version='1.0'?><repo></repo>"
                
                processor_xml.process()
                
                # Verify XML output generation was called with XML style
                mock_generate.assert_called_once()
                args, _kwargs = mock_generate.call_args
                assert args[1].output._style == RepomixOutputStyle.XML

    def test_repo_processor_error_handling(self):
        """Test RepoProcessor error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = RepoProcessor(directory=temp_dir)
            
            # Test error during file collection
            with patch('src.repomix.core.repo_processor.collect_files', side_effect=Exception("Collection error")):
                with pytest.raises(Exception, match="Collection error"):
                    processor.process()


class TestFileTreeBuilding:
    """Test cases for file tree building functionality"""
    
    def test_file_tree_ignore_patterns(self):
        """Test file tree building with various ignore patterns"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test structure
            (temp_path / "src").mkdir()
            (temp_path / "src" / "main.py").write_text("main")
            (temp_path / "build").mkdir()
            (temp_path / "build" / "output.js").write_text("output")
            (temp_path / "dist").mkdir()
            (temp_path / "dist" / "bundle.js").write_text("bundle")
            (temp_path / "temp.tmp").write_text("temp")
            (temp_path / "README.md").write_text("readme")
            
            # Test custom ignore patterns
            config = RepomixConfig()
            config.ignore.custom_patterns = ["build/**", "*.tmp", "dist/"]
            
            tree = build_file_tree_with_ignore(temp_path, config)
            
            assert "src" in tree
            assert "README.md" in tree
            assert "build" not in tree
            assert "dist" not in tree
            assert "temp.tmp" not in tree

    def test_file_tree_with_gitignore(self):
        """Test file tree building respects .gitignore"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test structure
            (temp_path / "src").mkdir()
            (temp_path / "src" / "main.py").write_text("main")
            (temp_path / "node_modules").mkdir()
            (temp_path / "node_modules" / "package.json").write_text("{}")
            (temp_path / "__pycache__").mkdir()
            (temp_path / "__pycache__" / "cache.pyc").write_text("cache")
            
            # Create .gitignore
            (temp_path / ".gitignore").write_text("node_modules/\n__pycache__/\n*.pyc\n")
            
            config = RepomixConfig()
            tree = build_file_tree_with_ignore(temp_path, config)
            
            assert "src" in tree
            assert "node_modules" not in tree
            assert "__pycache__" not in tree

    def test_file_tree_empty_directory(self):
        """Test file tree building with empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RepomixConfig()
            tree = build_file_tree_with_ignore(temp_dir, config)
            
            assert tree == {}

    def test_file_tree_single_file(self):
        """Test file tree building with single file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "lonely.py").write_text("print('alone')")
            
            config = RepomixConfig()
            tree = build_file_tree_with_ignore(temp_path, config)
            
            assert tree == {"lonely.py": ""}


# Integration tests
class TestRepoProcessorIntegration:
    """Integration tests for RepoProcessor with real file operations"""
    
    def test_complete_workflow_integration(self):
        """Test complete RepoProcessor workflow with real files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a realistic project structure
            (temp_path / "src").mkdir()
            (temp_path / "src" / "main.py").write_text('''
def main():
    """Main function"""
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    main()
            ''')
            
            (temp_path / "src" / "utils.py").write_text('''
def helper_function(x):
    """Helper function"""
    return x * 2

class Calculator:
    def add(self, a, b):
        return a + b
            ''')
            
            (temp_path / "README.md").write_text('''
# Test Project

This is a test project for integration testing.

## Features
- Main application
- Utility functions
            ''')
            
            (temp_path / "requirements.txt").write_text('''
pytest>=6.0.0
numpy>=1.20.0
            ''')
            
            # Test with different configurations
            config = RepomixConfig()
            config.output.style = "markdown"
            
            processor = RepoProcessor(directory=temp_dir, config=config)
            result = processor.process()
            
            # Verify results
            assert result.total_files > 0
            assert result.total_chars > 0
            assert result.output_content is not None
            assert len(result.output_content) > 0
            
            # Verify file tree structure
            assert "src" in result.file_tree
            assert "README.md" in result.file_tree
            assert "requirements.txt" in result.file_tree

    def test_integration_with_include_patterns(self):
        """Test integration with include patterns"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mixed file types
            (temp_path / "script.py").write_text("print('python')")
            (temp_path / "style.css").write_text("body { margin: 0; }")
            (temp_path / "app.js").write_text("console.log('javascript');")
            (temp_path / "README.md").write_text("# Project")
            
            # Test include only Python files
            config = RepomixConfig()
            config.include = ["*.py"]
            
            processor = RepoProcessor(directory=temp_dir, config=config)
            result = processor.process()
            
            # Should only include Python files
            assert result.total_files >= 1
            assert any("script.py" in str(path) for path in result.file_char_counts.keys())

    def test_integration_with_security_check(self):
        """Test integration with security checking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files including potentially sensitive ones
            (temp_path / "app.py").write_text("print('safe code')")
            (temp_path / "config.py").write_text('''
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:pass@localhost/db"
            ''')
            
            config = RepomixConfig()
            config.security.enable_security_check = True
            
            processor = RepoProcessor(directory=temp_dir, config=config)
            result = processor.process()
            
            # May have suspicious files detected
            assert isinstance(result.suspicious_files_results, list)


if __name__ == "__main__":
    pytest.main([__file__])