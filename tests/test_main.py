from pathlib import Path

import pytest

from src.exceptions import InputNotFoundError
from src.main import find_csv_files, main


def test_find_csv_files_not_found(tmp_path):
    """Prueba que find_csv_files lanza InputNotFoundError cuando el directorio de entrada no existe."""
    with pytest.raises(InputNotFoundError):
        find_csv_files(tmp_path / "nonexistent")


def test_main_execution(tmp_path, monkeypatch, capsys):
    """Prueba la ejecución estándar del CLI con --mes y --anio, verificando que se genere el archivo Excel esperado."""
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

    expected_output = output_dir / "Planilla_Horas_Rodrigo_Gil_2026_08.xlsx"
    assert expected_output.exists()


def test_main_multiple_csv(tmp_path, monkeypatch):
    """Prueba que el CLI procese múltiples archivos CSV en input/ para el mismo mes/año sin error (modo consolidado)."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Copy sample csv twice to simulate multiple users/files
    sample_csv = Path("Ejemplos/Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv")
    (input_dir / "user1.csv").write_text(
        sample_csv.read_text(encoding="utf-8-sig"), encoding="utf-8"
    )
    (input_dir / "user2.csv").write_text(
        sample_csv.read_text(encoding="utf-8-sig"), encoding="utf-8"
    )

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


def test_main_multiple_csv_different_months(tmp_path, monkeypatch):
    """Prueba el filtrado por mes específico cuando hay archivos CSV con registros de distintos meses."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Create a CSV with July data and another with August data
    csv_july = (
        "Cliente;Usuario;Fecha de inicio;Fecha de fin;Duración;Horas;Proyecto;Tarea;Facturable;Facturado;Archivado;Zona horaria;Moneda;Notas\n"
        "Cirion;Usuario Julio;15/07/2026 10:00:00;15/07/2026 12:00:00;2:00:00;2;Cirion;Tarea Julio;true;false;false;GMT-03:00;USD;-\n"
    )
    csv_august = (
        "Cliente;Usuario;Fecha de inicio;Fecha de fin;Duración;Horas;Proyecto;Tarea;Facturable;Facturado;Archivado;Zona horaria;Moneda;Notas\n"
        "Cirion;Usuario Agosto;15/08/2026 10:00:00;15/08/2026 12:00:00;2:00:00;2;Cirion;Tarea Agosto;true;false;false;GMT-03:00;USD;-\n"
    )

    (input_dir / "july.csv").write_text(csv_july, encoding="utf-8-sig")
    (input_dir / "august.csv").write_text(csv_august, encoding="utf-8-sig")

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

    expected_output = output_dir / "Planilla_Horas_Usuario_Agosto_2026_08.xlsx"
    assert expected_output.exists()


def test_main_batch_todos(tmp_path, monkeypatch):
    """Prueba el modo batch (--todos) que genera planillas independientes por cada combinación de año/mes y usuario."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    csv_data = (
        "Cliente;Usuario;Fecha de inicio;Fecha de fin;Duración;Horas;Proyecto;Tarea;Facturable;Facturado;Archivado;Zona horaria;Moneda;Notas\n"
        "Cirion;Priscila Scharf;14/01/2025 10:00:00;14/01/2025 11:00:00;1:00:00;1;Electra;Admin;false;false;false;GMT-03:00;USD;-\n"
    )
    (input_dir / "enero_2025.csv").write_text(csv_data, encoding="utf-8-sig")

    sample_csv = Path("Ejemplos/Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv")
    (input_dir / "agosto_2026.csv").write_text(
        sample_csv.read_text(encoding="utf-8-sig"), encoding="utf-8"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--todos",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
    )
    exit_code = main()
    assert exit_code == 0

    assert (output_dir / "Planilla_Horas_Priscila_Scharf_2025_01.xlsx").exists()
    assert (output_dir / "Planilla_Horas_Rodrigo_Gil_2026_08.xlsx").exists()


def test_main_batch_todos_por_usuario(tmp_path, monkeypatch):
    """Prueba el modo batch (--todos) con --modo-salida por_usuario, generando un archivo Excel por cada usuario detectado."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    csv_data = (
        "Cliente;Usuario;Fecha de inicio;Fecha de fin;Duración;Horas;Proyecto;Tarea;Facturable;Facturado;Archivado;Zona horaria;Moneda;Notas\n"
        "Cirion;Priscila Scharf;14/01/2025 10:00:00;14/01/2025 11:00:00;1:00:00;1;Electra;Admin;false;false;false;GMT-03:00;USD;-\n"
    )
    (input_dir / "enero_2025.csv").write_text(csv_data, encoding="utf-8-sig")

    sample_csv = Path("Ejemplos/Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv")
    (input_dir / "agosto_2026.csv").write_text(
        sample_csv.read_text(encoding="utf-8-sig"), encoding="utf-8"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--todos",
            "--modo-salida",
            "por_usuario",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
    )
    exit_code = main()
    assert exit_code == 0

    assert (output_dir / "Planilla_Horas_Priscila_Scharf_2025_01.xlsx").exists()
    assert (output_dir / "Planilla_Horas_Rodrigo_Gil_2026_08.xlsx").exists()


def test_main_mes_anio_por_usuario(tmp_path, monkeypatch):
    """Prueba el modo específico (--mes/--anio) con --modo-salida por_usuario cuando hay múltiples usuarios en el mismo mes."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    csv_data = (
        "Cliente;Usuario;Fecha de inicio;Fecha de fin;Duración;Horas;Proyecto;Tarea;Facturable;Facturado;Archivado;Zona horaria;Moneda;Notas\n"
        "Cirion;Usuario A;15/08/2026 10:00:00;15/08/2026 12:00:00;2:00:00;2;Cirion;Tarea A;true;false;false;GMT-03:00;USD;-\n"
        "Cirion;Usuario B;15/08/2026 14:00:00;15/08/2026 16:00:00;2:00:00;2;Cirion;Tarea B;true;false;false;GMT-03:00;USD;-\n"
    )
    (input_dir / "agosto_2026.csv").write_text(csv_data, encoding="utf-8-sig")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--mes",
            "8",
            "--anio",
            "2026",
            "--modo-salida",
            "por_usuario",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ],
    )
    exit_code = main()
    assert exit_code == 0

    assert (output_dir / "Planilla_Horas_Usuario_A_2026_08.xlsx").exists()
    assert (output_dir / "Planilla_Horas_Usuario_B_2026_08.xlsx").exists()


def test_main_interactivo_mocked(tmp_path, monkeypatch):
    """Prueba el modo interactivo (--interactivo) simulando respuestas de input() para generar una planilla específica."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    sample_csv = Path("Ejemplos/Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv")
    target_csv = input_dir / sample_csv.name
    target_csv.write_text(sample_csv.read_text(encoding="utf-8-sig"), encoding="utf-8")

    responses = iter(
        [
            str(input_dir),  # input dir
            str(output_dir),  # output dir
            "especifico",  # tipo ejecución
            "8",  # mes
            "2026",  # año
            "",  # usuario (default/detectar automáticamente)
            "consolidado",  # modo salida
            "n",  # verbose
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--interactivo",
        ],
    )
    exit_code = main()
    assert exit_code == 0

    expected_output = output_dir / "Planilla_Horas_Rodrigo_Gil_2026_08.xlsx"
    assert expected_output.exists()
