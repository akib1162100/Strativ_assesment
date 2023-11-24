from base.schemas.base_schema import BaseSchema, UpdateBaseSchema
from typing import Optional


class DivisionBase(BaseSchema):
    name: str


class DivisionUpdate(UpdateBaseSchema):
    name: Optional[str]


class DivisionRead(DivisionUpdate):
    id: Optional[int]

