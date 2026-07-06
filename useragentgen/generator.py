import json
import random
from importlib.resources import files
from typing import Any, Dict, List, Optional

from . import parser

_DATA_PKG = "useragentgen.data"

# Module-level state
_rng = random.Random()
_data: Dict[str, Any] = {}
_configs: Dict[str, Any] = {}
_exclusions: Dict[str, List[str]] = {}
_engines: Dict[str, str] = {}
_mobile_tokens: Dict[str, str] = {}
_initialized = False


def _read_resource(filename: str) -> str:
    return files(_DATA_PKG).joinpath(filename).read_text(encoding="utf-8")


def _parse_single(filename: str) -> str:
    for raw in _read_resource(filename).splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            return parser.parse_line(line)
    return ""


def _parse_list(filename: str) -> List[str]:
    results = []
    for raw in _read_resource(filename).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        results.append(parser.parse_line(line))
    return results


def _parse_lookup(filename: str) -> Dict[str, str]:
    results = {}
    for raw in _read_resource(filename).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        results[key.strip()] = parser.parse_line(value.strip())
    return results


# OS detection helpers (same as before)
def _is_windows(s: str) -> bool:
    return s.startswith("Windows")


def _is_macos(s: str) -> bool:
    return s.startswith("Macintosh")


def _is_android(s: str) -> bool:
    return "Android" in s and "iPhone" not in s and "iPad" not in s


def _is_ios(s: str) -> bool:
    return "iPhone" in s or "iPad" in s


def _is_excluded(browser: str, os_str: str) -> bool:
    for pattern in _exclusions.get(browser, []):
        if pattern in os_str:
            return True
    return False


def _safari_suffix(os_str: str) -> str:
    if _is_ios(os_str):
        return _rng.choice(["Safari/604.1", "Safari/605.1.15"])
    return "Safari/605.1.15"


# Rule interpreters (same logic, using module _rng)
def _check_os(rule: Dict[str, Any], os_str: str) -> bool:
    if "os_allow" in rule:
        allowed = rule["os_allow"]
        if allowed == "*":
            return True
        return any(globals()[f"_is_{opt}"](os_str) for opt in allowed)
    if "os_exclude" in rule:
        excluded = rule["os_exclude"]
        return not any(globals()[f"_is_{opt}"](os_str) for opt in excluded)
    return True


def _check_version(rule: Dict[str, Any], version: str, os_str: str) -> bool:
    """Evaluate version_prefix rules, with optional OS conditions."""
    prefixes = rule["version_prefix"]
    if isinstance(prefixes, str):
        prefixes = [prefixes]

    for p in prefixes:
        if isinstance(p, str):
            # Simple string prefix
            if version.startswith(p):
                return True
        else:
            # Dict with OS conditions: {"prefix": "rv:", "os_exclude": ["android"]}
            if not version.startswith(p["prefix"]):
                continue

            # Check OS conditions if present
            excluded = p.get("os_exclude", [])
            if any(globals()[f"_is_{opt}"](os_str) for opt in excluded):
                continue
            allowed = p.get("os_allow", [])
            if allowed:  # Only check if explicitly defined
                if not any(globals()[f"_is_{opt}"](os_str) for opt in allowed):
                    continue
                return True
            else:
                return True  # No restrictions means it's allowed
    return False


def _get_mobile_token(rule: Dict[str, Any], os_str: str) -> Optional[str]:
    mobile_cfg = rule.get("mobile_token")
    if not mobile_cfg:
        return None
    condition = mobile_cfg["if"]
    if globals()[f"_is_{condition}"](os_str):
        token_name = mobile_cfg["value"]
        return _mobile_tokens.get(token_name, token_name)
    return None


