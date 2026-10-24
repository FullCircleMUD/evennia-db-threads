# Test plan — evennia-db-threads

Every test case this library commits to covering, and the test function that covers it. Behaviour is
agreed here before any test or code is written.

Case IDs are stable and referenceable. Do not renumber; retire an ID rather than reuse it. Every test
function carries its case ID as its docstring, so the trail reads in both directions. An empty **Test
function** cell means the case is agreed but not yet covered.

All test functions live in `src/evennia_db_threads/tests.py`. From the library root:

    python runtests.py

| Prefix | Covers |
|---|---|
| `TH` | `defer_to_db_thread` — leaving the reactor without leaving a connection behind |

## TH — `defer_to_db_thread()`

Django holds connections in thread-local storage, one per thread and alias, opened lazily on first
use. Nothing in a Twisted worker thread ever closes them: the `request_started` / `request_finished`
signals that drive `close_old_connections()` fire for the web request cycle only. A thread dispatched
with `deferToThread` or Evennia's `run_async` opens its connections and keeps them for the life of the
thread, and the reactor's pool holds its threads indefinitely.

Two things follow. **The pool fills:** one idle connection for every alias each pooled thread has
touched, per process. **A connection goes stale:** after a database restart, a thread keeps a dead
connection, and the next job to land on that thread — any job, from any code — fails on it.

**The close happens on the worker thread, and that is the whole design.** The call site, the callback
and the errback all run on the reactor, and `close_all()` there would walk the reactor's own
connections rather than the worker's. Wrapping the target function is the only place a `finally` runs
on the right side of the boundary.

**Imports inside the function.** `django.db` and `twisted` are reached when the function runs, not
when the module loads, so the package root can be imported from a consumer's settings module.

| ID | Case | Test function |
|---|---|---|
| TH-01 | The target's return value arrives through the Deferred | `test_th_01_the_return_value_arrives_through_the_deferred` |
| TH-02 | Positional and keyword arguments reach the target untouched | `test_th_02_arguments_reach_the_target_untouched` |
| TH-03 | The connections are closed after the target returns | `test_th_03_the_connections_are_closed_after_the_target_returns` |
| TH-04 | The connections are closed when the target raises, and the failure still reaches the errback | `test_th_04_the_connections_are_closed_when_the_target_raises` |
| TH-05 | The close runs on the worker thread, not the thread that dispatched | `test_th_05_the_close_runs_on_the_worker_thread` |
| TH-06 | `defer_to_db_thread` resolves from the package root | `test_th_06_the_dispatch_resolves_from_the_package_root` |
| TH-07 | Importing the package root imports neither Django nor Twisted | `test_th_07_the_package_root_imports_neither_django_nor_twisted` |

- **TH-04** is the case that matters in production. A close that ran only on success would leak a
  connection per failure — fastest exactly when things are already going wrong.
- **TH-05** is what a `finally` at the call site would get wrong while looking correct. Asserting
  *where* it ran is the only way to tell the two apart.
- **TH-07** keeps the package importable from settings. A module-scope Django import raises inside a
  consumer's settings module, before the server starts.
