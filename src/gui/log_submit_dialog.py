"""Dialog to collect log submission details from the user."""

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)


class LogSubmitDialog(QDialog):
    """Require a short description before sending logs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Send Logs to Jas')
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)

        label = QLabel(
            'Please describe what you were doing when the error occurred.\n'
            'This helps diagnose the issue faster.'
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self._notes = QTextEdit()
        self._notes.setPlaceholderText(
            'Example: Attached a PNG, selected Twitter + Bluesky, clicked OK...'
        )
        self._notes.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._notes)

        self._buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        self._send_btn = self._buttons.addButton('Send Logs', QDialogButtonBox.AcceptRole)
        self._send_btn.setEnabled(False)
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)
        layout.addWidget(self._buttons)

    def _on_text_changed(self):
        text = self._notes.toPlainText().strip()
        self._send_btn.setEnabled(bool(text))

    def get_notes(self) -> str:
        return self._notes.toPlainText().strip()