def _get_suffix(rule: Dict[str, Any], version: str, os_str: str) -> Optional[str]:
    suffix_rule = rule.get("suffix")
    if suffix_rule is None:
        return None
    if isinstance(suffix_rule, str):
        return suffix_rule
    if "method" in suffix_rule:
        return globals()[suffix_rule["method"]](os_str)
    if "template" in suffix_rule:
        template = suffix_rule["template"]
        result = template
        for key, val in suffix_rule.items():
            if key == "template":
                continue
            if isinstance(val, list) and len(val) == 2:
                result = result.replace(f"{{{key}}}", str(_rng.randint(val[0], val[1])))
        return result
    return None


def init(seed: Optional[int] = None) -> None:
    """Initialize or reinitialize the generator with an optional seed."""
    global _initialized, _rng, _data, _configs, _exclusions, _engines, _mobile_tokens

    _rng = random.Random(seed)
    parser.init_parser(seed)  # Sync parser RNG

    # Core data
    _data = {
        "prefix": _parse_single("prefix.txt"),
        "os_list": _parse_list("os.txt"),
        "versions": _parse_list("version.txt"),
    }

    # Browser configs from JSON
    _configs = json.loads(_read_resource("configs.json"))

    # Engine and mobile token lookups
    _engines = _parse_lookup("engine.txt")
    _mobile_tokens = _parse_lookup("mobile_token.txt")

    # Exclusion rules
    browsers = ("chrome", "firefox", "safari", "edge", "opera")
    _exclusions = {b: [] for b in browsers}
    try:
        content = _read_resource("exclusions.txt")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            browser, pattern = line.split(":", 1)
            browser = browser.strip().lower()
            if browser in _exclusions:
                _exclusions[browser].append(pattern.strip())
    except FileNotFoundError:
        pass

    _initialized = True


def _ensure_init() -> None:
    if not _initialized:
        init()


def generate(browser: Optional[str] = None) -> str:
    """Generate a single User-Agent string."""
    _ensure_init()

    browsers = ("chrome", "firefox", "safari", "edge", "opera")
    if browser is None:
        browser = _rng.choice(browsers)
    else:
        browser = browser.lower()

    cfg = _configs.get(browser)
    if not cfg:
        raise ValueError(f"Unknown browser: {browser!r}. Choose from: {browsers}")

    valid_os = [
        os_str
        for os_str in _data["os_list"]
        if _check_os(cfg, os_str) and not _is_excluded(browser, os_str)
    ]
    if not valid_os:
        raise ValueError(f"No valid OS found for browser: {browser!r}")
    os_str = _rng.choice(valid_os)



    # In generate() function, after selecting OS:
    if browser == "firefox":
        # Firefox needs both rv: (in parens) and Firefox/ (after engine)
        version_num = _rng.randint(115, 135)
        rv_version = f"rv:{version_num}.0"
        fx_version = f"Firefox/{version_num}.0"
        
        # Insert rv: into OS parentheses
        os_str = os_str.rstrip(')') + f"; {rv_version})"
        engine = _engines.get(cfg["engine"], cfg["engine"])
        parts = [_data["prefix"], f"({os_str}", engine, fx_version]
    else:
        # valid_versions = [v for v in _data["versions"] if _check_version(cfg, v)]
        valid_versions = [v for v in _data["versions"] if _check_version(cfg, v, os_str)]

        if not valid_versions:
            raise ValueError(f"No valid version tokens found for browser: {browser!r}")
        version = _rng.choice(valid_versions)

        parts = [_data["prefix"], f"({os_str})"]

        if cfg.get("engine"):
            engine = _engines.get(cfg["engine"], cfg["engine"])
            parts.append(engine)

        mobile = _get_mobile_token(cfg, os_str)
        if mobile:
            parts.append(mobile)

        parts.append(version)

        suffix = _get_suffix(cfg, version, os_str)
        if suffix:
            parts.append(suffix)

    return " ".join(parts)


def generate_many(count: int = 10, browser: Optional[str] = None) -> List[str]:
    """Generate multiple User-Agent strings."""
    return [generate(browser) for _ in range(count)]
