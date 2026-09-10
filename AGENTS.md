# AGENTS.md — Guía del Proyecto para Agentes IA y Automatización

> **Versión del Proyecto:** 1.0.0 (Basado en la Especificación Técnica v1.1)  
> **Propósito:** Guía de referencia técnica y arquitectura para agentes de inteligencia artificial, sistemas de automatización y desarrolladores que interactúan con el repositorio **Tracking Time → Excel Mensual**.

---

## 1. Visión General del Proyecto

El proyecto **Tracking Time → Excel Mensual** automatiza la transformación de reportes mensuales en formato CSV exportados desde Tracking Time en una planilla Excel (`.xlsx`) ejecutiva, profesional y estandarizada. 

La aplicación procesa los datos en Python aplicando reglas de negocio deterministas, validaciones estrictas y cálculos previos, generando una hoja de **Resumen general** y hojas individuales por **Cliente** con fórmulas, formatos y estilos consistentes.

---

## 2. Arquitectura y Principios de Diseño

El sistema sigue una arquitectura modular con separación estricta de responsabilidades:
1. **Parsing (`parser.py`)**: Lectura robusta de archivos CSV (`utf-8-sig`, delimitador `;`), normalización de encabezados y conversión a entidades de dominio (`TimeEntry`).
2. **Validación (`validators.py`)**: Validación defensiva de esquemas, tipos de datos, rangos de fechas/meses, unicidad de usuario y campos obligatorios.
3. **Transformación (`transformer.py`)**: Filtrado estricto por mes/año, agrupación alfabética por cliente, ordenamiento determinista de registros y cálculo previo de métricas de negocio.
4. **Generación de Excel (`excel_writer.py`)**: Construcción del libro con `openpyxl`, aplicando paleta de colores corporativa, fuentes, bordes, alineaciones, fórmulas nativas de Excel y celdas congeladas (`freeze_panes`).
5. **Orquestación CLI (`main.py`)**: Interfaz de línea de comandos, gestión de logging, códigos de salida estándar y control de excepciones de dominio.

### Principios Obligatorios:
- **Determinismo:** Misma entrada + mismos parámetros = mismo resultado exacto.
- **Idempotencia:** La ejecución repetida sobrescribe el archivo de salida de forma segura.
- **Lógica en Python:** Los cálculos se realizan en Python; Excel se utiliza como capa de presentación y resumen estático/fórmula.
- **Conservación de Horarios:** Se mantiene la hora local del CSV sin conversiones a UTC.

---

## 3. Estructura de Carpetas

La estructura completa del repositorio es la siguiente:

```text
project/
├── input/                  # Directorio para colocar el CSV de Tracking Time de entrada
├── output/                 # Directorio de salida para los archivos .xlsx generados
├── src/                    # Código fuente principal de la aplicación
│   ├── __init__.py
│   ├── main.py             # Orquestador CLI y punto de entrada
│   ├── parser.py           # Lector y parser de archivos CSV
│   ├── transformer.py      # Filtros, agrupación y cálculos de negocio
│   ├── excel_writer.py     # Generador de planillas Excel con openpyxl
│   ├── validators.py       # Reglas de validación y parsing de tipos
│   ├── exceptions.py       # Excepciones personalizadas y códigos de error
│   └── models.py           # Dataclasses y propiedades de dominio (TimeEntry)
├── tests/                  # Suite de pruebas automatizadas con pytest
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_validators.py
│   ├── test_excel_writer.py
│   ├── test_integration.py
│   └── test_edge_cases.py
├── Ejemplos/               # Archivos de referencia y golden master
├── TrackingTime_Excel_Specificacion_Desarrollo_v1.1.md # Especificación técnica completa
├── pyproject.toml          # Configuración del proyecto, pytest y Ruff
├── requirements.txt        # Dependencias de producción y desarrollo
└── README.md               # Documentación general para usuarios finales
```

---

