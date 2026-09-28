import uuid

import pytest

from domain.models import ShortLink
from domain.value_objects import Url, ShortCode


@pytest.fixture
def example_link():
    url = "https://example.com"
    code = "123abc"
    return ShortLink(
        id=uuid.uuid4(),
        url=Url(url),
        code=ShortCode(code),
    )
