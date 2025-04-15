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
    _style: RepomixOutputStyle = RepomixOutputStyle.MARKDOWN
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

    def _process_style_value(self, value):
        """Process style value and set _style accordingly"""
        if isinstance(value, RepomixOutputStyle):
            self._style = value
        elif isinstance(value, str):
            try:
                self._style = RepomixOutputStyle(value.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid style value: {value}. Must be one of: {', '.join(s.value for s in RepomixOutputStyle)}"
                )
        else:
            raise TypeError("Style must be either string or RepomixOutputStyle enum")

    @property
    def style(self) -> RepomixOutputStyle:
        """Get the output style"""
        return self._style

    @style.setter
    def style(self, value):
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
class RepomixConfig:
    """Repomix main configuration class"""

    output: RepomixConfigOutput = field(default_factory=RepomixConfigOutput)
    security: RepomixConfigSecurity = field(default_factory=RepomixConfigSecurity)
    ignore: RepomixConfigIgnore = field(default_factory=RepomixConfigIgnore)
    include: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing to handle nested dictionaries"""
        # Handle output if it's a dictionary
        if isinstance(self.output, dict):
            output_dict = self.output.copy()
            # Handle style attribute specifically
            style_value = output_dict.pop("style", None)
            # Create output object with remaining parameters
            self.output = RepomixConfigOutput(**output_dict)
            # Set style if it was provided
            if style_value is not None:
                self.output.style = style_value

        # Handle security if it's a dictionary
        if isinstance(self.security, dict):
            self.security = RepomixConfigSecurity(**self.security)

        # Handle ignore if it's a dictionary
        if isinstance(self.ignore, dict):
            self.ignore = RepomixConfigIgnore(**self.ignore)


# Default configuration
default_config = RepomixConfig()
