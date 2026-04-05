"""Parse file specifications with optional page range selectors."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pdf_combiner.exceptions import InvalidPageRangeError

# Matches "path.pdf:ranges" where the colon+ranges part is optional
_FILE_SPEC_PATTERN = re.compile(r"^(.+\.pdf)(?::(.+))?$", re.IGNORECASE)


@dataclass(frozen=True)
class FileSpec:
    """A file path with optional page range selection.

    Attributes:
        path: Path to the PDF file.
        pages: Zero-based page ranges to extract, or empty list for all pages.
    """

    path: Path
    pages: list[range] = field(default_factory=list)

    @property
    def has_page_selection(self) -> bool:
        """Return True if specific pages are selected."""
        return len(self.pages) > 0


def parse_page_ranges(range_str: str, *, max_pages: int | None = None) -> list[range]:
    """Parse a page range string into a list of zero-based ranges.

    Args:
        range_str: Comma-separated page ranges like "1-3,5,7-".
            Pages are 1-based in the input and converted to 0-based ranges.
        max_pages: If provided, validate that page numbers don't exceed this.

    Returns:
        List of zero-based range objects.

    Raises:
        InvalidPageRangeError: If the range string is malformed or invalid.
    """
    ranges: list[range] = []

    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part and not part.startswith("-"):
            start_str, end_str = part.split("-", 1)
            start = _parse_page_number(start_str)

            if end_str == "":
                # Open-ended range like "5-"
                if max_pages is None:
                    msg = f"Open-ended range '{part}' requires known page count"
                    raise InvalidPageRangeError(msg)
                end = max_pages
            else:
                end = _parse_page_number(end_str)

            if start > end:
                msg = f"Invalid range '{part}': start ({start}) > end ({end})"
                raise InvalidPageRangeError(msg)

            # Convert from 1-based to 0-based
            ranges.append(range(start - 1, end))
        else:
            page = _parse_page_number(part)
            # Convert from 1-based to 0-based
            ranges.append(range(page - 1, page))

    if max_pages is not None:
        for r in ranges:
            if r.stop > max_pages:
                msg = f"Page {r.stop} exceeds document length of {max_pages} pages"
                raise InvalidPageRangeError(msg)

    return ranges


def parse_file_spec(spec: str) -> FileSpec:
    """Parse a file specification string into a FileSpec.

    Args:
        spec: A string like "file.pdf" or "file.pdf:1-3,5,7-9".

    Returns:
        A FileSpec with the path and optional page ranges.

    Raises:
        InvalidPageRangeError: If the page range portion is malformed.
    """
    match = _FILE_SPEC_PATTERN.match(spec)
    if match:
        path_str, range_str = match.groups()
        path = Path(path_str)
        if range_str:
            pages = parse_page_ranges(range_str)
            return FileSpec(path=path, pages=pages)
        return FileSpec(path=path)

    # No .pdf extension match — treat the whole string as a path
    return FileSpec(path=Path(spec))


def _parse_page_number(s: str) -> int:
    """Parse and validate a 1-based page number string.

    Raises:
        InvalidPageRangeError: If the string is not a valid positive integer.
    """
    s = s.strip()
    if not s.isdigit() or int(s) == 0:
        msg = f"Invalid page number: '{s}' (must be a positive integer)"
        raise InvalidPageRangeError(msg)
    return int(s)
