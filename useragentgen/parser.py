import re
import random
from typing import Optional

# Module-level RNG (can be seeded via init_parser)
_rng: random.Random = random.Random()

CHOICE_PATTERN = re.compile(r"\{([^}]+)\}")
RANGE_PATTERN = re.compile(r"^(\d+)-(\d+)$")


def init_parser(seed: Optional[int] = None) -> None:
    """Initialize or reseed the parser's RNG."""
    global _rng
    _rng = random.Random(seed)


def parse_line(line: str) -> str:
    """Expand all {a|b} and {1-10} patterns in a template string."""

    def replace_match(match: re.Match) -> str:
        content = match.group(1)
        range_match = RANGE_PATTERN.match(content)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            return str(_rng.randint(start, end))
        if "|" in content:
            return _rng.choice(content.split("|"))
        return content

    return CHOICE_PATTERN.sub(replace_match, line)