## 4. Descripción de Módulos (`src/`)

### `src/models.py`
Define la dataclass `TimeEntry` que modela cada registro de tiempo del CSV, junto con propiedades calculadas:
- `fecha`: Extrae el objeto `date` de `fecha_inicio`.
- `hora_inicio`: Extrae el objeto `time` de `fecha_inicio`.
- `hora_fin`: Extrae el objeto `time` de `fecha_fin`.
- `duracion_timedelta`: Convierte el string de duración (`H:MM:SS` o `HH:MM:SS`) a `timedelta`.

### `src/parser.py`
Lee el archivo CSV utilizando `csv.DictReader` con codificación `utf-8-sig` y delimitador `;`. Valida la presencia de cabeceras requeridas, detecta de forma automática los usuarios y construye la lista de objetos `TimeEntry`.

### `src/validators.py`
Contiene funciones de validación estricta:
- `validate_headers`: Verifica columnas obligatorias (`Cliente`, `Usuario`, `Fecha de inicio`, `Fecha de fin`, `Duración`, `Horas`).
- `validate_month_year`: Valida que el mes esté entre 1 y 12 y el año sea `>= 2000`.
- `parse_hours`: Convierte strings con coma decimal (`1,5`) a `float`.
- `parse_datetime`: Parsea fechas en formatos `%d/%m/%Y %H:%M:%S` o `%Y-%m-%d %H:%M:%S`.
- `parse_duration`: Valida formato de duración de tiempo.
- `validate_client`: Asegura que el cliente no esté vacío.
- `validate_single_user`: Asegura que el archivo contenga un único usuario (salvo que se use `--usuario`).

### `src/transformer.py`
- `filter_by_month`: Filtra los registros según el mes y año solicitados mediante comparación de objetos `date`.
- `group_by_client`: Agrupa los registros por cliente, ordenando los clientes alfabéticamente y los registros internos por `fecha_inicio`, `fecha_fin` y `tarea`.
- `calculate_client_summary` / `calculate_general_summary`: Calculan horas totales, cantidad de registros y días trabajados por cliente y en total.

### `src/excel_writer.py`
Genera el archivo Excel (`.xlsx`) utilizando `openpyxl`:
- Crea la hoja **Resumen general** con fórmulas (`SUM`, `ROWS`, `COUNTA`, `_xlfn.UNIQUE`) y porcentajes respecto al total.
- Crea una hoja por cada **Cliente** sanitizando el nombre de la hoja (máximo 31 caracteres, sin caracteres prohibidos `\ / * ? [ ] :`) y resolviendo colisiones determinísticamente (`Cliente_A_2`).
- Aplica formato visual profesional (colores corporativos azul oscuro y gris claro, bordes, anchos de columna automáticos controlados, paneles congelados `freeze_panes = "A4"`, y autofiltros).

### `src/exceptions.py`
Define la jerarquía de excepciones de dominio (`TrackingTimeError`) asociadas a códigos de error estándar y códigos de salida específicos de CLI.

### `src/main.py`
Punto de entrada de la aplicación mediante CLI (`argparse`). Orquesta la lectura, validación, transformación y escritura del Excel, gestionando códigos de salida y logging detallado (`--verbose`).

---

## 5. Comandos de Ejecución y CLI

