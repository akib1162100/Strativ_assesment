from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from base.db import Base, BaseModel
from forcast.models.division import Division


class District(Base, BaseModel):
    __tablename__ = "district"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    division = relationship("DivisionDIS", back_populates="div_district")
    division_id = Column(Integer, ForeignKey("division.id", ondelete="CASCADE"))


class DivisionDIS(Division):
    div_district = relationship("District", back_populates="division")
