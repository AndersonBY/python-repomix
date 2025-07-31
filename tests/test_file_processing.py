"""
Test suite for file processing functionality
"""

import tempfile
import pytest
from pathlib import Path
import os

from src.repomix.core.file.file_search import search_files, get_ignore_patterns
from src.repomix.core.file.file_collect import collect_files  
from src.repomix.core.file.file_process import process_files, process_content
from src.repomix.core.file.file_types import RawFile
from src.repomix.core.file.permission_check import check_file_permission
from src.repomix.config.config_schema import RepomixConfig


class TestFileCollection:
    """Test cases for file collection functionality"""
    
    def test_collect_files_basic(self):
        """Test basic file collection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "main.py").write_text("print('main')")
            (temp_path / "utils.py").write_text("def helper(): pass")
            (temp_path / "README.md").write_text("# Project")
            
            config = RepomixConfig()
            result = search_files(temp_dir, config)
            
            assert len(result.file_paths) >= 3
            file_names = [Path(f).name for f in result.file_paths]
            assert "main.py" in file_names
            assert "utils.py" in file_names
            assert "README.md" in file_names

    def test_collect_files_with_subdirectories(self):
        """Test file collection with subdirectories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create nested structure
            (temp_path / "src").mkdir()
            (temp_path / "src" / "app.py").write_text("app code")
            (temp_path / "tests").mkdir()
            (temp_path / "tests" / "test_app.py").write_text("test code")
            (temp_path / "docs").mkdir()
            (temp_path / "docs" / "guide.md").write_text("documentation")
            
            config = RepomixConfig()
            result = search_files(temp_dir, config)
            
            assert len(result.file_paths) >= 3
            file_paths = result.file_paths
            assert any("src/app.py" in path or "src\\app.py" in path for path in file_paths)
            assert any("tests/test_app.py" in path or "tests\\test_app.py" in path for path in file_paths)
            assert any("docs/guide.md" in path or "docs\\guide.md" in path for path in file_paths)

    def test_collect_files_with_ignore_patterns(self):
        """Test file collection with ignore patterns"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files including ones to ignore
            (temp_path / "main.py").write_text("main")
            (temp_path / "temp.tmp").write_text("temporary")
            (temp_path / "build").mkdir()
            (temp_path / "build" / "output.js").write_text("build output")
            (temp_path / ".gitignore").write_text("*.tmp\nbuild/\n")
            
            config = RepomixConfig()
            result = search_files(temp_dir, config)
            
            file_names = [Path(f).name for f in result.file_paths]
            assert "main.py" in file_names
            assert "temp.tmp" not in file_names
            assert "output.js" not in file_names

    def test_collect_files_with_include_patterns(self):
        """Test file collection with include patterns"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mixed file types
            (temp_path / "script.py").write_text("python code")
            (temp_path / "style.css").write_text("css code")
            (temp_path / "app.js").write_text("javascript code")
            (temp_path / "README.md").write_text("documentation")
            
            config = RepomixConfig()
            config.include = ["*.py", "*.js"]
            
            result = search_files(temp_dir, config)
            
            file_names = [Path(f).name for f in result.file_paths]
            assert "script.py" in file_names
            assert "app.js" in file_names
            assert "style.css" not in file_names
            assert "README.md" not in file_names

    def test_collect_files_empty_directory(self):
        """Test file collection in empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RepomixConfig()
            result = search_files(temp_dir, config)
            
            assert len(result.file_paths) == 0


class TestFileSearch:
    """Test cases for file search functionality"""
    
    def test_search_files_basic(self):
        """Test basic file search"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "file1.py").write_text("content1")
            (temp_path / "file2.js").write_text("content2")
            (temp_path / "file3.md").write_text("content3")
            
            config = RepomixConfig()
            result = search_files(temp_dir, config)
            
            assert len(result.file_paths) >= 3
            file_names = [Path(f).name for f in result.file_paths]
            assert "file1.py" in file_names
            assert "file2.js" in file_names
            assert "file3.md" in file_names

    def test_search_files_with_patterns(self):
        """Test file search with patterns"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "main.py").write_text("python")
            (temp_path / "test.py").write_text("python test")
            (temp_path / "style.css").write_text("css")
            (temp_path / "script.js").write_text("javascript")
            
            # Search for Python files only
            config = RepomixConfig()
            config.include = ["*.py"]
            result = search_files(temp_dir, config)
            
            assert len(result.file_paths) == 2
            file_names = [Path(f).name for f in result.file_paths]
            assert "main.py" in file_names
            assert "test.py" in file_names
            assert "style.css" not in file_names

    def test_get_ignore_patterns(self):
        """Test getting ignore patterns from gitignore and config"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create .gitignore
            (temp_path / ".gitignore").write_text("node_modules/\n*.log\n__pycache__/\n")
            
            config = RepomixConfig()
            config.ignore.custom_patterns = ["*.tmp", "build/"]
            
            patterns = get_ignore_patterns(temp_dir, config)
            
            assert "node_modules/" in patterns
            assert "*.log" in patterns
            assert "__pycache__/" in patterns
            assert "*.tmp" in patterns
            assert "build/" in patterns

    def test_get_ignore_patterns_no_gitignore(self):
        """Test getting ignore patterns when no .gitignore exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RepomixConfig()
            config.ignore.custom_patterns = ["*.tmp"]
            
            patterns = get_ignore_patterns(temp_dir, config)
            
            # Should include custom patterns and default patterns
            assert "*.tmp" in patterns
            assert len(patterns) > 1  # Should have default patterns too


class TestFileProcessing:
    """Test cases for file processing functionality"""
    
    def test_process_files_basic(self):
        """Test basic file processing"""
        # Create test RawFile objects
        raw_files = [
            RawFile(path="small.py", content="print('small')"),
            RawFile(path="large.py", content="print('large file with more content')"),
            RawFile(path="README.md", content="# Documentation\n\nThis is documentation.")
        ]
        
        config = RepomixConfig()
        processed_files = process_files(raw_files, config)
        
        assert len(processed_files) == 3
        
        # Verify that files were processed
        file_paths = [f.path for f in processed_files]
        assert "small.py" in file_paths
        assert "large.py" in file_paths
        assert "README.md" in file_paths
        
        # Verify content is preserved (since no compression by default)
        for processed_file in processed_files:
            assert len(processed_file.content) > 0

    def test_process_content_basic(self):
        """Test basic content processing"""
        content = "def hello():\n    print('Hello, World!')\n    return True"
        file_path = "test.py"
        config = RepomixConfig()
        
        result = process_content(content, file_path, config)
        
        assert result == content  # Should return unchanged for basic processing

    def test_process_content_with_compression(self):
        """Test content processing with compression"""
        content = "def calculate_sum(a, b):\n    return a + b"
        
        file_path = "calculator.py"  # .py extension should return PythonManipulator
        config = RepomixConfig()
        config.compression.enabled = True
        
        result = process_content(content, file_path, config)
        
        # For Python files with compression enabled, should get compressed content
        # The actual compression logic is tested elsewhere, here we just verify
        # that the compression path is taken
        assert result != content  # Should be different from original due to compression
        assert len(result) > 0

    def test_process_files_with_empty_files(self):
        """Test processing files including empty ones"""
        raw_files = [
            RawFile(path="content.py", content="print('content')"),
            RawFile(path="empty.py", content="")
        ]
        
        config = RepomixConfig()
        processed_files = process_files(raw_files, config)
        
        assert len(processed_files) == 2
        
        # Find processed files by path
        content_file = next(f for f in processed_files if f.path == "content.py")
        empty_file = next(f for f in processed_files if f.path == "empty.py")
        
        assert len(content_file.content) > 0
        assert len(empty_file.content) == 0

    def test_process_files_with_unreadable_files(self):
        """Test processing works with readable files (unreadable files would be filtered earlier)"""
        raw_files = [
            RawFile(path="readable.py", content="print('readable')"),
            RawFile(path="another.py", content="print('another')")
        ]
        
        config = RepomixConfig()
        processed_files = process_files(raw_files, config)
        
        # Should process all provided files successfully
        assert len(processed_files) == 2
        for processed_file in processed_files:
            assert len(processed_file.content) > 0


class TestPermissionCheck:
    """Test cases for permission checking"""
    
    def test_has_read_permission_readable_file(self):
        """Test permission check for readable file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")
            
            result = check_file_permission(test_file)
            assert result.has_permission is True

    def test_has_read_permission_nonexistent_file(self):
        """Test permission check for non-existent file"""
        nonexistent_file = Path("/non/existent/file.txt")
        
        result = check_file_permission(nonexistent_file)
        assert result.has_permission is False

    @pytest.mark.skipif(os.name == 'nt', reason="POSIX permissions not applicable on Windows")
    def test_has_read_permission_unreadable_file(self):
        """Test permission check for unreadable file (Unix/Linux only)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "unreadable.txt"
            test_file.write_text("test content")
            
            # Remove read permission
            test_file.chmod(0o000)
            
            try:
                result = check_file_permission(test_file)
                assert result.has_permission is False
            finally:
                # Restore permissions for cleanup
                test_file.chmod(0o644)


class TestFileProcessingIntegration:
    """Integration tests for file processing"""
    
    def test_complete_file_processing_workflow(self):
        """Test complete file processing workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create realistic project structure
            (temp_path / "src").mkdir()
            (temp_path / "src" / "main.py").write_text('''
#!/usr/bin/env python3
"""Main application module."""

def main():
    """Main function."""
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    main()
            ''')
            
            (temp_path / "src" / "utils.py").write_text('''
"""Utility functions."""

def calculate(x, y):
    """Calculate sum."""
    return x + y

class Helper:
    """Helper class."""
    
    def __init__(self):
        self.value = 0
    
    def process(self, data):
        """Process data."""
        return data.upper()
            ''')
            
            (temp_path / "tests").mkdir()
            (temp_path / "tests" / "test_main.py").write_text('''
"""Tests for main module."""

import unittest
from src.main import main

class TestMain(unittest.TestCase):
    """Test cases for main function."""
    
    def test_main(self):
        """Test main function."""
        result = main()
        self.assertEqual(result, 0)
            ''')
            
            (temp_path / "README.md").write_text('''
# Project

This is a test project.

## Features
- Main application
- Utility functions
- Comprehensive tests
            ''')
            
            (temp_path / ".gitignore").write_text('''
__pycache__/
*.pyc
.env
            ''')
            
            # Test complete workflow
            config = RepomixConfig()
            
            # Step 1: Search and collect files
            from src.repomix.core.file.file_search import search_files
            search_result = search_files(temp_dir, config)
            files = collect_files(search_result.file_paths, temp_dir)
            assert len(files) >= 4
            
            # Step 2: Process files
            processed_files = process_files(files, config)
            
            # Verify results
            assert len(processed_files) >= 4
            assert all(isinstance(f.path, str) for f in processed_files)
            assert all(isinstance(f.content, str) for f in processed_files)
            
            # Verify specific files were processed
            file_names = [f.path for f in processed_files]
            assert any("main.py" in name for name in file_names)
            assert any("utils.py" in name for name in file_names)
            assert any("README.md" in name for name in file_names)
            
            # Verify content lengths are reasonable
            total_chars = sum(len(f.content) for f in processed_files)
            
            assert total_chars > 0

    def test_file_processing_with_compression(self):
        """Test file processing with compression enabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create Python file with detailed content
            python_file = temp_path / "complex.py"
            python_content = '''
"""Complex Python module."""

import os
import sys
from typing import List, Dict, Optional

class DataProcessor:
    """Process data with various methods."""
    
    def __init__(self, config: Dict):
        """Initialize processor."""
        self.config = config
        self.results = []
    
    def process_data(self, data: List[str]) -> Optional[List[str]]:
        """Process input data."""
        try:
            processed = []
            for item in data:
                # Complex processing logic
                if self.validate_item(item):
                    processed.append(self.transform_item(item))
            return processed
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def validate_item(self, item: str) -> bool:
        """Validate individual item."""
        return len(item) > 0 and item.isalnum()
    
    def transform_item(self, item: str) -> str:
        """Transform individual item."""
        return item.upper().strip()
            '''
            python_file.write_text(python_content)
            
            config = RepomixConfig()
            config.compression.enabled = True
            
            # Create RawFile objects instead of Path objects
            from src.repomix.core.file.file_types import RawFile
            raw_files = [RawFile(path="complex.py", content=python_content)]
            
            # Test actual compression functionality instead of mocking
            # This tests the real behavior including multiprocessing
            processed_files = process_files(raw_files, config)
            
            assert len(processed_files) == 1
            assert processed_files[0].path == "complex.py"
            assert len(processed_files[0].content) > 0
            
            # For Python files with compression enabled, the output should be compressed
            # The actual compressed content depends on the PythonManipulator implementation
            processed_content = processed_files[0].content
            
            # Verify processing occurred (content may be different due to compression or formatting)
            assert isinstance(processed_content, str)
            # The processed content should have some meaningful content
            assert len(processed_content.strip()) > 0


if __name__ == "__main__":
    pytest.main([__file__])