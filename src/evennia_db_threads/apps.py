# SPDX-License-Identifier: BSD-3-Clause
"""Django AppConfig for evennia-db-threads.

Inert: the library is one function, imported where it is used, with nothing to
install at boot. Present so the package can sit in ``INSTALLED_APPS`` without
Django complaining; it does not need to be there to work.
"""
from django.apps import AppConfig


class EvenniaDbThreadsConfig(AppConfig):
    name = "evennia_db_threads"
    default_auto_field = "django.db.models.BigAutoField"
