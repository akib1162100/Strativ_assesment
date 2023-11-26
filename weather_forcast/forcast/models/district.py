from sqlalchemy import Column, Integer, String, ForeignKey, Float, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from base.db import Base, BaseModel
from forcast.models.division import Division


class District(Base, BaseModel):
    __tablename__ = "district"
    # p_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float)
    long = Column(Float)
    division = relationship("DivisionDIS", back_populates="div_district")
    division_id = Column(Integer, ForeignKey("division.id", ondelete="CASCADE"))

    __table_args__ = (PrimaryKeyConstraint("id", name="district_id_pkey"),)


class DivisionDIS(Division):
    div_district = relationship("District", back_populates="division")

