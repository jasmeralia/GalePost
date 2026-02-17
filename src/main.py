"""GaleFling - Application entry point."""

import os
import sys

# Ensure src is importable when running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from src.core.auth_manager import AuthManager
from src.core.config_manager import ConfigManager
from src.core.logger import setup_logging
from src.gui.main_window import MainWindow
from src.utils.constants import APP_NAME


def _windows_prefers_dark() -> bool:
    if sys.platform != 'win32':
        return False
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize',
        )
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        return value == 0
    except Exception:
        return False


def _set_windows_dark_title_bar(window: MainWindow) -> None:
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        from ctypes import wintypes

        hwnd = int(window.winId())

        # Attribute values vary by Windows build. Try 20 first, then 19.
        dwmwa_use_immersive_dark_mode = 20
        dwmwa_use_immersive_dark_mode_before_20h1 = 19
        value = wintypes.BOOL(1)

        dwmapi = ctypes.WinDLL('dwmapi', use_last_error=True)
        for attr in (dwmwa_use_immersive_dark_mode, dwmwa_use_immersive_dark_mode_before_20h1):
            dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(hwnd),
                wintypes.DWORD(attr),
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
    except Exception:
        # Best-effort only. If this fails, the title bar stays default.
        return


def _apply_dark_palette(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)


def main():
    # Initialize config first
    config = ConfigManager()

    # Set up logging
    setup_logging(debug_mode=config.debug_mode)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    if _windows_prefers_dark():
        app.setStyle('Fusion')
        _apply_dark_palette(app)

    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # Initialize auth
    auth_manager = AuthManager()

    # Create and show main window
    window = MainWindow(config, auth_manager)
    window.show()
    if _windows_prefers_dark():
        _set_windows_dark_title_bar(window)

    # Post-show actions
    window.restore_draft()
    window.check_for_updates_on_startup()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
