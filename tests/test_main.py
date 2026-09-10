from pathlib import Path

import pytest

from src.exceptions import InputNotFoundError
from src.main import find_csv_file, main


def test_find_csv_file_not_found(tmp_path):
    with pytest.raises(InputNotFoundError):
        find_csv_file(tmp_path / "nonexistent")


def test_main_execution(tmp_path, monkeypatch, capsys):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Copy sample csv to input_dir
    sample_csv = Path("Ejemplos/Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv")
    target_csv = input_dir / sample_csv.name
    target_csv.write_text(sample_csv.read_text(encoding="utf-8-sig"), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--mes",
            "8",
            "--anio",
            "2026",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
    )
    exit_code = main()
    assert exit_code == 0

    expected_output = output_dir / "Planilla_Horas_Rodrigo_Gil_Agosto_2026.xlsx"
    assert expected_output.exists()


def test_main_multiple_csv(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "a.csv").write_text("a", encoding="utf-8")
    (input_dir / "b.csv").write_text("b", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--mes",
            "8",
            "--anio",
            "2026",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
    )
    exit_code = main()
    assert exit_code == 2
