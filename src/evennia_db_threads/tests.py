# SPDX-License-Identifier: BSD-3-Clause
"""evennia-db-threads' tests. The cases are in docs/test-plan.md.

``deferToThread`` is replaced with a real thread joined at once, so each
dispatch runs to completion in the test, on a thread that is not the test's.
"""
import sys
import threading
import unittest
from unittest import mock

from twisted.internet import defer
from twisted.python.failure import Failure

from evennia_db_threads import defer_to_db_thread


def _on_a_real_thread(target):
    """Stand in for ``deferToThread``: run ``target`` on a new thread, wait for
    it, and hand back an already-fired Deferred."""
    outcome = {}

    def wrapper():
        try:
            outcome["value"] = target()
        except BaseException:
            outcome["failure"] = Failure()

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join()

    if "failure" in outcome:
        return defer.fail(outcome["failure"])
    return defer.succeed(outcome["value"])


class DeferToDbThreadTest(unittest.TestCase):
    """TH — leaving the reactor without leaving a connection behind."""

    def dispatch(self, fn, *args, **kwargs):
        """Run a dispatch to completion and return what the Deferred fired."""
        fired = {}
        with mock.patch(
            "twisted.internet.threads.deferToThread", side_effect=_on_a_real_thread
        ):
            deferred = defer_to_db_thread(fn, *args, **kwargs)
        deferred.addBoth(lambda result: fired.setdefault("result", result))
        return fired["result"]

    def test_th_01_the_return_value_arrives_through_the_deferred(self):
        """TH-01"""
        with mock.patch("django.db.connections.close_all"):
            self.assertEqual(self.dispatch(lambda: "answer"), "answer")

    def test_th_02_arguments_reach_the_target_untouched(self):
        """TH-02"""
        seen = {}

        def target(first, second, third=None):
            seen.update(first=first, second=second, third=third)

        with mock.patch("django.db.connections.close_all"):
            self.dispatch(target, 1, 2, third=3)

        self.assertEqual(seen, {"first": 1, "second": 2, "third": 3})

    def test_th_03_the_connections_are_closed_after_the_target_returns(self):
        """TH-03"""
        with mock.patch("django.db.connections.close_all") as closed:
            self.dispatch(lambda: None)

        closed.assert_called_once_with()

    def test_th_04_the_connections_are_closed_when_the_target_raises(self):
        """TH-04"""

        def target():
            raise RuntimeError("the query went wrong")

        with mock.patch("django.db.connections.close_all") as closed:
            result = self.dispatch(target)

        closed.assert_called_once_with()
        self.assertEqual(result.type, RuntimeError)

    def test_th_05_the_close_runs_on_the_worker_thread(self):
        """TH-05"""
        dispatching = threading.current_thread().ident
        seen = {}

        def target():
            seen["target"] = threading.current_thread().ident

        def closing():
            seen["close"] = threading.current_thread().ident

        with mock.patch("django.db.connections.close_all", side_effect=closing):
            self.dispatch(target)

        self.assertEqual(seen["close"], seen["target"], "the close ran on a different thread from the work")
        self.assertNotEqual(
            seen["close"],
            dispatching,
            "the close ran on the dispatching thread, whose connections are not the ones that were opened",
        )


class DeferToDbThreadSurfaceTest(unittest.TestCase):
    """TH — the name is published, and publishing it costs nothing at import."""

    def test_th_06_the_dispatch_resolves_from_the_package_root(self):
        """TH-06"""
        import evennia_db_threads

        self.assertIn("defer_to_db_thread", evennia_db_threads.__all__)
        self.assertIs(evennia_db_threads.defer_to_db_thread, defer_to_db_thread)

    def test_th_07_the_package_root_imports_neither_django_nor_twisted(self):
        """TH-07"""
        # A subprocess, because this suite has already imported both. Only a
        # fresh interpreter can say what importing the package alone pulls in.
        import subprocess

        source = (
            "import sys, evennia_db_threads;"
            " bad = [m for m in sys.modules"
            " if m == 'django' or m.startswith('django.')"
            " or m == 'twisted' or m.startswith('twisted.')];"
            " sys.exit(1 if bad else 0)"
        )
        result = subprocess.run([sys.executable, "-c", source], capture_output=True)

        self.assertEqual(
            result.returncode,
            0,
            "importing the package root pulled in Django or Twisted, which raises inside a "
            f"consumer's settings module: {result.stderr.decode()}",
        )
