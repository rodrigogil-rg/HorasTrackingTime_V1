# Memoria Persistente del Proyecto (Memory.md)

Este documento registra los antecedentes, decisiones arquitectónicas, convenciones y estado actual del proyecto Tracking Time -> Excel Mensual.

---

## 1. Visión y Objetivo
Automatizar la transformación de reportes mensuales en formato CSV exportados desde Tracking Time en planillas Excel (.xlsx) ejecutivas, profesionales, estandarizadas y corporativas.

## 2. Decisiones Arquitectónicas Clave
- Lógica en Python: Toda la agregación, filtrado, validación y cálculos de negocio se realizan en Python. Excel se utiliza exclusivamente como capa de presentación.
- Compatibilidad Universal con Excel: Para evitar errores como #¡NOMBRE? en versiones antiguas (ej. Excel 2016), los días trabajados únicos se calculan directamente en Python utilizando conjuntos y se escriben como valores fijos.
- Soporte Batch y Múltiples CSVs: La herramienta soporta la lectura masiva de múltiples archivos CSV en input/, abarcando distintos usuarios, meses y años (--todos).
- Manejo de Feriados: Los registros con la palabra FERIADO en las notas y 0 horas son omitidos automáticamente, permitiendo clientes o duraciones vacías.
- Nomenclatura Estandarizada: Los archivos Excel generados siguen estrictamente el formato: Planilla_Horas_{Usuario}_{Año}_{MesNum}.xlsx (Ej: Planilla_Horas_Priscila_Scharf_2025_01.xlsx).

## 3. Comandos Esenciales
- Procesamiento Masivo (Batch): python -m src.main --todos
- Procesamiento por Mes/Año: python -m src.main --mes 8 --anio 2026
- Tests con Cobertura: pytest --cov=src -v
- Linting y Formateo: ruff check src tests y ruff format src tests
