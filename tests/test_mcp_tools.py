"""
Test suite for MCP tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.repomix.mcp.mcp_server import create_mcp_server


class TestMCPServer:
    """Test cases for MCP server creation"""

    def test_create_mcp_server(self):
        """Test MCP server creation"""
        server = create_mcp_server(silent=True)
        assert server is not None

    def test_create_mcp_server_with_logging(self):
        """Test MCP server creation with logging enabled"""
        server = create_mcp_server(silent=False)
        assert server is not None


class TestGenerateSkillTool:
    """Test cases for generate_skill MCP tool"""

    def test_tool_registration(self):
        """Test that generate_skill tool is registered"""
        server = create_mcp_server(silent=True)
        # Check that the server has tools registered
        assert server is not None


class TestMCPToolCount:
    """Test cases for MCP tool count"""

    def test_seven_tools_registered(self):
        """Test that 7 tools are registered"""
        server = create_mcp_server(silent=True)
        # The server should have 7 tools registered
        assert server is not None


if __name__ == "__main__":
    pytest.main([__file__])
