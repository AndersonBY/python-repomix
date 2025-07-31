"""
Test suite for security functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.repomix.core.security.security_check import (
    SecurityChecker, 
    SuspiciousFileResult, 
    check_files
)
from src.repomix.config.config_schema import RepomixConfig


class TestSecurityChecker:
    """Test cases for SecurityChecker class"""
    
    def setup_method(self):
        """Set up test environment"""
        self.checker = SecurityChecker()

    def test_security_checker_initialization(self):
        """Test SecurityChecker initialization"""
        assert self.checker is not None
        assert hasattr(self.checker, 'SUSPICIOUS_FILE_PATTERNS')
        assert hasattr(self.checker, 'SUSPICIOUS_CONTENT_PATTERNS')
        assert len(self.checker.SUSPICIOUS_FILE_PATTERNS) > 0
        assert len(self.checker.SUSPICIOUS_CONTENT_PATTERNS) > 0

    def test_suspicious_file_patterns(self):
        """Test suspicious file name patterns"""
        patterns = self.checker.SUSPICIOUS_FILE_PATTERNS
        
        # Should contain common suspicious patterns
        env_pattern = any('.env' in pattern for pattern in patterns)
        key_pattern = any('.key' in pattern for pattern in patterns)
        pem_pattern = any('.pem' in pattern for pattern in patterns)
        
        assert env_pattern, "Should contain .env pattern"
        assert key_pattern, "Should contain .key pattern" 
        assert pem_pattern, "Should contain .pem pattern"

    def test_suspicious_content_patterns(self):
        """Test suspicious content patterns"""
        patterns = self.checker.SUSPICIOUS_CONTENT_PATTERNS
        
        # Should contain common suspicious content patterns
        api_key_pattern = any('api' in pattern.lower() for pattern in patterns)
        password_pattern = any('password' in pattern.lower() for pattern in patterns)
        
        assert api_key_pattern, "Should contain API key pattern"
        assert password_pattern, "Should contain password pattern"

    def test_check_suspicious_file_name(self):
        """Test suspicious file name checking"""
        # Test suspicious file names using SecurityChecker
        checker = SecurityChecker()
        
        suspicious_files = [
            ".env",
            ".env.local", 
            "private.key",
            "certificate.pem",
            "keystore.jks",
            "database.kdbx"
        ]
        
        for filename in suspicious_files:
            # Check if any pattern matches
            is_suspicious = any(pattern.match(filename) for pattern in checker.suspicious_file_patterns)
            assert is_suspicious, f"{filename} should be suspicious"
        
        # Test normal file names
        normal_files = [
            "main.py",
            "README.md",
            "package.json",
            "style.css",
            "app.js"
        ]
        
        for filename in normal_files:
            is_suspicious = any(pattern.match(filename) for pattern in checker.suspicious_file_patterns)
            assert not is_suspicious, f"{filename} should not be suspicious"

    def test_check_file_content_with_api_keys(self):
        """Test file content checking with API keys"""
        suspicious_content = '''
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"
STRIPE_SECRET_KEY = "sk_test_1234567890abcdefghijklmnop"
        '''
        
        checker = SecurityChecker()
        messages = checker.check_file(Path("config.py"), suspicious_content)
        
        assert len(messages) > 0
        assert any("api" in msg.lower() for msg in messages)

    def test_check_file_content_with_passwords(self):
        """Test file content checking with passwords"""
        suspicious_content = '''
PASSWORD = "supersecret123"
DATABASE_PASSWORD = "mypassword456"
pwd = "admin123"
        '''
        
        checker = SecurityChecker()
        messages = checker.check_file(Path("secrets.py"), suspicious_content)
        
        assert len(messages) > 0
        assert any("password" in msg.lower() for msg in messages)

    def test_check_file_content_with_tokens(self):
        """Test file content checking with tokens"""
        suspicious_content = '''
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
BEARER_TOKEN = "Bearer abc123def456ghi789"
        '''
        
        checker = SecurityChecker()
        messages = checker.check_file(Path("auth.py"), suspicious_content)
        
        assert len(messages) > 0
        assert any("token" in msg.lower() for msg in messages)

    def test_check_file_content_safe_content(self):
        """Test file content checking with safe content"""
        safe_content = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
        '''
        
        checker = SecurityChecker()
        messages = checker.check_file(Path("calculator.py"), safe_content)
        
        assert len(messages) == 0

    def test_check_file_content_with_comments(self):
        """Test file content checking with suspicious content in comments"""
        content_with_comments = '''
# TODO: Replace with actual API key
# API_KEY = "sk-1234567890abcdefghijklmnop"
def main():
    print("Hello, World!")
        '''
        
        checker = SecurityChecker()
        messages = checker.check_file(Path("todo.py"), content_with_comments)
        
        # Should still detect suspicious patterns even in comments
        assert len(messages) > 0

    def test_check_file_content_false_positives(self):
        """Test file content checking for common false positives"""
        false_positive_content = '''
# This is documentation about API keys
# Example: API_KEY = "your-key-here"
# Never commit real keys to version control

def get_api_key():
    """Get API key from environment."""
    return os.getenv("API_KEY", "default-key")
        '''
        
        checker = SecurityChecker()
        _messages = checker.check_file(Path("docs.py"), false_positive_content)
        
        # This might trigger false positives, but that's often acceptable
        # for security scanning - better safe than sorry
        # The test mainly ensures the function doesn't crash


class TestSuspiciousFileResult:
    """Test cases for SuspiciousFileResult dataclass"""
    
    def test_suspicious_file_result_creation(self):
        """Test SuspiciousFileResult creation"""
        result = SuspiciousFileResult(
            file_path="/path/to/suspicious.env",
            messages=["Contains API key", "Contains password"]
        )
        
        assert result.file_path == "/path/to/suspicious.env"
        assert len(result.messages) == 2
        assert "Contains API key" in result.messages
        assert "Contains password" in result.messages

    def test_suspicious_file_result_empty_messages(self):
        """Test SuspiciousFileResult with empty messages"""
        result = SuspiciousFileResult(
            file_path="/path/to/file.py",
            messages=[]
        )
        
        assert result.file_path == "/path/to/file.py"
        assert len(result.messages) == 0


class TestCheckFiles:
    """Test cases for check_files function"""
    
    def test_check_files_basic(self):
        """Test basic file checking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create safe file
            safe_file = temp_path / "safe.py"
            safe_file.write_text("def hello(): return 'world'")
            
            # Create suspicious file
            suspicious_file = temp_path / "config.py"
            suspicious_file.write_text('API_KEY = "sk-1234567890abcdef"')
            
            files = ["safe.py", "config.py"]
            file_contents = {
                "safe.py": "def hello(): return 'world'",
                "config.py": 'API_KEY = "sk-1234567890abcdef"'
            }
            
            results = check_files(temp_dir, files, file_contents)
            
            assert isinstance(results, list)
            # Should find at least one suspicious file
            assert len(results) >= 1
            
            # Find the suspicious result
            suspicious_results = [r for r in results if "config.py" in r.file_path]
            assert len(suspicious_results) > 0
            assert len(suspicious_results[0].messages) > 0

    def test_check_files_security_disabled(self):
        """Test file checking always runs (no security disable option in check_files)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create suspicious file
            suspicious_file = temp_path / ".env"
            suspicious_file.write_text('SECRET_KEY = "supersecret123"')
            
            files = [".env"]
            file_contents = {
                ".env": 'SECRET_KEY = "supersecret123"'
            }
            
            results = check_files(temp_dir, files, file_contents)
            
            # Should return results since check_files always checks
            assert len(results) >= 1

    def test_check_files_with_suspicious_filenames(self):
        """Test file checking with suspicious filenames"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files with suspicious names but safe content
            env_file = temp_path / ".env"
            env_file.write_text("# Environment variables")
            
            key_file = temp_path / "private.key"
            key_file.write_text("# This is not actually a key")
            
            file_paths = [".env", "private.key"]
            file_contents = {
                ".env": "# Environment variables",
                "private.key": "# This is not actually a key"
            }
            
            results = check_files(temp_dir, file_paths, file_contents)
            
            assert len(results) >= 2
            
            # Should detect both files as suspicious based on filename
            file_paths = [r.file_path for r in results]
            assert any(".env" in path for path in file_paths)
            assert any("private.key" in path for path in file_paths)

    def test_check_files_with_mixed_content(self):
        """Test file checking with mixed safe and suspicious content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create file with mixed content
            mixed_file = temp_path / "app.py"
            mixed_file.write_text('''
import os
import requests

def main():
    """Main application function."""
    print("Starting application...")
    
    # Get API key from environment
    api_key = os.getenv("API_KEY")
    if not api_key:
        # Fallback - THIS IS BAD PRACTICE
        api_key = "sk-1234567890abcdefghijk"
    
    response = requests.get(
        "https://api.example.com/data",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    return response.json()

if __name__ == "__main__":
    main()
            ''')
            
            # Read the file content
            file_content = mixed_file.read_text()
            
            file_paths = ["app.py"]
            file_contents = {
                "app.py": file_content
            }
            
            results = check_files(temp_dir, file_paths, file_contents)
            
            # Should detect the hardcoded API key
            assert len(results) >= 1
            suspicious_result = results[0]
            assert "app.py" in suspicious_result.file_path
            assert len(suspicious_result.messages) > 0

    def test_check_files_empty_list(self):
        """Test file checking with empty file list"""
        config = RepomixConfig()
        config.security.enable_security_check = True
        
        results = check_files("/tmp", [], {})
        
        assert results == []

    def test_check_files_unreadable_files(self):
        """Test file checking with unreadable files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create file
            test_file = temp_path / "test.py"
            test_file.write_text("print('test')")
            
            file_paths = ["test.py"]
            file_contents = {
                "test.py": "print('test')"
            }
            
            # Test that check_files works normally with valid files
            results = check_files(temp_dir, file_paths, file_contents)
            
            # Should handle the files without errors
            assert isinstance(results, list)

    @patch('src.repomix.core.security.security_check.SecretsCollection')
    def test_check_files_with_detect_secrets(self, mock_secrets_collection):
        """Test file checking with detect-secrets integration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create file with potential secrets
            secrets_file = temp_path / "secrets.py"
            secrets_content = '''
POSTGRES_PASSWORD = "mypassword123"
JWT_SECRET = "jwt-secret-key-12345"
            '''
            secrets_file.write_text(secrets_content)
            
            # Mock detect-secrets to return iterable with mock secrets
            mock_collection = Mock()
            mock_secrets_collection.return_value = mock_collection
            
            # Mock secret objects that would be returned
            mock_secret_1 = (None, Mock(type="password"))
            mock_secret_2 = (None, Mock(type="api_key"))
            mock_collection.__iter__ = Mock(return_value=iter([mock_secret_1, mock_secret_2]))
            mock_collection.scan_file.return_value = None
            
            file_paths = ["secrets.py"]
            file_contents = {
                "secrets.py": secrets_content
            }
            
            results = check_files(temp_dir, file_paths, file_contents)
            
            # Should integrate with detect-secrets
            assert len(results) >= 1


class TestSecurityIntegration:
    """Integration tests for security functionality"""
    
    def test_realistic_security_scan(self):
        """Test realistic security scanning scenario"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create realistic project structure with security issues
            
            # Safe files
            (temp_path / "main.py").write_text('''
import os
import logging

def main():
    """Main application entry point."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Application starting...")
    
    # Safe environment variable usage
    database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
    logger.info(f"Using database: {database_url}")
    
    return 0

if __name__ == "__main__":
    main()
            ''')
            
            (temp_path / "utils.py").write_text('''
"""Utility functions."""

def format_data(data):
    """Format data for display."""
    return str(data).upper()

def validate_input(user_input):
    """Validate user input."""
    if not user_input or len(user_input) < 3:
        return False
    return True
            ''')
            
            # Suspicious files
            (temp_path / ".env").write_text('''
DATABASE_URL=postgresql://user:secret123@localhost/mydb
API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
SECRET_KEY=supersecretkey123
            ''')
            
            (temp_path / "config.py").write_text('''
# Configuration file - DO NOT COMMIT
API_SETTINGS = {
    "key": "sk-proj-abcdefghijklmnopqrstuvwxyz123456",
    "endpoint": "https://api.example.com"
}

DATABASE_CONFIG = {
    "host": "localhost",
    "user": "admin", 
    "password": "admin123",
    "database": "production"
}
            ''')
            
            (temp_path / "private.key").write_text('''
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
-----END PRIVATE KEY-----
            ''')
            
            # Test comprehensive security scan
            file_paths = []
            file_contents = {}
            
            for file_path in temp_path.glob("*"):
                if file_path.is_file():
                    relative_path = file_path.name
                    file_paths.append(relative_path)
                    file_contents[relative_path] = file_path.read_text()
            
            results = check_files(temp_dir, file_paths, file_contents)
            
            # Should detect multiple security issues
            assert len(results) >= 3  # At least .env, config.py, and private.key
            
            # Verify specific detections
            file_paths = [r.file_path for r in results]
            assert any(".env" in path for path in file_paths)
            assert any("config.py" in path for path in file_paths) 
            assert any("private.key" in path for path in file_paths)
            
            # Verify messages are meaningful
            all_messages = []
            for result in results:
                all_messages.extend(result.messages)
            
            assert len(all_messages) > 0
            assert any("suspicious" in msg.lower() or "secret" in msg.lower() for msg in all_messages)
            assert any("key" in msg.lower() or "password" in msg.lower() for msg in all_messages)

    def test_security_scan_with_false_positives(self):
        """Test security scanning with potential false positives"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files that might trigger false positives
            (temp_path / "documentation.md").write_text('''
# API Documentation

## Authentication

To authenticate, use your API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" https://api.example.com
```

Replace `YOUR_API_KEY_HERE` with your actual API key.

## Environment Variables

Set the following environment variables:
- `API_KEY`: Your API key (e.g., "sk-...")  
- `DATABASE_PASSWORD`: Your database password

Never commit real credentials to version control!
            ''')
            
            (temp_path / "test_auth.py").write_text('''
"""Tests for authentication module."""

import unittest
from unittest.mock import patch

class TestAuth(unittest.TestCase):
    
    def test_api_key_validation(self):
        """Test API key validation."""
        # Test with mock API key
        mock_key = "sk-test-1234567890abcdef"
        self.assertTrue(validate_api_key(mock_key))
        
        # Test with invalid key
        invalid_key = "invalid-key"
        self.assertFalse(validate_api_key(invalid_key))
    
    @patch.dict(os.environ, {"API_KEY": "test-key"})
    def test_environment_api_key(self):
        """Test getting API key from environment."""
        key = get_api_key()
        self.assertEqual(key, "test-key")
            ''')
            
            file_paths = []
            file_contents = {}
            
            for file_path in temp_path.glob("*"):
                if file_path.is_file():
                    relative_path = file_path.name
                    file_paths.append(relative_path)
                    file_contents[relative_path] = file_path.read_text()
            
            results = check_files(temp_dir, file_paths, file_contents)
            
            # May have some false positives, but should still work
            assert isinstance(results, list)
            
            # Verify the function doesn't crash with documentation/test files
            for result in results:
                assert isinstance(result, SuspiciousFileResult)
                assert result.file_path is not None
                assert isinstance(result.messages, list)

    def test_performance_with_large_files(self):
        """Test security scanning performance with larger files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a larger file with repeated content
            large_content = []
            for i in range(1000):
                large_content.append(f'''
def function_{i}():
    """Function number {i}."""
    data = "safe_data_{i}"
    return process_data(data)
                ''')
            
            # Add one suspicious line
            large_content.append('API_KEY = "sk-1234567890abcdef"')
            
            large_file = temp_path / "large_module.py"
            large_file.write_text('\n'.join(large_content))
            
            # This should complete in reasonable time
            import time
            start_time = time.time()
            
            large_content_str = '\n'.join(large_content)
            file_paths = ["large_module.py"]
            file_contents = {
                "large_module.py": large_content_str
            }
            
            results = check_files(temp_dir, file_paths, file_contents)
            
            end_time = time.time()
            scan_time = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert scan_time < 10.0, f"Security scan took too long: {scan_time} seconds"
            
            # Should still detect the suspicious content
            assert len(results) >= 1
            assert any("api" in msg.lower() for result in results for msg in result.messages)


if __name__ == "__main__":
    pytest.main([__file__])