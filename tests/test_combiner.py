from pathlib import Path

import pikepdf
import pytest

from pdf_combiner.combiner import combine_pdfs


@pytest.fixture()
def sample_pdfs(tmp_path: Path) -> list[Path]:
    """Create 3 small single-page PDFs for testing."""
    paths = []
    for i in range(1, 4):
        pdf = pikepdf.Pdf.new()
        pdf.add_blank_page(page_size=(612, 792))
        path = tmp_path / f"page {i}.pdf"
        pdf.save(path)
        paths.append(path)
    return paths


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
    # Compressed should be no larger than uncompressed
    assert compressed.stat().st_size <= plain.stat().st_size


def test_combine_single_file(sample_pdfs: list[Path], tmp_path: Path):
    output = tmp_path / "single.pdf"
    stats = combine_pdfs([sample_pdfs[0]], output)

    assert stats["input_count"] == 1
    with pikepdf.open(output) as pdf:
        assert len(pdf.pages) == 1
