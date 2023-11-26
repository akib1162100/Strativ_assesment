from fastapi import APIRouter
from forcast.routers.forcast_router import weather_forcast_router


app_router = APIRouter(
    prefix="/weather",
    responses={404: {"description": "Not found"}},
)

app_router.include_router(
    weather_forcast_router,
    tags=["weather"],
)
