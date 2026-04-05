# pdf-combiner

Combine multiple PDF files into a single document with lossless compression. Uses [pikepdf](https://pikepdf.readthedocs.io/) (QPDF) for intelligent object deduplication and stream recompression — ideal for merging numbered instruction sheets, manuals, or any PDF series without quality loss.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd pdf-combiner
uv sync
```

## Usage

```bash
# Basic merge (natural sort by filename)
uv run pdf-combiner file1.pdf file2.pdf file3.pdf -o merged.pdf

# Merge with glob pattern and compression
uv run pdf-combiner ~/Downloads/"BT FTTP BBU "*.pdf -c -o combined.pdf

# Maximum compression with verbose output
uv run pdf-combiner *.pdf -c --compress-level 3 -v -o output.pdf
```

### Options

| Option | Description |
|---|---|
| `-o, --output PATH` | Output file path (default: `combined.pdf`) |
| `-c, --compress` | Enable lossless compression |
| `--compress-level [1\|2\|3]` | 1=fast, 2=balanced (default), 3=maximum |
| `--no-sort` | Disable natural filename sorting |
| `-v, --verbose` | Show file list and compression stats |
| `--version` | Show version |

### Compression levels

All levels are **lossless** — text, images, and vector content are never degraded.

- **Level 1**: Object stream generation + flate recompression
- **Level 2**: + content stream normalization (better dedup for same-template PDFs)
- **Level 3**: + linearization (optimized structure)

## Development

```bash
uv run ruff check src/ tests/    # lint
uv run ruff format src/ tests/   # format
uv run pytest                     # test
```
