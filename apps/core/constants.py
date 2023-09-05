from enum import Enum

from apps.config import get_settings

settings = get_settings()

CSSP_ELIGIBILITY_URL = settings.ARMS_API_URL + "/jobs/cssp_eligibility"
CUPE_FACULTIES_URL = settings.ARMS_API_URL + "/faculty/cupe_faculties"
CUPE_FACULTY_UNITS_URL = settings.ARMS_API_URL + "/faculty/cupe_faculty_units"
CUPE1_ASSNS_FEED_URL = settings.ARMS_API_URL + "/cupe1assns"
FACULTY_DEPT_EMAILS_URL = settings.ARMS_API_URL + "/faculty/emails"
FACULTY_POSTINGS_FEED_URL = settings.ARMS_API_URL + "/postings/faculty_postings_feed"
NEW_POSTINGS_ALERT = settings.ARMS_API_URL + "/postings/new_postings_alert"
NRA_CSSP_URL = settings.ARMS_API_URL + "/nra"
TCA_ELIGIBILITY_URL = settings.ARMS_API_URL + "/jobs/tca_eligibility"


class AcademicSession(str, Enum):
    SUMMER = "S"
    FALL_WINTER = "FW"


class CupeUnit(str, Enum):
    CUPE_1 = "1"
    CUPE_2 = "2"
    CUPE_3 = "3"


class NotificationType(str, Enum):
    BLANKET = "Blanket"
    POSTING = "Posting"


class NraType(str, Enum):
    NRA_TYPE = "N"
    CSSP_TYPE = "C"
