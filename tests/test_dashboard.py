from __future__ import annotations

import importlib


def test_dashboard_imports_without_error():
    importlib.import_module("app.streamlit_app")
