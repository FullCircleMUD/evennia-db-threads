# SPDX-License-Identifier: BSD-3-Clause
"""Worker-thread dispatch that releases its database connections. See TH in
docs/test-plan.md.

Django holds connections in thread-local storage, one per thread and alias, and
nothing in a Twisted worker thread ever closes them. Left open they fill the
database's connection limit, and after a database restart they go dead for
whichever job lands on that thread next.

**The close has to happen on the worker thread.** The call site, the callback
and the errback all run on the reactor, and closing there would walk the
reactor's own connections. Wrapping the target is the only place a ``finally``
runs on the right side of the boundary.

**The imports are inside the function,** so importing the package imports
neither Django nor Twisted and a consumer's settings module can do it.
"""


def defer_to_db_thread(fn, *args, **kwargs):
    """Run ``fn`` on a worker thread, closing its connections afterwards.

    A drop-in replacement for ``twisted.internet.threads.deferToThread`` — same
    argument forwarding, same Deferred, so callbacks and errbacks are
    unchanged. The connections close in a ``finally``, so the failure path
    releases them too.

    Args:
        fn (callable): the blocking work, run on a worker thread.
        *args: positional arguments for ``fn``.
        **kwargs: keyword arguments for ``fn``.

    Returns:
        Deferred: fires with ``fn``'s return value, or its failure.
    """
    from django.db import connections
    from twisted.internet import threads

    def run():
        try:
            return fn(*args, **kwargs)
        finally:
            connections.close_all()

    return threads.deferToThread(run)
