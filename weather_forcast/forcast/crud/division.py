from typing import List, Union, Optional
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from forcast.schemas.division import (
    DivisionBase,
    DivisionRead,
    DivisionUpdate,
    DivisionReadDetails,
)
from forcast.schemas.district import DistrictRead
from base.db import async_session_maker
from forcast.models.district import DivisionDIS
from forcast.models.division import Division


class DivisionDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, division: DivisionBase):
        new_division = Division(**division.dict())
        self.db_session.add(new_division)
        await self.db_session.commit()
        await self.db_session.flush()
        return DivisionRead(**new_division.__dict__)

    def _proc_data(self, dis):
        response = []
        for data in dis:
            data_dict = data.__dict__
            if data_dict.get("div_district"):
                data_dict["div_district"] = data_dict.get("div_district").__dict__

            response.append(DistrictRead(**data_dict))
        return response

    async def get_details(
        self,
        id: Union[int, None] = None,
        name: Union[str, None] = None,
    ) -> List[DivisionReadDetails]:
        if id:
            q = await self.db_session.execute(
                select(DivisionDIS)
                .where(DivisionDIS.id == id)
                .options(selectinload(DivisionDIS.div_district))
            )
            temps = q.scalars().all()
            resp = self._proc_data(temps=temps)
            return resp

        if name:
            q = await self.db_session.execute(
                select(DivisionDIS)
                .where(DivisionDIS.name == name)
                .options(selectinload(DivisionDIS.div_district))
            )
            temps = q.scalars().all()
            resp = self._proc_data(temps=temps)
            return resp
        else:
            q = await self.db_session.execute(
                select(DivisionDIS).options(selectinload(DivisionDIS.div_district))
            )
            temps = q.scalars().all()
            resp = self._proc_data(temps=temps)
            return resp

    async def get(
        self,
        id: Union[int, None] = None,
        name: Union[str, None] = None,
    ) -> List[DivisionRead]:
        if id:
            q = await self.db_session.execute(
                select(DistrictRead).where(DistrictRead.id == id)
            )
            temps = q.scalars().all()
            resp = [DivisionRead(**temp.__dict__) for temp in temps]
            return resp

        if name:
            q = await self.db_session.execute(
                select(DistrictRead).where(DistrictRead.name == name)
            )
            temps = q.scalars().all()
            resp = [DivisionRead(**temp.__dict__) for temp in temps]
            return resp
        else:
            q = await self.db_session.execute(select(DistrictRead))
            temps = q.scalars().all()
            resp = [DivisionRead(**temp.__dict__) for temp in temps]
            return resp

    async def update(
        self,
        id: Optional[int],
        name: Optional[str],
        division: DivisionUpdate,
    ):
        if not (id or name):
            return False
        if id:
            q = update(Division).where(Division.id == id)
            data_dict = division.dict(exclude_unset=True)
            q = q.values(**data_dict)
            q.execution_options(synchronize_session="fetch")
            await self.db_session.execute(q)
            await self.db_session.commit()
            return data_dict
        if name:
            q = update(Division).where(Division.name == name)
            data_dict = division.dict(exclude_unset=True)
            q = q.values(**data_dict)
            q.execution_options(synchronize_session="fetch")
            await self.db_session.execute(q)
            await self.db_session.commit()
            return data_dict

    async def delete(self, id: int):
        request = await self.db_session.execute(
            select(Division).where(Division.id == id)
        )
        await self.db_session.delete(request.scalar_one())
        await self.db_session.commit()


async def get_division_dal():
    async with async_session_maker() as session:
        async with session.begin():
            yield DivisionDAL(session)
