# AGENTS.md -- Guía del Proyecto para Agentes IA y Automatización

## 1. Visión General
El proyecto automatiza la transformación de reportes CSV de Tracking Time en planillas Excel mensuales con soporte para múltiples archivos, múltiples usuarios, distintos meses/años, omisión automática de feriados y compatibilidad universal con Excel.

## 2. Comandos Principales
- Batch masivo: `python -m src.main --todos`
- Específico: `python -m src.main --mes 8 --anio 2026`
- Interactivo: `python -m src.main --interactivo`
- Tests: `pytest --cov=src -v`
- Lint: `ruff check src tests`

## 3. Nomenclatura de Salida
`Planilla_Horas_{Usuario}_{Año}_{MesNum}.xlsx` (Ej: `Planilla_Horas_Priscila_Scharf_2025_01.xlsx`).
Cuando hay múltiples usuarios en el mismo mes/año y no se especifica `--usuario`, se genera:
`Planilla_Horas_Consolidado_{Año}_{MesNum}.xlsx`

## 4. Parámetros CLI
- `--mes <1-12>`: Mes a procesar.
- `--anio <YYYY>`: Año a procesar (>= 2000).
- `--todos`: Procesa automáticamente todas las planillas por cada año/mes y usuario encontrados.
- `--modo-salida consolidado|por_usuario`: Modo de salida cuando hay varios usuarios (default: consolidado).
- `--interactivo`: Solicita parámetros por consola con valores por defecto.
- `--input <ruta>`: Directorio de entrada.
- `--output <ruta>`: Directorio de salida.
- `--usuario "<Nombre>"`: Sobrescribe o fuerza el nombre de usuario.
- `--verbose`: Muestra trazas de error detalladas.
