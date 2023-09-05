import csv
import logging
import time
from typing import Dict

import requests
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Query
from fastapi.responses import JSONResponse

from apps.core import constants
from apps.core.constants import AcademicSession
from apps.lib.calendar import validate_year
from apps.lib.helper import send_request

router = APIRouter()

logger = logging.getLogger(__name__)


@router.put(
    "/create_yearly_postings_feed_for_faculty/",
    response_model=Dict,
    response_description="Create faculty postings feed in json format for given year.",
)
async def create_yearly_postings_feed_for_faculty(
    request: Request,
    faculty: str,
    academic_year: str = Query(default=None, description="Year format: YYYY"),
):
    faculty = faculty.upper()
    faculty_postings_feed_url = f"{constants.FACULTY_POSTINGS_FEED_URL}?faculty={faculty}&academic_year={academic_year}"
    logger.info(faculty_postings_feed_url)
    resp = requests.get(faculty_postings_feed_url)
    data = resp.json()
    postings_feed = f"postings_feed_{faculty}_{academic_year}"
    data["name"] = postings_feed
    if (
        result := await request.app.mongodb["postings"].find_one_and_replace(
            {"name": postings_feed}, data, {"_id": 0}
        )
    ) is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    else:
        await request.app.mongodb["postings"].insert_one(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"detail": "Created yearly postings feed for faculty."},
        )


@router.put(
    "/create_yearly_postings_feed_for_all_faculties/",
    response_description="Create yearly postings feed in json format for all faculties.",
)
async def create_yearly_postings_feed_for_all_faculties(
    request: Request,
    academic_year: str = Query(default=None, description="Year format: YYYY"),
):
    logger.info(f"Creating yearly postings feed for all faculties - {academic_year}")

    await create_postings(request, academic_year)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Postings feed created for all faculties - {academic_year}",
    )


async def create_postings(request, fiscal_year):
    faculties = send_request(f"{constants.CUPE_FACULTIES_URL}")
    start = time.perf_counter()
    for faculty in faculties:
        faculty = faculty.upper()
        postings_feed = f"postings_feed_{faculty}_{fiscal_year}"
        url = f"{constants.FACULTY_POSTINGS_FEED_URL}?faculty={faculty}&academic_year={fiscal_year}"
        data = send_request(url)
        data["name"] = postings_feed
        if (
            result := await request.app.mongodb["postings"].find_one_and_replace(
                {"name": postings_feed}, data, {"_id": 0}
            )
        ) is not None:
            logger.info(f"Postings feed updated - {fiscal_year} {faculty}")
        else:
            await request.app.mongodb["postings"].insert_one(data)
            logger.info(f"Postings feed created - {fiscal_year} {faculty}")
    end = time.perf_counter()
    elapsed_time = (end - start) / 60
    logger.info(
        f"Total time taken to create postings for fiscal year {fiscal_year} ---> {round(elapsed_time)} minutes."
    )


@router.get(
    "/faculty_postings_feed",
    response_description="Read faculty postings feed by fiscal year.",
)
async def get_faculty_postings_feed_by_fiscal_year(
    request: Request,
    faculty: str,
    fiscal_year: str = Query(default=None, description="Year format: YYYY"),
):
    faculty = faculty.upper()
    postings_feed = f"postings_feed_{faculty}_{fiscal_year}"
    if (
        result := await request.app.mongodb["postings"].find_one(
            {"name": postings_feed}
        )
    ) is not None:
        result.pop("_id", None)
        result.pop("name", None)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"No faculty posting feed for fiscal year {fiscal_year}."},
    )


@router.put(
    "/postings_csv/",
    response_description="Create postings CSV for fiscal year and academic session.",
)
async def create_postings_csv(
    request: Request, fiscal_year: str = Query(description="Year format: YYYY")
):
    validate_year(fiscal_year)

    faculties = await request.app.mongodb["faculty"].find_one(
        {"name": "cupe_faculty_list"}
    )
    faculties.pop("_id", None)
    faculties.pop("name", None)

    start = time.perf_counter()

    for academic_session in AcademicSession:
        if academic_session == "FW":
            filename = fiscal_year + academic_session + "_jobs.csv"
        elif academic_session == "S":
            filename = fiscal_year + "SU" + "_jobs.csv"

        await get_cupe1_cupe2_downloads(
            request, fiscal_year, academic_session, filename, faculties
        )
        await get_cupe3_downloads(
            request, fiscal_year, academic_session, filename, faculties
        )
    end = time.perf_counter()
    elapsed_time = (end - start) / 60
    logger.info(
        f"Total time taken to create postings for fiscal year {fiscal_year} ---> {round(elapsed_time)} minutes."
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Created postings CSV file downloads for {fiscal_year}",
    )


async def get_cupe1_cupe2_downloads(
    request, academic_year, academic_session, filename, faculties
):
    with open(filename, mode="a") as csv_file:
        writer = csv.writer(csv_file)

        for cupe in ["CUPE_1", "CUPE_2"]:
            for faculty in faculties:
                posting_feed = await get_posting_feed(request, academic_year, faculty)

                for item in posting_feed[cupe][academic_session]:
                    faculty = item["responsible_faculty"]
                    unit = item["responsible_unit"].strip()
                    posting_type = item["posting_type"]
                    document_name = item["document_name"]
                    position = item["position"]
                    application_deadline = item["application_deadline"]

                    posting_row = []
                    posting_row.append(faculty)
                    posting_row.append(posting_type)
                    posting_row.append(document_name)
                    posting_row.append(academic_year)

                    for course in item["courses"]:
                        row = []
                        row.append(course["session"])
                        row.append(unit)
                        row.append(course["coursenumber"])
                        row.append(course["creditweight"])
                        row.append(course["instructionalformat"])
                        row.append(cupe[-1])
                        row.append(course["session"])
                        row.append(course["course_description"])
                        row.append(position)
                        row.append(application_deadline)

                        writer.writerow(posting_row + row)


async def get_cupe3_downloads(
    request, academic_year, academic_session, filename, faculties
):
    with open(filename, mode="a") as csv_file:
        writer = csv.writer(csv_file)

        for faculty in faculties:
            posting_feed = await get_posting_feed(request, academic_year, faculty)

            for item in posting_feed["CUPE_3"][academic_session]:
                posting_row = []
                faculty = item["responsible_faculty"]
                posting_type = item["posting_doc_type"]
                document_name = item["document_name"]
                session = item["session"].strip()
                position = item["position"]
                supervisor = item["supervisor"]
                hours = item["hours"]
                assigns = item["assigns"]
                application_deadline = item["application_deadline"]

                posting_row.append(faculty)
                posting_row.append(posting_type)
                posting_row.append(document_name)
                posting_row.append(academic_year)
                posting_row.append(session)
                posting_row.append("3")
                posting_row.append(position)
                posting_row.append(supervisor)
                posting_row.append(hours)
                posting_row.append(assigns)
                posting_row.append(application_deadline)
                writer.writerow(posting_row)


async def get_posting_feed(request, academic_year, faculty):
    faculty = faculty.upper()
    postings_feed_name = f"postings_feed_{faculty}_{academic_year}"
    posting_feed = await request.app.mongodb["postings"].find_one(
        {"name": postings_feed_name}
    )
    if posting_feed is None:
        raise HTTPException(
            status_code=400,
            detail=f"Posting feed {postings_feed_name} not found.",
        )
    posting_feed.pop("_id", None)
    posting_feed.pop("name", None)
    return posting_feed
