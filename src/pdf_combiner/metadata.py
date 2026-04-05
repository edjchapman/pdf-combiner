"""Set PDF metadata using XMP."""

from pathlib import Path

import pikepdf


def set_metadata(
    pdf_path: Path,
    *,
    title: str | None = None,
    author: str | None = None,
    subject: str | None = None,
) -> None:
    """Set XMP metadata on an existing PDF file.

    Args:
        pdf_path: Path to the PDF to modify in-place.
        title: Document title (dc:title).
        author: Document author (dc:creator).
        subject: Document subject/description (dc:description).
    """
    if not any([title, author, subject]):
        return

    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        with pdf.open_metadata() as meta:
            if title:
                meta["dc:title"] = title
            if author:
                meta["dc:creator"] = [author]
            if subject:
                meta["dc:description"] = subject
        pdf.save(pdf_path)
