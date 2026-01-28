"""
Configuration Module - Defines Repomix Configuration Schema and Default Values
"""

from enum import Enum
from typing import List, Optional, Union
from dataclasses import dataclass, field


class RepomixOutputStyle(str, Enum):
    """Output style enumeration"""

    PLAIN = "plain"
    XML = "xml"
    MARKDOWN = "markdown"
    JSON = "json"


@dataclass
class RepomixConfigGit:
    """Git-related output configuration"""

    sort_by_changes: bool = True
    sort_by_changes_max_commits: int = 100
    include_diffs: bool = False
    include_logs: bool = False
    include_logs_count: int = 50


@dataclass
class RepomixConfigInput:
    """Input configuration"""

    max_file_size: int = 50 * 1024 * 1024  # Default: 50MB


@dataclass
class RepomixConfigOutput:
    """Output configuration"""

    file_path: str = "repomix-output.md"
    style: str = "markdown"  # Using string type for easier initialization, converted via property
    header_text: str = ""
    instruction_file_path: str = ""
    remove_comments: bool = False
    remove_empty_lines: bool = False
    top_files_length: int = 5
    show_line_numbers: bool = False
    copy_to_clipboard: bool = False
    include_empty_directories: bool = False
    calculate_tokens: bool = False
    show_file_stats: bool = False
    show_directory_structure: bool = True
    parsable_style: bool = False
    truncate_base64: bool = False
    stdout: bool = False
    # New configuration items from TypeScript version
    include_full_directory_structure: bool = False
    split_output: Optional[int] = None  # Max bytes per output file for splitting
    token_count_tree: Union[bool, int, str] = False  # Token count tree display
    compress: bool = False  # Enable code compression
    # Git configuration (nested)
    git: RepomixConfigGit = field(default_factory=RepomixConfigGit)
    # Legacy field for backward compatibility (deprecated, use git.include_diffs)
    include_diffs: bool = False

    def __post_init__(self):
        """Convert string style to enum after initialization"""
        # Store the original style value
        self._original_style = self.style

        if isinstance(self.style, str):
            try:
                self._style_enum = RepomixOutputStyle(self.style.lower())
            except ValueError:
                self._style_enum = RepomixOutputStyle.MARKDOWN
        elif isinstance(self.style, RepomixOutputStyle):
            self._style_enum = self.style
        else:
            self._style_enum = RepomixOutputStyle.MARKDOWN

        # Handle git config if it's a dictionary
        if isinstance(self.git, dict):
            self.git = RepomixConfigGit(**self.git)

        # Migrate legacy include_diffs to git.include_diffs
        if self.include_diffs and not self.git.include_diffs:
            self.git.include_diffs = True

    def _process_style_value(self, value):
        """Process style value and set _style accordingly"""
        if isinstance(value, RepomixOutputStyle):
            self._style_enum = value
            # Update the style field to match the enum value
            object.__setattr__(self, 'style', value.value)
        elif isinstance(value, str):
            try:
                self._style_enum = RepomixOutputStyle(value.lower())
                # Update the style field to match the enum value
                object.__setattr__(self, 'style', value.lower())
            except ValueError:
                raise ValueError(f"Invalid style value: {value}. Must be one of: {', '.join(s.value for s in RepomixOutputStyle)}") from None
        else:
            raise TypeError("Style must be either string or RepomixOutputStyle enum")

    def __setattr__(self, name, value):
        """Override setattr to validate style when it's set after initialization"""
        if name == 'style' and hasattr(self, '_style_enum'):
            # Only validate if we're setting style after initialization
            self._process_style_value(value)
        else:
            super().__setattr__(name, value)

    @property
    def style_enum(self) -> RepomixOutputStyle:
        """Get the output style as enum"""
        return self._style_enum if hasattr(self, '_style_enum') else RepomixOutputStyle.MARKDOWN

    @style_enum.setter
    def style_enum(self, value):
        """Set the output style, supports string or RepomixOutputStyle enum"""
        self._process_style_value(value)


@dataclass
class RepomixConfigSecurity:
    """Security configuration"""

    enable_security_check: bool = True
    exclude_suspicious_files: bool = True


@dataclass
class RepomixConfigIgnore:
    """Ignore configuration"""

    custom_patterns: List[str] = field(default_factory=list)
    use_gitignore: bool = True
    use_default_ignore: bool = True


@dataclass
class RepomixConfigCompression:
    """Compression configuration"""

    enabled: bool = False
    keep_signatures: bool = True
    keep_docstrings: bool = True
    keep_interfaces: bool = True


@dataclass
class RepomixConfigRemote:
    """Remote repository configuration"""

    url: str = ""
    branch: str = ""


@dataclass
class RepomixConfig:
    """Repomix main configuration class"""

    input: RepomixConfigInput = field(default_factory=RepomixConfigInput)
    output: RepomixConfigOutput = field(default_factory=RepomixConfigOutput)
    security: RepomixConfigSecurity = field(default_factory=RepomixConfigSecurity)
    ignore: RepomixConfigIgnore = field(default_factory=RepomixConfigIgnore)
    compression: RepomixConfigCompression = field(default_factory=RepomixConfigCompression)
    remote: RepomixConfigRemote = field(default_factory=RepomixConfigRemote)
    include: List[str] = field(default_factory=list)
    # Skill generation configuration (string for skill name, or bool to enable/disable)
    skill_generate: Union[str, bool] = False
    # Current working directory (set at runtime)
    cwd: str = "."

    def __post_init__(self):
        """Post-initialization processing to handle nested dictionaries"""
        # Handle input if it's a dictionary
        if isinstance(self.input, dict):
            self.input = RepomixConfigInput(**self.input)

        # Handle output if it's a dictionary
        if isinstance(self.output, dict):
            # Create output object with all parameters (including style)
            self.output = RepomixConfigOutput(**self.output)

        # Handle security if it's a dictionary
        if isinstance(self.security, dict):
            self.security = RepomixConfigSecurity(**self.security)

        # Handle ignore if it's a dictionary
        if isinstance(self.ignore, dict):
            self.ignore = RepomixConfigIgnore(**self.ignore)

        if isinstance(self.compression, dict):
            self.compression = RepomixConfigCompression(**self.compression)

        # Handle remote if it's a dictionary
        if isinstance(self.remote, dict):
            self.remote = RepomixConfigRemote(**self.remote)


# Default configuration
default_config = RepomixConfig()
