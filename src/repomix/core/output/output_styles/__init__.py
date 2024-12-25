"""
Output Style Factory Module - Responsible for Creating and Managing Different Output Styles
"""

from typing import Dict, Optional, Type

from .xml_style import XmlStyle
from .plain_style import PlainStyle
from .markdown_style import MarkdownStyle
from ..output_style_decorate import OutputStyle
from ....config.config_schema import RepomixConfig, RepomixOutputStyle

# Style mapping table
_style_map: Dict[RepomixOutputStyle, Type[OutputStyle]] = {
    RepomixOutputStyle.PLAIN: PlainStyle,
    RepomixOutputStyle.MARKDOWN: MarkdownStyle,
    RepomixOutputStyle.XML: XmlStyle,
}


def get_output_style(config: RepomixConfig) -> Optional[OutputStyle]:
    """Get an output style instance of the specified type

    Args:
        config: Repomix configuration

    Returns:
        Output style instance, or None if the style type is unknown
    """
    style_class = _style_map.get(config.output.style)
    return style_class(config) if style_class else None
