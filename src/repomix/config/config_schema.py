"""
Configuration Module - Defines Repomix Configuration Schema and Default Values
"""

from enum import Enum
from typing import List
from dataclasses import dataclass, field


class RepomixOutputStyle(str, Enum):
    """Output style enumeration"""

    PLAIN = "plain"
    XML = "xml"
    MARKDOWN = "markdown"


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
    include_diffs: bool = False

    def __post_init__(self):
        """Convert string style to enum after initialization"""
        if isinstance(self.style, str):
            try:
                self._style = RepomixOutputStyle(self.style.lower())
            except ValueError:
                self._style = RepomixOutputStyle.MARKDOWN
        elif isinstance(self.style, RepomixOutputStyle):
            self._style = self.style
        else:
            self._style = RepomixOutputStyle.MARKDOWN

    def _process_style_value(self, value):
        """Process style value and set _style accordingly"""
        if isinstance(value, RepomixOutputStyle):
            self._style = value
        elif isinstance(value, str):
            try:
                self._style = RepomixOutputStyle(value.lower())
            except ValueError:
                raise ValueError(f"Invalid style value: {value}. Must be one of: {', '.join(s.value for s in RepomixOutputStyle)}") from None
        else:
            raise TypeError("Style must be either string or RepomixOutputStyle enum")

    @property
    def style_enum(self) -> RepomixOutputStyle:
        """Get the output style as enum"""
        return self._style

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

    output: RepomixConfigOutput = field(default_factory=RepomixConfigOutput)
    security: RepomixConfigSecurity = field(default_factory=RepomixConfigSecurity)
    ignore: RepomixConfigIgnore = field(default_factory=RepomixConfigIgnore)
    compression: RepomixConfigCompression = field(default_factory=RepomixConfigCompression)
    remote: RepomixConfigRemote = field(default_factory=RepomixConfigRemote)
    include: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing to handle nested dictionaries"""
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
