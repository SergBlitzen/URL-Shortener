import pytest

from application.exceptions import ShortLinkCreationFailed, ShortLinkNotFound


@pytest.mark.asyncio
@pytest.mark.unit
async def test_short_link_create(
    short_link_service,
):
    url = "https://example.com"
    short_link = await short_link_service.create_short_link(url)

    assert short_link.code is not None
    assert short_link_service.uow.commited == True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_short_link_same_code(
    short_link_service,
    single_code_generator,
):
    short_link_service.CODE_GENERATOR = single_code_generator

    url = "https://example.com"
    short_link = await short_link_service.create_short_link(url)

    assert short_link is not None

    with pytest.raises(ShortLinkCreationFailed):
        await short_link_service.create_short_link(url)



@pytest.mark.asyncio
@pytest.mark.unit
async def test_short_link_get_by_code(
    short_link_service,
    example_link,
):
    short_link_service.uow.short_links.links[example_link.code] = example_link

    short_link = await short_link_service.get_by_code(example_link.code)

    assert short_link.code == example_link.code
    assert short_link.url == example_link.url
    assert short_link.clicks_count == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_short_link_not_found(
    short_link_service,
):
    code = "321cba"
    with pytest.raises(ShortLinkNotFound):
        await short_link_service.get_by_code(code)


