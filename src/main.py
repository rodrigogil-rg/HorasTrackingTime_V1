import argparse
import logging
import sys
from pathlib import Path

from src.excel_writer import write_excel
from src.exceptions import (
    InputNotFoundError,
    TrackingTimeError,
)
from src.parser import parse_csv_file
from src.transformer import filter_by_month
from src.validators import validate_month_year

# Configuración del logger principal de la aplicación
logger = logging.getLogger("trackingtime")


def find_csv_files(input_dir: Path) -> list[Path]:
    """Busca y valida que exista al menos un archivo CSV en el directorio de entrada."""
    if not input_dir.exists():
        raise InputNotFoundError(f"El directorio input no existe: {input_dir}")

    csv_files = list(input_dir.glob("*.csv"))
    if not csv_files:
        raise InputNotFoundError(f"No se encontró ningún archivo CSV en {input_dir}/")
    return csv_files


def main() -> int:
    """Punto de entrada principal de la CLI.

    Orquesta la lectura de múltiples CSVs, validación, transformación y generación del archivo Excel consolidado.
    """
    parser = argparse.ArgumentParser(
        description="Transforma múltiples CSVs mensuales de Tracking Time en Excel consolidado."
    )
    parser.add_argument("--mes", type=int, required=True, help="Mes (1..12)")
    parser.add_argument("--anio", type=int, required=True, help="Año (>= 2000)")
    parser.add_argument("--input", type=str, default="./input", help="Directorio de entrada")
    parser.add_argument("--output", type=str, default="./output", help="Directorio de salida")
    parser.add_argument("--usuario", type=str, default=None, help="Override explícito de usuario")
    parser.add_argument("--verbose", action="store_true", help="Mostrar traceback en errores")

    args = parser.parse_args()

    # Configurar nivel de logging según el argumento --verbose
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        # Validar mes y año proporcionados
        validate_month_year(args.mes, args.anio)
        input_dir = Path(args.input)
        output_dir = Path(args.output)

        # Buscar todos los archivos CSV de entrada (soporta múltiples usuarios)
        csv_files = find_csv_files(input_dir)
        all_entries = []

        for csv_path in csv_files:
            logger.info(f"Procesando archivo CSV: {csv_path}")
            entries = parse_csv_file(csv_path, override_usuario=args.usuario)
            all_entries.extend(entries)

        filtered_entries = filter_by_month(all_entries, args.mes, args.anio)

        if not filtered_entries:
            logger.warning(f"No se encontraron registros para el mes {args.mes}/{args.anio}.")

        # Determinar el nombre para el reporte (Consolidado si hay varios usuarios, o el nombre del usuario si es único)
        users_in_data = sorted({e.usuario for e in filtered_entries if e.usuario})
        if len(users_in_data) == 1:
            report_name = users_in_data[0]
        elif args.usuario:
            report_name = args.usuario
        else:
            report_name = "Consolidado"

        # Generar el archivo Excel resultante
        output_path = write_excel(filtered_entries, args.mes, args.anio, report_name, output_dir)
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
