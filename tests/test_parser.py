import pytest

from useragentgen.parser import init_parser, parse_line


class TestParseLineChoice:
    def test_single_choice(self):
        result = parse_line("{a|b|c}")
        assert result in ["a", "b", "c"]

    def test_two_choices(self):
        result = parse_line("{x|y}")
        assert result in ["x", "y"]

    def test_choice_with_surrounding_text(self):
        result = parse_line("foo_{a|b}_bar")
        assert result in ["foo_a_bar", "foo_b_bar"]


class TestParseLineRange:
    def test_range_in_bounds(self):
        result = parse_line("{1-10}")
        assert result.isdigit()
        assert 1 <= int(result) <= 10

    def test_range_with_surrounding_text(self):
        result = parse_line("v{1-5}.0")
        parts = result.split(".")
        assert len(parts) == 2
        assert parts[1] == "0"
        num = int(parts[0].lstrip("v"))
        assert 1 <= num <= 5

    def test_range_inverted(self):
        with pytest.raises(ValueError):
            parse_line("{10-5}")


class TestParseLineMixed:
    def test_choice_and_range(self):
        result = parse_line("{a|b} {1-3}")
        parts = result.split(" ")
        assert len(parts) == 2
        assert parts[0] in ["a", "b"]
        assert parts[1].isdigit()
        assert 1 <= int(parts[1]) <= 3


class TestParseLinePassthrough:
    def test_no_patterns(self):
        assert parse_line("Mozilla/5.0") == "Mozilla/5.0"

    def test_empty_string(self):
        assert parse_line("") == ""

    def test_whitespace_only(self):
        assert parse_line("   ") == "   "


class TestParseLineMultiple:
    def test_multiple_choice_patterns(self):
        result = parse_line("{a|b} {x|y}")
        parts = result.split(" ")
        assert len(parts) == 2
        assert parts[0] in ["a", "b"]
        assert parts[1] in ["x", "y"]


class TestParserDeterministic:
    def test_same_seed_same_output(self):
        init_parser(42)
        first = parse_line("{a|b|c}")
        init_parser(42)
        second = parse_line("{a|b|c}")
        assert first == second

    def test_same_seed_same_range(self):
        init_parser(42)
        first = parse_line("{1-1000}")
        init_parser(42)
        second = parse_line("{1-1000}")
        assert first == second
