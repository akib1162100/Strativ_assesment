from forcast.crud.district import DistrictDAL
from forcast.schemas.district import DistrictUpdate, DistrictRead
from forcast.crud.district import get_district_dal
import requests
import json


class DistrictService:
    def __init__(self) -> None:
        self.district_url = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"

    def _get_districts(self):
        response = requests.get(url=self.district_url)
        data = json.loads(response.content)
        dist_list = data.get("districts")
        return dist_list

    async def sync(self):
        dist_list = self._get_districts()
        district_dal_gen = get_district_dal()
        dist_update_list = [DistrictUpdate(**dist) for dist in dist_list]
        district_dal = await district_dal_gen.__anext__()
        return await district_dal.sync(dist_update_list)
