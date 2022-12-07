"""
API Client for Vintage Story MOD DB
"""
from dataclasses import dataclass
import pathlib
from typing import Dict, List
from app_config import AppConfig
from config import configuration
import requests
from os.path import exists, isfile

BASE_API_URI = "http://mods.vintagestory.at/api/{stub}"
BASE_FILE_URI = "https://mods.vintagestory.at/{file_path}"
FILE_CHUNK_SIZE = 8192


@dataclass
class SearchQueryParams:
    tagids: List[int]
    gameversion: str
    gameversions: List[str]
    author: int
    orderby: str
    orderdirection: str


class RequestClient:

    headers = {
        'User-Agent': 'Vintage Story Mod Manager',
        'From': 'thom.lambert@outlook.com'  # This is another valid field
    }
    def __init__(self, cfg: configuration):
        #todo: pass app config on init
        self.cfg = cfg
        pass

    def get(self, stub, params=None):
        query_params = params.as_dict() if params else None
        response = requests.get(BASE_API_URI.format(stub=stub), params=query_params, headers=self.headers)
        # todo: check response, raise exc
        return response.json()

    def download_archive(self, url, save_location: pathlib.Path) -> pathlib.Path:
        if exists(save_location) and isfile(save_location): return save_location # dont redownload existing files
        with requests.get(url, stream=True) as req:
            req.raise_for_status()
            with open(str(save_location), 'wb') as f:
                for chunk in req.iter_content(chunk_size=FILE_CHUNK_SIZE):
                    f.write(chunk)
        return save_location



class APIClient(RequestClient):

    def __init__(self, cfg: configuration):
        super().__init__(cfg)

    def get_tags(self) -> Dict:
        return self.get("tags")["tags"]

    def get_gameversions(self) -> Dict:
        return self.get("gameversions")["gameversions"]

    def get_comments(self, assetid: int = None) -> Dict:
        if not assetid:
            return self.get("comments")
        return self.get("comments/{}".format(assetid))["comments"]

    def get_changelogs(self, assetid: int = None) -> Dict:
        if not assetid:
            return self.get("changelogs")
        return self.get("/changelogs/{}".format(assetid))

    def get_mods(self, query: SearchQueryParams=None) -> Dict:
        return self.get("mods", query)["mods"]

    def get_mod_metadata(self, modid: int) -> Dict:
        return self.get("mod/{}".format(modid))["mod"]

    def download_mod(self, archive_asset_stub: str, save_location: pathlib.Path) -> pathlib.Path:
        return self.download_archive(BASE_FILE_URI.format(file_path=archive_asset_stub), save_location)

    def bulk_download_mods(self, mod_ids: List[int]) -> List[str]:
        downloaded_files = []
        for id in mod_ids:
            downloaded_files.append(self.download_archive(id))
            # todo: add rate limit
        return downloaded_files