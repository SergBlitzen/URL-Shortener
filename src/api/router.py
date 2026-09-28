from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status
from starlette.responses import RedirectResponse

from api.dependencies import get_short_link_service, ShortLinkServiceDep, ShortCodePath
from api.schemas import ShortLinkCreate, ShortLinkCode
from domain.value_objects import Url

router = APIRouter()


@router.post(
    "/links",
    status_code=status.HTTP_201_CREATED,
)
async def post_link(
    link: ShortLinkCreate,
    short_link_service: ShortLinkServiceDep,
) -> ShortLinkCode:
    short_link = await short_link_service.create_short_link(
        url=link.url,
    )
    return ShortLinkCode.from_domain(short_link)


@router.get(
    "/{code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
async def get_link(
    code: ShortCodePath,
    short_link_service = Depends(get_short_link_service)
) -> RedirectResponse:
    link = await short_link_service.get_by_code(code)
    return RedirectResponse(
        link.url.value,
        status_code=status.HTTP_302_FOUND,
    )
