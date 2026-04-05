"""Command-line interface for pdf-combiner."""

from __future__ import annotations

import logging
from pathlib import Path

import click

from pdf_combiner.combiner import combine_pdfs
from pdf_combiner.exceptions import EncryptedPdfError, InvalidPageRangeError
from pdf_combiner.metadata import set_metadata
from pdf_combiner.page_ranges import FileSpec, parse_file_spec
from pdf_combiner.sorting import natural_sort_key

logger = logging.getLogger(__name__)


def _resolve_file_args(files: tuple[str, ...]) -> list[FileSpec]:
    """Expand glob patterns and resolve file arguments to FileSpecs.

    Args:
        files: Raw CLI arguments — paths, globs, or "path:ranges" specs.

    Returns:
        Resolved list of FileSpec objects.

    Raises:
        click.BadParameter: If a glob matches nothing or a path doesn't exist.
    """
    resolved: list[FileSpec] = []
    for arg in files:
        spec = parse_file_spec(arg)
        pattern = str(spec.path)

        if any(c in pattern for c in ("*", "?", "[")):
            parent = spec.path.parent
            expanded = sorted(parent.glob(spec.path.name))
            if not expanded:
                msg = f"No files matched: {pattern}"
                raise click.BadParameter(msg)
            resolved.extend(FileSpec(path=p, pages=spec.pages) for p in expanded)
        else:
            if not spec.path.exists():
                msg = f"File not found: {pattern}"
                raise click.BadParameter(msg)
            resolved.append(spec)

    return resolved


@click.command()
@click.argument("files", nargs=-1, required=True)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=Path("combined.pdf"),
    show_default=True,
    help="Output PDF file path.",
)
@click.option(
    "-c",
    "--compress",
    is_flag=True,
    default=False,
    help="Enable lossless compression.",
)
@click.option(
    "--compress-level",
    type=click.IntRange(1, 3),
    default=2,
    show_default=True,
    help="Compression aggressiveness: 1=fast, 2=balanced, 3=maximum.",
)
@click.option("--no-sort", is_flag=True, help="Disable natural filename sorting.")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite output file without prompting.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without writing any files.",
)
@click.option("--title", default=None, help="Set PDF title metadata.")
@click.option("--author", default=None, help="Set PDF author metadata.")
@click.option("--subject", default=None, help="Set PDF subject metadata.")
@click.option(
    "--password",
    default=None,
    help="Password for encrypted input PDFs.",
)
@click.option("--debug", is_flag=True, help="Enable debug logging.")
@click.version_option(package_name="pdf-combiner")
def main(
    files: tuple[str, ...],
    output: Path,
    compress: bool,
    compress_level: int,
    no_sort: bool,
    verbose: bool,
    force: bool,
    dry_run: bool,
    title: str | None,
    author: str | None,
    subject: str | None,
    password: str | None,
    debug: bool,
) -> None:
    """Combine multiple PDF files into a single document.

    FILES can be individual file paths, shell glob patterns, or
    path:range specs (e.g. file.pdf:1-3,5).
    Files are sorted in natural order by default.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    try:
        specs = _resolve_file_args(files)
    except InvalidPageRangeError as exc:
        raise click.UsageError(str(exc)) from exc

    pdf_specs = [s for s in specs if s.path.suffix.lower() == ".pdf"]
    if not pdf_specs:
        raise click.UsageError("No PDF files found in the provided paths.")

    if not no_sort:
        pdf_specs.sort(key=lambda s: natural_sort_key(s.path))

    if dry_run:
        _print_dry_run(pdf_specs, output, compress, compress_level)
        return

    if (
        output.exists()
        and not force
        and not click.confirm(f"{output} already exists. Overwrite?")
    ):
        raise SystemExit(1)

    try:
        stats = combine_pdfs(
            input_files=pdf_specs,
            output_path=output,
            compress=compress,
            compress_level=compress_level,
            password=password,
        )
    except EncryptedPdfError as exc:
        raise click.UsageError(str(exc)) from exc
    except InvalidPageRangeError as exc:
        raise click.UsageError(str(exc)) from exc

    if any([title, author, subject]):
        set_metadata(output, title=title, author=author, subject=subject)

    _print_summary(stats, output, compress, verbose, pdf_specs)


def _print_dry_run(
    specs: list[FileSpec],
    output: Path,
    compress: bool,
    compress_level: int,
) -> None:
    """Print what would happen without actually combining."""
    click.echo(f"Dry run — would combine {len(specs)} files:")
    for i, spec in enumerate(specs, 1):
        page_info = _format_page_info(spec)
        click.echo(f"  {i}. {spec.path.name} ({page_info})")
    click.echo(f"Output: {output}")
    if compress:
        click.echo(f"Compression: level {compress_level}")


def _format_page_info(spec: FileSpec) -> str:
    """Format page selection info for display."""
    if not spec.has_page_selection:
        return "all pages"
    parts: list[str] = []
    for r in spec.pages:
        if len(r) == 1:
            parts.append(str(r.start + 1))
        else:
            parts.append(f"{r.start + 1}-{r.stop}")
    return f"pages {', '.join(parts)}"


def _print_summary(
    stats: dict[str, int],
    output: Path,
    compress: bool,
    verbose: bool,
    specs: list[FileSpec],
) -> None:
    """Print the combination summary."""
    if verbose:
        click.echo(f"Combined {len(specs)} files:")
        for spec in specs:
            page_info = _format_page_info(spec)
            click.echo(f"  {spec.path.name} ({page_info})")

    input_mb = stats["input_size"] / (1024 * 1024)
    output_mb = stats["output_size"] / (1024 * 1024)
    click.echo(
        f"Combined {stats['input_count']} files -> {output} "
        f"({input_mb:.1f} MB -> {output_mb:.1f} MB)"
    )
    if compress and stats["input_size"] > 0:
        ratio = (1 - stats["output_size"] / stats["input_size"]) * 100
        click.echo(f"Compression saved {ratio:.1f}%")
