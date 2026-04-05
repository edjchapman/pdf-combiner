import glob as globmodule
from pathlib import Path

import click

from pdf_combiner.combiner import combine_pdfs
from pdf_combiner.sorting import natural_sort_key


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
@click.version_option(package_name="pdf-combiner")
def main(
    files: tuple[str, ...],
    output: Path,
    compress: bool,
    compress_level: int,
    no_sort: bool,
    verbose: bool,
) -> None:
    """Combine multiple PDF files into a single document.

    FILES can be individual file paths or shell glob patterns.
    Files are sorted in natural order by default.
    """
    resolved: list[Path] = []
    for pattern in files:
        expanded = globmodule.glob(pattern)
        if not expanded:
            raise click.BadParameter(f"No files matched: {pattern}")
        resolved.extend(Path(p) for p in expanded)

    pdf_files = [p for p in resolved if p.suffix.lower() == ".pdf"]
    if not pdf_files:
        raise click.UsageError("No PDF files found in the provided paths.")

    if not no_sort:
        pdf_files.sort(key=natural_sort_key)

    if verbose:
        click.echo(f"Combining {len(pdf_files)} files:")
        for f in pdf_files:
            click.echo(f"  {f.name}")

    stats = combine_pdfs(
        input_files=pdf_files,
        output_path=output,
        compress=compress,
        compress_level=compress_level,
    )

    input_mb = stats["input_size"] / (1024 * 1024)
    output_mb = stats["output_size"] / (1024 * 1024)
    click.echo(
        f"Combined {stats['input_count']} files -> {output} "
        f"({input_mb:.1f} MB -> {output_mb:.1f} MB)"
    )
    if compress and stats["input_size"] > 0:
        ratio = (1 - stats["output_size"] / stats["input_size"]) * 100
        click.echo(f"Compression saved {ratio:.1f}%")
