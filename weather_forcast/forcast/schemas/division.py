from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional, List
from forcast.schemas.district import DistrictRead


class DivisionBase(BaseSchema):
    name: str


class DivisionUpdate(UpdateBaseSchema):
    name: Optional[str]


class DivisionRead(DivisionUpdate):
    id: Optional[int]


class DivisionReadDetails(DivisionRead):
    div_district: Optional[List[DistrictRead]]
