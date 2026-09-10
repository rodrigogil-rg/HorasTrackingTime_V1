# Especificación de Desarrollo — Tracking Time → Excel Mensual

**Versión:** 1.1  
**Estado:** Lista para desarrollo  
**Tipo:** Especificación técnica / contrato de implementación

## 1. Objetivo

Desarrollar una aplicación Python que transforme el CSV mensual exportado desde Tracking Time en un archivo Excel `.xlsx` con:

1. Una hoja `Resumen general`.
2. Una hoja individual por cada cliente.
3. Cálculos, fórmulas, formatos y estructura consistentes con la planilla de referencia.
4. Ejecución mediante CLI.
5. Tests automatizados.
6. Validaciones y errores claros.

La lógica de negocio debe ejecutarse en Python. Excel es la representación final.

## 2. Principios obligatorios

- Determinismo: misma entrada + mismos parámetros = mismo resultado.
- Idempotencia: repetir el proceso reemplaza el resultado de forma segura.
- Separación de responsabilidades entre parsing, validación, transformación y Excel.
- Business logic en Python; no depender de funciones modernas de Excel para calcular resultados.
- Compatibilidad con Excel moderno y, cuando sea posible, LibreOffice.
- Errores trazables a archivo, fila y campo.
- No inventar datos.
- Conservar la hora local del CSV; no convertir a UTC.

## 3. CSV de entrada

Formato:
- UTF-8.
- Separador `;`.
- Campos potencialmente entrecomillados.
- Decimal con coma (`1,5`).
- Fecha/hora `DD/MM/YYYY HH:MM:SS`.
- Duración `H:MM:SS`.
- Zona habitual `GMT-03:00`.

Columnas del CSV de referencia:

| Índice | Campo |
|---:|---|
| 0 | Servicio |
| 1 | Cliente |
| 2 | Proyecto |
| 3 | Usuario |
| 4 | Lista de tareas |
| 5 | Tarea |
| 6 | Fecha de entrega |
| 7 | Horas estimadas |
| 8 | Facturable |
| 9 | Facturado |
| 10 | Precio por hora |
| 11 | Archivado |
| 12 | Fecha de inicio |
| 13 | Fecha de fin |
| 14 | Zona horaria |
| 15 | Duración |
| 16 | Horas |
| 17 | Notas |
| 18 | Total |
| 19 | Costo por hora |
| 20 | Costo |
| 21 | Moneda |

### Contrato de headers

No depender exclusivamente de índices. Leer encabezados, normalizarlos, construir `nombre -> índice` y validar columnas requeridas:

- Cliente
- Usuario
- Fecha de inicio
- Fecha de fin
- Duración
- Horas

Si falta una columna, finalizar con error controlado.

## 4. Parsing

### Strings
- Conservar texto.
- Campos opcionales vacíos → `None`.
- Notas multilinea deben conservar saltos de línea.

### Booleanos
`true` / `false`, case-insensitive.

### Horas
Convertir `1,5` → `1.5` mediante reemplazo de coma por punto y `float`.

### Fecha/hora
Parsear `%d/%m/%Y %H:%M:%S` a `datetime`. No convertir a UTC.

### Duración
Convertir `H:MM:SS` a `timedelta`. Debe soportar más de 24 horas.

### Cliente
Cliente vacío = error. Ejemplo:
`Fila N: el campo Cliente es obligatorio.`

## 5. Usuario

Detectar automáticamente el usuario. V1 asume un único usuario.

Si aparecen varios usuarios distintos:
`ERROR: Se detectaron múltiples usuarios en el CSV.`

`--usuario` permite override explícito.

## 6. Modelo de datos

Implementar:

```python
@dataclass
class TimeEntry:
    servicio: str
    cliente: str
    proyecto: str
    usuario: str
    lista_tareas: str
    tarea: str
    fecha_entrega: Optional[str]
    horas_estimadas: Optional[str]
    facturable: bool
    facturado: bool
    precio_hora: Optional[str]
    archivado: bool
    fecha_inicio: datetime
    fecha_fin: datetime
    zona_horaria: str
    duracion_str: str
    horas: float
    notas: str
    total: Optional[str]
    costo_hora: Optional[str]
    costo: Optional[str]
    moneda: str
```

