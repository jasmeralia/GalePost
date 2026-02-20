from PyQt5.QtWidgets import QTextBrowser

from src.gui.update_dialog import UpdateAvailableDialog


def test_update_dialog_renders_markdown_links(qtbot):
    dialog = UpdateAvailableDialog(
        None,
        title='Update Available',
        latest_version='1.2.3',
        current_version='1.2.0',
        release_label='stable',
        release_name='Release 1.2.3',
        release_notes='See [notes](https://example.com).',
    )
    qtbot.addWidget(dialog)

    notes = dialog.findChild(QTextBrowser)
    assert notes is not None
    html = notes.toHtml()
    assert 'href="https://example.com"' in html
    assert notes.openExternalLinks() is True
