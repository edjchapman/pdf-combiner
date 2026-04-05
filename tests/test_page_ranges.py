"""Tests for the page range parser."""

from pathlib import Path

import pytest

from pdf_combiner.exceptions import InvalidPageRangeError
from pdf_combiner.page_ranges import FileSpec, parse_file_spec, parse_page_ranges


def test_parse_plain_path():
    spec = parse_file_spec("document.pdf")
    assert spec.path == Path("document.pdf")
    assert not spec.has_page_selection


def test_parse_single_page():
    spec = parse_file_spec("doc.pdf:3")
    assert spec.path == Path("doc.pdf")
    assert spec.pages == [range(2, 3)]


def test_parse_page_range():
    spec = parse_file_spec("doc.pdf:1-5")
    assert spec.pages == [range(0, 5)]


def test_parse_multiple_ranges():
    spec = parse_file_spec("doc.pdf:1-3,5,7-9")
    assert spec.pages == [range(0, 3), range(4, 5), range(6, 9)]


def test_parse_open_ended_range():
    ranges = parse_page_ranges("5-", max_pages=10)
    assert ranges == [range(4, 10)]


def test_parse_open_ended_without_max_pages():
    with pytest.raises(InvalidPageRangeError, match="requires known page count"):
        parse_page_ranges("5-")


def test_parse_invalid_range_text():
    with pytest.raises(InvalidPageRangeError, match="Invalid page number"):
        parse_page_ranges("abc")


def test_parse_zero_page():
    with pytest.raises(InvalidPageRangeError, match="must be a positive integer"):
        parse_page_ranges("0")


def test_parse_reversed_range():
    with pytest.raises(InvalidPageRangeError, match=r"start.*>.*end"):
        parse_page_ranges("5-3")


def test_validate_exceeds_max_pages():
    with pytest.raises(InvalidPageRangeError, match="exceeds document length"):
        parse_page_ranges("100", max_pages=3)


def test_parse_path_without_pdf_extension():
    spec = parse_file_spec("notes.txt")
    assert spec.path == Path("notes.txt")
    assert not spec.has_page_selection


def test_file_spec_has_page_selection():
    no_pages = FileSpec(path=Path("a.pdf"))
    with_pages = FileSpec(path=Path("a.pdf"), pages=[range(0, 1)])

    assert not no_pages.has_page_selection
    assert with_pages.has_page_selection
