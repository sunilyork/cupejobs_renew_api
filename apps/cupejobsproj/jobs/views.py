from operator import itemgetter
from typing import Union

from fastapi import APIRouter, HTTPException, Header, Request

from apps.cupejobsproj import __version__
from apps.lib.calendar import (
    get_blanket_end_date,
    get_blanket_start_date,
    get_cssp_end_date,
    get_cssp_start_date,
    get_current_fiscal_year,
    is_blanket_application_period,
    is_cssp_application_period,
    show_next_fiscal_year,
)

router = APIRouter()

TERMS = ["S", "FW"]
INVALID_FACULTIES = ["AD", "AK", "AS"]
CUPE_UNITS = ["1", "2", "3"]
FACULTIES = {
    "AP": "Faculty of Liberal Arts and Professional Studies",
    "ED": "Faculty of Education",
    "EU": "Faculty of Environmental and Urban Change",
    "FA": "School of the Arts, Media, Performance & Design",
    "GL": "Glendon",
    "GS": "Faculty of Graduate Studies",
    "HH": "Faculty of Health",
    "LE": "Lassonde School of Engineering",
    "LW": "Osgoode Hall Law School",
    "SB": "Schulich SB",
    "SC": "Faculty of Science",
    "TC": "Teaching Commons",
}

# 2020-05-15 SEM -- added EU to the list
# 2021-12-15 SEM -- added EUC |ENST to list as per Josephine's request
NOT_IN_BLANKET = {
    "AP": "",
    "ED": "PHIL|UNMA",
    "ES": "",
    "EU": "EUC |ENST",
    "FA": "ARTH|D.O.|DESN|F.A.|FA |FACS|INDV|YSDS|VISA",
    "GL": "CSLA|MDS ",
    "GS": "",
    "HH": "D.O.|RYER|IHST",
    "LE": "",
    "LW": "",
    "SB": "",
    "SC": "CSE |EATS|ENG |RYER",
    "TC": "",
}


def isSubDict(subDict, dictionary):
    for key in subDict.keys():
        if (key not in dictionary) or (not subDict[key] == dictionary[key]):
            return False
    return True


def get_key(val, faculties_dict):
    for key, value in faculties_dict.items():
        if val == value:
            return key

    return "key doesn't exist"


async def get_nra_rows(request, _faculty, _units, _YEARS):
    """
    get_nra_rows - this function will provide list of nras on the main page of https://cupejobs.uit.yorku.ca/
    """

    unit_item = {}
    col = {}
    rows = []
    col_count = 0

    for year in _YEARS:
        for unit in _units:
            for term in TERMS:
                academic_year = year if term == "FW" else str(int(year) - 1)

                for document in (
                    await request.app.mongodb["nra_cssp"]
                    .find(
                        {
                            "metadata": {
                                "academicyear": int(academic_year),
                                "acadsession": term,
                            },
                            "nras": {
                                "$elemMatch": {
                                    "document_name": {
                                        "$regex": "^N-*",
                                        "$options": "i",
                                    }
                                }
                            },
                        }
                    )
                    .to_list(length=100)
                ):
                    if document:
                        for idx in range(0, len(document["nras"])):
                            if (
                                str(
                                    document["nras"][idx]["responsible_faculty"]
                                ).strip()
                                == _faculty.strip()
                                and str(
                                    document["nras"][idx]["responsible_unit"]
                                ).strip()
                                == unit["unit"].strip()
                            ):
                                unit_item["year"] = year
                                unit_item["fileyear"] = academic_year
                                unit_item["unit"] = unit["unit"].strip()
                                unit_item["term"] = term
                                col[col_count] = unit_item
                                unit_item = {}
                                col_count += 1
                                if col_count == 2:
                                    rows.append(col)
                                    col = {}
                                    col_count = 0
                                break
                            else:
                                pass
    if col_count > 0:
        rows.append(col)

    return rows


