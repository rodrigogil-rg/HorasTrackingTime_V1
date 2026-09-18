from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass
class TimeEntry:
    """Modela un registro individual de tiempo exportado desde Tracking Time."""

    servicio: str | None
    cliente: str
    proyecto: str
    usuario: str
    lista_tareas: str | None
    tarea: str
    fecha_entrega: str | None
    horas_estimadas: str | None
    facturable: bool
    facturado: bool
    precio_hora: str | None
    archivado: bool
    fecha_inicio: datetime
    fecha_fin: datetime
    zona_horaria: str
    duracion_str: str
    horas: float
    notas: str
    total: str | None
    costo_hora: str | None
    costo: str | None
    moneda: str

    @property
    def fecha(self) -> date:
        """Extrae la fecha de inicio como objeto date."""
        return self.fecha_inicio.date()

    @property
    def hora_inicio(self) -> time:
        """Extrae la hora de inicio como objeto time."""
        return self.fecha_inicio.time()

    @property
    def hora_fin(self) -> time:
        """Extrae la hora de fin como objeto time."""
        return self.fecha_fin.time()

    @property
    def duracion_timedelta(self) -> timedelta:
        """Convierte la duración en formato string H:MM:SS a un objeto timedelta."""
        parts = self.duracion_str.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return timedelta(hours=h, minutes=m, seconds=s)
        elif len(parts) == 2:
            h, m = map(int, parts)
            return timedelta(hours=h, minutes=m)
        return timedelta()
