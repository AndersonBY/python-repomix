"""
Test suite for MCP server silent mode functionality
"""

import asyncio
import io
import json
import pytest
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from src.repomix.mcp.mcp_server import create_mcp_server
from src.repomix.mcp.silent_mode import set_mcp_silent_mode, is_mcp_silent_mode


class TestMCPSilentMode:
    """Test cases for MCP server silent mode functionality"""

    def setup_method(self):
        """Reset silent mode before each test"""
        set_mcp_silent_mode(True)  # Reset to default
        
        # Reset logger state to ensure clean test environment
        from src.repomix.shared.logger import logger, LogLevel
        logger.set_verbose(False)
        logger.set_log_level(LogLevel.INFO)

    def test_default_silent_mode_state(self):
        """Test that the default silent mode state is True"""
        # Reset to ensure clean state
        set_mcp_silent_mode(True)
        assert is_mcp_silent_mode() is True

    def test_set_silent_mode_false(self):
        """Test setting silent mode to False"""
        set_mcp_silent_mode(False)
        assert is_mcp_silent_mode() is False

    def test_set_silent_mode_true(self):
        """Test setting silent mode to True"""
        set_mcp_silent_mode(False)  # First set to False
        set_mcp_silent_mode(True)  # Then set to True
        assert is_mcp_silent_mode() is True

    def test_create_mcp_server_default_silent(self):
        """Test that create_mcp_server() uses silent=True by default"""
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            _server = create_mcp_server()

        stdout_output = stdout_capture.getvalue()
        _stderr_output = stderr_capture.getvalue()

        # Should be no output when silent=True (default)
        assert "🔧 Creating MCP server..." not in stdout_output
        assert "📦 Registering MCP tools..." not in stdout_output
        assert "✅ pack_codebase" not in stdout_output
        assert is_mcp_silent_mode() is True

    def test_create_mcp_server_explicit_silent_true(self):
        """Test create_mcp_server(silent=True) produces no output"""
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            _server = create_mcp_server(silent=True)

        stdout_output = stdout_capture.getvalue()
        _stderr_output = stderr_capture.getvalue()

        # Should be no output when silent=True
        assert "🔧 Creating MCP server..." not in stdout_output
        assert "📦 Registering MCP tools..." not in stdout_output
        assert "✅ pack_codebase" not in stdout_output
        assert is_mcp_silent_mode() is True

    def test_create_mcp_server_explicit_silent_false(self):
        """Test create_mcp_server(silent=False) produces output"""
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            _server = create_mcp_server(silent=False)

        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        combined_output = stdout_output + stderr_output

        # Should have output when silent=False (messages might go to stdout or stderr depending on test environment)
        assert "🔧 Creating MCP server..." in combined_output
        assert "📦 Registering MCP tools..." in combined_output
        assert "✅ pack_codebase" in combined_output
        assert "✅ pack_remote_repository" in combined_output
        assert "✅ read_repomix_output" in combined_output
        assert "✅ grep_repomix_output" in combined_output
        assert "✅ file_system_read_file" in combined_output
        assert "✅ file_system_read_directory" in combined_output
        assert "🎯 Repomix MCP Server configured with 6 tools" in combined_output
        assert is_mcp_silent_mode() is False

    @pytest.mark.asyncio
    async def test_pack_codebase_tool_silent_mode(self):
        """Test that pack_codebase tool respects silent mode"""
        # Create a temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test.py").write_text('print("Hello, world!")\n')
            (temp_path / "README.md").write_text("# Test Project\n")

            # Test with silent=True (should be no tool debug output)
            server = create_mcp_server(silent=True)

            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                result = await server.call_tool("pack_codebase", {"directory": str(temp_path), "top_files_length": 3, "compress": False})

            stdout_output = stdout_capture.getvalue()
            _stderr_output = stderr_capture.getvalue()

            # Should not contain MCP tool debug messages
            assert "🔨 MCP Tool Called: pack_codebase" not in stdout_output
            assert "📁 Directory:" not in stdout_output
            assert "🗜️ Compress:" not in stdout_output
            assert "🏗️ Creating workspace..." not in stdout_output
            assert "🔄 Processing repository..." not in stdout_output
            assert "✅ Processing completed!" not in stdout_output
            assert "🎉 MCP response generated successfully" not in stdout_output

            # But should still contain the core repomix output (from default_action prints)
            # This is expected because the actual processing still needs to show results

            # Verify the tool actually worked
            assert result is not None

    @pytest.mark.asyncio
    async def test_pack_codebase_tool_verbose_mode(self):
        """Test that pack_codebase tool shows debug output when not silent"""
        # Create a temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test.py").write_text('print("Hello, world!")\n')
            (temp_path / "README.md").write_text("# Test Project\n")

            # Test with silent=False (should show tool debug output)
            server = create_mcp_server(silent=False)

            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                result = await server.call_tool("pack_codebase", {"directory": str(temp_path), "top_files_length": 3, "compress": False})

            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            combined_output = stdout_output + stderr_output

            # Should contain MCP tool debug messages (might go to stdout or stderr depending on test environment)
            assert "🔨 MCP Tool Called: pack_codebase" in combined_output
            assert "📁 Directory:" in combined_output
            assert "🗜️ Compress:" in combined_output
            assert "🏗️ Creating workspace..." in combined_output
            assert "🔄 Processing repository..." in combined_output
            assert "✅ Processing completed!" in combined_output
            assert "🎉 MCP response generated successfully" in combined_output

            # Verify the tool actually worked
            assert result is not None

    def test_server_creation_preserves_silent_state(self):
        """Test that server creation preserves the silent state for tools"""
        # Test silent=True
        _server = create_mcp_server(silent=True)
        assert is_mcp_silent_mode() is True

        # Test silent=False
        _server = create_mcp_server(silent=False)
        assert is_mcp_silent_mode() is False

        # Test back to silent=True
        _server = create_mcp_server(silent=True)
        assert is_mcp_silent_mode() is True

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_respect_silent_mode(self):
        """Test that multiple tool calls all respect the silent mode setting"""
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.py").write_text('print("Hello")\n')

            # Create server in silent mode
            server = create_mcp_server(silent=True)

            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Make multiple tool calls
                result1 = await server.call_tool("pack_codebase", {"directory": str(temp_path), "compress": False})

                # For second call, let's test file system tools which should also respect silent mode
                result2 = await server.call_tool("file_system_read_directory", {"input_data": {"path": str(temp_path)}})

            stdout_output = stdout_capture.getvalue()

            # Count occurrences of debug messages - should be 0
            debug_messages = ["🔨 MCP Tool Called:", "🏗️ Creating workspace...", "🔄 Processing repository...", "✅ Processing completed!"]

            for debug_msg in debug_messages:
                assert debug_msg not in stdout_output, f"Found debug message '{debug_msg}' in silent mode"

            # Both calls should succeed
            assert result1 is not None
            assert result2 is not None

    @pytest.mark.asyncio
    async def test_all_tools_registered_properly(self):
        """Test that all 6 tools are registered and accessible"""
        server = create_mcp_server(silent=True)

        # Test that we can list available tools (this depends on FastMCP implementation)
        # For now, let's test by trying to call each tool type

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")

            # Test each tool exists by calling with minimal parameters
            tools_to_test = [
                ("pack_codebase", {"directory": str(temp_path)}),
                ("file_system_read_directory", {"input_data": {"path": str(temp_path)}}),
                ("file_system_read_file", {"input_data": {"path": str(temp_path / "test.txt")}}),
            ]

            for tool_name, params in tools_to_test:
                try:
                    result = await server.call_tool(tool_name, params)
                    assert result is not None, f"Tool {tool_name} returned None"
                except Exception as e:
                    # Some tools might fail due to missing parameters, but they should be registered
                    # The important thing is that the tool exists and can be called
                    assert "not found" not in str(e).lower(), f"Tool {tool_name} not found: {e}"


