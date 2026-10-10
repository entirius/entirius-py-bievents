# AGENTS.md

Business Intelligence events — structured JSON BI event logging on top of Python `logging`.
Distribution `entirius-py-bievents`, import `bievents`.

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the import package `bievents` — it is a public API contract.
- Default: do not commit — git is the user's call.
- No AI attribution in commits or PR descriptions.

## Architecture

- `bievents/__init__.py` — public API and constants (`BI_LOGGER_NAME`, event statuses).
- `bievents/bi_log_formatter.py` — `BiFormatter` (JSON formatter over `json-log-formatter`).
- `bievents/event_abstract.py` — core: `BiEventAbstract` (one-shot and ongoing events, success/error/exception,
  MRO-based versioning), `BiCeleryTaskEventAbstract` (Celery task counters),
  `bi_django_command_decorator` (Django command events; Django/Celery imported lazily, not declared as deps).
