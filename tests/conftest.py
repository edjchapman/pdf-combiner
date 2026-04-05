"""Shared test fixtures for pdf-combiner."""

from pathlib import Path

import pikepdf
import pytest


@pytest.fixture
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


@pytest.fixture
def multi_page_pdf(tmp_path: Path) -> Path:
    """Create a single PDF with 5 pages."""
    pdf = pikepdf.Pdf.new()
    for _ in range(5):
        pdf.add_blank_page(page_size=(612, 792))
    path = tmp_path / "multi.pdf"
    pdf.save(path)
    return path


@pytest.fixture
def encrypted_pdf(tmp_path: Path) -> Path:
    """Create a password-protected PDF."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page(page_size=(612, 792))
    path = tmp_path / "encrypted.pdf"
    pdf.save(
        path,
        encryption=pikepdf.Encryption(owner="owner123", user="user123"),
    )
    return path
