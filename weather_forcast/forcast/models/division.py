from sqlalchemy import (
    Column,
    Integer,
    String,
)

from base.db import Base, BaseModel


class Division(Base, BaseModel):
    __tablename__ = "division"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
