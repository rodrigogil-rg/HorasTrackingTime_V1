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

    Orquesta la lectura de múltiples CSVs, validación y generación de planillas Excel.
    Soporta modo específico (--mes y --anio) o modo batch automático (--todos).
    """
    parser = argparse.ArgumentParser(
        description="Transforma múltiples CSVs mensuales de Tracking Time en Excel."
    )
    parser.add_argument("--mes", type=int, default=None, help="Mes (1..12)")
    parser.add_argument("--anio", type=int, default=None, help="Año (>= 2000)")
    parser.add_argument(
        "--todos",
        action="store_true",
        help="Procesa y genera automáticamente todas las planillas por cada año/mes y usuario encontrados",
    )
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
        input_dir = Path(args.input)
        output_dir = Path(args.output)

        # Buscar todos los archivos CSV de entrada
        csv_files = find_csv_files(input_dir)
        all_entries = []

        for csv_path in csv_files:
            logger.info(f"Procesando archivo CSV: {csv_path}")
            entries = parse_csv_file(csv_path, override_usuario=args.usuario)
            all_entries.extend(entries)

        if args.todos:
            # Modo batch: extraer todas las combinaciones únicas de (anio, mes) presentes en los datos
            periods = sorted({(e.fecha.year, e.fecha.month) for e in all_entries})
            if not periods:
                logger.warning("No se encontraron registros en los archivos CSV.")
                return 0

            generated_files = []
            for anio, mes in periods:
                filtered_entries = filter_by_month(all_entries, mes, anio)
                if not filtered_entries:
                    continue

                users_in_data = sorted({e.usuario for e in filtered_entries if e.usuario})
                if len(users_in_data) == 1:
                    report_name = users_in_data[0]
                elif args.usuario:
                    report_name = args.usuario
                else:
                    report_name = "Consolidado"

                output_path = write_excel(filtered_entries, mes, anio, report_name, output_dir)
                logger.info(f"Planilla generada con éxito: {output_path}")
                generated_files.append(output_path)

            logger.info(
                f"Proceso batch finalizado. Se generaron {len(generated_files)} planillas en total."
            )
            return 0

        else:
            # Modo tradicional específico por mes y año
            if args.mes is None or args.anio is None:
                parser.error("Se requieren los argumentos --mes y --anio (o utilizar --todos).")

            validate_month_year(args.mes, args.anio)
            filtered_entries = filter_by_month(all_entries, args.mes, args.anio)

            if not filtered_entries:
                logger.warning(
                    f"No se encontraron registros para el mes {args.mes}/{args.anio} entre los archivos proporcionados."
                )

            users_in_data = sorted({e.usuario for e in filtered_entries if e.usuario})
            if len(users_in_data) == 1:
                report_name = users_in_data[0]
            elif args.usuario:
                report_name = args.usuario
            else:
                report_name = "Consolidado"

            output_path = write_excel(
                filtered_entries, args.mes, args.anio, report_name, output_dir
            )
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
