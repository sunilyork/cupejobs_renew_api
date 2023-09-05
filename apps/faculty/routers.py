import requests
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from apps.core import constants

router = APIRouter()


@router.put(
    "/create_faculty_department_emails",
    response_description="Create contact emails for faculty departments.",
)
async def create_faculty_department_emails(request: Request):
    return await upsert_faculty_department_emails(request)


@router.put(
    "/create_cupe_faculty_list",
    response_description="Create cupe faculty list.",
)
async def create_cupe_faculty_list(request: Request):
    return await upsert_cupe_faculty_list(request)


@router.put(
    "/cupe_faculty_units",
    response_description="Create cupe faculty department list.",
)
async def create_cupe_faculty_units(request: Request):
    return await upsert_cupe_faculty_units(request)


@router.get("/cupe_faculty_list", response_description="Get faculty list.")
async def read_cupe_faculty_list(request: Request):
    if (
        result := await request.app.mongodb["faculty"].find_one(
            {"name": "cupe_faculty_list"}
        )
    ) is not None:
        result.pop("_id", None)
        result.pop("name", None)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Faculty list not found."},
        )


@router.get(
    "/get_faculty_department_emails",
    response_description="Read contact emails for faculty departments.",
)
async def get_faculty_department_emails(request: Request):
    if (
        result := await request.app.mongodb["faculty"].find_one(
            {"name": "faculty_department_emails"}
        )
    ) is not None:
        result.pop("_id", None)
        result.pop("name", None)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Faculty emails not found."},
        )


@router.get("/cupe_faculty_units", response_description="Get faculty units.")
async def read_cupe_faculty_list(request: Request):
    if (
        result := await request.app.mongodb["faculty"].find_one(
            {"name": "cupe_faculty_units"}
        )
    ) is not None:
        result.pop("_id", None)
        result.pop("name", None)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Faculty units not found."},
        )


async def upsert_faculty_department_emails(request):
    resp = requests.get(constants.FACULTY_DEPT_EMAILS_URL)
    data = resp.json()
    faculty_department_emails = "faculty_department_emails"
    data["name"] = faculty_department_emails
    if (
        result := await request.app.mongodb["faculty"].find_one_and_replace(
            {"name": faculty_department_emails}, data, {"_id": 0}
        )
    ) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        await request.app.mongodb["faculty"].insert_one(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"detail": "Created Department Emails."},
        )


async def upsert_cupe_faculty_list(request):
    resp = requests.get(constants.CUPE_FACULTIES_URL)
    data = resp.json()
    cupe_faculty_list = "cupe_faculty_list"
    data["name"] = cupe_faculty_list
    if (
        result := await request.app.mongodb["faculty"].find_one_and_replace(
            {"name": cupe_faculty_list}, data, {"_id": 0}
        )
    ) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        await request.app.mongodb["faculty"].insert_one(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"detail": "Created Cupe Faculty List."},
        )


async def upsert_cupe_faculty_units(request):
    resp = requests.get(constants.CUPE_FACULTY_UNITS_URL)
    data = resp.json()
    cupe_faculty_units = "cupe_faculty_units"
    data["name"] = cupe_faculty_units
    if (
        result := await request.app.mongodb["faculty"].find_one_and_replace(
            {"name": cupe_faculty_units}, data, {"_id": 0}
        )
    ) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        await request.app.mongodb["faculty"].insert_one(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"detail": "Created Cupe Faculty Units."},
        )
