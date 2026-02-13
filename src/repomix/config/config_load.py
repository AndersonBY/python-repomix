"""
Configuration Loading Module - Responsible for Loading and Merging Configurations
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

from ..shared.error_handle import RepomixError
from ..shared.logger import logger
from .config_schema import RepomixConfig, RepomixOutputStyle
from .global_directory import get_global_directory


def migrate_config_format(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate old configuration format to new format

    This function handles backward compatibility by:
    - Converting '_style' to 'style' in output configuration
    - Removing deprecated internal fields like '_original_style' and '_style_enum'
    - Any other future migrations can be added here

    Args:
        config_dict: Configuration dictionary

    Returns:
        Migrated configuration dictionary
    """
    # Make a deep copy to avoid modifying the original
    import copy

    migrated_config = copy.deepcopy(config_dict)

    # Handle output._style -> output.style migration
    if "output" in migrated_config and isinstance(migrated_config["output"], dict):
        output_config = migrated_config["output"]

        # If we have _style but no style, migrate it
        if "_style" in output_config and "style" not in output_config:
            output_config["style"] = output_config["_style"]
            del output_config["_style"]
            logger.info("Migrated configuration: '_style' -> 'style'")
        # If we have both, remove the old _style
        elif "_style" in output_config and "style" in output_config:
            del output_config["_style"]
            logger.info("Removed deprecated '_style' parameter (using 'style' instead)")

        # Remove deprecated internal fields that should not be saved to configuration
        deprecated_fields = ["_original_style", "_style_enum"]
        for field in deprecated_fields:
            if field in output_config:
                del output_config[field]
                logger.info(f"Removed deprecated internal field '{field}' from configuration")

    return migrated_config


def load_config(
    directory: str | Path,
    cwd: str | Path,
    config_path: str | None = None,
    cli_options: Dict[str, Any] | None = None,
) -> RepomixConfig:
    """Load configuration

    Args:
        directory: Target directory
        cwd: Current working directory
        config_path: Custom configuration file path (optional)
        cli_options: Command line options (optional)

    Returns:
        Merged configuration object

    Raises:
        RepomixError: When configuration loading fails
    """
    # Load global configuration
    global_config = load_global_config()

    # Load local configuration
    local_config = load_local_config(directory, cwd, config_path)

    # Merge configurations
    merged_config = merge_configs(global_config, local_config, cli_options or {})

    # Validate and process configuration
    process_config(merged_config, directory)

    return merged_config


def load_global_config() -> RepomixConfig | None:
    """Load global configuration

    Returns:
        Global configuration object, or None if it does not exist
    """
    global_config_path = Path(get_global_directory()) / "repomix.config.json"

    if not global_config_path.exists():
        return None

    try:
        config_dict = json.loads(global_config_path.read_text(encoding="utf-8"))

        # Migrate old configuration format
        config_dict = migrate_config_format(config_dict)

        # Try to update the global config file if migration was needed
        try:
            updated_content = json.dumps(config_dict, indent=2, ensure_ascii=False)
            if updated_content != global_config_path.read_text(encoding="utf-8"):
                global_config_path.write_text(updated_content, encoding="utf-8")
                logger.info("Updated global configuration file to new format")
        except Exception as e:
            logger.warn(f"Failed to update global configuration file: {e}")

        return RepomixConfig(**config_dict)
    except Exception as error:
        logger.warn(f"Failed to load global configuration: {error}")
        return None


def load_local_config(directory: str | Path, cwd: str | Path, config_path: str | None = None) -> RepomixConfig | None:
    """Load local configuration

    Args:
        directory: Target directory
        cwd: Current working directory
        config_path: Custom configuration file path (optional)

    Returns:
        Local configuration object, or None if it does not exist

    Raises:
        RepomixError: When configuration file is invalid
    """
    if config_path:
        # Use custom configuration file path
        config_path_obj = Path(config_path)
        if not config_path_obj.is_absolute():
            config_path_obj = Path(cwd) / config_path
    elif (Path(cwd) / "repomix.config.json").exists():
        # Use default configuration file path
        config_path_obj = Path(cwd) / "repomix.config.json"
    elif (Path(directory) / "repomix.config.json").exists():
        config_path_obj = Path(directory) / "repomix.config.json"
    else:
        return None

    if not config_path_obj.exists():
        return None

    try:
        config_dict = json.loads(config_path_obj.read_text(encoding="utf-8"))

        # Migrate old configuration format
        config_dict = migrate_config_format(config_dict)

        return RepomixConfig(**config_dict)
    except json.JSONDecodeError as error:
        raise RepomixError(f"Invalid configuration file format: {config_path_obj}") from error
    except Exception as error:
        raise RepomixError(f"Failed to load configuration file: {error}") from error


