# Tracking Time → Excel Mensual

Aplicación en Python que transforma el reporte mensual en formato CSV exportado desde Tracking Time en una planilla Excel `.xlsx` estructurada con una hoja de resumen general y hojas individuales por cliente, aplicando fórmulas, estilos, validaciones y reglas de negocio deterministas.

## 1. Objetivo
Automatizar la conversión de exports de Tracking Time a planillas ejecutivas mensuales profesionales y estandarizadas.

## 2. Requisitos
- Python >= 3.10
- openpyxl >= 3.1.0

## 3. Instalación y Dependencias
```bash
pip install -r requirements.txt
```

O instalación editable del proyecto:
```bash
pip install -e .
```

## 4. Estructura del Proyecto
```text
project/
├── input/
├── output/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── parser.py
│   ├── transformer.py
│   ├── excel_writer.py
│   ├── validators.py
│   ├── exceptions.py
│   └── models.py
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_transformer.py
│   ├── test_excel_writer.py
│   ├── test_validators.py
│   ├── test_main.py
│   ├── test_edge_cases.py
│   └── test_integration.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 5. CSV de Entrada
El sistema procesa archivos CSV delimitados por punto y coma (`;`), codificados en UTF-8 (con o sin BOM), respetando las columnas estándar de exportación de Tracking Time (Cliente, Proyecto, Usuario, Fechas, Duración, Horas, Notas, etc.).

## 6. Uso en el Día a Día (CLI)

Para procesar tus reportes mensuales de forma rápida y sencilla:

1. **Colocar el CSV**: Copia el archivo CSV exportado desde Tracking Time dentro de la carpeta `input/`:
   ```text
   input/
   └── Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv
   ```
2. **Ejecutar el comando**: Abre tu terminal en la raíz del proyecto y ejecuta el comando indicando el **mes** y el **año** que deseas procesar:
   ```bash
   python -m src.main --mes 8 --anio 2026
   ```
3. **Obtener el resultado**: Encontrarás tu planilla ejecutiva formateada con la paleta de colores oficial y fórmulas en la carpeta `output/`:
   ```text
   output/
   └── Planilla_Horas_Rodrigo_Gil_Agosto_2026.xlsx
   ```

### Parámetros adicionales disponibles:
- `--input <ruta>`: Especifica un directorio de entrada personalizado (por defecto `./input`).
- `--output <ruta>`: Especifica un directorio de salida personalizado (por defecto `./output`).
- `--usuario "<Nombre>"`: Sobrescribe o fuerza el nombre de usuario mostrado en los títulos.
- `--verbose`: Muestra trazas de error detalladas para soporte y depuración.

## 7. Pruebas y Validación de Calidad
Ejecutar suite de tests con cobertura:
```bash
pytest --cov=src -v
```

Verificación de linting y formateo con Ruff:
```bash
ruff check src tests
ruff format src tests
```

## 8. Limitaciones de V1
- Asume un único usuario en el archivo CSV (a menos que se use `--usuario`).
- Los cálculos se realizan en Python con fórmulas de resumen estáticas en Excel.
