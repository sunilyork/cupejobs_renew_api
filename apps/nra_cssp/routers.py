import json
import logging
import time
import urllib.request
from urllib.error import HTTPError

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.responses import Response

from apps.core import constants
from apps.lib.calendar import is_cssp_application_period
from .models import NraCsspModel
from ..lib.validation_error import ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/nra_feed", response_description="Create NRA Feed")
async def nra_feed(request: Request, nra: NraCsspModel = Depends()):
    """Create NRA Feed"""
    try:
        created_nra = await create_nra_feed(
            request, nra.academic_year, nra.academic_session.value, nra.nra_type.value
        )
    except HTTPError as e:
        content = e.read()
        return Response(content=content, status_code=500)
    except ValidationError as ve:
        return Response(content=ve.error_msg, status_code=ve.status_code)
    return JSONResponse(status_code=status.HTTP_200_OK, content=created_nra)


async def create_nra_feed(request, academic_year, acad_session, nra_type):
    logger.info(f"BEGIN create_nra_feed for {academic_year} {acad_session} {nra_type}")
    start = time.perf_counter()
    url = f"{constants.NRA_CSSP_URL}?acad_session={acad_session}&nra_type={nra_type}&academicYear={academic_year}"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    if data["nras"]:
        document = await request.app.mongodb["nra_cssp"].find_one(
            {
                "metadata.academicyear": data["metadata"]["academicyear"],
                "metadata.acadsession": data["metadata"]["acadsession"],
                "nras.document_name": data["nras"][0]["document_name"],
            }
        )
        if document:
            await request.app.mongodb["nra_cssp"].delete_many(document)

        new_nra = await request.app.mongodb["nra_cssp"].insert_one(data)
        created_nra = await request.app.mongodb["nra_cssp"].find_one(
            {"_id": ObjectId(new_nra.inserted_id)}, {"_id": 0}
        )
        end = time.perf_counter()
        elapsed_time = (end - start) / 60
        logger.info(
            f"Time taken to create nra feed for fiscal year {academic_year} {acad_session} {nra_type} ---> {round(elapsed_time)} minutes."
        )
    else:
        raise HTTPException(status_code=404, detail="No data found.")
    return created_nra


@router.get(
    "/cssp_application_period",
    response_description="Determine if CSSP application period is open",
)
async def cssp_application_period():
    return is_cssp_application_period()
