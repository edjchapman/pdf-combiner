# Contributing

## Setup

```bash
git clone https://github.com/edjchapman/pdf-combiner.git
cd pdf-combiner
uv sync
uv run pre-commit install
```

## Development workflow

1. Create a branch from `main`
2. Make your changes
3. Run the quality checks:

```bash
uv run ruff check src/ tests/       # lint
uv run ruff format src/ tests/       # format
uv run mypy src/pdf_combiner/        # type check
uv run pytest                         # test (90%+ coverage required)
```

4. Open a PR against `main`

## PR expectations

- Tests for new functionality
- Type hints on all public functions
- Passing CI (lint, type-check, tests on Python 3.12 and 3.13)
