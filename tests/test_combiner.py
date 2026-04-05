"""Tests for the core PDF combining logic."""

from pathlib import Path

import pikepdf
import pytest

from pdf_combiner.combiner import combine_pdfs
from pdf_combiner.exceptions import EncryptedPdfError, InvalidPageRangeError
from pdf_combiner.page_ranges import FileSpec


def test_combine_creates_output(sample_pdfs: list[Path], tmp_path: Path):
    output = tmp_path / "out.pdf"
    stats = combine_pdfs(sample_pdfs, output)

    assert output.exists()
    assert stats["input_count"] == 3
    assert stats["output_size"] > 0

    with pikepdf.open(output) as pdf:
        assert len(pdf.pages) == 3


def test_combine_with_compression(sample_pdfs: list[Path], tmp_path: Path):
    plain = tmp_path / "plain.pdf"
    compressed = tmp_path / "compressed.pdf"

    combine_pdfs(sample_pdfs, plain)
    combine_pdfs(sample_pdfs, compressed, compress=True, compress_level=2)

    assert compressed.exists()
    assert compressed.stat().st_size <= plain.stat().st_size


def test_combine_single_file(sample_pdfs: list[Path], tmp_path: Path):
    output = tmp_path / "single.pdf"
    stats = combine_pdfs([sample_pdfs[0]], output)

    assert stats["input_count"] == 1
    with pikepdf.open(output) as pdf:
        assert len(pdf.pages) == 1


def test_combine_all_compression_levels(sample_pdfs: list[Path], tmp_path: Path):
    for level in (1, 2, 3):
        output = tmp_path / f"level{level}.pdf"
        stats = combine_pdfs(sample_pdfs, output, compress=True, compress_level=level)
        assert output.exists()
        assert stats["output_size"] > 0
        with pikepdf.open(output) as pdf:
            assert len(pdf.pages) == 3


def test_combine_with_page_ranges(multi_page_pdf: Path, tmp_path: Path):
    output = tmp_path / "ranged.pdf"
    spec = FileSpec(path=multi_page_pdf, pages=[range(0, 2), range(3, 4)])
    stats = combine_pdfs([spec], output)

    assert stats["input_count"] == 1
    with pikepdf.open(output) as pdf:
        assert len(pdf.pages) == 3  # pages 1-2 and 4


def test_combine_page_range_out_of_bounds(multi_page_pdf: Path, tmp_path: Path):
    output = tmp_path / "bad.pdf"
    spec = FileSpec(path=multi_page_pdf, pages=[range(0, 100)])
    with pytest.raises(InvalidPageRangeError, match="exceeds"):
        combine_pdfs([spec], output)


def test_combine_encrypted_pdf_without_password(encrypted_pdf: Path, tmp_path: Path):
    output = tmp_path / "out.pdf"
    with pytest.raises(EncryptedPdfError, match="password-protected"):
        combine_pdfs([encrypted_pdf], output)


def test_combine_encrypted_pdf_with_password(encrypted_pdf: Path, tmp_path: Path):
    output = tmp_path / "out.pdf"
    stats = combine_pdfs([encrypted_pdf], output, password="user123")

    assert output.exists()
    assert stats["input_count"] == 1
    with pikepdf.open(output) as pdf:
        assert len(pdf.pages) == 1


def test_combine_accepts_file_specs(sample_pdfs: list[Path], tmp_path: Path):
    output = tmp_path / "specs.pdf"
    specs = [FileSpec(path=p) for p in sample_pdfs]
    stats = combine_pdfs(specs, output)

    assert stats["input_count"] == 3
    with pikepdf.open(output) as pdf:
        assert len(pdf.pages) == 3
