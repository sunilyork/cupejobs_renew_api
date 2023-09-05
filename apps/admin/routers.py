import logging
import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query

from apps.config import get_settings
from apps.faculty.routers import (
    upsert_cupe_faculty_list,
    upsert_cupe_faculty_units,
    upsert_faculty_department_emails,
)
from apps.lib.calendar import get_current_fiscal_year
from apps.nra_cssp.routers import create_nra_feed
from apps.postings.routers import create_postings

settings = get_settings()

router = APIRouter()

logger = logging.getLogger(__name__)


@router.put(
    "/initialize_database",
    response_description="Initialize database.",
)
async def initialize_database(
    request: Request,
    start_fiscal_year: int = Query(default=None, description="Year format: YYYY"),
    end_fiscal_year: int = Query(default=None, description="Year format: YYYY"),
):
    await upsert_faculty_department_emails(request)
    await upsert_cupe_faculty_list(request)
    await upsert_cupe_faculty_units(request)

    current_fiscal_year = get_current_fiscal_year()

    await init_postings(
        request, current_fiscal_year, start_fiscal_year, end_fiscal_year
    )

    await init_nra(request, current_fiscal_year, start_fiscal_year, end_fiscal_year)


async def create_postings_feed(request, current_fiscal_year):
    logger.info(f"BEGIN create_postings_feed for {current_fiscal_year}")
    await create_postings(request, current_fiscal_year)
    logger.info(f"END create_postings_feed for {current_fiscal_year}")


async def create_nra_feeds(request, fiscal_year):
    logger.info(f"BEGIN create_nra_feeds for {fiscal_year}")
    start = time.perf_counter()
    for acad_session in ["S", "FW"]:
        for nra_type in ["N", "C"]:
            try:
                created_nra = await create_nra_feed(
                    request, fiscal_year, acad_session, nra_type
                )
            except HTTPException as e:
                logger.error(
                    f"HttpException: {e} for fiscal year {fiscal_year}, acad_session {acad_session}, nra_type {nra_type}"
                )
            continue
    end = time.perf_counter()
    elapsed_time = (end - start) / 60
    logger.info(
        f"Total time taken to create nra feeds for fiscal year {fiscal_year} ---> {round(elapsed_time)} minutes."
    )


async def init_postings(
    request, current_fiscal_year, start_fiscal_year, end_fiscal_year
):
    if start_fiscal_year < 2010:
        start_fiscal_year = 2010
    if end_fiscal_year > current_fiscal_year:
        end_fiscal_year = current_fiscal_year
    assert start_fiscal_year < end_fiscal_year
    for fiscal_year in range(start_fiscal_year, end_fiscal_year + 1):
        await create_postings_feed(request, fiscal_year)
    return end_fiscal_year, start_fiscal_year


async def init_nra(request, current_fiscal_year, start_fiscal_year, end_fiscal_year):
    if start_fiscal_year < 2014:
        start_fiscal_year = 2014
    if end_fiscal_year > current_fiscal_year:
        end_fiscal_year = current_fiscal_year
    assert start_fiscal_year < end_fiscal_year
    for fiscal_year in range(start_fiscal_year, end_fiscal_year + 1):
        await create_nra_feeds(request, fiscal_year)
