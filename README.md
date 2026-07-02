# bievents

Business Intelligence events — structured JSON BI event logging on top of Python `logging`.

## Installation

```shell
pip install git+https://github.com/entirius/entirius-py-bievents.git@v2.0.0
```

(PyPI release planned: `pip install entirius-py-bievents`.)

## Example usage

Emitting a simple event:

```python
import logging
from bievents import (
    BiFormatter,
    BI_LOGGER_NAME,
    BiEventAbstract,
)

json_handler = logging.FileHandler(filename="example-json.log")
json_handler.setFormatter(BiFormatter())
logger = logging.getLogger(BI_LOGGER_NAME)
logger.addHandler(json_handler)
logger.setLevel(logging.DEBUG)


class SimpleEvent(BiEventAbstract):
    details_type = "Simple Event test"
    version = 2


SimpleEvent(
    source="example source name",
    business_unit="example business unit",
    environment="example environment",
    status="success",
)
```

The code above appends one JSON event to `example-json.log`:

```json
{
  "details_type": "Simple Event test",
  "event_source": "example source name",
  "business_unit": "example business unit",
  "environment": "example environment",
  "id": "199f75bb-260b-46e2-8c8d-3463b9981c92",
  "version": "0.0.1",
  "status": "success",
  "resources": [
    "xxxx"
  ],
  "is_ongoing_event": false,
  "time_start": "2022-05-13T12:29:35.705751+00:00",
  "time_end": "2022-05-13T12:29:35.705751+00:00",
  "time_duration": 0,
  "details": {}
}
```

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest)
```

Development and agent instructions: [AGENTS.md](AGENTS.md).

## License

Mozilla Public License 2.0 — see [LICENSE](LICENSE).
