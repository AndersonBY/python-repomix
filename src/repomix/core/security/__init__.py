"""
安全模块 - 提供文件和内容的安全性检查功能
"""

from .security_check import SecurityChecker, SuspiciousFileResult, check_files

__all__ = ["SecurityChecker", "SuspiciousFileResult", "check_files"]
