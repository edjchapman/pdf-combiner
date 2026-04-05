"""CLI integration tests using click.testing.CliRunner."""

from pathlib import Path

import pikepdf
from click.testing import CliRunner

from pdf_combiner.cli import main


def _create_test_pdfs(directory: Path, count: int = 3) -> list[Path]:
    """Create numbered test PDFs in a directory."""
    paths = []
    for i in range(1, count + 1):
        pdf = pikepdf.Pdf.new()
        pdf.add_blank_page(page_size=(612, 792))
        path = directory / f"doc {i}.pdf"
        pdf.save(path)
        paths.append(path)
    return paths


def test_cli_basic_merge(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(main, [*[str(p) for p in pdfs], "-o", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "Combined 3 files" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Combine multiple PDF files" in result.output


def test_cli_no_args():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code != 0


def test_cli_nonexistent_file():
    runner = CliRunner()
    result = runner.invoke(main, ["/nonexistent/file.pdf"])

    assert result.exit_code != 0
    output_lower = result.output.lower()
    assert "not found" in output_lower or "no files matched" in output_lower


def test_cli_verbose(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(main, [*[str(p) for p in pdfs], "-o", str(output), "-v"])

    assert result.exit_code == 0
    assert "doc 1.pdf" in result.output
    assert "all pages" in result.output


def test_cli_compress(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(main, [*[str(p) for p in pdfs], "-o", str(output), "-c"])

    assert result.exit_code == 0
    assert "Compression saved" in result.output


def test_cli_no_sort(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(
        main, [*[str(p) for p in reversed(pdfs)], "-o", str(output), "--no-sort"]
    )

    assert result.exit_code == 0


def test_cli_dry_run(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(
        main, [*[str(p) for p in pdfs], "-o", str(output), "--dry-run"]
    )

    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert not output.exists()


def test_cli_dry_run_with_compression(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(
        main, [*[str(p) for p in pdfs], "-o", str(output), "--dry-run", "-c"]
    )

    assert result.exit_code == 0
    assert "Compression: level 2" in result.output


def test_cli_overwrite_protection(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    output.write_bytes(b"existing")
    runner = CliRunner()

    result = runner.invoke(
        main, [*[str(p) for p in pdfs], "-o", str(output)], input="n\n"
    )

    assert result.exit_code != 0


def test_cli_force_overwrite(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    output.write_bytes(b"existing")
    runner = CliRunner()

    result = runner.invoke(main, [*[str(p) for p in pdfs], "-o", str(output), "-f"])

    assert result.exit_code == 0
    assert output.stat().st_size > len(b"existing")


def test_cli_metadata(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            *[str(p) for p in pdfs],
            "-o",
            str(output),
            "--title",
            "Test Title",
            "--author",
            "Test Author",
            "--subject",
            "Test Subject",
        ],
    )

    assert result.exit_code == 0
    with pikepdf.open(output) as pdf, pdf.open_metadata() as meta:
        assert meta.get("dc:title") == "Test Title"


def test_cli_page_ranges(tmp_path: Path):
    pdf = pikepdf.Pdf.new()
    for _ in range(5):
        pdf.add_blank_page(page_size=(612, 792))
    path = tmp_path / "multi.pdf"
    pdf.save(path)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(main, [f"{path}:1-3", "-o", str(output)])

    assert result.exit_code == 0
    with pikepdf.open(output) as result_pdf:
        assert len(result_pdf.pages) == 3


def test_cli_encrypted_without_password(encrypted_pdf: Path, tmp_path: Path):
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(main, [str(encrypted_pdf), "-o", str(output)])

    assert result.exit_code != 0
    assert "password" in result.output.lower()


def test_cli_encrypted_with_password(encrypted_pdf: Path, tmp_path: Path):
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(
        main, [str(encrypted_pdf), "-o", str(output), "--password", "user123"]
    )

    assert result.exit_code == 0
    assert output.exists()


def test_cli_debug_logging(tmp_path: Path):
    pdfs = _create_test_pdfs(tmp_path, count=1)
    output = tmp_path / "out.pdf"
    runner = CliRunner()

    result = runner.invoke(main, [str(pdfs[0]), "-o", str(output), "--debug"])

    assert result.exit_code == 0
