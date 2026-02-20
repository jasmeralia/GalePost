"""Tests for platform client behavior with mocked APIs."""

from __future__ import annotations

from types import SimpleNamespace

from src.platforms.bluesky import BlueskyPlatform
from src.platforms.twitter import TwitterPlatform


class _FakeAuth:
    def __init__(self, twitter=None, bluesky=None):
        self._twitter = twitter
        self._bluesky = bluesky

    def get_twitter_auth(self):
        return self._twitter

    def get_bluesky_auth(self):
        return self._bluesky


class _FakeOAuth:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class _FakeTwitterAPI:
    def __init__(self, auth):
        self.auth = auth

    def media_upload(self, filename):
        return SimpleNamespace(media_id='media123')


class _FakeTwitterClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._me = SimpleNamespace(data=SimpleNamespace(username='tester'))

    def get_me(self):
        return self._me

    def create_tweet(self, text, media_ids=None):
        return SimpleNamespace(data={'id': 'tweet123'})


class _UnauthorizedError(Exception):
    pass


class _TooManyRequestsError(Exception):
    pass


class _ForbiddenError(Exception):
    pass


def test_twitter_post_success(monkeypatch, tmp_path):
    import src.platforms.twitter as twitter_mod

    fake_tweepy = SimpleNamespace(
        OAuth1UserHandler=_FakeOAuth,
        API=_FakeTwitterAPI,
        Client=_FakeTwitterClient,
        Unauthorized=_UnauthorizedError,
        TooManyRequests=_TooManyRequestsError,
        Forbidden=_ForbiddenError,
    )
    monkeypatch.setattr(twitter_mod, 'tweepy', fake_tweepy)

    auth = _FakeAuth(
        twitter={
            'api_key': 'k',
            'api_secret': 's',
            'access_token': 't',
            'access_token_secret': 'ts',
            'username': 'tester',
        }
    )
    platform = TwitterPlatform(auth)

    image_path = tmp_path / 'image.png'
    image_path.write_bytes(b'data')

    result = platform.post('Hello', image_path=image_path)

    assert result.success
    assert result.post_url == 'https://twitter.com/tester/status/tweet123'


def test_twitter_test_connection_unauthorized(monkeypatch):
    import src.platforms.twitter as twitter_mod

    class _BadClient(_FakeTwitterClient):
        def get_me(self):
            raise _UnauthorizedError('nope')

    fake_tweepy = SimpleNamespace(
        OAuth1UserHandler=_FakeOAuth,
        API=_FakeTwitterAPI,
        Client=_BadClient,
        Unauthorized=_UnauthorizedError,
        TooManyRequests=_TooManyRequestsError,
        Forbidden=_ForbiddenError,
    )
    monkeypatch.setattr(twitter_mod, 'tweepy', fake_tweepy)

    auth = _FakeAuth(
        twitter={
            'api_key': 'k',
            'api_secret': 's',
            'access_token': 't',
            'access_token_secret': 'ts',
            'username': 'tester',
        }
    )
    platform = TwitterPlatform(auth)

    success, error = platform.test_connection()

    assert not success
    assert error == 'TW-AUTH-EXPIRED'


class _FakeBskyClient:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.me = SimpleNamespace(did='did:plc:123', handle='user.bsky.social')
        self.com = SimpleNamespace(
            atproto=SimpleNamespace(repo=SimpleNamespace(create_record=self._create_record))
        )

    def login(self, identifier, app_password):
        self._login = (identifier, app_password)

    def get_profile(self, did):
        return SimpleNamespace(handle='user.bsky.social')

    def upload_blob(self, img_data):
        return SimpleNamespace(blob='blobdata')

    def _create_record(self, data):
        return SimpleNamespace(uri='at://did/app.bsky.feed.post/abc123', cid='cid123')


class _FailingBskyClient(_FakeBskyClient):
    def upload_blob(self, img_data):
        raise RuntimeError('upload failed')


def test_bluesky_post_success(monkeypatch, tmp_path):
    import src.platforms.bluesky as bluesky_mod

    monkeypatch.setattr(bluesky_mod, 'BskyClient', _FakeBskyClient)

    auth = _FakeAuth(
        bluesky={
            'identifier': 'user.bsky.social',
            'app_password': 'pw',
            'service': 'https://bsky.social',
        }
    )
    platform = BlueskyPlatform(auth)

    image_path = tmp_path / 'image.png'
    image_path.write_bytes(b'data')

    result = platform.post('Hello', image_path=image_path)

    assert result.success
    assert result.post_url.endswith('/post/abc123')


def test_bluesky_image_upload_failure(monkeypatch, tmp_path):
    import src.platforms.bluesky as bluesky_mod

    monkeypatch.setattr(bluesky_mod, 'BskyClient', _FailingBskyClient)

    auth = _FakeAuth(
        bluesky={
            'identifier': 'user.bsky.social',
            'app_password': 'pw',
            'service': 'https://bsky.social',
        }
    )
    platform = BlueskyPlatform(auth)

    image_path = tmp_path / 'image.png'
    image_path.write_bytes(b'data')

    result = platform.post('Hello', image_path=image_path)

    assert not result.success
    assert result.error_code == 'IMG-UPLOAD-FAILED'
