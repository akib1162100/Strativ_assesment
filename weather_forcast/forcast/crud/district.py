from typing import List, Union, Optional
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from forcast.schemas.district import (
    DistrictBase,
    DistrictRead,
    DistrictUpdate,
    DistrictReadTemp,
)
from forcast.schemas.temperature import TempReadBase
from base.db import async_session_maker
from forcast.models.district import District
from forcast.models.temp_data import DistrictTemp


class DistrictDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, district: DistrictBase):
        new_district = District(**district.dict())
        self.db_session.add(new_district)
        await self.db_session.commit()
        await self.db_session.flush()
        return DistrictRead(**new_district.__dict__)

    def _proc_data(self, temp):
        response = []
        for data in temp:
            data_dict = data.__dict__
            if data_dict.get("temp_datas"):
                data_dict["temp_datas"] = data_dict.get("temp_datas").__dict__

            response.append(TempReadBase(**data_dict))
        return response

    async def get_details(
        self,
        id: Union[int, None] = None,
        name: Union[str, None] = None,
    ) -> List[DistrictReadTemp]:
        if id:
            q = await self.db_session.execute(
                select(DistrictTemp)
                .where(DistrictTemp.id == id)
                .options(selectinload(DistrictTemp.temp_datas))
            )
            temps = q.scalars().all()
            resp = self._proc_data(temps=temps)
            return resp

        if name:
            q = await self.db_session.execute(
                select(DistrictTemp)
                .where(DistrictTemp.name == name)
                .options(selectinload(DistrictTemp.temp_datas))
            )
            temps = q.scalars().all()
            resp = self._proc_data(temps=temps)
            return resp
        else:
            q = await self.db_session.execute(
                select(DistrictTemp).options(selectinload(DistrictTemp.temp_datas))
            )
            temps = q.scalars().all()
            resp = self._proc_data(temps=temps)
            return resp

    async def get(
        self,
        id: Union[int, None] = None,
        name: Union[str, None] = None,
    ) -> List[DistrictRead]:
        if id:
            q = await self.db_session.execute(
                select(DistrictTemp).where(DistrictTemp.id == id)
            )
            temps = q.scalars().all()
            resp = [DistrictRead(**temp.__dict__) for temp in temps]
            return resp

        if name:
            q = await self.db_session.execute(
                select(DistrictTemp).where(DistrictTemp.name == name)
            )
            temps = q.scalars().all()
            resp = [DistrictRead(**temp.__dict__) for temp in temps]
            return resp
        else:
            q = await self.db_session.execute(select(DistrictTemp))
            temps = q.scalars().all()
            resp = [DistrictRead(**temp.__dict__) for temp in temps]
            return resp

    async def update(
        self,
        id: Optional[int],
        name: Optional[str],
        district: DistrictUpdate,
    ):
        if not (id or name):
            return False
        if id:
            q = update(District).where(District.id == id)
            data_dict = district.dict(exclude_unset=True)
            q = q.values(**data_dict)
            q.execution_options(synchronize_session="fetch")
            await self.db_session.execute(q)
            await self.db_session.commit()
            return data_dict
        if name:
            q = update(District).where(District.name == name)
            data_dict = district.dict(exclude_unset=True)
            q = q.values(**data_dict)
            q.execution_options(synchronize_session="fetch")
            await self.db_session.execute(q)
            await self.db_session.commit()
            return data_dict

    async def delete(self, id: int):
        request = await self.db_session.execute(
            select(District).where(District.id == id)
        )
        await self.db_session.delete(request.scalar_one())
        await self.db_session.commit()


async def get_district_dal():
    async with async_session_maker() as session:
        async with session.begin():
            yield DistrictDAL(session)
