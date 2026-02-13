"""
Test suite for --remote-branch CLI flag (Issue #15)
"""

from src.repomix.cli.cli_run import create_parser


class TestRemoteBranchFlag:
    """Test cases for --remote-branch CLI flag"""

    def test_parser_remote_branch_flag(self):
        """Test parser recognizes --remote-branch flag"""
        parser = create_parser()
        args = parser.parse_args(["--remote-branch", "develop"])
        assert args.remote_branch == "develop"

    def test_parser_remote_branch_default_none(self):
        """Test --remote-branch defaults to None"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.remote_branch is None

    def test_parser_branch_still_works(self):
        """Test deprecated --branch flag still works"""
        parser = create_parser()
        args = parser.parse_args(["--branch", "main"])
        assert args.branch == "main"

    def test_parser_remote_branch_with_remote(self):
        """Test --remote-branch used with --remote"""
        parser = create_parser()
        args = parser.parse_args(["--remote", "user/repo", "--remote-branch", "v2.0"])
        assert args.remote == "user/repo"
        assert args.remote_branch == "v2.0"

    def test_parser_branch_backward_compat_with_remote(self):
        """Test deprecated --branch still works with --remote"""
        parser = create_parser()
        args = parser.parse_args(["--remote", "user/repo", "--branch", "v1.0"])
        assert args.remote == "user/repo"
        assert args.branch == "v1.0"

    def test_remote_branch_takes_priority_in_options(self):
        """Test --remote-branch takes priority over --branch in options override"""
        from src.repomix.cli.actions.default_action import _build_cli_options_override

        options = {"remote_branch": "new-branch", "branch": "old-branch"}
        override = _build_cli_options_override(options)
        assert override["remote"]["branch"] == "new-branch"

    def test_branch_fallback_in_options(self):
        """Test --branch is used as fallback when --remote-branch is not set"""
        from src.repomix.cli.actions.default_action import _build_cli_options_override

        options = {"remote_branch": None, "branch": "fallback-branch"}
        override = _build_cli_options_override(options)
        assert override["remote"]["branch"] == "fallback-branch"
