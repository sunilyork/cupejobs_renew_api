import logging
import re

import requests

from datetime import datetime, timedelta

from fastapi import HTTPException

from apps.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def get_current_academic_year():
    today = get_today()
    academic_year = today.year if today.month >= 9 else today.year - 1
    logger.debug(f"Current academic year: {academic_year}")
    return academic_year


def get_current_fiscal_year():
    current_fiscal_year_url = settings.ARMS_API_URL + "/faculty/current_fiscal_year"
    response = requests.get(current_fiscal_year_url)
    data = response.json()
    logger.info(f"Current fiscal year: {data}")
    return data


def is_blanket_application_period():
    today = get_today()
    today_str = "%04d-%02d-%02d" % (today.year, today.month, today.day)
    return (
        get_blanket_start_date()
        <= datetime.strptime(today_str, "%Y-%m-%d")
        <= get_blanket_end_date()
    )


def is_cssp_application_period():
    today = get_today()
    today_str = "%04d-%02d-%02d" % (today.year, today.month, today.day)
    return (
        get_cssp_start_date()
        <= datetime.strptime(today_str, "%Y-%m-%d")
        <= get_cssp_end_date()
    )


def get_blanket_start_date():
    academic_year = get_current_academic_year()
    blanket_start_date = str(academic_year) + "-11-15"
    logger.debug(
        f"blanket_start_date: {blanket_start_date} for academic year {academic_year}"
    )
    return datetime.strptime(blanket_start_date, "%Y-%m-%d")


def get_blanket_end_date():
    # Monday == 0...Sunday == 6
    academic_year = get_current_academic_year()
    blanket_end_date = datetime.strptime(str(academic_year + 1) + "-01-31", "%Y-%m-%d")
    if blanket_end_date.weekday() == 5:
        blanket_end_date = blanket_end_date + timedelta(days=2)
    if blanket_end_date.weekday() == 6:
        blanket_end_date = blanket_end_date + timedelta(days=1)
    logger.debug(
        f"blanket_end_date: {blanket_end_date} for academic year {academic_year}"
    )
    return blanket_end_date


def get_cssp_start_date():
    academic_year = get_current_academic_year()
    cssp_start_date = str(academic_year) + "-10-01"
    logger.debug(
        f"cssp_start_date: {cssp_start_date} for academic year {academic_year}"
    )
    return datetime.strptime(cssp_start_date, "%Y-%m-%d")


def get_cssp_end_date():
    # Monday == 0...Sunday == 6
    academic_year = get_current_academic_year()
    cssp_end_date = datetime.strptime(str(academic_year) + "-11-01", "%Y-%m-%d")
    if cssp_end_date.weekday() == 5:
        cssp_end_date = cssp_end_date + timedelta(days=2)
    if cssp_end_date.weekday() == 6:
        cssp_end_date = cssp_end_date + timedelta(days=1)
    logger.debug(f"cssp_end_date: {cssp_end_date} for academic year {academic_year}")
    return cssp_end_date


def show_next_fiscal_year():
    # determine if we are in the Jan. 1 - Apr. 22 time period.  if so, then
    # we will need to be able to show both current year and next year at the
    # same time on the main page
    today = datetime.today()
    today_str = "%04d-%02d-%02d" % (today.year, today.month, today.day)
    first_day = "%04d-01-01" % today.year
    last_day = "%04d-04-22" % today.year
    need_next_year = (today_str >= first_day) and (today_str <= last_day)
    return need_next_year


def validate_year(year):
    if not re.match("^\\d{4}$", year):
        raise HTTPException(status_code=400, detail="Expected year format: YYYY")


def get_today():
    return datetime.today()
