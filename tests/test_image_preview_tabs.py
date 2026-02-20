"""Tests for image preview tabs and dialog."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from src.gui.image_preview_tabs import ImagePreviewDialog, ImagePreviewTab, _format_size
from src.utils.constants import TWITTER_SPECS


def _write_image(path: Path, size=(10, 10), color=(255, 0, 0)) -> Path:
    image = Image.new('RGB', size, color)
    image.save(path)
    return path


def test_format_size():
    assert _format_size(10) == '10 B'
    assert _format_size(2048).endswith('KB')
    assert _format_size(5 * 1024 * 1024).endswith('MB')


def test_cached_preview_tab_loads_cached_image(qtbot, tmp_path):
    original = _write_image(tmp_path / 'original.png')
    cached = _write_image(tmp_path / 'cached.png', size=(20, 20))

    tab = ImagePreviewTab(original, TWITTER_SPECS, cached_path=cached)
    qtbot.addWidget(tab)

    tab.load_preview()

    assert tab.get_processed_path() == cached
    assert tab._progress.value() == 100
    assert 'Cached preview' in tab._status_label.text()
    assert 'Cached' in tab._details_label.text()

    pixmap = tab._preview_label.pixmap()
    assert pixmap is not None
    assert pixmap.width() > 0


def test_preview_dialog_with_cached_paths_enables_ok(qtbot, tmp_path):
    original = _write_image(tmp_path / 'original.png')
    cached_tw = _write_image(tmp_path / 'tw.png', size=(30, 30))
    cached_bs = _write_image(tmp_path / 'bs.png', size=(40, 40))

    dialog = ImagePreviewDialog(
        original,
        ['twitter', 'bluesky'],
        existing_paths={'twitter': cached_tw, 'bluesky': cached_bs},
    )
    qtbot.addWidget(dialog)

    assert dialog._ok_btn.isEnabled()
    paths = dialog.get_processed_paths()
    assert paths['twitter'] == cached_tw
    assert paths['bluesky'] == cached_bs


def test_preview_dialog_without_platforms_enables_ok(qtbot, tmp_path):
    original = _write_image(tmp_path / 'original.png')

    dialog = ImagePreviewDialog(original, [])
    qtbot.addWidget(dialog)

    assert dialog._ok_btn.isEnabled()
