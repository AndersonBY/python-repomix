#!/usr/bin/env python3
"""
🚀 Repomix Release Wizard - 交互式发布向导

这个脚本会一步步引导您完成发布流程，无需记住任何命令！
"""

import subprocess
from pathlib import Path
from typing import List, Tuple


# 颜色和格式化
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_step(step: int, total: int, title: str):
    """打印步骤标题"""
    print(f"{Colors.OKBLUE}{Colors.BOLD}📍 步骤 {step}/{total}: {title}{Colors.ENDC}")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def ask_yes_no(question: str, default: bool = True) -> bool:
    """询问是否问题"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{Colors.BOLD}❓ {question} ({default_str}): {Colors.ENDC}").strip().lower()
        if not response:
            return default
        if response in ["y", "yes", "是", "好"]:
            return True
        if response in ["n", "no", "否", "不"]:
            return False
        print_warning("请输入 y/yes/是 或 n/no/否")


def ask_choice(question: str, choices: List[str], default: int = 0) -> int:
    """询问选择问题"""
    print(f"{Colors.BOLD}❓ {question}{Colors.ENDC}")
    for i, choice in enumerate(choices):
        marker = "👉" if i == default else "  "
        print(f"{marker} {i + 1}. {choice}")

    while True:
        response = input(f"请选择 (1-{len(choices)}, 默认 {default + 1}): ").strip()
        if not response:
            return default
        try:
            choice = int(response) - 1
            if 0 <= choice < len(choices):
                return choice
            print_warning(f"请输入 1-{len(choices)} 之间的数字")
        except ValueError:
            print_warning("请输入有效数字")


def ask_string(question: str, default: str = "") -> str:
    """询问字符串问题"""
    prompt = f"{Colors.BOLD}❓ {question}"
    if default:
        prompt += f" (默认: {default})"
    prompt += f": {Colors.ENDC}"

    response = input(prompt).strip()
    return response if response else default


def run_command(cmd: List[str], cwd: str | None = None) -> Tuple[bool, str]:
    """运行命令"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=cwd)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # 合并 stderr 和 stdout，因为有些工具把错误信息输出到 stdout
        error_output = ""
        if e.stderr and e.stderr.strip():
            error_output += e.stderr.strip()
        if e.stdout and e.stdout.strip():
            if error_output:
                error_output += "\n" + e.stdout.strip()
            else:
                error_output = e.stdout.strip()
        return False, error_output


def wait_for_user(message: str = "按 Enter 继续..."):
    """等待用户输入"""
    input(f"⏸️  {message}")


def cleanup_test_files():
    """清理测试生成的临时文件"""
    import os

    temp_files = ["repomix-output.md", "repomix-output.txt", "repomix-output.xml"]

    for file_name in temp_files:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print_info(f"清理临时文件: {file_name}")
            except Exception as e:
                print_warning(f"无法删除临时文件 {file_name}: {e}")


def check_prerequisites() -> bool:
    """检查前置条件"""
    print_step(1, 8, "检查环境")

    # 检查是否在 git 仓库中
    success, _ = run_command(["git", "rev-parse", "--git-dir"])
    if not success:
        print_error("当前目录不是 Git 仓库")
        return False

    # 检查工作目录是否干净
    success, output = run_command(["git", "status", "--porcelain"])
    if success and output.strip():
        print_warning("Git 工作目录不干净，有未提交的更改:")
        print(output)
        if not ask_yes_no("是否继续? (建议先提交或储藏更改)", False):
            return False

    # 检查是否在主分支
    success, branch = run_command(["git", "branch", "--show-current"])
    if success and branch != "main":
        print_warning(f"当前分支是 '{branch}'，不是 'main'")
        if not ask_yes_no("是否继续?", False):
            return False

    # 检查必要文件
    required_files = ["pyproject.toml", "src/repomix/__init__.py"]
    for file in required_files:
        if not Path(file).exists():
            print_error(f"找不到必要文件: {file}")
            return False

    print_success("环境检查通过!")
    return True