Propiedades:
- `fecha -> date`
- `hora_inicio -> time`
- `hora_fin -> time`
- `duracion_timedelta -> timedelta`

## 7. Filtrado mensual

CLI:
```text
--mes 1..12
--anio >= 2000
```

Procesar únicamente registros cuya `Fecha de inicio` pertenezca al mes/año solicitados.

Ejemplo `--mes 8 --anio 2026`:
`01/08/2026 00:00:00` hasta `31/08/2026 23:59:59`.

Comparar usando `datetime/date`, no strings.

Tests obligatorios para límites de mes y cambio de mes.

## 8. Agrupación

Flujo:
```text
TimeEntry[] → filter_by_month() → group_by_client()
```

Clientes ordenados alfabéticamente.

Registros por cliente ordenados por:
1. `fecha_inicio`
2. `fecha_fin`
3. `tarea`

## 9. Resumen general

Primera hoja: `Resumen general`.

Título en `A1:E1`, fusionado:
`Resumen general de horas - {usuario} - {mes_nombre} {año}`

Fila 2: en blanco.

Fila 3:

| Columna | Valor |
|---|---|
| A | Cliente |
| B | Horas totales |
| C | Registros |
| D | Días trabajados |
| E | % del total |

Por cliente:
- A: cliente.
- B: horas totales.
- C: cantidad de registros.
- D: cantidad de fechas distintas.
- E: horas cliente / horas generales.

Los cálculos deben realizarse primero en Python.

Última fila:
- A = `TOTAL GENERAL`
- B = suma horas
- C = suma registros
- D = vacío
- E = suma porcentajes.

Cuando corresponda, usar fórmulas como:
```excel
='Cirion'!K2
=SUM(B4:B5)
=B4/$B$6
```
pero no depender de la recalculación de Excel para la lógica.

## 10. Hojas por cliente

Una hoja por cliente.

Título fusionado `A1:K1`:
`Horas de {usuario} - {cliente} - {mes_nombre} {año}`

Fila 2:
- `A2:H2` fusionado: `Detalle de horas informadas por cliente`
- `I2`: `Total de horas`
- `K2`: `=SUM(I4:I{last_data_row})`

Fila 3:

| Columna | Encabezado |
|---|---|
| A | Usuario |
| B | Proyecto |
| C | Tarea |
| D | Cliente |
| E | Servicio |
| F | Notas |
| G | Fecha |
| H | Duración |
| I | Horas |
| J | Desde |
| K | Hasta |

Mapping:
- A ← Usuario
- B ← Proyecto
- C ← Tarea
- D ← Cliente
- E ← Servicio
- F ← Notas
- G ← Fecha de inicio
- H ← Duración
- I ← Horas
- J ← Fecha de inicio
- K ← Fecha de fin

## 11. Nombres de hojas

Excel permite máximo 31 caracteres y prohíbe:
`\ / * ? [ ] :`

Sanitización base:
```python
invalid = r'[\/*?:\[\]]'
name = re.sub(invalid, '_', name)
name = name[:31]
```

Resolver colisiones determinísticamente:
`Cliente_A`, `Cliente_A_2`, `Cliente_A_3`.

Si hay sufijo, mantener siempre máximo 31 caracteres.

## 12. Formato Excel

Usar `openpyxl>=3.1.0`.

Título:
- bold
- tamaño 14.

Subtítulo:
- bold
- tamaño 11.

Headers:
- bold
- gris claro
- borde fino
- centrado.

Datos:
- borde fino
- texto izquierda
- fechas/horas centradas
- números derecha
- notas con `wrap_text=True`.

Totales:
- bold
- borde inferior doble.

Formatos:
- Horas: `0.00`
- Duración: `[h]:mm`
- Fecha: `dd/mm/yyyy`
- Hora: `h:mm AM/PM`

## 13. Usabilidad

