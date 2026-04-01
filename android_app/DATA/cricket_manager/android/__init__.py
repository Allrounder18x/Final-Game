"""
Android app support layer for Cricket Manager.

This package is intentionally UI-framework agnostic. The Kivy app, tests, or
other frontends can import `CricketAppService` and `AndroidSaveStore`.
"""

from .service_facade import CricketAppService
from .save_store import AndroidSaveStore

__all__ = ["CricketAppService", "AndroidSaveStore"]
