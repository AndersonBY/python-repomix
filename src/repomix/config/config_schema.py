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

    @property
    def style(self) -> RepomixOutputStyle:
        """Get the output style"""
        return self._style

    @style.setter
    def style(self, value):
        """Set the output style, supports string or RepomixOutputStyle enum"""
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


# Default configuration
default_config = RepomixConfig()
