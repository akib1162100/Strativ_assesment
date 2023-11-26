from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional, List
from forcast.schemas.temperature import TempReadBase


class DistrictBase(BaseSchema):
    name: str
    lat: float
    long: float
    division_id: int
    id: Optional[int]


class DistrictUpdate(UpdateBaseSchema):
    name: Optional[str]
    lat: Optional[float]
    long: Optional[float]
    division_id: Optional[int]
    id: Optional[int]


class DistrictRead(DistrictUpdate):
    pass


class DistrictReadBase(UpdateBaseSchema):
    lat: Optional[float]
    long: Optional[float]


class DistrictReadTemp(DistrictUpdate):
    temp_datas: List[TempReadBase]
