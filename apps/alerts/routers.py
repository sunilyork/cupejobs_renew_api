import datetime
import json
import requests

from bson import json_util
from fastapi import APIRouter, Request, status
from fastapi.params import Query
from fastapi.responses import JSONResponse

from apps.core import constants

router = APIRouter()


@router.put(
    "/new_postings_alert",
    response_description="Create new postings alert for faculties.",
)
async def create_new_postings_alert(
    request: Request,
    academic_year: str = Query(default=None, description="Year format: YYYY"),
    days_delta: int = 7,
):
    print(f"Postings alert for postings created in the last {days_delta} days.")
    new_postings_alert = "new_postings_alert"
    new_postings_alert_url = f"{constants.NEW_POSTINGS_ALERT}?academic_year={academic_year}&days_delta={days_delta}"
    resp = requests.get(new_postings_alert_url)
    faculties = resp.json()
    list = [count for faculty, count in faculties.items()]
    data = {
        "faculties": faculties,
        "name": new_postings_alert,
        "alert_date": datetime.datetime.today().replace(microsecond=0),
        "total_new_postings": sum(list),
        "duration_in_days": days_delta,
    }
    if (
        result := await request.app.mongodb["alerts"].find_one_and_replace(
            {"name": new_postings_alert}, data, {"_id": 0}
        )
    ) is not None:
        result = json.dumps(result, default=json_util.default)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        await request.app.mongodb["alerts"].insert_one(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"detail": "Created new postings alert."},
        )


@router.get("/new_postings_alert", response_description="Get new postings alert.")
async def get_new_postings_alert(request: Request):
    if (
        result := await request.app.mongodb["alerts"].find_one(
            {"name": "new_postings_alert"}
        )
    ) is not None:
        result.pop("_id", None)
        result.pop("name", None)
        result = json.dumps(result, default=json_util.default)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "No new postings alert."},
        )