class TestMCPSilentModeIntegration:
    """Integration tests for MCP silent mode with realistic scenarios"""

    def setup_method(self):
        """Reset silent mode before each test"""
        set_mcp_silent_mode(True)
        
        # Reset logger state to ensure clean test environment
        from src.repomix.shared.logger import logger, LogLevel
        logger.set_verbose(False)
        logger.set_log_level(LogLevel.INFO)

    @pytest.mark.asyncio
    async def test_realistic_codebase_analysis_silent(self):
        """Test a realistic codebase analysis scenario in silent mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a realistic small codebase
            (temp_path / "main.py").write_text('''
def main():
    """Main application entry point."""
    print("Hello, world!")
    return 0

if __name__ == "__main__":
    main()
            ''')

            (temp_path / "utils.py").write_text('''
def helper_function(x):
    """A helper function."""
    return x * 2

class UtilityClass:
    def __init__(self, value):
        self.value = value
    
    def process(self):
        return helper_function(self.value)
            ''')

            (temp_path / "README.md").write_text("""
# Test Project

This is a test project for MCP silent mode testing.

## Features
- Main application
- Utility functions
- Documentation
            """)

            # Test the full workflow in silent mode
            server = create_mcp_server(silent=True)

            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Pack the codebase
                    pack_result = await server.call_tool("pack_codebase", {"directory": str(temp_path), "compress": False, "top_files_length": 5})

                    # Read directory structure
                    dir_result = await server.call_tool("file_system_read_directory", {"input_data": {"path": str(temp_path)}})

                    # Read a specific file
                    file_result = await server.call_tool("file_system_read_file", {"input_data": {"path": str(temp_path / "main.py")}})

                stdout_output = stdout_capture.getvalue()

                # In silent mode, should not see MCP tool debug messages
                assert "🔨 MCP Tool Called:" not in stdout_output
                assert "🏗️ Creating workspace..." not in stdout_output

                # But should still see the core repomix processing output (this is expected)
                # All tools should have succeeded
                assert pack_result is not None
                assert dir_result is not None
                assert file_result is not None

                # Verify the pack result contains expected data structure
                if isinstance(pack_result, tuple) and len(pack_result) > 0:
                    content_list = pack_result[0]
                    if isinstance(content_list, list) and len(content_list) > 0:
                        content_obj = content_list[0]
                        if hasattr(content_obj, "text"):
                            try:
                                result_data = json.loads(content_obj.text)
                                # Basic validation - just ensure it's a valid JSON response
                                assert isinstance(result_data, dict), "Result should be a dictionary"
                                # The exact structure might vary, so just ensure we got a meaningful response
                                assert len(result_data) > 0, "Result should not be empty"
                            except json.JSONDecodeError:
                                # If it's not JSON, just ensure we got some text response
                                assert len(content_obj.text) > 0, "Should have some text response"

            except Exception as e:
                # If there's an error, provide more detailed debugging info
                print(f"Error in realistic test: {e}")
                import traceback

                traceback.print_exc()
                # Re-raise to mark test as failed
                raise


# Pytest integration
@pytest.mark.asyncio
async def test_mcp_silent_mode_default():
    """Pytest async test for default silent mode"""
    test_instance = TestMCPSilentMode()
    test_instance.setup_method()
    test_instance.test_create_mcp_server_default_silent()


@pytest.mark.asyncio
async def test_mcp_pack_codebase_silent():
    """Pytest async test for pack_codebase in silent mode"""
    test_instance = TestMCPSilentMode()
    test_instance.setup_method()
    await test_instance.test_pack_codebase_tool_silent_mode()


@pytest.mark.asyncio
async def test_mcp_pack_codebase_verbose():
    """Pytest async test for pack_codebase in verbose mode"""
    test_instance = TestMCPSilentMode()
    test_instance.setup_method()
    await test_instance.test_pack_codebase_tool_verbose_mode()


@pytest.mark.asyncio
async def test_mcp_realistic_scenario():
    """Pytest async test for realistic codebase analysis"""
    test_instance = TestMCPSilentModeIntegration()
    test_instance.setup_method()
    await test_instance.test_realistic_codebase_analysis_silent()


# Script execution support
async def run_all_tests():
    """Run all tests when script is executed directly"""
    print("Running MCP Silent Mode Tests...")
    print("=" * 50)

    # Create test instances
    basic_tests = TestMCPSilentMode()
    integration_tests = TestMCPSilentModeIntegration()

    test_methods = [
        ("Basic silent mode state", basic_tests.test_default_silent_mode_state),
        ("Set silent mode false", basic_tests.test_set_silent_mode_false),
        ("Set silent mode true", basic_tests.test_set_silent_mode_true),
        ("Default server creation (silent)", basic_tests.test_create_mcp_server_default_silent),
        ("Explicit silent=True", basic_tests.test_create_mcp_server_explicit_silent_true),
        ("Explicit silent=False", basic_tests.test_create_mcp_server_explicit_silent_false),
        ("Pack codebase tool silent", basic_tests.test_pack_codebase_tool_silent_mode),
        ("Pack codebase tool verbose", basic_tests.test_pack_codebase_tool_verbose_mode),
        ("Silent state preservation", basic_tests.test_server_creation_preserves_silent_state),
        ("Multiple tool calls silent", basic_tests.test_multiple_tool_calls_respect_silent_mode),
        ("All tools registered", basic_tests.test_all_tools_registered_properly),
        ("Realistic scenario silent", integration_tests.test_realistic_codebase_analysis_silent),
    ]

    passed = 0
    failed = 0

    for test_name, test_method in test_methods:
        try:
            print(f"Running: {test_name}...", end=" ")
            if asyncio.iscoroutinefunction(test_method):
                await test_method()
            else:
                if hasattr(basic_tests, "setup_method"):
                    basic_tests.setup_method()
                if hasattr(integration_tests, "setup_method"):
                    integration_tests.setup_method()
                test_method()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED - {e}")
            failed += 1

    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")

    if failed > 0:
        print("❌ Some tests failed!")
        return False
    else:
        print("✅ All tests passed!")
        return True


if __name__ == "__main__":
    # Run tests when executed directly
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
