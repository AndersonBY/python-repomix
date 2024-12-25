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
    style: RepomixOutputStyle = RepomixOutputStyle.MARKDOWN
    header_text: str = ""
    instruction_file_path: str = ""
    remove_comments: bool = False
    remove_empty_lines: bool = False
    top_files_length: int = 5
    show_line_numbers: bool = False
    copy_to_clipboard: bool = False
    include_empty_directories: bool = False


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


@dataclass
class RepomixConfigFile(RepomixConfig):
    """Configuration file configuration class"""

    pass


@dataclass
class RepomixConfigCli(RepomixConfig):
    """CLI configuration class"""

    pass


@dataclass
class RepomixConfigMerged(RepomixConfig):
    """Merged configuration class"""

    pass


# Default configuration
default_config = RepomixConfig()
