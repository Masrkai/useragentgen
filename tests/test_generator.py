import pytest

import useragentgen.generator as gen
from useragentgen import generate, generate_many, init
from useragentgen.generator import (
    _check_os,
    _check_version,
    _get_mobile_token,
    _get_suffix,
    _is_android,
    _is_excluded,
    _is_ios,
    _is_macos,
    _is_windows,
    _parse_lookup,
)


class TestIsWindows:
    def test_positive(self):
        assert _is_windows("Windows NT 10.0; Win64; x64")

    def test_negative(self):
        assert not _is_windows("Macintosh; Intel Mac OS X 10_15_7")
        assert not _is_windows("")


class TestIsMacos:
    def test_positive(self):
        assert _is_macos("Macintosh; Intel Mac OS X 10_15_7")

    def test_negative(self):
        assert not _is_macos("Windows NT 10.0; Win64; x64")
        assert not _is_macos("")


class TestIsAndroid:
    def test_positive(self):
        assert _is_android("Linux; Android 13; Pixel 7")

    def test_negative_iphone(self):
        assert not _is_android("iPhone; CPU iPhone OS 16_0 like Mac OS X")

    def test_negative_ipad(self):
        assert not _is_android("iPad; CPU OS 16_0 like Mac OS X")

    def test_empty(self):
        assert not _is_android("")


class TestIsIos:
    def test_iphone(self):
        assert _is_ios("iPhone; CPU iPhone OS 16_0 like Mac OS X")

    def test_ipad(self):
        assert _is_ios("iPad; CPU OS 16_0 like Mac OS X")

    def test_negative(self):
        assert not _is_ios("Windows NT 10.0; Win64; x64")

    def test_empty(self):
        assert not _is_ios("")


class TestIsExcluded:
    def test_excluded(self):
        init(0)
        assert _is_excluded("safari", "Windows NT 10.0; Win64; x64")

    def test_not_excluded(self):
        init(0)
        assert not _is_excluded("chrome", "Windows NT 10.0; Win64; x64")

    def test_browser_not_in_exclusions(self):
        init(0)
        assert not _is_excluded("nonexistent", "Windows NT 10.0")


class TestCheckOs:
    def test_allow_all(self):
        rule = {"os_allow": "*"}
        assert _check_os(rule, "Windows NT 10.0; Win64; x64")
        assert _check_os(rule, "Macintosh; Intel Mac OS X 10_15_7")

    def test_allow_list(self):
        rule = {"os_allow": ["macos", "ios"]}
        assert _check_os(rule, "Macintosh; Intel Mac OS X 10_15_7")
        assert _check_os(rule, "iPhone; CPU iPhone OS 16_0 like Mac OS X")
        assert not _check_os(rule, "Windows NT 10.0; Win64; x64")

    def test_exclude_list(self):
        rule = {"os_exclude": ["ios"]}
        assert not _check_os(rule, "iPhone; CPU iPhone OS 16_0 like Mac OS X")
        assert _check_os(rule, "Windows NT 10.0; Win64; x64")

    def test_no_rule(self):
        rule = {}
        assert _check_os(rule, "anything")


class TestCheckVersion:
    def test_simple_prefix_match(self):
        rule = {"version_prefix": "Chrome/"}
        assert _check_version(rule, "Chrome/120.0.0.0", "any")
        assert not _check_version(rule, "Firefox/120.0", "any")

    def test_list_of_prefixes(self):
        rule = {"version_prefix": ["Chrome/", "Edg/"]}
        assert _check_version(rule, "Chrome/120.0.0.0", "any")
        assert _check_version(rule, "Edg/120.0.0.0", "any")
        assert not _check_version(rule, "Firefox/120.0", "any")

    def test_conditional_prefix(self):
        rule = {
            "version_prefix": [
                {"prefix": "rv:", "os_exclude": ["android", "ios"]}
            ]
        }
        assert _check_version(rule, "rv:120.0", "Windows NT 10.0; Win64; x64")
        assert not _check_version(
            rule, "rv:120.0", "Linux; Android 13; Pixel 7"
        )

    def test_conditional_prefix_allow(self):
        rule = {"version_prefix": [{"prefix": "v", "os_allow": ["macos"]}]}
        assert _check_version(rule, "v2.0", "Macintosh; Intel Mac OS X 10_15_7")
        assert not _check_version(rule, "v2.0", "Windows NT 10.0; Win64; x64")


