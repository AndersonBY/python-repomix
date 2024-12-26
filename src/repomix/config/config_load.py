"""
Configuration Loading Module - Responsible for Loading and Merging Configurations
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..shared.error_handle import RepomixError
from ..shared.logger import logger
from .config_schema import RepomixConfig, RepomixOutputStyle
from .global_directory import get_global_directory


def load_config(
    directory: str | Path,
    cwd: str | Path,
    config_path: Optional[str] = None,
    cli_options: Optional[Dict[str, Any]] = None,
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


def load_global_config() -> Optional[RepomixConfig]:
    """Load global configuration

    Returns:
        Global configuration object, or None if it does not exist
    """
    global_config_path = Path(get_global_directory()) / "repomix.config.json"

    if not global_config_path.exists():
        return None

    try:
        config_dict = json.loads(global_config_path.read_text())
        return RepomixConfig(**config_dict)
    except Exception as error:
        logger.warn(f"Failed to load global configuration: {error}")
        return None


def load_local_config(
    directory: str | Path, cwd: str | Path, config_path: Optional[str] = None
) -> Optional[RepomixConfig]:
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
        config_dict = json.loads(config_path_obj.read_text())
        return RepomixConfig(**config_dict)
    except json.JSONDecodeError:
        raise RepomixError(f"Invalid configuration file format: {config_path_obj}")
    except Exception as error:
        raise RepomixError(f"Failed to load configuration file: {error}")


def merge_configs(
    global_config: Optional[RepomixConfig], local_config: Optional[RepomixConfig], cli_options: Dict[str, Any]
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
            if cli_options.get("output", {}).get("style") == RepomixOutputStyle.MARKDOWN:
                cli_options["output"]["file_path"] = "repomix-output.md"
            elif cli_options.get("output", {}).get("style") == RepomixOutputStyle.XML:
                cli_options["output"]["file_path"] = "repomix-output.xml"
            elif cli_options.get("output", {}).get("style") == RepomixOutputStyle.PLAIN:
                cli_options["output"]["file_path"] = "repomix-output.txt"
        merge_config_dict(merged_config.__dict__, cli_options)

    return merged_config


def merge_config_dict(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Merge configuration dictionaries

    Args:
        target: Target dictionary
        source: Source dictionary
    """
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
