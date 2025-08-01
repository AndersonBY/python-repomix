"""
Base64 Truncation Module - Handles truncation of base64 encoded data to reduce file size
"""

import re
from typing import Set

# Constants for base64 detection and truncation
MIN_BASE64_LENGTH_DATA_URI = 40
MIN_BASE64_LENGTH_STANDALONE = 60
TRUNCATION_LENGTH = 32
MIN_CHAR_DIVERSITY = 10
MIN_CHAR_TYPE_COUNT = 3


def truncate_base64_content(content: str) -> str:
    """Truncates base64 encoded data in content to reduce file size.

    Detects common base64 patterns like data URIs and standalone base64 strings.

    Args:
        content: The content to process

    Returns:
        Content with base64 data truncated
    """
    # Pattern to match data URIs (e.g., data:image/png;base64,...)
    data_uri_pattern = re.compile(
        rf"data:([a-zA-Z0-9/\-\+]+)(;[a-zA-Z0-9\-=]+)*;base64,([A-Za-z0-9+/]{{{MIN_BASE64_LENGTH_DATA_URI},}}=*)",
        re.MULTILINE,
    )

    # Pattern to match standalone base64 strings
    # This matches base64 strings that are likely encoded binary data
    standalone_base64_pattern = re.compile(rf"([A-Za-z0-9+/]{{{MIN_BASE64_LENGTH_STANDALONE},}}=*)", re.MULTILINE)

    processed_content = content

    # Replace data URIs
    def replace_data_uri(match):
        mime_type = match.group(1)
        params = match.group(2) or ""
        base64_data = match.group(3)
        preview = base64_data[:TRUNCATION_LENGTH]
        return f"data:{mime_type}{params};base64,{preview}..."

    processed_content = data_uri_pattern.sub(replace_data_uri, processed_content)

    # Replace standalone base64 strings
    def replace_standalone_base64(match):
        base64_string = match.group(1)
        # Check if this looks like actual base64 (not just a long string)
        if is_likely_base64(base64_string):
            preview = base64_string[:TRUNCATION_LENGTH]
            return f"{preview}..."
        return match.group(0)

    processed_content = standalone_base64_pattern.sub(replace_standalone_base64, processed_content)

    return processed_content


def is_likely_base64(s: str) -> bool:
    """Checks if a string is likely to be base64 encoded data.

    Args:
        s: The string to check

    Returns:
        True if the string appears to be base64 encoded
    """
    # Check for valid base64 characters only
    if not re.match(r"^[A-Za-z0-9+/]+=*$", s):
        return False

    # Check for reasonable distribution of characters (not all same char)
    char_set: Set[str] = set(s)
    if len(char_set) < MIN_CHAR_DIVERSITY:
        return False

    # Additional check: base64 encoded binary data typically has good character distribution
    # Must have at least MIN_CHAR_TYPE_COUNT of the 4 character types (numbers, uppercase, lowercase, special)
    has_numbers = bool(re.search(r"[0-9]", s))
    has_uppercase = bool(re.search(r"[A-Z]", s))
    has_lowercase = bool(re.search(r"[a-z]", s))
    has_special_chars = bool(re.search(r"[+/]", s))

    char_type_count = sum([has_numbers, has_uppercase, has_lowercase, has_special_chars])

    return char_type_count >= MIN_CHAR_TYPE_COUNT
