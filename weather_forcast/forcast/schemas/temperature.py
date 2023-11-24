from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional
from datetime import date, time
from forcast.schemas.district import DistrictRead


class TempBase(BaseSchema):
    district_id: int
    date: date
    time: time
    temperature: float


class TempUpdate(UpdateBaseSchema):
    district_id: Optional[int]
    date: Optional[date]
    time: Optional[time]
    temperature: Optional[float]
    temp_avg: Optional[float]


class TempReadBase(TempUpdate):
    id: Optional[int]


class TempReadDetails(TempReadBase):
    district: Optional[DistrictRead]
