from src.gui.log_submit_dialog import LogSubmitDialog


def test_log_submit_dialog_requires_notes(qtbot):
    dialog = LogSubmitDialog()
    qtbot.addWidget(dialog)

    assert not dialog._send_btn.isEnabled()

    dialog._notes.setPlainText('Something went wrong')
    assert dialog._send_btn.isEnabled()