def collect_commits() -> str | None:
    """收集提交信息"""
    print_step(2, 8, "收集提交信息")

    # 获取最新标签
    success, latest_tag = run_command(["git", "describe", "--tags", "--abbrev=0"])
    if success:
        print_info(f"发现最新标签: {latest_tag}")
        use_tag = ask_yes_no(f"从标签 {latest_tag} 开始收集提交?", True)
    else:
        print_info("没有找到任何标签")
        use_tag = False
        latest_tag = None

    # 询问收集方式
    if use_tag:
        choices = [f"收集自 {latest_tag} 以来的所有提交", "收集最近的 10 次提交", "收集最近的 20 次提交", "自定义提交数量"]
    else:
        choices = ["收集所有提交", "收集最近的 10 次提交", "收集最近的 20 次提交", "自定义提交数量"]

    choice = ask_choice("选择收集方式:", choices)

    # 构建命令
    cmd = ["python", "scripts/collect-commits.py"]

    if choice == 0:  # 所有提交或自标签以来
        if use_tag:
            cmd.extend(["--since-tag", latest_tag])
        else:
            cmd.append("--all")
    elif choice == 1:  # 最近 10 次
        cmd.extend(["--count", "10"])
        if use_tag:
            cmd.extend(["--since-tag", latest_tag])
    elif choice == 2:  # 最近 20 次
        cmd.extend(["--count", "20"])
        if use_tag:
            cmd.extend(["--since-tag", latest_tag])
    else:  # 自定义数量
        count = ask_string("请输入提交数量", "15")
        cmd.extend(["--count", count])
        if use_tag:
            cmd.extend(["--since-tag", latest_tag])

    # 运行收集脚本
    print_info("正在收集提交信息...")
    success, output = run_command(cmd)

    if success:
        print_success("提交信息收集完成!")
        print(output)
        return "commits-for-changelog.md"
    else:
        print_error(f"收集提交信息失败: {output}")
        return None


def generate_changelog(commits_file: str) -> bool:
    """生成 CHANGELOG"""
    print_step(3, 8, "生成 CHANGELOG 内容")

    print_info("现在需要使用 Claude Code 来生成 CHANGELOG 内容")
    print_info(f"已生成提交摘要文件: {commits_file}")

    print(f"\n{Colors.BOLD}请按照以下步骤操作:{Colors.ENDC}")
    print("1. 在新的终端窗口中运行:")
    print(f"{Colors.OKCYAN}claude{Colors.ENDC}")

    print("\n2. 然后在 Claude Code 交互模式中输入:")
    simple_prompt = f"请查看 {commits_file} 并将这些提交转换为专业的 CHANGELOG.md 条目，突出用户价值，使用 Keep a Changelog 格式，然后将生成的内容写入到 CHANGELOG.md 文件中"
    print(f"{Colors.OKCYAN}{simple_prompt}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}或者使用一次性命令:{Colors.ENDC}")
    detailed_prompt = """请查看 commits-for-changelog.md 并将这些 git 提交转换为专业的 CHANGELOG.md 条目：

1. 使用 Keep a Changelog 格式 (## [版本] - 日期)
2. 按以下类别组织: Added, Changed, Fixed, Security, Performance
3. 重点突出用户价值，而不是技术实现细节
4. 合并相关的提交为单个条目
5. 忽略纯内部的重构、格式化和构建变更
6. 为重要功能添加简短的价值说明

输出格式示例:
## [0.3.1] - 2024-12-25

### Added
- 🐳 Docker support for easy deployment and consistent environments
- 📊 Enhanced CI/CD pipeline with multi-Python version testing

### Fixed
- 🐛 Line numbering now works correctly with --output-show-line-numbers
- 🔧 Resolved Docker build issues on ARM platforms

请生成对应的 CHANGELOG 条目，并将生成的内容添加到 CHANGELOG.md 文件的 [Unreleased] 部分下方。"""

    print(f'{Colors.OKCYAN}claude "{detailed_prompt}"{Colors.ENDC}')

    wait_for_user("运行完 Claude Code 命令后按 Enter 继续...")

    return ask_yes_no("Claude Code 是否成功生成了 CHANGELOG 内容?", True)


