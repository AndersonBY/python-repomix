"""
Test script to verify config loading handles style attribute correctly
"""

import json

from src.repomix.config.config_schema import RepomixConfig, RepomixConfigOutput, RepomixOutputStyle

print("=== Test 1: Setting style through property ===")
# Create a test configuration object manually
test_output = RepomixConfigOutput()
# Set the style using property
test_output.style = "xml"
print(f"Output style set through property: {test_output.style}")
print(f"Internal _style value: {test_output._style}")
print(f"Is XML? {test_output.style == RepomixOutputStyle.XML}")

print("\n=== Test 2: Nested config initialization ===")
# Define output configuration as a dictionary
output_dict = {
    "file_path": "test-output.xml",
    "style": "xml",  # This will be handled by __post_init__
    "calculate_tokens": True,
}

# Create full config with nested output dictionary
full_config_dict = {"output": output_dict, "include": ["*"]}

# Initialize the complete config
full_config = RepomixConfig(**full_config_dict)

# Verify the config structure
print(f"Output type: {type(full_config.output)}")
print(f"Output style: {full_config.output.style}")
print(f"Internal _style value: {full_config.output._style}")
print(f"Is XML? {full_config.output.style == RepomixOutputStyle.XML}")
print(f"Calculate tokens: {full_config.output.calculate_tokens}")

print("\n=== Test 3: Simulate loading from JSON ===")
# Create a complete config similar to repomix.config.json
complete_config = {
    "output": {
        "file_path": "instructor-repo.xml",
        "style": "xml",
        "header_text": "",
        "instruction_file_path": "",
        "remove_comments": False,
        "remove_empty_lines": False,
        "top_files_length": 5,
        "show_line_numbers": False,
        "copy_to_clipboard": False,
        "include_empty_directories": False,
        "calculate_tokens": True,
    },
    "include": ["*"],
}
# Convert to JSON and back to simulate file loading
json_str = json.dumps(complete_config)
loaded_dict = json.loads(json_str)
loaded_config = RepomixConfig(**loaded_dict)

# Verify loaded configuration
print(f"Loaded output type: {type(loaded_config.output)}")
print(f"Loaded output style: {loaded_config.output.style}")
print(f"Loaded internal _style value: {loaded_config.output._style}")
print(f"Is XML? {loaded_config.output.style == RepomixOutputStyle.XML}")
print(f"Calculate tokens: {loaded_config.output.calculate_tokens}")
