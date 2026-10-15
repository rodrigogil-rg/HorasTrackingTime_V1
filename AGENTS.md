# AGENTS.md -- Guía del Proyecto para Agentes IA y Automatización

## 1. Visión General
El proyecto automatiza la transformación de reportes CSV de Tracking Time en planillas Excel mensuales con soporte para múltiples archivos, múltiples usuarios, distintos meses/años, omisión automática de feriados y compatibilidad universal con Excel.

## 2. Comandos Principales
- Batch masivo: python -m src.main --todos
- Específico: python -m src.main --mes 8 --anio 2026
- Tests: pytest --cov=src -v
- Lint: ruff check src tests

## 3. Nomenclatura de Salida
Planilla_Horas_{Usuario}_{Año}_{MesNum}.xlsx (Ej: Planilla_Horas_Priscila_Scharf_2025_01.xlsx).
