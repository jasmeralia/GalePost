"""GaleFling - Application entry point."""

import os
import sys
import threading

# Ensure src is importable when running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox

from src.core.auth_manager import AuthManager
from src.core.config_manager import ConfigManager
from src.core.logger import get_logger, setup_logging
from src.gui.main_window import MainWindow
from src.utils.constants import APP_NAME, APP_ORG
from src.utils.theme import apply_theme


def _abort_if_elevated():
    if sys.platform != 'win32':
        return
    try:
        import ctypes

        shell32 = ctypes.windll.shell32  # type: ignore[attr-defined]
        if shell32.IsUserAnAdmin() != 0:
            QMessageBox.critical(
                None,
                'Administrator Mode Not Supported',
                f'{APP_NAME} cannot run as administrator. Please launch it normally.',
            )
            sys.exit(1)
    except Exception:
        return


def main():
    # Initialize config first
    config = ConfigManager()

    # Set up logging
    setup_logging(debug_mode=config.debug_mode)
    _install_exception_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORG)
    apply_theme(app, None, config.theme_mode)
    _abort_if_elevated()

    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # Initialize auth
    auth_manager = AuthManager()

    # Create and show main window
    window = MainWindow(config, auth_manager)
    window.show()
    apply_theme(app, window, config.theme_mode)

    # Post-show actions
    window.restore_draft()
    window.check_for_updates_on_startup()

    sys.exit(app.exec_())


def _install_exception_logging():
    logger = get_logger()

    def handle_exception(exc_type, exc, tb):
        logger.error('Unhandled exception', exc_info=(exc_type, exc, tb))
        QMessageBox.critical(
            None,
            'Unexpected Error',
            'An unexpected error occurred. Please send your logs to Jas for support.',
        )

    def handle_thread_exception(args):
        logger.error(
            'Unhandled thread exception',
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = handle_exception
    if hasattr(threading, 'excepthook'):
        threading.excepthook = handle_thread_exception


if __name__ == '__main__':
    main()
