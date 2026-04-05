# pdf-combiner

[![CI](https://github.com/edjchapman/pdf-combiner/actions/workflows/ci.yml/badge.svg)](https://github.com/edjchapman/pdf-combiner/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/edjchapman/pdf-combiner/branch/main/graph/badge.svg)](https://codecov.io/gh/edjchapman/pdf-combiner)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A command-line tool for combining multiple PDF files into a single document with lossless compression. Built on [pikepdf](https://pikepdf.readthedocs.io/) (QPDF) for intelligent object deduplication and stream recompression — ideal for merging numbered instruction sheets, manuals, or any PDF series without quality loss.

## Features

- **Natural filename sorting** — `page 10.pdf` sorts after `page 9.pdf`, not after `page 1.pdf`
- **Lossless compression** — three levels of QPDF-powered compression that never degrade content
- **Page range selection** — extract specific pages with `file.pdf:1-3,5,7-9` syntax
- **PDF metadata** — set title, author, and subject on the combined document
- **Encrypted PDF support** — open password-protected files with `--password`
- **Overwrite protection** — prompts before overwriting unless `--force` is passed
- **Dry-run mode** — preview the operation without writing any files
- **Debug logging** — `--debug` flag for troubleshooting

## Project Structure

```
pdf-combiner/
├── src/pdf_combiner/
│   ├── __init__.py          # Package version
│   ├── cli.py               # Click CLI entry point
│   ├── combiner.py          # Core merge and compression logic
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── metadata.py          # XMP metadata helpers
│   ├── page_ranges.py       # FileSpec dataclass and range parser
│   └── sorting.py           # Natural sort key function
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_cli.py          # CLI integration tests
│   ├── test_combiner.py     # Core logic tests
│   ├── test_metadata.py     # Metadata tests
│   ├── test_page_ranges.py  # Parser tests
│   └── test_sorting.py      # Sorting tests
├── .github/
│   ├── workflows/ci.yml     # Lint, type-check, test (3.12 + 3.13)
│   ├── workflows/release.yml
│   └── dependabot.yml
├── pyproject.toml
└── .pre-commit-config.yaml
```

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/edjchapman/pdf-combiner.git
cd pdf-combiner
uv sync
```

## Quick Start

```bash
# Combine PDFs in natural order
uv run pdf-combiner file1.pdf file2.pdf file3.pdf

# Glob pattern with compression
uv run pdf-combiner ~/Documents/*.pdf -c -o merged.pdf

# Select specific pages from each file
uv run pdf-combiner intro.pdf chapter.pdf:1-5 appendix.pdf:3,7-9 -o book.pdf

# Set metadata on the combined document
uv run pdf-combiner *.pdf --title "Manual" --author "Ed Chapman" -o manual.pdf

# Preview without writing
uv run pdf-combiner *.pdf --dry-run

# Open encrypted PDFs
uv run pdf-combiner secret.pdf --password mypass -o decrypted.pdf
```

## CLI Reference

```
Usage: pdf-combiner [OPTIONS] FILES...
```

| Option | Description |
|---|---|
| `-o, --output PATH` | Output file path (default: `combined.pdf`) |
| `-c, --compress` | Enable lossless compression |
| `--compress-level [1\|2\|3]` | 1=fast, 2=balanced (default), 3=maximum |
| `--no-sort` | Disable natural filename sorting |
| `-v, --verbose` | Show file list and compression stats |
| `-f, --force` | Overwrite output without prompting |
| `--dry-run` | Show what would be done without writing |
| `--title TEXT` | Set PDF title metadata |
| `--author TEXT` | Set PDF author metadata |
| `--subject TEXT` | Set PDF subject metadata |
| `--password TEXT` | Password for encrypted input PDFs |
| `--debug` | Enable debug logging |
| `--version` | Show version |

### Compression Levels

All levels are **lossless** — text, images, and vector content are never degraded.

| Level | Strategy |
|---|---|
| 1 | Object stream generation + flate recompression |
| 2 | + content stream normalisation (better dedup for same-template PDFs) |
| 3 | Linearisation (optimised structure, replaces normalisation) |

### Page Range Syntax

```
file.pdf:1-3      # Pages 1 through 3
file.pdf:5        # Page 5 only
file.pdf:1-3,5,8  # Pages 1-3, 5, and 8
file.pdf:5-       # Page 5 to end (requires known page count)
file.pdf           # All pages (default)
```

## Development

```bash
# Install dependencies
uv sync

# Set up pre-commit hooks
uv run pre-commit install

# Run linter and formatter
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run type checker
uv run mypy src/pdf_combiner/

# Run tests with coverage
uv run pytest
```

## License

[MIT](LICENSE)
