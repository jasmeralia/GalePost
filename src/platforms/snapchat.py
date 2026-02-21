"""Snapchat platform implementation using WebView."""

from src.platforms.base_webview import BaseWebViewPlatform
from src.utils.constants import SNAPCHAT_SPECS, PlatformSpecs


class SnapchatPlatform(BaseWebViewPlatform):
    """Snapchat posting via embedded WebView at web.snapchat.com."""

    COMPOSER_URL = 'https://web.snapchat.com/'
    TEXT_SELECTOR = 'div[contenteditable="true"]'
    SUCCESS_URL_PATTERN = ''  # SPA — URL capture unlikely
    PREFILL_DELAY_MS = 500  # Snapchat SPA loads slowly

    def get_platform_name(self) -> str:
        if self._profile_name:
            return f'Snapchat ({self._profile_name})'
        return 'Snapchat'

    def get_specs(self) -> PlatformSpecs:
        return SNAPCHAT_SPECS
