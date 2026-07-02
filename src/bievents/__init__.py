from importlib import metadata

from bievents.bi_log_formatter import BiFormatter
from bievents.event_abstract import (
    BI_BUSINESS_UNIT_UNKNOWN,
    BI_EVENT_STATUS_ERROR,
    BI_EVENT_STATUS_EXCEPTION,
    BI_EVENT_STATUS_SUCCESS,
    BI_LOGGER_NAME,
    BiCeleryTaskEventAbstract,
    BiEventAbstract,
    DjangoCommandHasBeenExecutedEvent,
    bi_django_command_decorator,
)

try:
    # dist name (entirius-py-bievents) != import name (bievents)
    __version__ = metadata.version("entirius-py-bievents")
except metadata.PackageNotFoundError:
    __version__ = "99.99.99"


def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value


VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = [
    "BI_BUSINESS_UNIT_UNKNOWN",
    "BI_EVENT_STATUS_ERROR",
    "BI_EVENT_STATUS_EXCEPTION",
    "BI_EVENT_STATUS_SUCCESS",
    "BI_LOGGER_NAME",
    "BiCeleryTaskEventAbstract",
    "BiEventAbstract",
    "BiFormatter",
    "DjangoCommandHasBeenExecutedEvent",
    "bi_django_command_decorator",
]
