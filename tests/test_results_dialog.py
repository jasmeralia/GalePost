"""Tests for results dialog behavior."""

from __future__ import annotations

from types import SimpleNamespace

from PyQt5.QtWidgets import QApplication, QLabel, QPushButton

from src.gui.results_dialog import ResultsDialog
from src.utils.constants import PostResult


def _fake_clipboard(captured):
    def set_text(text):
        captured['text'] = text

    return SimpleNamespace(setText=set_text)


def test_results_dialog_success_shows_links(qtbot, monkeypatch):
    captured = {}
    monkeypatch.setattr(QApplication, 'clipboard', staticmethod(lambda: _fake_clipboard(captured)))

    results = [PostResult(success=True, platform='Twitter', post_url='https://example.com')]
    dialog = ResultsDialog(results)
    qtbot.addWidget(dialog)

    labels = dialog.findChildren(QLabel)
    assert any('https://example.com' in label.text() for label in labels)
    assert any(label.openExternalLinks() for label in labels)

    copy_all = next(
        btn for btn in dialog.findChildren(QPushButton) if btn.text() == 'Copy All Links'
    )
    copy_all.click()

    assert 'https://example.com' in captured['text']


def test_results_dialog_failure_shows_send_logs(qtbot):
    results = [
        PostResult(
            success=False,
            platform='Twitter',
            error_code='POST-FAILED',
            error_message='Failed',
        )
    ]
    dialog = ResultsDialog(results)
    qtbot.addWidget(dialog)

    send_btn = next(
        btn for btn in dialog.findChildren(QPushButton) if btn.text() == 'Send Logs to Jas'
    )
    send_btn.click()

    assert dialog.send_logs_requested


def test_results_dialog_open_settings_sets_result(qtbot):
    results = [
        PostResult(
            success=False,
            platform='Bluesky',
            error_code='BS-AUTH-EXPIRED',
            error_message='Expired',
        )
    ]
    dialog = ResultsDialog(results)
    qtbot.addWidget(dialog)

    settings_btn = next(
        btn for btn in dialog.findChildren(QPushButton) if btn.text() == 'Open Settings'
    )
    settings_btn.click()

    assert dialog.result() == 2
