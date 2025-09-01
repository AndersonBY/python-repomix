"""
Initialization Action Module - Create new configuration file
"""

import json
from pathlib import Path

from ...config.config_schema import RepomixConfig
from ...config.global_directory import get_global_directory
from ...shared.error_handle import RepomixError
from ...shared.logger import logger


def run_init_action(cwd: str | Path, use_global: bool = False) -> None:
    """Execute initialization operation

    Args:
        cwd: Current working directory
        use_global: Whether to use global configuration

    Raises:
        RepomixError: When configuration file already exists or creation fails
    """
    if use_global:
        config_dir = Path(get_global_directory())
        config_path = config_dir / "repomix.config.json"
        config_type = "Global"
    else:
        config_dir = Path(cwd)
        config_path = config_dir / "repomix.config.json"
        config_type = "Local"

    # Check if configuration file already exists
    if config_path.exists():
        raise RepomixError(f"{config_type} configuration file already exists: {config_path}")

    # Create configuration directory (if it doesn't exist)
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create default configuration
    config = RepomixConfig()

    # Convert configuration to serializable dictionary
    # Get only public fields, excluding internal fields that start with underscore
    output_dict = {k: v for k, v in config.output.__dict__.items() if not k.startswith('_')}
    # Ensure style is exported as string value
    if hasattr(config.output, 'style_enum'):
        output_dict["style"] = config.output.style_enum.value

    config_dict = {
        "remote": config.remote.__dict__,
        "output": output_dict,
        "security": config.security.__dict__,
        "compression": config.compression.__dict__,
        "ignore": config.ignore.__dict__,
        "include": config.include,
    }

    # Write configuration to file
    try:
        with open(config_path, "w") as f:
            json.dump(config_dict, f, indent=2)
        logger.success(f"Created {config_type.lower()} configuration file: {config_path}")
    except Exception as error:
        raise RepomixError(f"Failed to create configuration file: {error}") from error
