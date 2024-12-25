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
    config_dict = {
        "output": config.output.__dict__,
        "security": config.security.__dict__,
        "ignore": config.ignore.__dict__,
        "include": config.include,
    }

    # Write configuration to file
    try:
        with open(config_path, "w") as f:
            json.dump(config_dict, f, indent=2)
        logger.success(f"Created {config_type.lower()} configuration file: {config_path}")
    except Exception as error:
        raise RepomixError(f"Failed to create configuration file: {error}")
