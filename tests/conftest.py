import os


def pytest_configure():
    if os.environ.get('GITHUB_ACTIONS') == 'true' or os.environ.get('CI') == 'true':
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
