"""Tests for crash logging and exception hooks."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src import main as main_module
from src.core import logger as logger_module


def _capture_exception():
    try:
        raise RuntimeError('boom')
    except RuntimeError as exc:
        return exc, exc.__traceback__


def _set_logs_dir(monkeypatch: pytest.MonkeyPatch, path: Path) -> None:
    monkeypatch.setattr(main_module, 'get_logs_dir', lambda: path)
    monkeypatch.setattr(logger_module, 'get_logs_dir', lambda: path)


def test_write_crash_log_creates_file(tmp_path, monkeypatch):
    _set_logs_dir(monkeypatch, tmp_path)
    exc, tb = _capture_exception()

    main_module._write_crash_log(type(exc), exc, tb, context='test')

    crash_files = list(tmp_path.glob('crash_*.log'))
    assert crash_files, 'Expected crash log file to be created.'
    content = crash_files[0].read_text(encoding='utf-8')
    assert 'RuntimeError' in content
    assert 'boom' in content


def test_sys_excepthook_writes_crash_log(tmp_path, monkeypatch):
    _set_logs_dir(monkeypatch, tmp_path)
    monkeypatch.setattr(main_module, '_FAULT_LOG_FILE', None)
    monkeypatch.setattr(main_module.faulthandler, 'enable', lambda **_: None)
    monkeypatch.setattr(main_module.QMessageBox, 'critical', lambda *args, **kwargs: None)

    original_hook = sys.excepthook
    main_module._install_exception_logging()

    exc, tb = _capture_exception()
    sys.excepthook(type(exc), exc, tb)

    sys.excepthook = original_hook

    crash_files = list(tmp_path.glob('crash_*.log'))
    assert crash_files, 'Expected crash log file to be created via excepthook.'
