# Registro de Cambios (CheckLog / Changelog)

Todas las modificaciones notables de este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere al versionado semántico.

---

## [1.2.0] - 2026-09-24

### Agregado
- Soporte para **múltiples archivos CSV de entrada** en el directorio `input/`, permitiendo consolidar reportes provenientes de diversos usuarios en una única ejecución.
- Detección automática de múltiples usuarios en los datos combinados, asignando el nombre `Consolidado` al archivo de salida cuando intervienen varios usuarios, o el nombre del usuario individual si solo hay uno.
- Creación del archivo de especificación de agentes `AGENTS.md`.

---

## [1.1.0] - 2026-09-24

### Agregado
- Soporte para la omisión automática de **días feriados** (registros marcados con `"FERIADO"` en las notas y con `0` horas).
- Flexibilidad en validadores y parser para permitir registros de feriados con clientes o duraciones opcionales/vacías.
- Comentarios de documentación exhaustivos en **español** en todos los módulos del código fuente (`src/`).

### Cambios
- Optimización del cálculo de **días trabajados** en Python (`{e.fecha for e in client_entries}`) en lugar de depender de la función `=COUNTA(_xlfn.UNIQUE(...))`, garantizando **compatibilidad universal 100%** con versiones antiguas de Excel (como Excel 2016).

---

## [1.0.0] - 2026-09-24

### Agregado
- Versión inicial completa basada en la Especificación Técnica v1.1.
- Módulos principales implementados: `models.py`, `exceptions.py`, `validators.py`, `parser.py`, `transformer.py`, `excel_writer.py` y `main.py` (CLI).
- Generación de libro Excel (`.xlsx`) con hoja de **Resumen general** y hojas individuales por **Cliente**, aplicando paleta de colores corporativa exacta (azul oscuro `#17365D`, azul medio `#1F4E78`, durazno `#F4B183`), fuentes, bordes dobles en totales, paneles congelados (`freeze_panes = "A4"`) y autofiltros.
- Suite robusta de pruebas automatizadas con `pytest` y `pytest-cov` (cobertura > 90%).
- Verificación estática de código con `Ruff`.