class TestGetSuffix:
    def test_string_suffix(self):
        rule = {"suffix": "Safari/537.36"}
        result = _get_suffix(rule, "Chrome/120.0.0.0", "any")
        assert result == "Safari/537.36"

    def test_template_suffix(self):
        rule = {"suffix": {"template": "Chrome/{rnd}.0.0.0", "rnd": [115, 134]}}
        result = _get_suffix(rule, "Edg/120.0.0.0", "any")
        assert result.startswith("Chrome/")
        assert result.endswith(".0.0.0")
        num = int(result.split("/")[1].split(".")[0])
        assert num >= 115
        assert num <= 134

    def test_method_suffix(self):
        rule = {"suffix": {"method": "_safari_suffix"}}
        result = _get_suffix(rule, "Version/16.0", "Macintosh; Intel Mac OS X 10_15_7")
        assert "Safari/" in result

    def test_none_suffix(self):
        rule = {"suffix": None}
        result = _get_suffix(rule, "any", "any")
        assert result is None

    def test_no_suffix_key(self):
        rule = {}
        result = _get_suffix(rule, "any", "any")
        assert result is None


class TestGetMobileToken:
    def test_no_mobile_token_rule(self):
        rule = {"mobile_token": None}
        result = _get_mobile_token(rule, "Linux; Android 13; Pixel 7")
        assert result is None

    def test_condition_met(self):
        init(0)
        rule = {"mobile_token": {"if": "android", "value": "android_chrome"}}
        result = _get_mobile_token(rule, "Linux; Android 13; Pixel 7")
        assert result == gen._mobile_tokens.get("android_chrome")

    def test_condition_not_met(self):
        init(0)
        rule = {"mobile_token": {"if": "android", "value": "android_chrome"}}
        result = _get_mobile_token(rule, "Windows NT 10.0; Win64; x64")
        assert result is None

    def test_no_mobile_token_key(self):
        rule = {}
        result = _get_mobile_token(rule, "any")
        assert result is None


class TestEngines:
    def test_loaded(self):
        init(0)
        assert "webkit_chrome" in gen._engines
        assert "webkit_safari" in gen._engines
        assert "gecko" in gen._engines
        assert "gecko_android" in gen._engines

    def test_values_not_empty(self):
        init(0)
        for key, value in gen._engines.items():
            assert isinstance(value, str)
            assert len(value) > 0, f"Engine {key} has empty value"


class TestMobileTokens:
    def test_loaded(self):
        init(0)
        assert "ios_safari" in gen._mobile_tokens
        assert "android_chrome" in gen._mobile_tokens
        assert "safari_604" in gen._mobile_tokens
        assert "safari_605" in gen._mobile_tokens
        assert "safari_537" in gen._mobile_tokens

    def test_values_not_empty(self):
        init(0)
        for key, value in gen._mobile_tokens.items():
            assert isinstance(value, str)
            assert len(value) > 0, f"Mobile token {key} has empty value"


class TestParseLookup:
    def test_basic_parse(self):
        result = _parse_lookup("engine.txt")
        assert "webkit_chrome" in result
        assert "gecko" in result

    def test_values_are_strings(self):
        result = _parse_lookup("engine.txt")
        for value in result.values():
            assert isinstance(value, str)


class TestGenerateReturnType:
    def test_returns_string(self):
        init(0)
        result = generate()
        assert isinstance(result, str)

    def test_auto_init(self):
        gen._initialized = False
        result = generate()
        assert isinstance(result, str)


class TestDeterministic:
    def test_same_seed_same_first(self):
        init(42)
        first = generate("chrome")
        init(42)
        second = generate("chrome")
        assert first == second

    def test_same_seed_same_sequence(self):
        init(42)
        first = [generate("chrome") for _ in range(5)]
        init(42)
        second = [generate("chrome") for _ in range(5)]
        assert first == second

    def test_different_seed_different_output(self):
        init(1)
        first = generate("chrome")
        init(2)
        second = generate("chrome")
        assert first != second


class TestReinit:
    def test_reinit_resets_state(self):
        init(42)
        first = generate("chrome")
        init(42)
        second = generate("chrome")
        assert first == second

    def test_reinit_different_seed_changes_output(self):
        init(1)
        first = generate("chrome")
        init(2)
        second = generate("chrome")
        assert first != second


class TestGenerateChrome:
    def test_format(self):
        init(0)
        ua = generate("chrome")
        assert ua.startswith("Mozilla/5.0")
        assert "Chrome/" in ua
        assert "Safari/537.36" in ua
        assert "Firefox/" not in ua
        assert "OPR/" not in ua

    def test_no_ios(self):
        init(0)
        for _ in range(20):
            ua = generate("chrome")
            assert "iPhone" not in ua
            assert "iPad" not in ua


