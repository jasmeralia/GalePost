"""Theme utilities for light/dark mode handling."""

from __future__ import annotations

import sys

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget


def windows_prefers_dark() -> bool:
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


def resolve_theme_mode(mode: str) -> str:
    if mode == 'dark':
        return 'dark'
    if mode == 'light':
        return 'light'
    return 'dark' if windows_prefers_dark() else 'light'


def _apply_dark_palette(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)


def set_windows_dark_title_bar(window: QWidget, enabled: bool) -> None:
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        from ctypes import wintypes

        hwnd = int(window.winId())

        # Attribute values vary by Windows build. Try 20 first, then 19.
        dwmwa_use_immersive_dark_mode = 20
        dwmwa_use_immersive_dark_mode_before_20h1 = 19
        value = wintypes.BOOL(1 if enabled else 0)

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


def apply_theme(app: QApplication, window: QWidget | None, mode: str) -> str:
    resolved = resolve_theme_mode(mode)
    use_dark = resolved == 'dark'

    app.setStyle('Fusion')
    if use_dark:
        _apply_dark_palette(app)
    else:
        style = app.style()
        if style is not None:
            app.setPalette(style.standardPalette())
        else:
            app.setPalette(QPalette())

    if window is not None:
        set_windows_dark_title_bar(window, use_dark)

    return resolved
