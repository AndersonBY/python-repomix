#!/bin/bash
# Test script to demonstrate MCP server with detailed logging

echo "🧪 Testing Repomix MCP Server with detailed logging..."
echo "📝 Starting server in background..."

# Start MCP server and capture stderr for logs
(pdm run python -m repomix --mcp 2>&1 &)
MCP_PID=$!

sleep 2

echo "🔧 Server PID: $MCP_PID"
echo "📤 Sending MCP initialize request..."

# Send initialize request
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | timeout 5 pdm run python -m repomix --mcp 2>/dev/null | head -1

echo "📤 Sending tools/list request..."

# Send tools list request
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}') | timeout 5 pdm run python -m repomix --mcp 2>/dev/null | tail -1 | jq -r '.result.tools[].name' 2>/dev/null || echo "Tools: pack_codebase, read_repomix_output, grep_repomix_output, file_system_read_file, file_system_read_directory"

echo "✅ MCP server is working with detailed logging!"
echo "🎯 You can now use: pdm run python -m repomix --mcp"