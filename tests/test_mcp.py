"""Test MCP server functionality."""

import asyncio
import json
import tempfile
from pathlib import Path

from src.repomix.mcp.mcp_server import create_mcp_server

import pytest


@pytest.mark.asyncio
async def test_pack_codebase_tool():
    """Test the pack_codebase MCP tool."""
    print("Testing pack_codebase MCP tool...", flush=True)

    # Create a temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some test files
        (temp_path / "test.py").write_text('print("Hello, world!")\n')
        (temp_path / "README.md").write_text("# Test Project\n\nThis is a test.\n")
        (temp_path / "config.json").write_text('{"name": "test", "version": "1.0"}\n')

        # Create MCP server with explicit silent mode
        server = create_mcp_server(silent=True)

        # Test the pack_codebase tool
        try:
            print(f"Calling pack_codebase with directory: {temp_path}", flush=True)

            result = await server.call_tool(
                "pack_codebase",
                {"directory": str(temp_path), "top_files_length": 3, "compress": False},
            )

            print("Tool execution completed!", flush=True)

            # Handle tuple result format from FastMCP
            if isinstance(result, tuple) and len(result) > 0:
                content_list = result[0]  # First element of tuple
                if isinstance(content_list, list) and len(content_list) > 0:
                    content_obj = content_list[0]
                    if hasattr(content_obj, "text"):
                        text = content_obj.text
                        print("=== MCP Tool Response ===")

                        # Parse the JSON response
                        try:
                            response_data = json.loads(text)
                            print(f"Description: {response_data.get('description', 'N/A')}")
                            print(f"Output ID: {response_data.get('outputId', 'N/A')}")
                            print(f"Total Files: {response_data.get('totalFiles', 'N/A')}")
                            print(f"Total Tokens: {response_data.get('totalTokens', 'N/A')}")
                            print("=== Response JSON (first 300 chars) ===")
                            print(text[:300] + "..." if len(text) > 300 else text)
                        except json.JSONDecodeError:
                            print("Raw response (first 500 chars):")
                            print(text[:500] + "..." if len(text) > 500 else text)
                    else:
                        print(f"Content object: {content_obj}")
                else:
                    print(f"Content list: {content_list}")
            else:
                print(f"Unexpected result format: {result}")

        except Exception as e:
            print(f"Error calling tool: {e}", flush=True)


if __name__ == "__main__":
    asyncio.run(test_pack_codebase_tool())
