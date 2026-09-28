import pytest

from domain.exceptions import InvalidUrlError, InvalidShortCodeError
from domain.models import ShortLink


@pytest.mark.unit
def test_create_valid_short_link():
    url = "https://example.com"
    short_code = "123abc"

    ShortLink.create(url, short_code)


@pytest.mark.unit
def test_create_short_link_invalid_url():
    short_code = "123abc"
    urls = [
        "abc",
    ]

    for url in urls:
        with pytest.raises(InvalidUrlError):
            ShortLink.create(url, short_code)


@pytest.mark.unit
def test_create_short_link_invalid_code():
    url = "https://example.com"

    short_codes = [
        "123ab",
        "///",
        "12345.",
        "123ABC",
    ]

    for short_code in short_codes:
        with pytest.raises(InvalidShortCodeError):
            ShortLink.create(url, short_code)