def merge_configs(
    global_config: RepomixConfig | None,
    local_config: RepomixConfig | None,
    cli_options: Dict[str, Any],
) -> RepomixConfig:
    """Merge configurations

    Args:
        global_config: Global configuration object
        local_config: Local configuration object
        cli_options: Command line options

    Returns:
        Merged configuration object
    """
    # Create base configuration
    merged_config = RepomixConfig()

    # Merge configurations by priority: global config < local config < CLI options
    if global_config:
        merge_config_dict(merged_config.__dict__, global_config.__dict__)

    if local_config:
        merge_config_dict(merged_config.__dict__, local_config.__dict__)

    # Merge CLI options
    if cli_options:
        if cli_options.get("output", {}).get("file_path") is None:
            if cli_options.get("output", {}).get("style") == "markdown":
                cli_options["output"]["file_path"] = "repomix-output.md"
            elif cli_options.get("output", {}).get("style") == "xml":
                cli_options["output"]["file_path"] = "repomix-output.xml"
            elif cli_options.get("output", {}).get("style") == "plain":
                cli_options["output"]["file_path"] = "repomix-output.txt"
            elif cli_options.get("output", {}).get("style") == "json":
                cli_options["output"]["file_path"] = "repomix-output.json"
        merge_config_dict(merged_config.__dict__, cli_options)

    return merged_config


def merge_config_dict(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Merge configuration dictionaries

    Args:
        target: Target dictionary
        source: Source dictionary
    """
    from .config_schema import RepomixConfigOutput

    for key, value in source.items():
        if value is not None:
            if isinstance(value, dict):
                if key in target:
                    # If target is a dictionary, merge recursively
                    if isinstance(target[key], dict):
                        merge_config_dict(target[key], value)
                    # If target is an object, merge into its __dict__
                    elif hasattr(target[key], "__dict__"):
                        merge_config_dict(target[key].__dict__, value)
                        # Special handling for RepomixConfigOutput to update _style when style changes
                        if isinstance(target[key], RepomixConfigOutput) and "style" in value:
                            target[key]._process_style_value(value["style"])
                    else:
                        target[key] = value
                else:
                    target[key] = value
            else:
                target[key] = value


def process_config(config: RepomixConfig, directory: str | Path) -> None:
    """Process and validate configuration

    Args:
        config: Configuration object
        directory: Target directory

    Raises:
        RepomixError: When configuration is invalid
    """
    # Process output file path
    if not config.output.file_path:
        # Set default file name based on output style
        if config.output.style == RepomixOutputStyle.MARKDOWN:
            ext = ".md"
        elif config.output.style == RepomixOutputStyle.XML:
            ext = ".xml"
        elif config.output.style == RepomixOutputStyle.JSON:
            ext = ".json"
        else:
            ext = ".txt"
        config.output.file_path = f"repomix-output{ext}"

    # Ensure output path is an absolute path
    output_path = Path(config.output.file_path)
    if not output_path.is_absolute():
        output_path = Path(directory) / config.output.file_path
    config.output.file_path = str(output_path)

    # Validate if output directory is writable
    output_dir = output_path.parent
    if not os.access(output_dir, os.W_OK):
        raise RepomixError(f"Output directory is not writable: {output_dir}")

    # Process include patterns
    if not config.include:
        config.include = ["*"]  # Default to include all files

    # Validate other configuration items
    if config.output.top_files_length < 1:
        raise RepomixError("top_files_length must be greater than 0")
