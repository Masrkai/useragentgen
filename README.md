# useragentgen

Random User-Agent string generator for Chrome, Firefox, Safari, Edge, and Opera.
All browser templates are **embedded inside the package** — no external files needed after install.

## Installation

```bash
pip install useragentgen
```

## Quick start

```python
import useragentgen

# Single UA, random browser
useragentgen.generate()

# Single UA, specific browser
useragentgen.generate("chrome")
useragentgen.generate("firefox")
useragentgen.generate("safari")
useragentgen.generate("edge")
useragentgen.generate("opera")

# Batch generation
useragentgen.generate_many(10)            # 10 random-browser UAs
useragentgen.generate_many(5, "chrome")   # 5 Chrome UAs
```

Reproducible output with a seed:

```python
import useragentgen

useragentgen.init(42)
print(useragentgen.generate("chrome"))  # same result every run
```

## Command Line Interface


```bash
$  useragent-gen --help
usage: useragent-gen [-h] [-b BROWSER] [-c COUNT]

Generate random User-Agent strings.

options:
  -h, --help            show this help message and exit
  -b, --browser BROWSER
                        Specify browser (chrome, firefox, safari, edge, opera)
  -c, --count COUNT     Number of User-Agent strings to generate
```

default behaviour is:

```bash
useragent-gen
Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) OPR/108.0.4836.57 Chrome/121.0.0.0 Safari/537.36
```

in case you just don't want to install it and use it from src directly:

```bash
# Generate 1 random User-Agent string
python -m useragentgen.cli

# Generate 5 Chrome User-Agent strings
python -m useragentgen.cli -b chrome -c 5
```

## Supported browsers

| Key        | Covers                         |
|------------|-------------------------------|
| `chrome`   | Windows, macOS, Linux, Android |
| `firefox`  | All platforms                  |
| `safari`   | macOS, iOS, Windows            |
| `edge`     | Windows, macOS, Linux, Android |
| `opera`    | Windows, macOS, Linux          |

## Development

For local testing and development instructions, please refer to the [localtestingguide.md](localtestingguide.md).

## License

[MIT License Copyright (c) 2026 Masrkai, rights reserved](LICENSE)
