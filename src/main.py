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


def _prompt_valor_defecto(mensaje: str, valor_defecto: str) -> str:
    """Muestra un prompt interactivo con valor por defecto y retorna la respuesta del usuario."""
    respuesta = input(f"{mensaje} [{valor_defecto}]: ").strip()
    return respuesta if respuesta else valor_defecto


def _prompt_opcion(mensaje: str, opciones: list[str], valor_defecto: str) -> str:
    """Muestra un prompt con opciones válidas y retorna la opción seleccionada."""
    while True:
        respuesta = input(f"{mensaje} ({'/'.join(opciones)}) [{valor_defecto}]: ").strip()
        if not respuesta:
            return valor_defecto
        if respuesta in opciones:
            return respuesta
        print(f"Opción inválida. Elija una de: {', '.join(opciones)}")


def _obtener_parametros_interactivos() -> dict:
    """Solicita al usuario los parámetros de ejecución de forma interactiva."""
    print("\n=== Modo Interactivo - Generar Planilla de Horas ===\n")

    input_dir = _prompt_valor_defecto("Directorio de entrada", "./input")
    output_dir = _prompt_valor_defecto("Directorio de salida", "./output")

    tipo_ejecucion = _prompt_opcion(
        "Tipo de ejecución",
        ["especifico", "todos"],
        "todos",
    )

    params = {
        "input": input_dir,
        "output": output_dir,
        "todos": tipo_ejecucion == "todos",
        "mes": None,
        "anio": None,
        "usuario": None,
        "modo_salida": "consolidado",
    }

    if not params["todos"]:
        mes_str = input("Mes (1..12) [8]: ").strip()
        params["mes"] = int(mes_str) if mes_str else 8
        anio_str = input("Año (>= 2000) [2026]: ").strip()
        params["anio"] = int(anio_str) if anio_str else 2026

    usuario = input("Usuario (opcional, Enter para detectar automáticamente): ").strip()
    params["usuario"] = usuario if usuario else None

    params["modo_salida"] = _prompt_opcion(
        "Modo de salida (cuando hay varios usuarios)",
        ["consolidado", "por_usuario"],
        "consolidado",
    )

    verbose = input("¿Mostrar trazas de error detalladas? (s/n) [n]: ").strip().lower()
    params["verbose"] = verbose in ("s", "si", "sí", "y", "yes")

    return params


def _generar_planillas_por_periodo(
    entries: list,
    mes: int,
    anio: int,
    output_dir: Path,
    modo_salida: str,
    override_usuario: str | None = None,
) -> list[Path]:
    """Filtra los registros por mes/año y genera planillas según el modo de salida."""
    filtered_entries = filter_by_month(entries, mes, anio)

    if not filtered_entries:
        logger.warning(
            f"No se encontraron registros para el mes {mes}/{anio} entre los archivos proporcionados."
        )
        return []

    usuarios = sorted({e.usuario for e in filtered_entries if e.usuario})

    generated_files = []

    if modo_salida == "por_usuario" and len(usuarios) > 1:
        for usuario in usuarios:
            entries_usuario = [e for e in filtered_entries if e.usuario == usuario]
            output_path = write_excel(entries_usuario, mes, anio, usuario, output_dir)
            logger.info(f"Planilla generada con éxito: {output_path}")
            generated_files.append(output_path)
    else:
        if len(usuarios) == 1:
            report_name = usuarios[0]
        elif override_usuario:
            report_name = override_usuario
        else:
            report_name = "Consolidado"

        output_path = write_excel(filtered_entries, mes, anio, report_name, output_dir)
        logger.info(f"Planilla generada con éxito: {output_path}")
        generated_files.append(output_path)

    return generated_files


def main() -> int:
    """Punto de entrada principal de la CLI.

    Orquesta la lectura de múltiples CSVs, validación y generación de planillas Excel.
    Soporta modo específico (--mes y --anio), modo batch automático (--todos),
    modo interactivo (--interactivo) y modo de salida consolidado o por usuario (--modo-salida).
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
    parser.add_argument(
        "--modo-salida",
        type=str,
        choices=["consolidado", "por_usuario"],
        default="consolidado",
        help="Modo de salida cuando hay varios usuarios: 'consolidado' (un archivo) o 'por_usuario' (un archivo por cada usuario)",
    )
    parser.add_argument("--input", type=str, default="./input", help="Directorio de entrada")
    parser.add_argument("--output", type=str, default="./output", help="Directorio de salida")
    parser.add_argument("--usuario", type=str, default=None, help="Override explícito de usuario")
    parser.add_argument(
        "--interactivo",
        action="store_true",
        help="Modo interactivo: solicita parámetros por consola con valores por defecto",
    )
    parser.add_argument("--verbose", action="store_true", help="Mostrar traceback en errores")

    args = parser.parse_args()

    # Modo interactivo: solicitar parámetros por consola
    if args.interactivo:
        params = _obtener_parametros_interactivos()
        args.input = params["input"]
        args.output = params["output"]
        args.todos = params["todos"]
        args.mes = params["mes"]
        args.anio = params["anio"]
        args.usuario = params["usuario"]
        args.modo_salida = params["modo_salida"]
        args.verbose = params["verbose"]

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
                generated_files.extend(
                    _generar_planillas_por_periodo(
                        all_entries, mes, anio, output_dir, args.modo_salida, args.usuario
                    )
                )

            logger.info(
                f"Proceso batch finalizado. Se generaron {len(generated_files)} planillas en total."
            )
            return 0

        else:
            # Modo tradicional específico por mes y año
            if args.mes is None or args.anio is None:
                parser.error("Se requieren los argumentos --mes y --anio (o utilizar --todos).")

            validate_month_year(args.mes, args.anio)
            _generar_planillas_por_periodo(
                all_entries, args.mes, args.anio, output_dir, args.modo_salida, args.usuario
            )
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
