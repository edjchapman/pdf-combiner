from pathlib import Path

import pikepdf


def combine_pdfs(
    input_files: list[Path],
    output_path: Path,
    *,
    compress: bool = False,
    compress_level: int = 2,
) -> dict[str, int]:
    """Merge input PDFs into a single output PDF with optional compression.

    Returns a dict with stats: input_count, input_size, output_size.
    """
    output_pdf = pikepdf.Pdf.new()

    input_total_size = 0
    for pdf_path in input_files:
        input_total_size += pdf_path.stat().st_size
        with pikepdf.open(pdf_path) as src:
            output_pdf.pages.extend(src.pages)

    save_kwargs: dict = {}

    if compress:
        save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
        save_kwargs["compress_streams"] = True
        save_kwargs["stream_decode_level"] = pikepdf.StreamDecodeLevel.none
        save_kwargs["recompress_flate"] = True

        if compress_level >= 2:
            save_kwargs["normalize_content"] = True

        if compress_level >= 3:
            save_kwargs["linearize"] = True

    output_pdf.remove_unreferenced_resources()
    output_pdf.save(output_path, **save_kwargs)

    output_size = output_path.stat().st_size

    return {
        "input_count": len(input_files),
        "input_size": input_total_size,
        "output_size": output_size,
    }