class TestGenerateFirefox:
    def test_format(self):
        init(0)
        ua = generate("firefox")
        assert ua.startswith("Mozilla/5.0")
        assert "Firefox/" in ua
        assert "Gecko/" in ua
        assert "Chrome/" not in ua
        assert "Edg/" not in ua

    def test_rv_token(self):
        init(0)
        ua = generate("firefox")
        assert "rv:" in ua


class TestGenerateSafari:
    def test_format(self):
        init(0)
        ua = generate("safari")
        assert ua.startswith("Mozilla/5.0")
        assert "Version/" in ua
        assert "AppleWebKit/" in ua
        assert "Chrome/" not in ua
        assert "Firefox/" not in ua

    def test_only_macos_ios_windows(self):
        init(0)
        for _ in range(20):
            ua = generate("safari")
            is_macos = "Macintosh" in ua
            is_ios = "iPhone" in ua or "iPad" in ua
            is_windows = "Windows NT" in ua
            assert is_macos or is_ios or is_windows, f"Safari UA has unexpected OS: {ua}"


class TestGenerateEdge:
    def test_format(self):
        init(0)
        ua = generate("edge")
        assert ua.startswith("Mozilla/5.0")
        assert "Edg/" in ua
        assert "Edge/" not in ua
        assert "Firefox/" not in ua

    def test_no_ios(self):
        init(0)
        for _ in range(20):
            ua = generate("edge")
            assert "iPhone" not in ua
            assert "iPad" not in ua


class TestGenerateOpera:
    def test_format(self):
        init(0)
        ua = generate("opera")
        assert ua.startswith("Mozilla/5.0")
        assert "OPR/" in ua
        assert "Opera/" not in ua
        assert "Firefox/" not in ua

    def test_no_ios(self):
        init(0)
        for _ in range(20):
            ua = generate("opera")
            assert "iPhone" not in ua
            assert "iPad" not in ua


class TestGenerateBrowserCase:
    def test_uppercase(self):
        init(0)
        ua = generate("CHROME")
        assert "Chrome/" in ua

    def test_mixed_case(self):
        init(0)
        ua = generate("FiReFoX")
        assert "Firefox/" in ua


class TestGenerateInvalidBrowser:
    def test_invalid_browser(self):
        init(0)
        with pytest.raises(ValueError):
            generate("nonexistent")

    def test_empty_string_browser(self):
        init(0)
        with pytest.raises(ValueError):
            generate("")


class TestGenerateMany:
    def test_default_count(self):
        init(0)
        result = generate_many()
        assert len(result) == 10
        for ua in result:
            assert isinstance(ua, str)

    def test_custom_count(self):
        init(0)
        result = generate_many(3)
        assert len(result) == 3

    def test_zero_count(self):
        init(0)
        result = generate_many(0)
        assert result == []

    def test_negative_count(self):
        init(0)
        result = generate_many(-1)
        assert result == []

    def test_browser_filter(self):
        init(0)
        result = generate_many(5, "firefox")
        assert len(result) == 5
        for ua in result:
            assert "Firefox/" in ua


class TestDataIntegrityEngines:
    def test_all_engines_exist(self):
        init(0)
        for browser, cfg in gen._configs.items():
            engine_name = cfg.get("engine")
            if engine_name:
                assert engine_name in gen._engines, (
                    f"Browser '{browser}' references engine '{engine_name}' "
                    f"not found in engine.txt"
                )


class TestDataIntegrityMobileTokens:
    def test_all_mobile_tokens_exist(self):
        init(0)
        for browser, cfg in gen._configs.items():
            mobile_cfg = cfg.get("mobile_token")
            if mobile_cfg and mobile_cfg.get("value"):
                token_name = mobile_cfg["value"]
                assert token_name in gen._mobile_tokens, (
                    f"Browser '{browser}' references mobile_token '{token_name}' "
                    f"not found in mobile_token.txt"
                )


class TestSafariSuffix:
    def test_ios_suffix(self):
        init(0)
        for _ in range(10):
            ua = generate("safari")
            if "iPhone" in ua or "iPad" in ua:
                parts = ua.split()
                last_part = parts[-1]
                assert last_part in [
                    "Safari/604.1",
                    "Safari/605.1.15",
                ], f"iOS Safari suffix unexpected: {last_part}"
                return
        pytest.skip("No iOS Safari UA generated in 10 attempts")

    def test_desktop_suffix(self):
        init(0)
        for _ in range(50):
            ua = generate("safari")
            if "Macintosh" in ua or "Windows NT" in ua:
                parts = ua.split()
                last_part = parts[-1]
                assert (
                    last_part == "Safari/605.1.15"
                ), f"Desktop Safari suffix unexpected: {last_part}"
                return
        pytest.skip("No desktop Safari UA generated in 50 attempts")
