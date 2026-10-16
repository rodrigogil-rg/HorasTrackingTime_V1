# Registro de Cambios (Changelog)

Todas las modificaciones notables de este proyecto serán documentadas en este archivo.

El formato está basado en Keep a Changelog, y este proyecto adhiere al versionado semántico.

---

## [1.5.0] - 15/10/2026

### Agregado
- Documentación completa en `TrackingTime_Excel_Specificacion_Desarrollo_v1.1.md` de todas las funcionalidades implementadas: modo batch (`--todos`), modo de salida configurable (`--modo-salida`), modo interactivo (`--interactivo`), nomenclatura con mes numérico de 2 dígitos y comportamiento `Consolidado` para múltiples usuarios.
- Todos los archivos de documentación sincronizados: `README.md`, `AGENTS.md`, `memory.md`, `Changelog.md`.
- Tests con docstrings descriptivos en todos los archivos de `tests/`.

---

## [1.4.0] - 15/10/2026

### Agregado
- **Modo de salida configurable (--modo-salida)**: Permite elegir entre generar un único archivo `Consolidado` cuando hay varios usuarios (`consolidado`, por defecto) o generar un archivo Excel independiente por cada usuario detectado (`por_usuario`).
- **Modo interactivo (--interactivo)**: Solicita todos los parámetros de ejecución por consola con valores por defecto (directorio de entrada/salida, tipo de ejecución, mes/año, usuario, modo de salida y verbosidad).
- Documentación del comportamiento del nombre `Consolidado` cuando intervienen múltiples usuarios.

---

## [1.3.0] - 15/10/2026

### Agregado
- **Modo Batch Masivo (--todos)**: Permite procesar de forma completamente automática todos los archivos CSV en el directorio input/ desde enero hasta la actualidad, agrupando y generando planillas Excel independientes por cada combinación de Usuario, Año y Mes.
- Nomenclatura de archivos de salida estandarizada con el año antes del mes y formato numérico de dos dígitos para un perfecto ordenamiento alfabético: `Planilla_Horas_{Usuario}_{Año}_{MesNum}.xlsx` (Ej: `Planilla_Horas_Priscila_Scharf_2025_01.xlsx`).
- Archivo de memoria persistente del proyecto (`memory.md`).

---

## [1.2.0] - 24/09/2026

### Agregado
- Soporte para **múltiples archivos CSV de entrada** en el directorio `input/`, permitiendo consolidar reportes provenientes de diversos usuarios en una única ejecución.
- Detección automática de múltiples usuarios en los datos combinados, asignando el nombre `Consolidado` al archivo de salida cuando intervienen varios usuarios, o el nombre del usuario individual si solo hay uno.
- Creación del archivo de especificación de agentes `AGENTS.md`.

---

## [1.1.0] - 18/09/2026

### Agregado
- Soporte para la omisión automática de **días feriados** (registros marcados con `FERIADO` en las notas y con `0` horas, permitiendo clientes o duraciones vacías/opcionales).
- Comentarios de documentación exhaustivos en **español** en todos los módulos del código fuente (`src/`).

### Cambios
- Optimización del cálculo de **días trabajados** en Python en lugar de depender de la función `=COUNTA(_xlfn.UNIQUE(...))`, garantizando **compatibilidad universal 100%** con versiones antiguas de Excel (como Excel 2016).

---

## [1.0.0] - 10/09/2026

### Agregado
- Versión inicial completa basada en la Especificación Técnica v1.1.
- Módulos principales implementados: `models.py`, `exceptions.py`, `validators.py`, `parser.py`, `transformer.py`, `excel_writer.py` y `main.py` (CLI).
- Generación de libro Excel (`.xlsx`) con hoja de **Resumen general** y hojas individuales por **Cliente**, aplicando paleta de colores corporativa exacta, fuentes, bordes, paneles congelados y autofiltros.
- Suite robusta de pruebas automatizadas con `pytest` y `pytest-cov` (cobertura > 90%).
- Verificación estática de código con `Ruff`.
