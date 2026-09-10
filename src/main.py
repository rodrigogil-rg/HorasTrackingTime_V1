import argparse
import logging
import sys
from pathlib import Path

from src.excel_writer import write_excel
from src.exceptions import (
    InputNotFoundError,
    MultipleInputFilesError,
    TrackingTimeError,
)
from src.parser import parse_csv_file
from src.transformer import filter_by_month
from src.validators import validate_month_year

logger = logging.getLogger("trackingtime")


def find_csv_file(input_dir: Path) -> Path:
    if not input_dir.exists():
        raise InputNotFoundError(f"El directorio input no existe: {input_dir}")

    csv_files = list(input_dir.glob("*.csv"))
    if not csv_files:
        raise InputNotFoundError(f"No se encontró archivo CSV en {input_dir}/")
    if len(csv_files) > 1:
        raise MultipleInputFilesError(
            f"Múltiples archivos CSV encontrados en {input_dir}/. Deje solo uno."
        )
    return csv_files[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Transforma CSV mensual de Tracking Time en Excel."
    )
    parser.add_argument("--mes", type=int, required=True, help="Mes (1..12)")
    parser.add_argument("--anio", type=int, required=True, help="Año (>= 2000)")
    parser.add_argument("--input", type=str, default="./input", help="Directorio de entrada")
    parser.add_argument("--output", type=str, default="./output", help="Directorio de salida")
    parser.add_argument("--usuario", type=str, default=None, help="Override explícito de usuario")
    parser.add_argument("--verbose", action="store_true", help="Mostrar traceback en errores")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        validate_month_year(args.mes, args.anio)
        input_dir = Path(args.input)
        output_dir = Path(args.output)

        csv_path = find_csv_file(input_dir)
        logger.info(f"Procesando archivo CSV: {csv_path}")

        entries = parse_csv_file(csv_path, override_usuario=args.usuario)
        filtered_entries = filter_by_month(entries, args.mes, args.anio)

        if not filtered_entries:
            logger.warning(f"No se encontraron registros para el mes {args.mes}/{args.anio}.")

        # Detect usuario from entries if not provided
        usuario = args.usuario
        if not usuario and filtered_entries:
            usuario = filtered_entries[0].usuario
        elif not usuario and entries:
            usuario = entries[0].usuario
        elif not usuario:
            usuario = "Usuario"

        output_path = write_excel(filtered_entries, args.mes, args.anio, usuario, output_dir)
        logger.info(f"Planilla generada con éxito: {output_path}")
        return 0

    except TrackingTimeError as e:
        logger.error(f"ERROR: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return e.exit_code
    except Exception as e:  # noqa: BLE001
        logger.error(f"ERROR inesperado: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
