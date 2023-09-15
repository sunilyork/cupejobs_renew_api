import logging
import time

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from apps.core import constants
from apps.lib.helper import send_request

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(
    "/cupe1_assns_feed",
    response_description="Read CUPE1 Assignments.",
)
async def get_cupe1assns(
    request: Request,
):
    cupe1assns_feed = "cupe1assns"
    if (
        result := await request.app.mongodb["cupe1assns"].find_one(
            {"name": cupe1assns_feed}
        )
    ) is not None:
        result.pop("_id", None)
        result.pop("name", None)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "cupe1assns feed not found."},
    )


@router.put(
    "/create_cupe1_assns_feed/",
    response_description="Create CUPE1 Assignments feed in json format.",
)
async def create_cupe1_assns_feed(
    request: Request,
):
    logger.info("Creating CUPE-1 Assignments feed")

    await create_cupe1_assignments(request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="CUPE-1 Assignments feed created",
    )


async def create_cupe1_assignments(request):
    start = time.perf_counter()
    cupe1_assns_feed = "cupe1assns"
    url = f"{constants.CUPE1_ASSNS_FEED_URL}"
    data = send_request(url)
    data["name"] = cupe1_assns_feed
    if (
        await request.app.mongodb["cupe1assns"].find_one_and_replace(
            {"name": cupe1_assns_feed}, data, {"_id": 0}
        )
    ) is not None:
        logger.info("CUPE1 Assns feed updated")
    else:
        await request.app.mongodb["cupe1assns"].insert_one(data)
        logger.info("CUPE-1 Assns feed created")
    end = time.perf_counter()
    elapsed_time = (end - start) / 60
    logger.info(
        f"Total time taken to create CUPE-1 Assignments Feed ---> {round(elapsed_time)} minutes."
    )
