"""
Configuración centralizada de logging estructurado (JSON una línea por log).

Uso:
    from API.logging_config import configure_logging
    configure_logging()
    logger = logging.getLogger("iaim.algo")
    logger.info("mensaje", extra={"clave": "valor"})

Variables de entorno:
    LOG_LEVEL   Nivel raíz (DEBUG | INFO | WARNING | ERROR | CRITICAL).
                Por defecto INFO.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone

_LOG_RECORD_BUILTIN_ATTRS = {
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "module", "msecs",
    "message", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName", "taskName",
}


class JsonFormatter(logging.Formatter):
    """Convierte cada LogRecord en una línea JSON apta para Render/Datadog/etc."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Adjunta los campos extra pasados como `extra={...}`
        for key, value in record.__dict__.items():
            if key in _LOG_RECORD_BUILTIN_ATTRS:
                continue
            payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    """Configura el logger raíz para emitir JSON a stdout."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Uvicorn ya emite su propio access log; lo silenciamos para no duplicar
    # (nuestro middleware en main.py registra cada request en formato JSON).
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False

    # Que los logs de uvicorn (startup, shutdown, errores) también salgan en JSON.
    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
