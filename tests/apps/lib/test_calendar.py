from datetime import datetime

import pytest

from apps.lib.calendar import (
    get_blanket_end_date,
    get_cssp_end_date,
    is_blanket_application_period,
    is_cssp_application_period,
)


def test_get_blanket_end_date_for_academic_year(mocker):
    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=2020,
    )
    blanket_end_date = get_blanket_end_date()
    assert blanket_end_date == datetime(2021, 2, 1)
    # Since 2021-01-31 is Sunday, blanket_end_date is the next work day (Monday).
    assert blanket_end_date.weekday() == 0

    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=2021,
    )
    blanket_end_date = get_blanket_end_date()
    assert blanket_end_date == datetime(2022, 1, 31)

    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=2022,
    )
    blanket_end_date = get_blanket_end_date()
    assert blanket_end_date == datetime(2023, 1, 31)


def test_get_cssp_end_date_for_academic_year(mocker):
    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=2021,
    )
    cssp_end_date = get_cssp_end_date()
    assert cssp_end_date == datetime(2021, 11, 1)
    assert cssp_end_date.weekday() == 0

    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=2022,
    )
    cssp_end_date = get_cssp_end_date()
    assert cssp_end_date == datetime(2022, 11, 1)

    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=2025,
    )
    cssp_end_date = get_cssp_end_date()
    # Since 2025-11-1 is Saturday, cssp_end_date is the next work day (Monday).
    assert cssp_end_date == datetime(2025, 11, 3)


@pytest.mark.parametrize(
    "get_current_academic_year, get_today",
    [
        (2023, datetime(2023, 11, 15)),
        (2023, datetime(2024, 1, 15)),
        (2023, datetime(2024, 1, 31)),
        (2025, datetime(2025, 11, 15)),
        (2025, datetime(2026, 1, 31)),
    ],
)
def test_is_blanket_application_period_should_pass(
    mocker, get_current_academic_year, get_today
):
    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=get_current_academic_year,
    )
    mocker.patch("apps.lib.calendar.get_today", return_value=get_today)
    actual = is_blanket_application_period()
    assert actual is True


@pytest.mark.parametrize(
    "get_current_academic_year, get_today",
    [
        (2023, datetime(2023, 11, 14)),
        (2023, datetime(2024, 2, 1)),
        (2023, datetime(2024, 5, 31)),
    ],
)
def test_is_blanket_application_period_should_fail(
    mocker, get_current_academic_year, get_today
):
    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=get_current_academic_year,
    )
    mocker.patch("apps.lib.calendar.get_today", return_value=get_today)
    actual = is_blanket_application_period()
    assert actual is False


@pytest.mark.parametrize(
    "get_current_academic_year, get_today",
    [
        (2023, datetime(2023, 10, 1)),
        (2023, datetime(2023, 11, 1)),
        (2025, datetime(2025, 11, 1)),
    ],
)
def test_is_cssp_application_period_should_pass(
    mocker, get_current_academic_year, get_today
):
    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=get_current_academic_year,
    )
    mocker.patch("apps.lib.calendar.get_today", return_value=get_today)
    actual = is_cssp_application_period()
    assert actual is True


@pytest.mark.parametrize(
    "get_current_academic_year, get_today",
    [
        (2023, datetime(2023, 9, 30)),
        (2023, datetime(2023, 11, 2)),
        (2025, datetime(2025, 12, 1)),
        (2025, datetime(2026, 1, 1)),
    ],
)
def test_is_cssp_application_period_should_fail(
    mocker, get_current_academic_year, get_today
):
    mocker.patch(
        "apps.lib.calendar.get_current_academic_year",
        return_value=get_current_academic_year,
    )
    mocker.patch("apps.lib.calendar.get_today", return_value=get_today)
    actual = is_cssp_application_period()
    assert actual is False
