# Installing evennia-db-threads

## 1. Install the package

```bash
pip install -e path/to/evennia-db-threads
```

It depends on `evennia` and `evennia-logging-extension`.

## 2. Import it where work leaves the reactor

```python
from evennia_db_threads import defer_to_db_thread
```

Adding it to `INSTALLED_APPS` is not needed.

## 3. Dispatch through it

```python
defer_to_db_thread(fn, *args, **kwargs).addCallbacks(on_done, on_error)
```

In place of `twisted.internet.threads.deferToThread(fn, …)`, or Evennia's
`run_async(fn, at_return=on_done, at_err=on_error)`. The Deferred is the same, so callbacks and
errbacks are unchanged.

## Settings

There are no settings — no required settings and no optional settings.

## Not checked for you

- **A dispatch that bypasses it.** Work sent off the reactor with `deferToThread` or `run_async`
  directly leaves its thread's connections open, and nothing here can see it.
- **The game loop's own connections.** This library closes worker threads' connections only. The
  reactor thread keeps its own for the life of the process.
