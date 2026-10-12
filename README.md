# entirius-py-bievents

Structured JSON business intelligence (BI) event logging on top of Python `logging`, part of
Entirius, the open-source modular ecommerce platform. An event is a class: creating one, or finishing an ongoing one,
writes a single JSON record with its source, status, timing and details to the `business_intelligence` logger.

[![PyPI](https://img.shields.io/pypi/v/entirius-py-bievents.svg)](https://pypi.org/project/entirius-py-bievents/)
[![Python](https://img.shields.io/pypi/pyversions/entirius-py-bievents.svg)](https://pypi.org/project/entirius-py-bievents/)
[![License: MPL-2.0](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://github.com/entirius/entirius-py-bievents/blob/develop/LICENSE)

## What it does

- Logs one JSON record per event: source, business unit, environment, status, start and end time, duration, details.
- Logs one-shot events on creation and ongoing events when they finish (`finish_with_success()`,
  `finish_with_error()`, `finish_with_exception()`).
- Formats the record with `BiFormatter`, so any `logging` handler can carry the events.
- Tracks Celery subtasks, outbound requests and document statuses in the details (`BiCeleryTaskEventAbstract`).
- Records a Django management command run as an event (`bi_django_command_decorator`).

## Installation

```shell
uv add entirius-py-bievents
pip install entirius-py-bievents
```

The import name is `bievents`.

## Quick start

```python
import logging

from bievents import BI_LOGGER_NAME, BiEventAbstract, BiFormatter

handler = logging.FileHandler(filename="bi-events.json.log")
handler.setFormatter(BiFormatter())
logger = logging.getLogger(BI_LOGGER_NAME)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class OrderExported(BiEventAbstract):
    details_type = "Order exported"

OrderExported(source="erp-export", business_unit="store", environment="production", status="success")
```

## Requirements

- Python 3.11 or newer.
- `json-log-formatter` (installed as a dependency).
- Django only for `bi_django_command_decorator`; it is imported lazily and is not a declared dependency.

## Documentation

- Entirius documentation: https://docs.entirius.com/
- Changelog: https://github.com/entirius/entirius-py-bievents/blob/develop/CHANGELOG.md

## Part of Entirius

This library is the BI event layer of the Entirius backend service (Volkanos) and its modules.

- Backend service: https://github.com/entirius/entirius-service-volkanos
- Docker harness: https://github.com/entirius/entirius-zeno
- Consumer modules: https://github.com/entirius/entirius-django-pim, https://github.com/entirius/entirius-django-checkout, https://github.com/entirius/entirius-django-qms

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest)
```

Development and agent instructions: https://github.com/entirius/entirius-py-bievents/blob/develop/AGENTS.md

## License

Mozilla Public License 2.0 (MPL-2.0) — see https://github.com/entirius/entirius-py-bievents/blob/develop/LICENSE.
