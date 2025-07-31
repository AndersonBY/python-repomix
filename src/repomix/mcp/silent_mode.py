"""MCP silent mode context management."""

# Global MCP silent mode flag - used by tools to determine if they should log
_mcp_silent_mode = True

def set_mcp_silent_mode(silent: bool) -> None:
    """Set the global MCP silent mode flag."""
    global _mcp_silent_mode
    _mcp_silent_mode = silent

def is_mcp_silent_mode() -> bool:
    """Check if MCP is in silent mode."""
    global _mcp_silent_mode
    return _mcp_silent_mode