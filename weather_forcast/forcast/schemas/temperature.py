from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional
from datetime import date, time


class TempBase(BaseSchema):
    district_id: int
    date: date
    time: time
    temperature: float
    district_name: str


class TempUpdate(UpdateBaseSchema):
    district_id: Optional[int]
    date: Optional[date]
    time: Optional[time]
    temperature: Optional[float]
    temp_average: Optional[float]
    district_name: Optional[str]


class TempReadBase(TempUpdate):
    id: Optional[int]