async def get_cssp_rows(request, _faculty, _units, _YEARS):
    """
    get_cssp_rows - this function will provide list of cssp on the main page of https://cupejobs.uit.yorku.ca/
    """

    unit_item = {}
    col = {}
    rows = []
    col_count = 0

    for year in _YEARS:
        for unit in _units:
            for term in TERMS:
                academic_year = year if term == "FW" else str(int(year) - 1)

                for document in (
                    await request.app.mongodb["nra_cssp"]
                    .find(
                        {
                            "metadata": {
                                "academicyear": int(academic_year),
                                "acadsession": term,
                            },
                            "nras": {
                                "$elemMatch": {
                                    "document_name": {
                                        "$regex": "^C-*",
                                        "$options": "i",
                                    }
                                }
                            },
                        }
                    )
                    .to_list(length=100)
                ):
                    if document:
                        for idx in range(0, len(document["nras"])):
                            if (
                                str(
                                    document["nras"][idx]["responsible_faculty"]
                                ).strip()
                                == _faculty.strip()
                                and str(
                                    document["nras"][idx]["responsible_unit"]
                                ).strip()
                                == unit["unit"].strip()
                            ):
                                unit_item["year"] = year
                                unit_item["fileyear"] = academic_year
                                unit_item["unit"] = unit["unit"].strip()
                                unit_item["term"] = term
                                col[col_count] = unit_item
                                unit_item = {}
                                col_count += 1
                                if col_count == 4:
                                    rows.append(col)
                                    col = {}
                                    col_count = 0
                                break
                            else:
                                pass
    if col_count > 0:
        rows.append(col)

    return rows


def get_blanket_rows(_units, _not_in_blanket):
    """
    get_blanket_rows - This function use for blanket tab
    """

    unit_item = {}
    col = {}
    rows = []
    col_count = 0
    for unit in _units:
        if unit["unit"] not in _not_in_blanket:
            unit_item["unit"] = unit["unit"]
            unit_item["desc"] = unit["description"]
            col[col_count] = unit_item
            unit_item = {}
            col_count += 1
            if col_count == 4:
                rows.append(col)
                col = {}
                col_count = 0

    if col_count > 0:
        rows.append(col)

    return rows


@router.get("/", response_description="Read faculty blanket, nras and cssps.")
async def jobs_blanket_nra_cssp(
    request: Request, faculty_abbreviation: Union[str, None] = Header(default=None)
):
    """
    jobs - this function will display the main page nras, cssp, postings -
    https://cupejobs.uit.yorku.ca/.
    Determine if blankets are available or not.

    faculty_abbreviation - For e.g. AP
    """

    facs = []
    fac = {}
    units = []
    unit = {}

    fiscal_year = get_current_fiscal_year()
    need_next_year = show_next_fiscal_year()

    if need_next_year:
        YEARS = [
            str(fiscal_year),
            str(fiscal_year + 1),
        ]
    else:
        YEARS = [str(fiscal_year)]

    blankets_available = "T" if is_blanket_application_period() else None
    cssps_available = "T" if is_cssp_application_period() else None

    for fac_depts in (
        await request.app.mongodb["faculty"]
        .find({"name": "faculty_department_emails"})
        .to_list(length=20)
    ):
        if fac_depts:
            for faculty, depts in fac_depts.items():
                if faculty in INVALID_FACULTIES:
                    continue

                if faculty_abbreviation:
                    if (
                        FACULTIES.get(faculty)
                        and str(faculty).strip() == faculty_abbreviation.strip()
                    ):
                        fac["fac"] = faculty
                        fac["fac_name"] = FACULTIES[faculty]

                        for idx in range(0, len(depts)):
                            unit["unit"] = depts[idx]["unit"].strip()
                            unit["desc"] = depts[idx]["description"].strip()
                            units.append(unit)
                            unit = {}

                        fac["units"] = units
                        units = []
                        fac["blanket_rows"] = get_blanket_rows(
                            depts, NOT_IN_BLANKET[faculty]
                        )
                        fac["nra_rows"] = await get_nra_rows(
                            request, faculty, depts, YEARS
                        )
                        fac["cssp_rows"] = await get_cssp_rows(
                            request, faculty, depts, YEARS
                        )
                        facs.append(fac)
                        fac = {}
                        break

    by_facs = sorted(facs, key=itemgetter("fac"))

    context = {
        "blankets_available": blankets_available,
        "cssps_available": cssps_available,
        "BLANKET_START_DT": get_blanket_start_date(),
        "BLANKET_END_DT": get_blanket_end_date(),
        "CSSP_START_DT": get_cssp_start_date(),
        "CSSP_END_DT": get_cssp_end_date(),
        "facs": by_facs,
        "cupe_units": CUPE_UNITS,
        "terms": TERMS,
        "years": YEARS,
        "next_academic_year": str(fiscal_year + 1) if need_next_year else None,
        "academic_year": str(fiscal_year),
        "last_academic_year": str(fiscal_year - 1),
        "app_version": __version__,
    }

    if context:
        return context
    else:
        raise HTTPException(status_code=404, detail="Not found.")


