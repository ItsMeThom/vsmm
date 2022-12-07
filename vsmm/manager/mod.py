from collections import OrderedDict
import json
from os import getcwd

from api.client import APIClient
from .file import FileManager
from datetime import datetime
from typing import Any, Dict, List, Optional
from config.configuration import Configuration
from os.path import exists, isfile
import pathlib
from pydantic import BaseModel




class ModInfo(BaseModel):
    modid: int
    assetid: int
    name: str
    text: str
    author: str
    logofile: str
    homepageurl: str
    dowwloads: int = 0
    follows: int = 0
    trendingpoints: int = 0
    side: str
    tags: List[str]
    releases: List[Any] #is a dict
    screenshots: List[Any]


class ModMetadata(BaseModel):
    modid: int
    assetid: int
    name: str
    author: str
    logo: Optional[str]
    downloads: Optional[int]
    lastreleased: Optional[str]
    tags: List[str]
    side: str

class ModCache(BaseModel):
    mods: List[ModMetadata]
    last_updated: datetime

class ModManager:
    
    def __init__(self, cfg: Configuration, api: APIClient, file: FileManager):
        self.cfg = cfg
        self.api = api
        self.file = file

        self.mod_cache = ModCache(mods=[], last_updated=datetime.now())
        self.load_cache_from_disk()

    def update_cache(self):
        """ Contacts the VS mod db API to update the local cache of available mods."""
        mods_metadata = [
            ModMetadata(**metadata) for metadata in self.api.get_mods()
        ]
        self.mod_cache = ModCache(mods=mods_metadata, last_updated=datetime.now())
        self.save_cache_to_disk()

    def clear_active_mods(self):
        # get path to VS mods folder from config
        # remove all active mods in that folder (delete zips)
        pass

    def download_mod_version(self, mod_id: int, mod_version: str) -> pathlib.Path:
        mod_info = self.get_mod_info(mod_id)
        release_links = self.get_available_mod_release_links(mod_info)
        asset_stub = release_links[mod_version] # todo: check this is valid first!
        archive_name = asset_stub.split('/')[-1]
        archive_save_location = pathlib.Path(getcwd(), self.cfg.app.downloads_location, archive_name)
        print(f"archive save location: {archive_save_location}")
        return self.api.download_mod(asset_stub, archive_save_location)

    def get_available_mod_release_links(self, mod_metadata: ModInfo) ->Dict[str, str]:
        """ Returns a ordered dict (most recent first) of mod semantic versions and the associated archive stubs"""
        versions = {}
        for release in mod_metadata.releases:
            versions[release["modversion"]] = release["mainfile"]
        return versions

    def mod_archive_local_path(self, mod_id: int, mod_version: str) -> pathlib.Path:
        """ Return a path to the archive for a given mod version if it exists, or None if it does not."""
        mod_info = self.get_mod_info(mod_id)
        release_links = self.get_available_mod_release_links(mod_info)
        if mod_version not in release_links.keys(): return False # unknown version
        archive_name = release_links[mod_version].split('/')[-1]
        archive_path = pathlib.Path(getcwd(), self.cfg.app.downloads_location, archive_name)
        if self.file.exists_locally(archive_path): 
            return archive_path 
        else: 
            return None

    def get_mod_info(self, mod_id: int) -> ModInfo:
        """ Retreive the detailed metadata for a mod. """
        mod_info = ModInfo(**self.api.get_mod_metadata(mod_id))
        return mod_info

    def load_cache_from_disk(self):
        """ Loads the mod definitions metadata from the local mod cache."""
        cache_filename = "mod_cache.json"
        mod_cache_path = pathlib.Path(getcwd(), self.cfg.app.downloads_location, cache_filename)
        if not exists(mod_cache_path) and not isfile(mod_cache_path):
            # if the mod_cache.json is missing, dont panic, just fetch the latest
            self.update_cache()
        else:
            #todo: fix to load mods as objects then populate cache
            self.mod_cache = ModCache(
                **json.loads(
                    self.file.read(
                        pathlib.Path(self.cfg.app.downloads_location, cache_filename)
                    )
                )
            )
            print("Cache loaded successfully!")

    def save_cache_to_disk(self):
        """ Write the mod definitions to disk as json so we dont have to contact the server as often."""
        cache_filename = "mod_cache.json"
        self.file.write(
            pathlib.Path(getcwd(), self.cfg.app.downloads_location, cache_filename),
            self.mod_cache.json()
        )
