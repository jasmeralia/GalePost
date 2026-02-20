"""Tests for utility helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import src.utils.helpers as helpers


def test_get_app_data_dir_linux(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    monkeypatch.setattr(Path, 'home', lambda: tmp_path)

    app_dir = helpers.get_app_data_dir()

    assert app_dir == tmp_path / '.config' / 'GaleFling'
    assert app_dir.exists()


def test_get_app_data_dir_windows_uses_appdata(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setenv('APPDATA', str(tmp_path / 'AppData' / 'Roaming'))

    app_dir = helpers.get_app_data_dir()

    assert app_dir == tmp_path / 'AppData' / 'Roaming' / 'GaleFling'
    assert app_dir.exists()


def test_get_installation_id_is_persistent(tmp_path, monkeypatch):
    monkeypatch.setattr(helpers, 'get_app_data_dir', lambda: tmp_path)

    first = helpers.get_installation_id()
    second = helpers.get_installation_id()

    assert first == second
    assert (tmp_path / 'installation_id').exists()


def test_get_resource_path_non_frozen(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'frozen', False, raising=False)
    base = Path(helpers.__file__).resolve().parent.parent.parent

    resource = helpers.get_resource_path('icon.png')

    assert resource == base / 'resources' / 'icon.png'


def test_get_resource_path_frozen(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    (tmp_path / 'resources').mkdir()

    resource = helpers.get_resource_path('icon.png')

    assert resource == tmp_path / 'resources' / 'icon.png'


def test_get_os_info_windows_11(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setattr(helpers.platform, 'win32_ver', lambda: ('10', '10.0.22000', 'SP0', ''))

    info = helpers.get_os_info()

    assert info['name'] == 'Windows'
    assert info['release'] == '11'
    assert 'Windows-11' in info['platform']


def test_get_os_info_non_windows(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    monkeypatch.setattr(helpers.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(helpers.platform, 'release', lambda: '6.1')
    monkeypatch.setattr(helpers.platform, 'version', lambda: '#1')
    monkeypatch.setattr(helpers.platform, 'platform', lambda: 'Linux-6.1')

    info = helpers.get_os_info()

    assert info['name'] == 'Linux'
    assert info['release'] == '6.1'
    assert info['platform'] == 'Linux-6.1'
