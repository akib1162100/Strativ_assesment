from typing import Optional
import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import json
from fastapi import status
from fastapi.responses import JSONResponse
from datetime import date, datetime, timedelta
from forcast.crud.district import get_district_dal
from forcast.schemas.temperature import TempUpdate
from forcast.utils.temp_priority import TemperaturePriorityQueue


class TempService:
    def __init__(self) -> None:
        self.cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
        self.temp_url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": None,
            "longitude": None,
            "hourly": "temperature_2m",
            "timezone": "auto",
            "forecast_days": 7,
        }
        self.recommand_params = {
            "latitude": None,
            "longitude": None,
            "hourly": ["temperature_2m", "rain"],
            "timezone": "auto",
            "start_date": "2023-11-30",
            "end_date": "2023-12-11",
        }
        self.comfortable_temperature_range = (
            20,
            25,
        )  # Example: Between 20 and 25 degrees Celsius
        self.max_rain_threshold = 1.0

    async def _get_districts(self, name: Optional[str]):
        district_dal_gen = get_district_dal()
        district_dal = await district_dal_gen.__anext__()
        if name:
            return await district_dal.get(name=name)
        else:
            return await district_dal.get()

    def _get_temp(self, is_recommand=False):
        try:
            if is_recommand:
                responses = self.openmeteo.weather_api(
                    self.temp_url, params=self.recommand_params
                )
                return responses
            responses = self.openmeteo.weather_api(self.temp_url, params=self.params)
            return responses
            # rolling_avg = (
            #     data_at_2pm["temperature_2m"].rolling(window=7, min_periods=1).mean()
            # )

            # # Add the rolling average to the DataFrame
            # data_at_2pm["rolling_avg"] = rolling_avg
            # data_at_2pm["rolling_avg"] = data_at_2pm["rolling_avg"].shift(-6)
            # return data_at_2pm.head(7).to_dict(orient="records")

        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
            )

    def _process_temp(self, respon):
        response = respon
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }
        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        data_at_2pm = hourly_dataframe[hourly_dataframe["date"].dt.hour == 14]

        return data_at_2pm["temperature_2m"].mean()

    async def find_cooler(self):
        districts = await self._get_districts()
        if isinstance(districts, JSONResponse):
            return districts
        lats = [dist.lat for dist in districts]
        longs = [dist.lat for dist in districts]
        self.names = [dist.name for dist in districts]
        temp_priority_list = TemperaturePriorityQueue(max_length=10)
        self.params["latitude"] = lats
        self.params["longitude"] = longs
        data = self._get_temp()
        for name, temp in zip(self.names, data):
            mean = self._process_temp(respon=temp)
            temp_priority_list.add_district(district_name=name, temperature=mean)
        coolest_dists = temp_priority_list.get_priority_districts()
        return coolest_dists

    def _process_recommand(self, resspon):
        response = resspon
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_rain = hourly.Variables(1).ValuesAsNumpy()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["rain"] = hourly_rain
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        data_at_2pm = hourly_dataframe[hourly_dataframe["date"].dt.hour == 14]

        travel_location = (
            data_at_2pm["temperature_2m"].between(*self.comfortable_temperature_range)
        ) & (data_at_2pm["rain"] <= self.max_rain_threshold)

        return travel_location

    async def recommand(self, start_dist: str, end_dist: str, return_date: date):
        from_dist = await self._get_districts(name=start_dist)
        to_dist = await self._get_districts(name=end_dist)
        if isinstance(from_dist, JSONResponse) or isinstance(to_dist, JSONResponse):
            return from_dist, to_dist
        todate = datetime.today().date()
        max_date = todate + timedelta(days=16)
        if return_date > max_date:
            return_date = max_date
        lats = [from_dist[0].lat, to_dist[0].lat]
        longs = [from_dist[0].long, to_dist[0].long]
        self.from_place = from_dist[0].name
        self.to_place = to_dist[0].name
        self.recommand_params["latitude"] = lats
        self.recommand_params["longitude"] = longs
        self.recommand_params["start_date"] = todate.strftime("%Y-%m-%d")
        self.recommand_params["end_date"] = todate.strftime("%Y-%m-%d")

        data = self._get_temp(is_recommand=True)
        if isinstance(data, JSONResponse):
            return data
        travel_current_location = self._process_recommand(resspon=data[0])
        travel_destination = self._process_recommand(resspon=data[1])

        if travel_current_location.all() and travel_destination.all():
            return JSONResponse(
                content={
                    "message": "Both locations have suitable weather conditions. You can consider traveling."
                },
                status_code=status.HTTP_200_OK,
            )
        elif travel_current_location.all():
            return JSONResponse(
                content={
                    "message": "Your current location has suitable weather conditions, but the destination may not be ideal."
                },
                status_code=status.HTTP_200_OK,
            )

        elif travel_destination.all():
            return JSONResponse(
                content={
                    "message": "The destination has suitable weather conditions, but your current location may not be ideal."
                },
                status_code=status.HTTP_200_OK,
            )

        else:
            return JSONResponse(
                content={
                    "message": "Neither your current location nor the destination has suitable weather conditions. Consider postponing your travel."
                },
                status_code=status.HTTP_200_OK,
            )

    # async def sync(self):
    #     districts = await self._get_districts()
    #     if isinstance(districts, JSONResponse):
    #         return districts
    #     temp_update_list = []
    #     for district in districts:
    #         self.params["latitude"] = district.lat
    #         self.params["longitude"] = district.long
    #         district_id = district.id
    #         district_name = district.name
    #         temp_data = self._get_temp()
    #         for temp in temp_data:
    #             temp_sync_obj = TempUpdate(
    #                 date=temp.get("date").date(),
    #                 time=temp.get("date").time(),
    #                 temperature=temp.get("temperature_2m"),
    #                 district_id=district_id,
    #                 district_name=district_name,
    #                 temp_average=temp.get("rolling_avg"),
    #             )
    #             temp_update_list.append(temp_sync_obj)
    #     # temp_update_list

    #     response = self.openmeteo.weather_api(self.url, params=self.params)
    #     data = json.loads(response.content)
    #     temp_list = data.get("temperature")
    #     return temp_list
