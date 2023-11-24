from typing import List, Union, Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

weather_forcast_router = APIRouter(
    prefix="/foscast",
    responses={404: {"description": "Not found"}},
)