def edit_changelog() -> bool:
    """编辑 CHANGELOG"""
    print_step(4, 8, "编辑 CHANGELOG.md")

    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print_warning("CHANGELOG.md 文件不存在")
        if ask_yes_no("是否创建新的 CHANGELOG.md 文件?", True):
            # 创建基本的 CHANGELOG 模板
            template = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 新功能在这里添加

### Changed
- 功能变更在这里添加

### Fixed
- 问题修复在这里添加

"""
            changelog_path.write_text(template, encoding="utf-8")
            print_success("已创建 CHANGELOG.md 模板")

    print_info("现在您需要编辑 CHANGELOG.md 文件")
    print_info("请根据 Claude Code 生成的内容更新 CHANGELOG.md")

    print(f"\n{Colors.BOLD}可以使用以下编辑器:{Colors.ENDC}")
    print("• vim CHANGELOG.md")
    print("• nano CHANGELOG.md")
    print("• code CHANGELOG.md  (VS Code)")
    print("• 或使用您喜欢的任何编辑器")

    wait_for_user("编辑完 CHANGELOG.md 后按 Enter 继续...")

    # 显示 Unreleased 部分的预览
    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8")

        # 提取 [Unreleased] 部分
        import re

        unreleased_match = re.search(r"## \[Unreleased\](.*?)(?=\n## \[|$)", content, re.DOTALL)

        if unreleased_match:
            unreleased_content = unreleased_match.group(1).strip()
            if unreleased_content:
                print(f"\n{Colors.BOLD}CHANGELOG.md 预览 - [Unreleased] 部分:{Colors.ENDC}")
                print(f"{Colors.OKCYAN}这是即将发布的内容:{Colors.ENDC}")
                print("-" * 50)
                print("## [Unreleased]")
                lines = unreleased_content.split("\n")
                # 限制显示行数，避免太长
                display_lines = lines[:15] if len(lines) > 15 else lines
                for line in display_lines:
                    print(line)
                if len(lines) > 15:
                    print("...")
                    print(f"{Colors.WARNING}(还有 {len(lines) - 15} 行内容){Colors.ENDC}")
                print("-" * 50)
            else:
                print_warning("CHANGELOG.md 中的 [Unreleased] 部分为空")
                print_info("请确保 Claude Code 已将内容添加到 [Unreleased] 部分")
        else:
            print_warning("CHANGELOG.md 中没有找到 [Unreleased] 部分")
            print_info("显示文件开头内容作为参考:")
            print("-" * 50)
            lines = content.split("\n")[:10]
            for line in lines:
                print(line)
            print("-" * 50)

    return ask_yes_no("CHANGELOG.md 编辑完成了吗?", True)


def determine_version() -> str | None:
    """确定版本号"""
    print_step(5, 8, "确定版本号")

    # 获取当前版本
    try:
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()
        import re

        match = re.search(r'version = "([^"]+)"', content)
        if match:
            current_version = match.group(1)
            print_info(f"当前版本: {current_version}")
        else:
            print_warning("无法从 pyproject.toml 获取当前版本")
            current_version = "0.0.0"
    except Exception as e:
        print_error(f"读取版本失败: {e}")
        current_version = "0.0.0"

    # 计算下一个版本号
    def get_next_version(current: str, bump_type: str) -> str:
        try:
            parts = current.split(".")
            if len(parts) != 3:
                return "1.0.0"

            major, minor, patch = map(int, parts)

            if bump_type == "patch":
                return f"{major}.{minor}.{patch + 1}"
            elif bump_type == "minor":
                return f"{major}.{minor + 1}.0"
            elif bump_type == "major":
                return f"{major + 1}.0.0"
            else:
                return current
        except Exception:
            return "1.0.0"

    # 预计算版本号
    next_patch = get_next_version(current_version, "patch")
    next_minor = get_next_version(current_version, "minor")
    next_major = get_next_version(current_version, "major")

    # 询问版本类型
    print_info("根据这次的更改，选择版本升级类型:")
    choices = [
        f"补丁版本 (Patch) - 主要是错误修复 ({current_version} → {next_patch})",
        f"次要版本 (Minor) - 新功能，向后兼容 ({current_version} → {next_minor})",
        f"主要版本 (Major) - 破坏性更改 ({current_version} → {next_major})",
        "手动指定版本号",
    ]

    choice = ask_choice("选择版本类型:", choices)

    if choice == 3:  # 手动指定
        while True:
            version = ask_string("请输入版本号 (例如: 1.2.3)")
            if re.match(r"^\d+\.\d+\.\d+$", version):
                return version
            print_warning("版本号格式无效，请使用 x.y.z 格式")
    else:
        version_types = ["patch", "minor", "major"]
        return version_types[choice]


def run_tests() -> bool:
    """运行测试"""
    print_step(6, 8, "运行测试和检查")

    if not ask_yes_no("是否运行测试和代码检查? (推荐)", True):
        print_warning("跳过测试检查")
        return True

    checks = [
        (["pdm", "run", "python", "-m", "pytest"], "运行测试"),
        (["pdm", "run", "ruff", "check", "."], "运行 Ruff 检查"),
        (["pdm", "run", "pyright"], "运行类型检查"),
    ]

    all_passed = True
    for cmd, description in checks:
        print_info(f"正在{description}...")
        success, output = run_command(cmd)

        if success:
            print_success(f"{description}通过")
            # 如果有输出内容且不是太长，可以显示简要信息
            if output.strip() and len(output) < 200:
                print(f"{Colors.OKCYAN}  {output.strip()}{Colors.ENDC}")
        else:
            print_error(f"{description}失败:")
            # 显示错误详情
            if output.strip():
                print(f"{Colors.FAIL}{'─' * 50}{Colors.ENDC}")
                # 限制错误输出长度，避免屏幕刷屏
                error_lines = output.strip().split("\n")
                if len(error_lines) > 20:
                    for line in error_lines[:15]:
                        print(f"{Colors.FAIL}{line}{Colors.ENDC}")
                    print(f"{Colors.WARNING}... (省略了 {len(error_lines) - 15} 行错误信息){Colors.ENDC}")
                    print(f"{Colors.WARNING}完整错误信息请查看上述命令的输出{Colors.ENDC}")
                else:
                    for line in error_lines:
                        print(f"{Colors.FAIL}{line}{Colors.ENDC}")
                print(f"{Colors.FAIL}{'─' * 50}{Colors.ENDC}")
            all_passed = False

            if not ask_yes_no(f"忽略{description}失败并继续?", False):
                return False

    if all_passed:
        print_success("所有检查都通过了!")

    # 清理测试生成的临时文件
    cleanup_test_files()

    return True


def commit_changelog() -> bool:
    """提交 CHANGELOG 更改"""
    print_step(7, 8, "提交 CHANGELOG 更改")

    # 检查是否有更改
    success, output = run_command(["git", "status", "--porcelain", "CHANGELOG.md"])
    if not success or not output.strip():
        print_info("CHANGELOG.md 没有更改")
        return True

    print_info("发现 CHANGELOG.md 有更改")
    if ask_yes_no("是否提交 CHANGELOG.md 的更改?", True):
        # 提交更改
        success, _ = run_command(["git", "add", "CHANGELOG.md"])
        if not success:
            print_error("添加 CHANGELOG.md 到暂存区失败")
            return False

        commit_msg = ask_string("提交信息", "docs: update changelog for release")
        success, output = run_command(["git", "commit", "-m", commit_msg])

        if success:
            print_success("CHANGELOG.md 已提交")
            return True
        else:
            print_error(f"提交失败: {output}")
            return False

    return True


def create_release(version_spec: str) -> bool:
    """创建发布"""
    print_step(8, 8, "创建发布")

    print_info(f"准备创建发布: {version_spec}")

    # 显示即将发布的内容预览
    changelog_path = Path("CHANGELOG.md")
    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8")
        import re

        unreleased_match = re.search(r"## \[Unreleased\](.*?)(?=\n## \[|$)", content, re.DOTALL)

        if unreleased_match:
            unreleased_content = unreleased_match.group(1).strip()
            if unreleased_content:
                print(f"\n{Colors.BOLD}📋 即将发布的内容预览:{Colors.ENDC}")
                print("-" * 40)
                lines = unreleased_content.split("\n")
                # 显示前10行作为预览
                preview_lines = lines[:10] if len(lines) > 10 else lines
                for line in preview_lines:
                    if line.strip():
                        print(f"{Colors.OKCYAN}{line}{Colors.ENDC}")
                if len(lines) > 10:
                    print(f"{Colors.WARNING}... (还有 {len(lines) - 10} 行){Colors.ENDC}")
                print("-" * 40)

    # 最终确认
    print(f"\n{Colors.BOLD}发布摘要:{Colors.ENDC}")
    print(f"• 版本规格: {version_spec}")
    print("• CHANGELOG.md 已更新")
    print("• 测试已通过 (或已跳过)")
    print("• 准备推送到 GitHub 并触发自动发布")

    if not ask_yes_no("确认创建发布?", True):
        print_warning("发布已取消")
        return False

    # 运行发布脚本
    if version_spec in ["patch", "minor", "major"]:
        cmd = ["python", "scripts/release.py", version_spec, "--yes"]
    else:
        cmd = ["python", "scripts/release.py", "patch", "--version", version_spec, "--yes"]

    print_info("正在创建发布...")
    success, output = run_command(cmd)

    if success:
        print_success("发布创建成功!")
        print(output)
        print_info("GitHub Actions 将自动构建并发布到 PyPI")
        print_info("请查看 GitHub 的 Actions 页面监控发布进度")
        return True
    else:
        print_error(f"发布创建失败: {output}")
        return False


def main():
    """主函数"""
    print_header("🚀 Repomix 发布向导")
    print_info("这个向导将引导您完成整个发布流程")
    print_info("每一步都会有详细说明，请按提示操作")

    if not ask_yes_no("是否开始发布流程?", True):
        print_info("发布已取消")
        return

    try:
        # 步骤 1: 检查前置条件
        if not check_prerequisites():
            print_error("前置条件检查失败，发布终止")
            return

        # 步骤 2: 收集提交信息
        commits_file = collect_commits()
        if not commits_file:
            print_error("收集提交信息失败，发布终止")
            return

        # 步骤 3: 生成 CHANGELOG
        if not generate_changelog(commits_file):
            print_error("生成 CHANGELOG 失败，发布终止")
            return

        # 步骤 4: 编辑 CHANGELOG
        if not edit_changelog():
            print_error("编辑 CHANGELOG 未完成，发布终止")
            return

        # 步骤 5: 确定版本号
        version_spec = determine_version()
        if not version_spec:
            print_error("版本号确定失败，发布终止")
            return

        # 步骤 6: 运行测试
        if not run_tests():
            print_error("测试失败，发布终止")
            return

        # 步骤 7: 提交 CHANGELOG
        if not commit_changelog():
            print_error("提交 CHANGELOG 失败，发布终止")
            return

        # 步骤 8: 创建发布
        if create_release(version_spec):
            print_header("🎉 发布完成!")
            print_success("恭喜！发布流程已成功完成")
            print_info("请检查:")
            print_info("• GitHub Actions 的运行状态")
            print_info("• PyPI 上的新版本")
            print_info("• GitHub Releases 页面")
        else:
            print_error("发布创建失败")

    except KeyboardInterrupt:
        print_error("\n发布流程被用户中断")
    except Exception as e:
        print_error(f"发布过程中出现意外错误: {e}")


if __name__ == "__main__":
    main()
