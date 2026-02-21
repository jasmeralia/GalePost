import os
import sys


def pytest_configure():
    if (
        os.environ.get('GITHUB_ACTIONS') == 'true'
        or os.environ.get('CI') == 'true'
        or (
            sys.platform == 'linux'
            and not os.environ.get('DISPLAY')
            and not os.environ.get('WAYLAND_DISPLAY')
        )
    ):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
