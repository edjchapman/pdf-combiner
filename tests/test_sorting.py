from pathlib import Path

from pdf_combiner.sorting import natural_sort_key


def test_numeric_order():
    paths = [Path(f"doc {i}.pdf") for i in [10, 2, 1, 9, 3]]
    result = sorted(paths, key=natural_sort_key)
    assert [p.stem for p in result] == ["doc 1", "doc 2", "doc 3", "doc 9", "doc 10"]


def test_bt_fttp_order():
    paths = [Path(f"BT FTTP BBU {i}.pdf") for i in [10, 1, 3, 2, 9, 5, 4, 7, 6, 8]]
    result = sorted(paths, key=natural_sort_key)
    expected = [f"BT FTTP BBU {i}" for i in range(1, 11)]
    assert [p.stem for p in result] == expected


def test_no_numbers():
    paths = [Path("charlie.pdf"), Path("alpha.pdf"), Path("bravo.pdf")]
    result = sorted(paths, key=natural_sort_key)
    assert [p.stem for p in result] == ["alpha", "bravo", "charlie"]


def test_case_insensitive():
    paths = [Path("Bravo.pdf"), Path("alpha.pdf")]
    result = sorted(paths, key=natural_sort_key)
    assert [p.stem for p in result] == ["alpha", "Bravo"]
