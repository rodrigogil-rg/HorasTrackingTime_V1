# Tracking Time -> Excel Mensual

Aplicación en Python que transforma reportes mensuales en formato CSV exportados desde Tracking Time en planillas Excel (.xlsx) ejecutivas, profesionales y estandarizadas.

## 1. Objetivo
Automatizar la conversión de exports de Tracking Time a planillas ejecutivas mensuales profesionales y estandarizadas.

## 2. Requisitos
- Python >= 3.10
- openpyxl >= 3.1.0

## 3. Instalación y Dependencias
```
pip install -r requirements.txt
```

## 4. Uso en el Día a Día (CLI)

### Procesamiento Masivo (Recomendado)
Coloca todos tus archivos CSV en la carpeta `input/` (sin importar de qué mes, año o usuario provengan) y ejecuta:
```
python -m src.main --todos
```
Esto generará automáticamente todas las planillas separadas en la carpeta `output/` con el formato estandarizado:
`Planilla_Horas_{Usuario}_{Año}_{MesNum}.xlsx` (Ej: `Planilla_Horas_Priscila_Scharf_2025_01.xlsx`).

Si hay registros de varios usuarios distintos en el mismo mes/año y no se especifica `--usuario`, se genera un archivo llamado `Planilla_Horas_Consolidado_{Año}_{MesNum}.xlsx` indicando que la planilla agrupa información de más de un usuario.

### Procesamiento Específico por Mes y Año
```
python -m src.main --mes 8 --anio 2026
```

### Modo de Salida: Consolidado vs. Por Usuario
- `--modo-salida consolidado` (por defecto): cuando hay múltiples usuarios, genera un único archivo `Consolidado`.
- `--modo-salida por_usuario`: cuando hay múltiples usuarios, genera un archivo Excel independiente por cada usuario detectado.

Ejemplo:
```
python -m src.main --mes 8 --anio 2026 --modo-salida por_usuario
```

### Modo Interactivo
El programa solicita todos los parámetros por consola con valores por defecto:
```
python -m src.main --interactivo
```

### Parámetros adicionales disponibles:
- `--input <ruta>`: Directorio de entrada (default `./input`).
- `--output <ruta>`: Directorio de salida (default `./output`).
- `--usuario "<Nombre>"`: Sobrescribe o fuerza el nombre de usuario mostrado en los títulos.
- `--verbose`: Muestra trazas de error detalladas para soporte y depuración.

## 5. Pruebas y Validación de Calidad
Ejecutar suite de tests con cobertura:
```
pytest --cov=src -v
```

Verificación de linting y formateo con Ruff:
```
ruff check src tests
ruff format src tests
```
