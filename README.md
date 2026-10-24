# evennia-db-threads

Run database work off the Evennia reactor without leaving connections behind on the worker thread.

```python
from evennia_db_threads import defer_to_db_thread

defer_to_db_thread(fn, *args, **kwargs).addCallbacks(on_done, on_error)
```

A drop-in replacement for Twisted's `deferToThread` and Evennia's `run_async`. The work runs on a
worker thread, and every database connection that thread opened is closed when the work ends —
returned or raised.

**Why it matters.** Django keeps one connection per thread and alias, and nothing closes a worker
thread's. Left open, they fill the database's connection limit; after a database restart they go
dead, and the next job to land on that thread — from any code — fails on one.

Install: [docs/installing.md](docs/installing.md). Behaviour, case by case:
[docs/test-plan.md](docs/test-plan.md).