### Requisitos Previos
- Python `>= 3.10`

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```
O instalación editable:
```bash
pip install -e .
```

### Ejecución Básica
Colocar el archivo CSV en la carpeta `input/` y ejecutar indicando el mes y el año:
```bash
python -m src.main --mes 8 --anio 2026
```

### Parámetros CLI Adicionales
- `--mes <1-12>`: Mes a procesar (Requerido).
- `--anio <YYYY>`: Año a procesar, `>= 2000` (Requerido).
- `--input <ruta>`: Directorio de entrada personalizado (por defecto `./input`).
- `--output <ruta>`: Directorio de salida personalizado (por defecto `./output`).
- `--usuario "<Nombre>"`: Fuerza un nombre de usuario específico.
- `--verbose`: Muestra trazas de error completas (stack trace) para depuración.

---

## 6. Validación de Datos y Manejo de Errores

### Códigos de Salida del CLI (`sys.exit`)
- **`0`**: Éxito.
- **`1`**: Error de datos, validación o negocio (ej. cabecera inválida, fecha inválida, cliente vacío).
- **`2`**: Error de configuración o argumentos (ej. directorio `input` no encontrado, múltiples archivos CSV en `input`).

### Códigos de Error de Dominio
- `INPUT_NOT_FOUND`
- `MULTIPLE_INPUT_FILES`
- `INVALID_MONTH`
- `INVALID_YEAR`
- `INVALID_HEADER`
- `INVALID_ROW`
- `INVALID_DATE`
- `INVALID_HOURS`
- `INVALID_DURATION`
- `EMPTY_CLIENT`
- `MULTIPLE_USERS`
- `OUTPUT_ERROR`

---

## 7. Pruebas Automatizadas y Calidad (`tests/`)

La suite completa de tests utiliza `pytest` y `pytest-cov`.

### Ejecutar Tests con Cobertura
```bash
pytest --cov=src -v
```

### Archivos de Test
- `tests/test_main.py`: Pruebas de integración CLI y argumentos.
- `tests/test_validators.py`: Pruebas unitarias de validadores, fechas, horas, duraciones y headers.
- `tests/test_excel_writer.py`: Pruebas de generación de hojas, nombres sanitizados, colisiones y estilos.
- `tests/test_integration.py`: Pruebas end-to-end de flujo completo (CSV → Parser → Transformer → Excel → Validación de salida).
- `tests/test_edge_cases.py`: Pruebas de casos borde (límites de mes, archivos vacíos, múltiples usuarios, sin registros en el mes).

---

## 8. Linting y Formateo (Ruff)

El proyecto utiliza `Ruff` para análisis estático y formateo de código, configurado en `pyproject.toml` (`line-length = 100`, `target-version = "py310"`).

### Ejecutar Verificación de Lint
```bash
ruff check src tests
```

### Ejecutar Formateo de Código
```bash
ruff format src tests
```

---

## 9. Convenciones de Código

1. **Tipado estricto:** Todo el código fuente debe incluir anotaciones de tipo (`type hints`) compatibles con Python 3.10+.
2. **Estilo de documentación y mensajes:** Nombres de variables, funciones y mensajes de error en español cuando corresponden a dominio de usuario, siguiendo PEP 8.
3. **Inmutabilidad de lógica de negocio:** Ninguna decisión de negocio depende de características volátiles de Excel; toda agregación y filtrado ocurre en Python.
4. **Manejo de excepciones:** Las excepciones de negocio heredan de `TrackingTimeError` y exponen un código claro y un mensaje descriptivo que indica fila y campo cuando aplica.

---

## 10. Interfaz Futura para Agentes IA (`GENERAR_PLANILLA_HORAS`)

Para la integración de agentes de automatización o llamadas programáticas mediante IA, el contrato lógico es el siguiente:

### Solicitud (JSON / Skill Input)
```json
{
  "mes": 8,
  "anio": 2026,
  "input_dir": "./input",
  "output_dir": "./output"
}
```

### Respuesta de Éxito (JSON)
```json
{
  "success": true,
  "output_file": "output/Planilla_Horas_Rodrigo_Gil_Agosto_2026.xlsx",
  "usuario": "Rodrigo Gil",
  "mes": 8,
  "anio": 2026,
  "registros_procesados": 147,
  "clientes": 8,
  "horas_totales": 152.5
}
```

### Respuesta de Error (JSON)
```json
{
  "success": false,
  "error_code": "INVALID_HEADER",
  "message": "El CSV no contiene la columna requerida: Fecha de inicio"
}
```
