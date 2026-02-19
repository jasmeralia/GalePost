import contextlib
import sys
import types

import src.main as app_main


def test_abort_if_elevated(monkeypatch):
    called = {}

    class DummyShell32:
        @staticmethod
        def IsUserAnAdmin():  # noqa: N802
            return 1

    class DummyWindll:
        shell32 = DummyShell32()

    def fake_critical(_parent, _title, _text):
        called['shown'] = True

    monkeypatch.setattr(app_main.sys, 'platform', 'win32')
    fake_ctypes = types.SimpleNamespace(windll=DummyWindll())
    monkeypatch.setitem(sys.modules, 'ctypes', fake_ctypes)
    monkeypatch.setattr(app_main, 'QMessageBox', type('Q', (), {'critical': fake_critical}))

    with contextlib.suppress(SystemExit):
        app_main._abort_if_elevated()

    assert called.get('shown') is True


def test_abort_if_elevated_noop_non_admin(monkeypatch):
    class DummyShell32:
        @staticmethod
        def IsUserAnAdmin():  # noqa: N802
            return 0

    class DummyWindll:
        shell32 = DummyShell32()

    monkeypatch.setattr(app_main.sys, 'platform', 'win32')
    fake_ctypes = types.SimpleNamespace(windll=DummyWindll())
    monkeypatch.setitem(sys.modules, 'ctypes', fake_ctypes)

    app_main._abort_if_elevated()
