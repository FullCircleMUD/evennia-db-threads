# SPDX-License-Identifier: BSD-3-Clause
"""Minimal Django settings for evennia-db-threads unit tests.

Imports Evennia's defaults, adds the library to INSTALLED_APPS, and uses an
in-memory sqlite test database. No gamedir required.
"""
import os
import sys
import tempfile

import evennia

# Evennia's migrations import ``typeclasses.objects`` (a gamedir module), so its
# game_template goes on sys.path for the import to resolve.
_game_template = os.path.join(os.path.dirname(evennia.__file__), "game_template")
if _game_template not in sys.path:
    sys.path.insert(0, _game_template)

from evennia.settings_default import *  # noqa: F401, F403, E402

GAME_DIR = tempfile.gettempdir()
LOG_DIR = os.path.join(tempfile.gettempdir(), "evennia_db_threads_test_logs")
os.makedirs(LOG_DIR, exist_ok=True)

INSTALLED_APPS = list(INSTALLED_APPS) + ["evennia_db_threads"]  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

SECRET_KEY = "test-only-secret"
ROOT_URLCONF = "tests.urls"
