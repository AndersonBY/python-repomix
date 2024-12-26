"""
CLI Print Module - Responsible for Formatting and Displaying Command Line Output
"""

from pathlib import Path
from typing import Dict, List

from ..config.config_schema import RepomixConfig
from ..core.security.security_check import SuspiciousFileResult
from ..shared.logger import logger


def print_summary(
    total_files: int,
    total_characters: int,
    total_tokens: int,
    output_path: str,
    suspicious_files_results: List[SuspiciousFileResult],
    config: RepomixConfig,
) -> None:
    """Print summary information

    Args:
        total_files: Total number of files
        total_characters: Total character count
        total_tokens: Total token count
        output_path: Output file path
        suspicious_files_results: List of suspicious file results
        config: Configuration object
    """
    security_check_message = ""
    if config.security.enable_security_check:
        if suspicious_files_results:
            security_check_message = f"Detected {len(suspicious_files_results)} suspicious files and excluded"
        else:
            security_check_message = "✔ No suspicious files detected"
    else:
        security_check_message = "Security check disabled"

    logger.log("\n📊 Packaging Summary:")
    logger.log("────────────────")
    logger.log(f" Total Files: {total_files} files")
    logger.log(f" Total Characters: {total_characters} characters")
    logger.log(f" Total Tokens: {total_tokens} tokens")
    logger.log(f" Output to: {output_path}")
    logger.log(f" Security: {security_check_message}")


def print_security_check(
    root_dir: str | Path,
    suspicious_files_results: List[SuspiciousFileResult],
    config: RepomixConfig,
) -> None:
    """Print security check results

    Args:
        root_dir: Root directory
        suspicious_files_results: List of suspicious file results
        config: Configuration object
    """
    if not config.security.enable_security_check:
        return

    logger.log("\n🔎 Security Check:")
    logger.log("──────────────────")

    if not suspicious_files_results:
        logger.success("No suspicious files detected")
    else:
        logger.log(f"Detected {len(suspicious_files_results)} suspicious files and excluded from output:")
        for i, suspicious_files_result in enumerate(suspicious_files_results):
            try:
                # Try to get relative path, fall back to absolute path if on different drives
                file_path = Path(suspicious_files_result.file_path)
                root_path = Path(root_dir)
                try:
                    relative_file_path = file_path.relative_to(root_path)
                except ValueError:
                    relative_file_path = file_path

                logger.log(f"{i + 1}. {relative_file_path}")
                logger.log(f"   - {', '.join(suspicious_files_result.messages)}")
            except Exception as e:
                logger.error(f"Error getting relative path for {suspicious_files_result.file_path}: {e}")
                logger.log(f"{i + 1}. {suspicious_files_result.file_path}")
                logger.log(f"   - {', '.join(suspicious_files_result.messages)}")
        logger.log("\nThese files have been excluded from the output due to security reasons.")
        logger.log("Please check these files for sensitive information.")


def print_top_files(
    file_char_counts: Dict[str, int],
    file_token_counts: Dict[str, int],
    top_files_length: int,
) -> None:
    """Print list of largest files

    Args:
        file_char_counts: File character count statistics
        file_token_counts: File token count statistics
        top_files_length: Number of files to display
    """
    top_files_length_str_len = len(str(top_files_length))
    logger.log(f"\n📈 Top {top_files_length} files by character and token count:")
    logger.log("─────────────────────────────────────────────────" + "─" * top_files_length_str_len)

    top_files = sorted(file_char_counts.items(), key=lambda item: item[1], reverse=True)[:top_files_length]

    for i, (file_path, char_count) in enumerate(top_files):
        token_count = file_token_counts[file_path]
        index_string = f"{i + 1}.".ljust(3, " ")
        logger.log(f"{index_string} {file_path} ({char_count} characters, {token_count} tokens)")


def print_completion() -> None:
    """Print completion message"""
    logger.log("\n🎉 Done!")
    logger.log("Your code repository has been successfully packaged.")
