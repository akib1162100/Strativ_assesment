import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import json
from fastapi import status
from fastapi.responses import JSONResponse

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

    async def _get_districts(self):
        district_dal_gen = get_district_dal()
        district_dal = await district_dal_gen.__anext__()
        return await district_dal.get()

    def _get_temp(self):
        try:
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
