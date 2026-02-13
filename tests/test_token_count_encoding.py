"""
Test suite for --token-count-encoding CLI flag (Issue #14)
"""


from src.repomix.cli.cli_run import create_parser
from src.repomix.config.config_schema import RepomixConfig, RepomixConfigTokenCount


class TestTokenCountEncoding:
    """Test cases for --token-count-encoding CLI flag"""

    def test_parser_token_count_encoding_flag(self):
        """Test parser recognizes --token-count-encoding flag"""
        parser = create_parser()
        args = parser.parse_args(["--token-count-encoding", "cl100k_base"])
        assert args.token_count_encoding == "cl100k_base"

    def test_parser_token_count_encoding_default_none(self):
        """Test --token-count-encoding defaults to None in CLI"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.token_count_encoding is None

    def test_config_token_count_default_encoding(self):
        """Test default encoding is o200k_base"""
        config = RepomixConfig()
        assert config.token_count.encoding == "o200k_base"

    def test_config_token_count_custom_encoding(self):
        """Test custom encoding in config"""
        config = RepomixConfig(token_count={"encoding": "cl100k_base"})
        assert config.token_count.encoding == "cl100k_base"

    def test_config_token_count_dataclass(self):
        """Test RepomixConfigTokenCount dataclass"""
        tc = RepomixConfigTokenCount()
        assert tc.encoding == "o200k_base"

        tc2 = RepomixConfigTokenCount(encoding="cl100k_base")
        assert tc2.encoding == "cl100k_base"

    def test_config_token_count_from_dict(self):
        """Test token_count config from dict (as loaded from JSON)"""
        config = RepomixConfig(token_count={"encoding": "p50k_base"})
        assert isinstance(config.token_count, RepomixConfigTokenCount)
        assert config.token_count.encoding == "p50k_base"
