from typing import List, Union, Optional
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.dialects.postgresql import insert
from base.db import async_session_maker

from forcast.models.temp_data import Temperature
from forcast.schemas.temperature import TempBase, TempReadBase, TempUpdate


class TempDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, temp: TempBase):
        new_temp = Temperature(**temp.dict())
        self.db_session.add(new_temp)
        await self.db_session.commit()
        await self.db_session.flush()
        return TempReadBase(**new_temp.__dict__)


    # async def get(
    #     self,
    #     id: Union[int, None] = None,
    #     name: Union[str, None] = None,
    # ) -> List[DistrictRead]:
    #     if id:
    #         q = await self.db_session.execute(select(District).where(District.id == id))
    #         temps = q.scalars().all()
    #         resp = [DistrictRead(**temp.__dict__) for temp in temps]
    #         return resp

    #     if name:
    #         q = await self.db_session.execute(
    #             select(District).where(District.name == name)
    #         )
    #         temps = q.scalars().all()
    #         resp = [DistrictRead(**temp.__dict__) for temp in temps]
    #         return resp
    #     else:
    #         q = await self.db_session.execute(select(District))
    #         temps = q.scalars().all()
    #         resp = [DistrictRead(**temp.__dict__) for temp in temps]
    #         return resp

    # async def update(
    #     self,
    #     id: Optional[int],
    #     district_id: Optional[int],
    #     district_name: Optional[str],
    #     temp: TempUpdate,
    # ):
    #     if not (district_id or district_name):
    #         return False
    #     if id:
    #         q = update(District).where(District.id == id)
    #         data_dict = district.dict(exclude_unset=True)
    #         q = q.values(**data_dict)
    #         q.execution_options(synchronize_session="fetch")
    #         await self.db_session.execute(q)
    #         await self.db_session.commit()
    #         return data_dict
    #     if name:
    #         q = update(District).where(District.name == name)
    #         data_dict = district.dict(exclude_unset=True)
    #         q = q.values(**data_dict)
    #         q.execution_options(synchronize_session="fetch")
    #         await self.db_session.execute(q)
    #         await self.db_session.commit()
    #         return data_dict

    # async def sync(
    #     self,
    #     district_list: List[DistrictUpdate],
    # ):
    #     for data in district_list:
    #         stmt = insert(District).values(
    #             id=data.id,
    #             name=data.name,
    #             lat=data.lat,
    #             long=data.long,
    #             division_id=data.division_id
    #             # Add more columns as needed
    #         )

    #         on_conflict_stmt = stmt.on_conflict_do_update(
    #             constraint="district_id_pkey",
    #             set_={
    #                 "name": stmt.excluded.name,
    #                 "lat": stmt.excluded.lat,
    #                 "long": stmt.excluded.long,
    #                 "division_id": stmt.excluded.division_id,
    #             },
    #         )

    #         await self.db_session.execute(on_conflict_stmt)

    #     # Commit the changes
    #     await self.db_session.commit()


async def get_temp_dal():
    async with async_session_maker() as session:
        async with session.begin():
            yield TempDAL(session)
