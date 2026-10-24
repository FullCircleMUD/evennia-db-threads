# Interoperability

This library against every sibling in `libraries/`. It is one function: run work on a Twisted worker
thread and close that thread's database connections when the work ends. It registers nothing, owns no
tables, reads no settings and makes no query of its own, so it imposes nothing on any sibling.

**It imports one sibling,** `evennia-logging-extension`, for the `log.py` binding. A sibling that
dispatches database work off the reactor uses it, and declares that dependency in its own
`interoperability.md`.

## evennia-ai-memory

**No coupling** from this side. Ai-memory dispatches its memory work off the reactor with
`defer_to_db_thread`, so its worker threads release their connections.

## evennia-archive

**No coupling.** The archive's expensive finds are meant to run off the reactor; a consumer wraps them
in `defer_to_db_thread`.

## evennia-calendar

**No coupling.**

## evennia-database-cascade

**No coupling.** The cascade multiplies a game's aliases — one idle connection per alias per worker
thread is what this library keeps from piling up. Neither imports the other.

## evennia-db-threads

This library.

## evennia-effects-conditions

**No coupling.**

## evennia-environment

**No coupling.**

## evennia-equipment

**No coupling.**

## evennia-llm-service

**No coupling.**

## evennia-logging-extension

**Hard dependency.** `log.py` binds `db_threads_log` through `make_logger`. Nothing calls it yet — see
`CLAUDE.md` § Out of scope.

## evennia-message-bus

**No coupling.**

## evennia-mob-spawner

**No coupling** from this side. The spawner's load commands dispatch with `defer_to_db_thread`.

## evennia-portal-multiplex

**No coupling.**

## evennia-scaling

**No coupling.**

## evennia-survival

**No coupling.**

## evennia-targeting

**No coupling.**

## evennia-world-builder

**No coupling** from this side. `wb_build` dispatches with `defer_to_db_thread`.

## evennia-yaml-reader

**No coupling.**

## fcm-subscriptions

**No coupling** from this side. Its commands dispatch with `defer_to_db_thread`.

## fcm-xrpl

**No coupling** from this side. Its commands and its settling of open intents dispatch with
`defer_to_db_thread`.
