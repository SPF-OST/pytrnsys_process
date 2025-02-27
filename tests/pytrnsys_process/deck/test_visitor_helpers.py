import lark as _lark
import pytest as _pytest

from pytrnsys_process.deck import visitor_helpers


class TestVisitorHelpers:
    @_pytest.fixture
    def sample_tree(self):
        return _lark.Tree(
            "root",
            [
                _lark.Token("INT", "42"),
                _lark.Token("STRING", "hello"),
                _lark.Token("INT", "123"),
                _lark.Tree("subtree", [_lark.Token("FLOAT", "3.14")]),
            ],
        )

    def test_get_child_token_value(self):
        tree = _lark.Tree("root", [_lark.Token("INT", "42")])
        assert visitor_helpers.get_child_token_value("INT", tree, int) == 42

        # Test error case when token doesn't exist
        with _pytest.raises(
            ValueError, match="doesn't contain a direct child token"
        ):
            visitor_helpers.get_child_token_value("FLOAT", tree, float)

    def test_get_child_token_value_or_none(self):
        tree = _lark.Tree("root", [_lark.Token("INT", "42")])

        # Test successful conversion
        assert (
            visitor_helpers.get_child_token_value_or_none("INT", tree, int)
            == 42
        )

        # Test when token doesn't exist
        assert (
            visitor_helpers.get_child_token_value_or_none("MISSING", tree, str)
            is None
        )

    def test_get_child_token_or_none(self, sample_tree):
        # Test finding existing token
        token = visitor_helpers.get_child_token_or_none("STRING", sample_tree)
        assert token.value == "hello"

        # Test when token doesn't exist
        assert (
            visitor_helpers.get_child_token_or_none("MISSING", sample_tree)
            is None
        )

        # Test error case with multiple tokens
        with _pytest.raises(ValueError, match="More than one token"):
            visitor_helpers.get_child_token_or_none("INT", sample_tree)

    def test_get_child_token_values(self, sample_tree):
        # Test getting multiple values
        assert visitor_helpers.get_child_token_values_or_empty_sequence(
            "INT", sample_tree
        ) == [
            "42",
            "123",
        ]

        # Test empty case
        assert (
            visitor_helpers.get_child_token_values_or_empty_sequence(
                "MISSING", sample_tree
            )
            == []
        )

    def test_get_child_token(self, sample_tree):
        # Test getting single token
        token = visitor_helpers.get_child_token("STRING", sample_tree)
        assert token.value == "hello"

        # Test error case when direct token doesn't exist
        with _pytest.raises(
            ValueError, match="doesn't contain a direct child token"
        ):
            visitor_helpers.get_child_token("MISSING", sample_tree)

    def test_get_child_tokens(self, sample_tree):
        # Test getting multiple tokens
        tokens = visitor_helpers.get_child_tokens_or_empty_sequence(
            "INT", sample_tree
        )
        assert len(tokens) == 2
        assert [t.value for t in tokens] == ["42", "123"]

        # Test empty case
        assert (
            visitor_helpers.get_child_tokens_or_empty_sequence(
                "MISSING", sample_tree
            )
            == []
        )
