from sqlalchemy import Column, Integer, Time, ForeignKey, Date, DateTime, Float
from sqlalchemy.orm import relationship
from base.db import Base, BaseModel
from forcast.models.district import District


class Temperature(Base, BaseModel):
    __tablename__ = "temperature_data"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    temp_avg = Column(Float)
    date = Column(Date)
    time = Column(Time)
    district = relationship("DistrictTemp", back_populates="temp_data")
    district_id = Column(Integer, ForeignKey("district.id", ondelete="CASCADE"))


class DistrictTemp(District):
    temp_datas = relationship("Temperature", back_populates="district")
