"""Tests for PDF metadata functionality."""

from pathlib import Path

import pikepdf

from pdf_combiner.metadata import set_metadata


def test_set_title(sample_pdfs: list[Path], tmp_path: Path):
    from pdf_combiner.combiner import combine_pdfs

    output = tmp_path / "titled.pdf"
    combine_pdfs(sample_pdfs, output)
    set_metadata(output, title="Test Document")

    with pikepdf.open(output) as pdf, pdf.open_metadata() as meta:
        assert meta.get("dc:title") == "Test Document"


def test_set_author(sample_pdfs: list[Path], tmp_path: Path):
    from pdf_combiner.combiner import combine_pdfs

    output = tmp_path / "authored.pdf"
    combine_pdfs(sample_pdfs, output)
    set_metadata(output, author="Test Author")

    with pikepdf.open(output) as pdf, pdf.open_metadata() as meta:
        assert "Test Author" in meta.get("dc:creator", "")


def test_set_subject(sample_pdfs: list[Path], tmp_path: Path):
    from pdf_combiner.combiner import combine_pdfs

    output = tmp_path / "described.pdf"
    combine_pdfs(sample_pdfs, output)
    set_metadata(output, subject="Test Subject")

    with pikepdf.open(output) as pdf, pdf.open_metadata() as meta:
        assert meta.get("dc:description") == "Test Subject"


def test_set_all_metadata(sample_pdfs: list[Path], tmp_path: Path):
    from pdf_combiner.combiner import combine_pdfs

    output = tmp_path / "full.pdf"
    combine_pdfs(sample_pdfs, output)
    set_metadata(output, title="Title", author="Author", subject="Subject")

    with pikepdf.open(output) as pdf, pdf.open_metadata() as meta:
        assert meta.get("dc:title") == "Title"
        assert "Author" in meta.get("dc:creator", "")
        assert meta.get("dc:description") == "Subject"


def test_no_metadata_noop(sample_pdfs: list[Path], tmp_path: Path):
    from pdf_combiner.combiner import combine_pdfs

    output = tmp_path / "noop.pdf"
    combine_pdfs(sample_pdfs, output)
    original_size = output.stat().st_size

    set_metadata(output)

    assert output.stat().st_size == original_size
