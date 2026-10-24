# CLAUDE.md

> **Project-wide working rules and cross-repo context live in the FCM umbrella repo's `CLAUDE.md`**,
> loaded automatically when you work from the umbrella root. If you opened this repo directly instead
> of via the umbrella, relaunch from the umbrella root for the full context. This file holds only this
> repo's specific instructions.

Instructions for Claude (and other LLM agents) working in this repository.

## What this project is

`evennia-db-threads` runs database work off the [Evennia](https://www.evennia.com/) reactor without
leaving connections behind on the worker thread. One function, `defer_to_db_thread`, a drop-in
replacement for Twisted's `deferToThread` and Evennia's `run_async`. Tagline: **"Leave the reactor
without leaving a connection behind."**

For the overview, read [README.md](README.md). For the docs, read [docs/INDEX.md](docs/INDEX.md).

## Project status

See [docs/progress.md](docs/progress.md).

## Where to read first

1. [README.md](README.md) — what it is and why it matters.
2. [docs/test-plan.md](docs/test-plan.md) — every case, and why. **A behavioural change starts here.**
3. [docs/installing.md](docs/installing.md) — what a consumer does.

## Load-bearing architectural principles

1. **The library does not own game concepts.** It knows about threads and Django connections, and
   nothing about rooms, items or characters.
2. **No FCM-specific assumptions.** Any Evennia game that leaves the reactor for database work can
   use it as it is.
3. **The close runs on the worker thread.** Wrapping the target in a `finally` is the only place it
   reaches the connections that thread opened. See TH-05.
4. **The package root imports neither Django nor Twisted,** so a consumer's settings module can import
   it. See TH-07.
5. **Test-first.** A case lands in [docs/test-plan.md](docs/test-plan.md), then the test, then the
   code.

## Out of scope

- **The reactor thread's own connections.** Those live for the process; a game that needs them dropped
  after a database restart does that itself.
- **Logging — an accepted divergence from the library standard.** `log.py` carries the standard
  binding (`db_threads_log`), but nothing calls it: the function has nothing to report, and a failure
  in the target reaches the caller's errback unchanged. The `library-standards-linter`'s
  `log_shim_unused` warning is expected here; do not "fix" it by adding call sites.

## Working conventions

- **Behavioural change starts in the test plan,** then the test, then the code. Keep the **Test
  function** column current — the linter checks it both ways.
- **License.** BSD 3-Clause. Source files carry `# SPDX-License-Identifier: BSD-3-Clause` on line one.

## Documentation discipline (load-bearing)

Documents in `docs/` record what was discussed and agreed with the project owner — nothing forward
designed or extrapolated. Flag what is open as `[TBD — needs discussion: <what is open>]`. Smaller is
better.

## Repository layout

```
evennia-db-threads/
├── CLAUDE.md
├── README.md
├── LICENSE                    # BSD 3-Clause
├── pyproject.toml
├── runtests.py                # standalone runner, no gamedir needed
├── docs/                      # INDEX, installing, interoperability, progress, test-plan
├── src/
│   └── evennia_db_threads/
│       ├── __init__.py        # the public surface: defer_to_db_thread
│       ├── apps.py            # inert AppConfig
│       ├── log.py             # db_threads_log binding — unused, see Out of scope
│       ├── threads.py         # defer_to_db_thread
│       └── tests.py           # unit tests, run via runtests.py
└── tests/                     # standalone test settings (test_settings.py, urls.py)
```

## Tools and environment

- Python 3.10+, pinned in `pyproject.toml`.
- Runtime dependencies: Evennia (for Django and Twisted) and `evennia-logging-extension`, which is not
  on PyPI — editable-install it from its checkout.
- Tests run through Django's test runner via `python runtests.py`, not pytest.
- A dedicated venv at `venv/` (gitignored).
