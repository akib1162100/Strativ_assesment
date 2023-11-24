from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional, List
from forcast.schemas.temperature import TempReadBase


class DistrictBase(BaseSchema):
    name: str
    latitude: float
    longitude: float
    division_id: int


class DistrictUpdate(UpdateBaseSchema):
    name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    division_id: Optional[int]


class DistrictRead(DistrictUpdate):
    id: Optional[int]


class DistrictReadTemp(DistrictRead):
    temp_data = Optional[List[TempReadBase]]
