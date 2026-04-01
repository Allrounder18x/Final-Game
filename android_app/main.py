"""
Kivy/KivyMD Android entry app shell.
"""

from __future__ import annotations

import os
import sys

# Ensure DATA package is importable when launched from project root.
# APK / Buildozer layout: DATA lives next to main.py inside android_app.
# Desktop layout: DATA is sibling of android_app (repo root).
_main_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(_main_dir, "DATA")):
    PROJECT_ROOT = _main_dir
    _repo_root = os.path.dirname(_main_dir)
else:
    PROJECT_ROOT = os.path.dirname(_main_dir)
    _repo_root = PROJECT_ROOT
DATA_DIR = os.path.join(PROJECT_ROOT, "DATA")
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from cricket_manager.android.service_facade import CricketAppService
from android_app.screens import register_screens

KV_ROOT = """
ScreenManager:
"""


class CricketAndroidApp(App):
    def build(self):
        Builder.load_string(KV_ROOT)
        storage_dir = os.path.join(PROJECT_ROOT, "android_runtime")
        self.service = CricketAppService(app_storage_dir=storage_dir)
        self.service.init_new_game()

        manager = ScreenManager()
        register_screens(manager, self.service)
        return manager


if __name__ == "__main__":
    CricketAndroidApp().run()
