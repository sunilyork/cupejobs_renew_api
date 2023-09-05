from pydantic import BaseModel, Field

from ..core.constants import AcademicSession, NraType


class NraCsspModel(BaseModel):
    academic_session: AcademicSession
    nra_type: NraType
    academic_year: int = Field(..., ge=2000)
