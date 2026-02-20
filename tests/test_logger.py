"""Tests for logging utilities."""

from __future__ import annotations

import src.core.logger as logger


def test_setup_logging_creates_log_file(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, 'get_logs_dir', lambda: tmp_path)

    log = logger.setup_logging(debug_mode=False)
    path = logger.get_current_log_path()

    assert path is not None
    assert path.exists()
    assert log.name == 'GaleFling'


def test_reset_log_file_rotates(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, 'get_logs_dir', lambda: tmp_path)

    logger.setup_logging(debug_mode=False)
    first_path = logger.get_current_log_path()

    logger.reset_log_file()
    second_path = logger.get_current_log_path()

    assert first_path is not None
    assert second_path is not None
    assert second_path.exists()


def test_log_error_writes_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, 'get_logs_dir', lambda: tmp_path)
    monkeypatch.setattr(logger, 'capture_screenshot', lambda *_: None)

    logger.setup_logging(debug_mode=False)

    logger.log_error('POST-FAILED', 'Twitter', details={'info': 'bad'})

    path = logger.get_current_log_path()
    assert path is not None
    content = path.read_text()
    assert 'POST-FAILED' in content
    assert 'Twitter' in content
