# Tracking Time -> Excel Mensual

Aplicación en Python que transforma reportes mensuales en formato CSV exportados desde Tracking Time en planillas Excel (.xlsx) ejecutivas, profesionales y estandarizadas.

## 1. Objetivo
Automatizar la conversión de exports de Tracking Time a planillas ejecutivas mensuales profesionales y estandarizadas.

## 2. Requisitos
- Python >= 3.10
- openpyxl >= 3.1.0

## 3. Instalación y Dependencias
`ash
pip install -r requirements.txt
`

## 4. Uso en el Día a Día (CLI)

### Procesamiento Masivo (Recomendado)
Coloca todos tus archivos CSV en la carpeta input/ (sin importar de qué mes, año o usuario provengan) y ejecuta:
`ash
python -m src.main --todos
`
Esto generará automáticamente todas las planillas separadas en la carpeta output/ con el formato estandarizado:
Planilla_Horas_{Usuario}_{Año}_{MesNum}.xlsx (Ej: Planilla_Horas_Priscila_Scharf_2025_01.xlsx).

### Procesamiento Específico por Mes y Año
`ash
python -m src.main --mes 8 --anio 2026
`

## 5. Pruebas y Validación de Calidad
Ejecutar suite de tests con cobertura:
`ash
pytest --cov=src -v
`

Verificación de linting y formateo con Ruff:
`ash
ruff check src tests
ruff format src tests
`
