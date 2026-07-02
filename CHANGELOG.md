# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-07-02

Initial public release.

### Added

- `BiEventAbstract` — one-shot and ongoing BI events (success / error / exception statuses,
  duration measurement, MRO-based versioning).
- `BiCeleryTaskEventAbstract` — BI events for Celery tasks (subtask / request / document counters).
- `bi_django_command_decorator` — BI events for Django management commands.
- `BiFormatter` — JSON log formatter (via `json-log-formatter`).
- Toolchain: uv (env + lock), ruff (lint + format), hatchling (build), pytest;
  MPL-2.0 with per-file headers; pre-commit + CI (lint, test, secret-scan).
