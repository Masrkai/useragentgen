"""
useragentgen
============
Random User-Agent string generator with embedded templates.

Quick start
-----------
>>> from useragentgen import generate, generate_many, init
>>> init(42)                    # optional seed for reproducibility
>>> generate()                  # random browser
>>> generate("firefox")         # specific browser
>>> generate_many(5)            # list of 5 random UAs
"""

from .generator import generate, generate_many, init
from .parser import init_parser, parse_line

__all__ = ["generate", "generate_many", "init", "parse_line", "init_parser"]