"""Core PDF merging and compression logic."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pikepdf

from pdf_combiner.exceptions import EncryptedPdfError
from pdf_combiner.page_ranges import FileSpec

logger = logging.getLogger(__name__)


def combine_pdfs(
    input_files: list[Path] | list[FileSpec],
    output_path: Path,
    *,
    compress: bool = False,
    compress_level: int = 2,
    password: str | None = None,
) -> dict[str, int]:
    """Merge input PDFs into a single output PDF with optional compression.

    Args:
        input_files: Paths or FileSpecs to combine. Plain Paths include all pages.
        output_path: Where to write the combined PDF.
        compress: Enable lossless compression.
        compress_level: Compression aggressiveness (1-3).
        password: Password for encrypted PDFs.

    Returns:
        Dict with keys: input_count, input_size, output_size.

    Raises:
        EncryptedPdfError: If a PDF is password-protected and no/wrong password given.
    """
    specs = _normalise_inputs(input_files)
    output_pdf = pikepdf.Pdf.new()

    input_total_size = 0
    for spec in specs:
        input_total_size += spec.path.stat().st_size
        logger.debug("Opening %s", spec.path.name)
        src = _open_pdf(spec.path, password=password)
        with src:
            pages = _select_pages(src, spec)
            output_pdf.pages.extend(pages)

    save_kwargs = _build_save_kwargs(compress, compress_level)

    output_pdf.remove_unreferenced_resources()
    output_pdf.save(output_path, **save_kwargs)

    output_size = output_path.stat().st_size
    logger.debug("Output size: %d bytes", output_size)

    return {
        "input_count": len(specs),
        "input_size": input_total_size,
        "output_size": output_size,
    }


def _normalise_inputs(
    input_files: list[Path] | list[FileSpec],
) -> list[FileSpec]:
    """Convert a mixed list of Paths and FileSpecs to all FileSpecs."""
    return [FileSpec(path=f) if isinstance(f, Path) else f for f in input_files]


def _open_pdf(path: Path, *, password: str | None = None) -> pikepdf.Pdf:
    """Open a PDF, handling encrypted files.

    Raises:
        EncryptedPdfError: If the PDF is encrypted and no/wrong password provided.
    """
    try:
        return pikepdf.open(path, password=password or "")
    except pikepdf.PasswordError as exc:
        msg = (
            f"{path.name} is password-protected. "
            "Use --password to provide the password."
        )
        raise EncryptedPdfError(msg) from exc


def _select_pages(pdf: pikepdf.Pdf, spec: FileSpec) -> list[pikepdf.Page]:
    """Extract the requested pages from a PDF based on the FileSpec.

    If the spec has page ranges, resolves open-ended ranges against the
    actual page count and validates bounds.
    """
    if not spec.has_page_selection:
        return list(pdf.pages)

    total_pages = len(pdf.pages)
    selected: list[pikepdf.Page] = []

    for page_range in spec.pages:
        # Re-parse open-ended ranges now that we know the page count
        if page_range.stop > total_pages:
            from pdf_combiner.exceptions import InvalidPageRangeError

            msg = (
                f"Page {page_range.stop} exceeds {spec.path.name} ({total_pages} pages)"
            )
            raise InvalidPageRangeError(msg)

        for i in page_range:
            selected.append(pdf.pages[i])

    return selected


def _build_save_kwargs(compress: bool, compress_level: int) -> dict[str, Any]:
    """Build pikepdf save kwargs for the requested compression level."""
    save_kwargs: dict[str, Any] = {}

    if compress:
        logger.debug("Compression level %d", compress_level)
        save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
        save_kwargs["compress_streams"] = True
        save_kwargs["stream_decode_level"] = pikepdf.StreamDecodeLevel.none
        save_kwargs["recompress_flate"] = True

        if compress_level >= 3:
            save_kwargs["linearize"] = True
        elif compress_level >= 2:
            save_kwargs["normalize_content"] = True

    return save_kwargs