Hojas de cliente:
- `freeze_panes = "A4"`
- autofiltro `A3:K{last_data_row}`
- anchos de columnas razonables
- ancho máximo controlado para evitar columnas gigantes.

## 14. Cálculos de negocio

Python debe calcular:

Por cliente:
- horas totales
- registros
- días trabajados

General:
- horas totales
- registros totales
- porcentaje por cliente

Si horas generales = 0, porcentaje = 0.

## 15. Nombre de salida

```text
Planilla_Horas_{usuario}_{mes_nombre}_{anio}.xlsx
```

Ejemplo:
`Planilla_Horas_Rodrigo_Gil_Agosto_2026.xlsx`

Reemplazar espacios por `_` y sanitizar caracteres inválidos.

## 16. CLI

```text
python -m src.main --mes 8 --anio 2026
```

Parámetros:
```text
--mes       requerido, 1..12
--anio      requerido, >= 2000
--input     default ./input
--output    default ./output
--usuario   opcional
--verbose   opcional
```

## 17. Detección de CSV

Buscar `.csv` en `input`.

Cero:
`No se encontró archivo CSV en input/`

Uno:
procesar.

Más de uno:
`Múltiples archivos CSV encontrados. Deje solo uno.`

Nunca elegir arbitrariamente.

## 18. Sin datos

Si no hay registros del mes:
- warning, no error fatal;
- generar Excel con estructura válida;
- resumen sin registros;
- no crear hojas de cliente vacías.

## 19. Errores

Códigos mínimos:
```text
INPUT_NOT_FOUND
MULTIPLE_INPUT_FILES
INVALID_MONTH
INVALID_YEAR
INVALID_HEADER
INVALID_ROW
INVALID_DATE
INVALID_HOURS
INVALID_DURATION
EMPTY_CLIENT
MULTIPLE_USERS
OUTPUT_ERROR
```

Ejemplo:
`ERROR: Fila 27: valor inválido en 'Horas': 'abc'`

Sin stack trace en modo normal; disponible con `--verbose`.

## 20. Logging y exit codes

Usar `logging` con INFO/WARNING/ERROR/DEBUG.

Exit codes:
```text
0 = éxito
1 = error de datos/validación
2 = error de argumentos/configuración
```