@router.get("/nra/{_nra}")
async def nras(request: Request, _nra: str):
    """
    nras - this function will display the detial list of specific nras
    based on nra year and term - https://cupejobs.uit.yorku.ca/.
    For e.g. SC_ADMN_2021_FW
    """

    nras = []
    nra = {}

    if _nra.count("_") != 3:
        raise HTTPException(status_code=404, detail="Not found.")

    faculty, unit, academic_year, term = _nra.split("_")

    if not (faculty or unit or academic_year or term):
        raise HTTPException(status_code=404, detail="Not found.")

    if faculty not in FACULTIES:
        raise HTTPException(status_code=404, detail="Not found.")

    for document in (
        await request.app.mongodb["nra_cssp"]
        .find({"nras.document_name": {"$regex": "^N-*", "$options": "i"}})
        .to_list(length=100)
    ):
        if document:
            if (
                document["metadata"]["academicyear"] == int(academic_year)
                and document["metadata"]["acadsession"] == term
            ):
                for idx in range(0, len(document["nras"])):
                    if (
                        document["nras"][idx]["responsible_unit"].strip() == unit
                        and document["nras"][idx]["responsible_faculty"].strip()
                        == faculty
                    ):
                        nra["nra_id"] = document["nras"][idx]["nra_id"]
                        nra["document_name"] = document["nras"][idx]["document_name"]
                        nra["nra_generated_on"] = document["nras"][idx][
                            "nra_generated_on"
                        ]
                        nras.append(nra)
                        nra = {}

    nra_mapping_list = sorted(nras, key=lambda item: item.get("nra_id"))

    context = {
        "faculty_abbreviation": get_key(FACULTIES[faculty], FACULTIES),
        "faculty_title": FACULTIES[faculty],
        "unit_title": unit,
        "session_title": "%s %s"
        % (
            term,
            academic_year if term == "FW" else str(int(academic_year) + 1),
        ),
        "nras": nra_mapping_list,
        "academic_year": academic_year,
    }

    if context["nras"]:
        return context
    else:
        raise HTTPException(status_code=404, detail="Not found")


@router.get("/cssp/{_cssps}")
async def cssps(request: Request, _cssps: str):
    """
    cssps - this function will display the detial list of specific cssps
    based on cssp year and term - https://cupejobs.uit.yorku.ca/.
    For e.g. SC_BIOL_2020_S.
    """

    cssps = []
    cssp = {}

    if _cssps.count("_") != 3:
        raise HTTPException(status_code=404, detail="Not found.")

    faculty, unit, academic_year, term = _cssps.split("_")

    if not (faculty or unit or academic_year or term):
        raise HTTPException(status_code=404, detail="Not found.")

    if faculty not in FACULTIES:
        raise HTTPException(status_code=404, detail="Not found.")

    for document in (
        await request.app.mongodb["nra_cssp"]
        .find({"nras.document_name": {"$regex": "^C-*", "$options": "i"}})
        .to_list(length=100)
    ):
        if document:
            if (
                document["metadata"]["academicyear"] == int(academic_year)
                and document["metadata"]["acadsession"] == term
            ):
                for idx in range(0, len(document["nras"])):
                    if (
                        document["nras"][idx]["responsible_unit"].strip() == unit
                        and document["nras"][idx]["responsible_faculty"].strip()
                        == faculty
                    ):
                        cssp["nra_id"] = document["nras"][idx]["nra_id"]
                        cssp["document_name"] = document["nras"][idx]["document_name"]
                        cssp["nra_generated_on"] = document["nras"][idx][
                            "nra_generated_on"
                        ]
                        cssps.append(cssp)
                        cssp = {}

    cssps_mapping_list = sorted(cssps, key=lambda item: item.get("nra_id"))

    context = {
        "faculty_abbreviation": get_key(FACULTIES[faculty], FACULTIES),
        "faculty_title": FACULTIES[faculty],
        "unit_title": unit,
        "session_title": "%s %s"
        % (
            term,
            academic_year if term == "FW" else str(int(academic_year) + 1),
        ),
        "cssps": cssps_mapping_list,
        "academic_year": academic_year,
    }

    if context["cssps"]:
        return context
    else:
        raise HTTPException(status_code=404, detail="Not found.")
