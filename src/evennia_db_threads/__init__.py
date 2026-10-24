# SPDX-License-Identifier: BSD-3-Clause
"""evennia-db-threads — run database work off the Evennia reactor without
leaving connections behind on the worker thread.

    from evennia_db_threads import defer_to_db_thread

    defer_to_db_thread(fn, *args, **kwargs).addCallbacks(on_done, on_error)

A drop-in replacement for Twisted's ``deferToThread`` and Evennia's
``run_async``: the same Deferred, and the worker's database connections are
closed when the work ends, however it ends.

Importing the package imports neither Django nor Twisted, so a consumer's
settings module can import it.
"""

from evennia_db_threads.threads import defer_to_db_thread

__version__ = "0.0.1"

__all__ = ["defer_to_db_thread"]