## 21. Arquitectura

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
│   ├── utils.py
│   └── models.py
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_transformer.py
│   ├── test_excel_writer.py
│   ├── test_validators.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── sample.csv
│       └── expected_output.xlsx
├── requirements.txt
├── pyproject.toml
└── README.md
```

Responsabilidades:
- `main.py`: orquestación CLI.
- `parser.py`: CSV → `TimeEntry`.
- `transformer.py`: filtros, agrupación y cálculos.
- `validators.py`: validaciones.
- `exceptions.py`: excepciones de dominio.
- `excel_writer.py`: exclusivamente creación del XLSX.
- `utils.py`: meses, nombres y utilidades.
- `models.py`: dataclasses.

## 22. Dependencias

```toml
[project]
name = "trackingtime-excel"
version = "1.0.0"
description = "Convierte CSV de Tracking Time a planilla Excel mensual"
requires-python = ">=3.10"
dependencies = ["openpyxl>=3.1.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov>=4.0", "ruff>=0.1.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

No agregar `python-dateutil` salvo necesidad demostrable.

## 23. Tests obligatorios

### Parser
- cantidad de registros
- headers
- decimal con coma
- fechas
- horas
- duración
- booleanos
- campos vacíos
- notas multilinea
- duración >24 h
- columnas reordenadas

### Validación
- header faltante
- fecha inválida
- hora inválida
- duración inválida
- cliente vacío
- múltiples usuarios
- mes/año inválidos

### Transformer
- filtrado mensual
- límites de mes
- agrupación
- orden determinista
- usuario
- horas
- registros
- días
- porcentajes
- cero horas

### Excel
- hojas
- orden
- títulos
- merges
- headers
- fórmulas
- datos
- totales
- formatos
- freeze panes
- autofiltro
- sanitización
- colisiones

### Integración
CSV → parser → transformer → Excel → reabrir XLSX con `openpyxl`.

## 24. Golden Master

Utilizar la planilla Excel real como Golden Master funcional/visual.

No comparar byte por byte.

Comparar:
- nombres y orden de hojas
- dimensiones
- títulos
- headers
- datos
- fórmulas
- merges
- formatos
- fuentes
- bordes
- rellenos
- alineaciones
- anchos
- freeze panes
- autofiltro.

Si un detalle del archivo de referencia contradice esta especificación, esta especificación tiene prioridad.

## 25. Archivos reales de referencia

```text
Planilla de tiempo, ago 1,2026 - ago 31,2026 - 80643.csv
Planilla_Horas_Rodrigo_Gil_Agosto_2026.xlsx
```

La IA desarrolladora debe inspeccionarlos antes de finalizar.

Debe documentar discrepancias entre CSV, Excel y esta especificación.

## 26. Performance

Soportar al menos 10.000 registros sin duplicaciones innecesarias de estructuras.

## 27. README

Debe explicar:
1. objetivo
2. requisitos
3. instalación
4. estructura
5. CSV
6. CLI
7. ejemplos
8. errores
9. tests
10. lint
11. mantenimiento
12. limitaciones V1

## 28. Definition of Done

- [ ] CSV real leído correctamente.
- [ ] Headers validados.
- [ ] Fechas correctas.
- [ ] Horas con decimal coma.
- [ ] Duraciones como `timedelta`.
- [ ] Horario local preservado.
- [ ] Filtrado mensual correcto.
- [ ] Usuario detectado.
- [ ] Clientes agrupados.
- [ ] Orden determinista.
- [ ] Resumen general generado.
- [ ] Una hoja por cliente.
- [ ] Nombres sanitizados y colisiones resueltas.
- [ ] Fórmulas requeridas.
- [ ] Totales correctos.
- [ ] Formatos correctos.
- [ ] Freeze panes.
- [ ] Autofiltro.
- [ ] Nombre de archivo correcto.
- [ ] Errores y logging.
- [ ] Exit codes.
- [ ] Idempotencia.
- [ ] Tests.
- [ ] Coverage >80%.
- [ ] Ruff sin errores.
- [ ] README completo.
- [ ] Golden Master validado.

## 29. Interfaz futura IA / Skill

Nombre lógico:
`GENERAR_PLANILLA_HORAS`

Entrada:
```json
{
  "mes": 8,
  "anio": 2026,
  "input_dir": "./input",
  "output_dir": "./output"
}
```

Éxito:
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

Error:
```json
{
  "success": false,
  "error_code": "INVALID_HEADER",
  "message": "El CSV no contiene la columna requerida: Fecha de inicio"
}
```

La IA interpreta la intención y Python ejecuta la lógica determinística.

## 30. Flujo futuro

```text
Usuario
  ↓
IA
  ↓
interpreta intención
  ↓
GENERAR_PLANILLA_HORAS
  ↓
Python
  ↓
CSV → Parser → Validación → Transformación → Excel
  ↓
Resultado
```

## 31. Instrucción final para la IA desarrolladora

Implementa el proyecto completo siguiendo esta especificación.

Antes de escribir código:
1. Inspecciona los archivos reales.
2. Verifica headers y tipos.
3. Inspecciona el workbook de referencia con `openpyxl`.
4. Documenta discrepancias.
5. No inventes columnas ni reglas.
6. Implementa modelos, parser y validaciones.
7. Implementa transformación.
8. Implementa Excel.
9. Implementa tests.
10. Ejecuta tests y lint.
11. Ejecuta end-to-end con el CSV real.
12. Reabre y valida el XLSX generado.
13. Entrega código completo y README.
14. No marques el trabajo como terminado con tests fallando.

Prioridad de fuentes de verdad:
1. Esta especificación.
2. CSV real para contrato de entrada.
3. Excel real para formato/salida.
4. Convenciones Python.

Si el archivo real contradice esta especificación, detenerse y reportar la discrepancia; no resolverla silenciosamente.
