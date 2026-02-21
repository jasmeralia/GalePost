"""Tests for WebView platform infrastructure."""

from src.platforms.base_webview import BaseWebViewPlatform
from src.utils.constants import PlatformSpecs


class ConcreteWebViewPlatform(BaseWebViewPlatform):
    """Minimal concrete implementation for testing."""

    COMPOSER_URL = 'https://example.com/compose'
    TEXT_SELECTOR = 'textarea.composer'
    SUCCESS_URL_PATTERN = r'example\.com/post/\d+'

    def get_platform_name(self) -> str:
        return 'TestPlatform'

    def get_specs(self) -> PlatformSpecs:
        return PlatformSpecs(
            platform_name='TestPlatform',
            max_image_dimensions=(1024, 1024),
            max_file_size_mb=5.0,
            supported_formats=['JPEG', 'PNG'],
            max_text_length=500,
            api_type='webview',
            auth_method='session_cookie',
            requires_user_confirm=True,
        )


def test_base_webview_platform_properties():
    platform = ConcreteWebViewPlatform(
        account_id='test_1',
        profile_name='testuser',
    )
    assert platform.account_id == 'test_1'
    assert platform.profile_name == 'testuser'
    assert platform.get_platform_name() == 'TestPlatform'
    assert platform.get_specs().api_type == 'webview'
    assert platform.get_specs().requires_user_confirm is True


def test_base_webview_authenticate_returns_ok():
    platform = ConcreteWebViewPlatform(account_id='test_1')
    success, error = platform.authenticate()
    assert success is True
    assert error is None


def test_base_webview_build_result_not_confirmed():
    platform = ConcreteWebViewPlatform(account_id='test_1', profile_name='user')
    result = platform.build_result()
    assert result.success is False
    assert result.error_code == 'WV-SUBMIT-TIMEOUT'
    assert result.user_confirmed is False
    assert result.account_id == 'test_1'
    assert result.profile_name == 'user'


def test_base_webview_build_result_confirmed_no_url():
    platform = ConcreteWebViewPlatform(account_id='test_1', profile_name='user')
    platform.mark_confirmed()
    result = platform.build_result()
    assert result.success is True
    assert result.post_url is None
    assert result.url_captured is False
    assert result.user_confirmed is True


def test_base_webview_build_result_confirmed_with_url():
    platform = ConcreteWebViewPlatform(account_id='test_1', profile_name='user')
    platform._post_confirmed = True
    platform._captured_post_url = 'https://example.com/post/12345'
    result = platform.build_result()
    assert result.success is True
    assert result.post_url == 'https://example.com/post/12345'
    assert result.url_captured is True
    assert result.user_confirmed is True


def test_base_webview_post_returns_error():
    """post() on a WebView platform should return an error since it needs the panel."""
    platform = ConcreteWebViewPlatform(account_id='test_1')
    result = platform.post('Hello')
    assert result.success is False
    assert result.error_code == 'WV-PREFILL-FAILED'


def test_webview_panel_importable():
    """Verify the WebView panel module can be imported."""
    from src.gui.webview_panel import WebViewPanel  # noqa: F401
