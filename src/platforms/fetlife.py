"""FetLife platform implementation using WebView."""

from src.platforms.base_webview import BaseWebViewPlatform
from src.utils.constants import FETLIFE_SPECS, PlatformSpecs


class FetLifePlatform(BaseWebViewPlatform):
    """FetLife posting via embedded WebView (traditional MPA)."""

    COMPOSER_URL = 'https://fetlife.com/statuses/new'
    TEXT_SELECTOR = 'textarea#status_body'
    SUCCESS_URL_PATTERN = r'fetlife\.com/users/\d+/statuses/\d+'
    SUCCESS_SELECTOR = ''
    PREFILL_DELAY_MS = 200  # Traditional server-rendered pages load fast

    def get_platform_name(self) -> str:
        if self._profile_name:
            return f'FetLife ({self._profile_name})'
        return 'FetLife'

    def get_specs(self) -> PlatformSpecs:
        return FETLIFE_SPECS
