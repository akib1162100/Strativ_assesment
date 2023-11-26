from typing import List, Union, Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from forcast.crud.district import get_district_dal, DistrictDAL
from forcast.services.district import DistrictService
from forcast.services.temperature import TempService
import timeit
import asyncio
from datetime import date, datetime

weather_forcast_router = APIRouter(
    prefix="/foscast",
    tags=["Forcast"],
    responses={404: {"description": "Not found"}},
)


@weather_forcast_router.get("/district_details", status_code=status.HTTP_200_OK)
async def get_district_details(
    id: Union[int, None] = None,
    name: Union[str, None] = None,
    district_dal: DistrictDAL = Depends(get_district_dal),
):
    try:
        return await district_dal.get_details(id=id, name=name)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )


@weather_forcast_router.get("/districts", status_code=status.HTTP_200_OK)
async def get_districts(
    id: Union[int, None] = None,
    name: Union[str, None] = None,
    district_dal: DistrictDAL = Depends(get_district_dal),
):
    try:
        return await district_dal.get(id=id, name=name)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )


@weather_forcast_router.post("/district_sync", status_code=status.HTTP_201_CREATED)
async def sync_district():
    dist_service = DistrictService()
    return await dist_service.sync()


@weather_forcast_router.get("/coolest_temp", status_code=status.HTTP_200_OK)
async def coolest_temp():
    temp_service = TempService()
    return await temp_service.find_cooler()


@weather_forcast_router.get("/recommand", status_code=status.HTTP_200_OK)
async def recommand_temp(start: str, dest: str, retrun_date: date):
    temp_service = TempService()
    return await temp_service.recommand(
        start_dist=start, end_dist=dest, return_date=retrun_date
    )
