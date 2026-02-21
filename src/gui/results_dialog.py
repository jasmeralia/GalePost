"""Post results dialog with clickable links and copy buttons."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.core.error_handler import format_error_details
from src.utils.constants import PostResult


class ResultsDialog(QDialog):
    """Display posting results with clickable URLs and copy buttons."""

    def __init__(self, results: list[PostResult], parent=None):
        super().__init__(parent)
        self._results = results
        self._send_logs_requested = False

        self.setWindowTitle('Post Results')
        self.setMinimumWidth(550)

        layout = QVBoxLayout(self)

        for result in results:
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet('QFrame { padding: 8px; margin: 4px; }')
            frame_layout = QVBoxLayout(frame)

            if result.success:
                self._add_success_row(frame_layout, result)
            else:
                self._add_failure_row(frame_layout, result)

            layout.addWidget(frame)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Bottom buttons
        btn_layout = QHBoxLayout()

        # "Send Logs to Jas" if any failures
        has_failure = any(not r.success for r in results)
        if has_failure:
            send_btn = QPushButton('Send Logs to Jas')
            send_btn.clicked.connect(self._on_send_logs)
            btn_layout.addWidget(send_btn)

        # "Copy All Links" if any successes
        success_results = [r for r in results if r.success and r.post_url]
        if success_results:
            copy_all_btn = QPushButton('Copy All Links')
            copy_all_btn.clicked.connect(lambda: self._copy_all_links(success_results))
            btn_layout.addWidget(copy_all_btn)

        btn_layout.addStretch()

        close_btn = QPushButton('Close')
        close_btn.setMinimumWidth(80)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _add_success_row(self, layout: QVBoxLayout, result: PostResult):
        # Show different messages for WebView confirm-click vs API results
        if result.user_confirmed and not result.url_captured:
            header = QLabel(
                f'<span style="color: #4CAF50; font-size: 14px;">'
                f'\u2713 {result.platform} - Posted (link unavailable)</span>'
            )
        else:
            header = QLabel(
                f'<span style="color: #4CAF50; font-size: 14px;">'
                f'\u2713 {result.platform} - Posted successfully!</span>'
            )
        layout.addWidget(header)

        if result.post_url:
            link = QLabel(f'<a href="{result.post_url}">{result.post_url}</a>')
            link.setOpenExternalLinks(True)
            link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            layout.addWidget(link)

            copy_btn = QPushButton('Copy Link')
            copy_btn.setMaximumWidth(100)
            post_url = result.post_url
            copy_btn.clicked.connect(lambda _, url=post_url: self._copy_text(url))
            layout.addWidget(copy_btn)

    def _add_failure_row(self, layout: QVBoxLayout, result: PostResult):
        header = QLabel(
            f'<span style="color: #F44336; font-size: 14px;">'
            f'\u274c {result.platform} - Failed to post</span>'
        )
        layout.addWidget(header)

        msg = QLabel(result.error_message or 'Unknown error')
        msg.setWordWrap(True)
        layout.addWidget(msg)

        if result.error_code:
            code_label = QLabel(f'<b>Error Code:</b> {result.error_code}')
            layout.addWidget(code_label)

        time_label = QLabel(f'<b>Time:</b> {result.timestamp}')
        layout.addWidget(time_label)

        btn_row = QHBoxLayout()

        copy_err_btn = QPushButton('Copy Error Details')
        copy_err_btn.clicked.connect(lambda: self._copy_text(format_error_details(result)))
        btn_row.addWidget(copy_err_btn)

        settings_btn = QPushButton('Open Settings')
        settings_btn.clicked.connect(self._on_open_settings)
        btn_row.addWidget(settings_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _copy_text(self, text: str | None):
        if not text:
            return
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def _copy_all_links(self, results: list[PostResult]):
        lines = [f'{r.platform}: {r.post_url}' for r in results if r.post_url]
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText('\n'.join(lines))

    def _on_send_logs(self):
        self._send_logs_requested = True
        self.accept()

    def _on_open_settings(self):
        # The main window handles this via the dialog result
        self.done(2)  # Custom result code for "open settings"

    @property
    def send_logs_requested(self) -> bool:
        return self._send_logs_requested
