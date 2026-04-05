import re
from pathlib import Path


def natural_sort_key(path: Path) -> list[str | int]:
    """Sort key that orders numbers numerically within strings.

    Splits the filename stem into alternating text/number chunks,
    converting number chunks to int so "10" sorts after "9".
    """
    parts = re.split(r"(\d+)", path.stem)
    return [int(part) if part.isdigit() else part.lower() for part in parts]
