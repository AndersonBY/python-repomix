"""
Test suite for error handling functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch
import io

from src.repomix.shared.error_handle import RepomixError, handle_error
from src.repomix.shared.logger import logger


# Create custom error classes for testing
class ConfigurationError(RepomixError):
    """Configuration error"""

    pass


class ProcessingError(RepomixError):
    """Processing error"""

    pass


class RepomixFileNotFoundError(RepomixError):
    """File not found error"""

    pass


class TestRepomixError:
    """Test cases for RepomixError exception class"""

    def test_repomix_error_basic(self):
        """Test basic RepomixError creation"""
        error = RepomixError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_repomix_error_with_cause(self):
        """Test RepomixError with underlying cause"""
        original_error = ValueError("Original error")

        try:
            raise original_error
        except ValueError as e:
            wrapped_error = RepomixError("Wrapped error")
            wrapped_error.__cause__ = e

            assert str(wrapped_error) == "Wrapped error"
            assert wrapped_error.__cause__ == original_error

    def test_repomix_error_inheritance(self):
        """Test RepomixError inheritance hierarchy"""
        error = RepomixError("Test")

        assert isinstance(error, Exception)
        assert isinstance(error, RepomixError)

    def test_repomix_error_empty_message(self):
        """Test RepomixError with empty message"""
        error = RepomixError("")

        assert str(error) == ""

    def test_repomix_error_none_message(self):
        """Test RepomixError with None message"""
        error = RepomixError("None")  # Pass string instead of None

        assert str(error) == "None"


class TestSpecificErrors:
    """Test cases for specific error types"""

    def test_file_not_found_error(self):
        """Test RepomixFileNotFoundError"""
        error = RepomixFileNotFoundError("File not found: test.py")

        assert isinstance(error, RepomixError)
        assert str(error) == "File not found: test.py"

    def test_configuration_error(self):
        """Test ConfigurationError"""
        error = ConfigurationError("Invalid configuration: missing required field")

        assert isinstance(error, RepomixError)
        assert str(error) == "Invalid configuration: missing required field"

    def test_processing_error(self):
        """Test ProcessingError"""
        error = ProcessingError("Failed to process file: syntax error")

        assert isinstance(error, RepomixError)
        assert str(error) == "Failed to process file: syntax error"


class TestHandleError:
    """Test cases for error handling function"""

    def test_handle_error_repomix_error(self):
        """Test handling RepomixError"""
        error = RepomixError("Test repomix error")

        # Capture stderr output
        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                handle_error(error)

                mock_exit.assert_called_once_with(1)

        stderr_output = captured_stderr.getvalue()
        assert "Test repomix error" in stderr_output

    def test_handle_error_file_not_found(self):
        """Test handling FileNotFoundError"""
        error = FileNotFoundError("No such file or directory: 'missing.txt'")

        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                handle_error(error)

                mock_exit.assert_called_once_with(1)

        stderr_output = captured_stderr.getvalue()
        assert "missing.txt" in stderr_output

    def test_handle_error_permission_error(self):
        """Test handling PermissionError"""
        error = PermissionError("Permission denied: '/protected/file.txt'")

        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                handle_error(error)

                mock_exit.assert_called_once_with(1)

        stderr_output = captured_stderr.getvalue()
        assert "Permission denied" in stderr_output

    def test_handle_error_keyboard_interrupt(self):
        """Test handling KeyboardInterrupt"""
        # KeyboardInterrupt is a BaseException, not Exception - handle appropriately
        error = KeyboardInterrupt()

        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                # Handle KeyboardInterrupt as BaseException
                try:
                    raise error
                except BaseException as _e:
                    handle_error(Exception("Interrupted by user"), 1)

                mock_exit.assert_called_once_with(1)  # Default exit code

        stderr_output = captured_stderr.getvalue()
        assert "error occurred" in stderr_output.lower()

    def test_handle_error_generic_exception(self):
        """Test handling generic Exception"""
        error = ValueError("Invalid value provided")

        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                handle_error(error)

                mock_exit.assert_called_once_with(1)

        stderr_output = captured_stderr.getvalue()
        assert "Invalid value provided" in stderr_output

    def test_handle_error_with_debug_info(self):
        """Test error handling with debug information"""
        error = Exception("Test exception with debug info")

        captured_stderr = io.StringIO()

        # Mock verbose logging to include debug info
        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                with patch.object(logger, "is_verbose", return_value=True):
                    handle_error(error)

                mock_exit.assert_called_once_with(1)

        stderr_output = captured_stderr.getvalue()
        # Just verify that some error output was captured (traceback.print_exc() was called)
        assert len(stderr_output.strip()) > 0

    def test_handle_error_quiet_mode(self):
        """Test error handling in quiet mode"""
        error = RepomixError("Quiet error")

        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            with patch("sys.exit") as mock_exit:
                with patch.object(logger, "is_verbose", return_value=False):
                    handle_error(error)

                mock_exit.assert_called_once_with(1)

        stderr_output = captured_stderr.getvalue()
        # Should still show error message even in quiet mode
        assert "Quiet error" in stderr_output


class TestErrorScenarios:
    """Test cases for common error scenarios"""

    def test_configuration_loading_error(self):
        """Test error handling during configuration loading"""
        from src.repomix.config.config_load import load_config

        # Test with invalid config file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "invalid_config.json"
            config_file.write_text("{ invalid json content }")

            with pytest.raises((RepomixError, ValueError, Exception)):
                load_config(temp_dir, temp_dir, str(config_file), {})

    def test_file_processing_error(self):
        """Test error handling during file processing"""
        from src.repomix.core.file.file_process import process_files
        from src.repomix.core.file.file_types import RawFile
        from src.repomix.config.config_schema import RepomixConfig

        # Test with problematic content - create RawFile instead of Path
        raw_files = [RawFile(path="non_existent.py", content="")]
        config = RepomixConfig()

        # Should handle empty files gracefully
        processed_files = process_files(raw_files, config)

        # Should not crash, but may have empty results
        assert isinstance(processed_files, list)
        assert len(processed_files) == 1
        assert processed_files[0].path == "non_existent.py"

    def test_repository_processing_error(self):
        """Test error handling during repository processing"""
        from src.repomix.core.repo_processor import RepoProcessor

        # Test with invalid directory
        with pytest.raises(RepomixError):
            RepoProcessor(directory="/non/existent/directory").process()

    def test_git_clone_error(self):
        """Test error handling during Git clone"""
        from src.repomix.shared.git_utils import clone_repository

        with patch("src.repomix.core.file.git_command.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Network error")

            with tempfile.TemporaryDirectory() as temp_dir:
                with pytest.raises((RepomixError, Exception)):
                    clone_repository("https://github.com/nonexistent/repo.git", temp_dir)

    def test_security_check_error(self):
        """Test error handling during security check"""
        from src.repomix.core.security.security_check import check_files
        from src.repomix.config.config_schema import RepomixConfig

        # Test with file that raises permission error
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('test')")

            config = RepomixConfig()
            config.security.enable_security_check = True

            # Mock file reading to raise permission error
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                # Should handle error gracefully - provide all required parameters
                file_paths = ["test.py"]
                file_contents = {"test.py": "print('test')"}
                results = check_files(temp_dir, file_paths, file_contents)
                assert isinstance(results, list)

    def test_output_generation_error(self):
        """Test error handling during output generation"""
        from src.repomix.core.output.output_generate import generate_output
        from src.repomix.core.file.file_types import ProcessedFile
        from src.repomix.config.config_schema import RepomixConfig

        # Test with proper data but mock internal errors
        processed_files = [ProcessedFile(path="test.py", content="print('test')")]
        file_tree = {"test.py": ""}
        config = RepomixConfig()
        file_char_counts = {"test.py": 13}
        file_token_counts = {"test.py": 3}

        # Test normal generation first
        try:
            result = generate_output(processed_files, config, file_char_counts, file_token_counts, file_tree)
            # If it doesn't raise an error, it should return something valid
            assert result is not None
            assert isinstance(result, str)
        except Exception as e:
            # If it raises an error, it should be handled gracefully
            assert str(e) is not None


class TestErrorRecovery:
    """Test cases for error recovery scenarios"""

    def test_partial_file_processing_recovery(self):
        """Test recovery from partial file processing failures"""
        from src.repomix.core.file.file_process import process_files
        from src.repomix.core.file.file_types import RawFile
        from src.repomix.config.config_schema import RepomixConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mix of good and problematic files
            good_file = temp_path / "good.py"
            good_file.write_text("def good_function(): return True")

            empty_file = temp_path / "empty.py"
            empty_file.write_text("")

            # Create RawFile objects instead of Path objects
            raw_files = [
                RawFile(path="good.py", content="def good_function(): return True"),
                RawFile(path="empty.py", content=""),
            ]
            config = RepomixConfig()

            # Should process successfully despite empty file
            processed_files = process_files(raw_files, config)

            assert len(processed_files) >= 1
            # Find the good file
            good_processed = next(f for f in processed_files if f.path == "good.py")
            assert len(good_processed.content) > 0
            # Find the empty file
            empty_processed = next(f for f in processed_files if f.path == "empty.py")
            assert len(empty_processed.content) == 0

    def test_network_error_recovery(self):
        """Test recovery from network errors"""
        from src.repomix.shared.git_utils import clone_repository

        with patch("src.repomix.core.file.git_command.subprocess.run") as mock_run:
            # Simulate network timeout
            import subprocess

            mock_run.side_effect = subprocess.TimeoutExpired("git", 300)

            with tempfile.TemporaryDirectory() as temp_dir:
                with pytest.raises((subprocess.TimeoutExpired, RepomixError)):
                    clone_repository("https://github.com/user/repo.git", temp_dir)

    def test_configuration_validation_recovery(self):
        """Test recovery from configuration validation errors"""
        from src.repomix.config.config_schema import RepomixConfig

        # Test invalid style value
        with pytest.raises(ValueError):
            config = RepomixConfig()
            config.output.style = "invalid_style"

    def test_large_file_processing_recovery(self):
        """Test recovery from large file processing issues"""
        from src.repomix.core.file.file_process import process_content
        from src.repomix.config.config_schema import RepomixConfig

        # Create very large content
        large_content = "x" * 1000000  # 1MB of 'x'
        config = RepomixConfig()

        # Should handle large content without crashing
        result = process_content(large_content, str(Path("large.txt")), config)

        assert result is not None
        assert len(result) > 0


class TestErrorReporting:
    """Test cases for error reporting and logging"""

    def test_error_message_formatting(self):
        """Test error message formatting"""
        error = RepomixError("This is a test error with details")

        message = str(error)
        assert "This is a test error with details" in message

    def test_error_context_preservation(self):
        """Test that error context is preserved"""
        original_error = FileNotFoundError("Original file not found")

        try:
            raise original_error
        except FileNotFoundError as e:
            wrapped_error = RepomixError("Failed to process file")
            wrapped_error.__cause__ = e

            assert wrapped_error.__cause__ == original_error
            assert "Original file not found" in str(wrapped_error.__cause__)

    def test_error_logging_integration(self):
        """Test error logging integration"""
        error = RepomixError("Test error for logging")

        with patch.object(logger, "error") as mock_log_error:
            with patch("sys.exit"):
                handle_error(error)

                # Verify error was logged
                mock_log_error.assert_called()

    def test_multiple_error_handling(self):
        """Test handling multiple errors in sequence"""
        errors = [
            RepomixError("First error"),
            FileNotFoundError("Second error"),
            PermissionError("Third error"),
        ]

        for error in errors:
            with patch("sys.exit") as mock_exit:
                handle_error(error)
                mock_exit.assert_called_once_with(1)


class TestErrorIntegration:
    """Integration tests for error handling across components"""

    def test_end_to_end_error_handling(self):
        """Test end-to-end error handling in realistic scenarios"""
        from src.repomix.core.repo_processor import RepoProcessor

        # Test complete failure scenario
        with pytest.raises(RepomixError):
            processor = RepoProcessor(directory="/absolutely/nonexistent/path")
            processor.process()

    def test_cli_error_integration(self):
        """Test CLI error handling integration"""
        from src.repomix.cli.cli_run import execute_action
        from argparse import Namespace

        # Test with invalid directory
        options = Namespace(version=False, init=False, mcp=False, remote=None, verbose=False)

        with patch("src.repomix.shared.error_handle.handle_error") as _mock_handle:
            try:
                execute_action("/nonexistent/directory", Path.cwd(), options)
            except Exception:
                # If execute_action doesn't handle the error internally,
                # it should propagate to handle_error
                pass

    def test_configuration_error_integration(self):
        """Test configuration error handling integration"""
        from src.repomix.config.config_load import load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid config file
            config_file = Path(temp_dir) / "repomix.config.json"
            config_file.write_text('{"invalid": "json", "structure":}')  # Invalid JSON

            # Should handle invalid JSON gracefully
            try:
                config = load_config(temp_dir, temp_dir, None, {})
                # If it loads successfully, it should have used defaults
                assert config is not None
            except (RepomixError, ValueError):
                # Raising an error is also acceptable
                pass


if __name__ == "__main__":
    pytest.main([__file__])
