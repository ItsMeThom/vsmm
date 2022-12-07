""" 
Responsible for:
    Deploying a profile to the game (moving mods)
    Filehandling operations (downloading, deleting mod archives) 
"""
import json
import os
from os import getcwd, listdir
from pathlib import Path
from .file import FileManager
from .mod import ModManager
from api.client import APIClient
from pydantic import BaseModel
from datetime import datetime
from typing import List
from config.configuration import Configuration
from os.path import pathsep





class ProfileModEntry(BaseModel):
    id: int
    name: str
    tags: List[str]
    version: str
    archive_path: Path
    archive_name: str


class Profile(BaseModel):
    name: str
    desc: str
    mods : List[ProfileModEntry] # todo: should this be a dataclass too for caching?
    last_update: datetime
    active: bool = False


class ProfileManager:

    def __init__(self, cfg: Configuration, api: APIClient, mod: ModManager, file: FileManager):
        self.cfg = cfg
        self.api = api
        self.mod = mod
        self.file = file

        self.profiles: List[Profile] = []
        self.load_profiles_from_disk()

    def create_profile(self, name: str, desc: str, mods: List[int]) -> bool:
        profile_path = f"{self.config.app.profiles_location}{pathsep}{name}.json"
        if self.file.exists_locally(profile_path):
            return False #profile already exists
        new_profile = Profile(name, desc, [], datetime.now())
        self.file.write(profile_path, new_profile.json())
        return True

    def get_profile(self, profile_name: str) -> Profile:
        for profile in self.profiles:
            if profile.name == profile_name: return profile
        return None

    def get_active_profile(self) -> Profile:
        for profile in self.profiles:
            if profile.active: return profile
        return None

    def delete_profile(self, profile_name: str) -> bool:
        profile_path = Path(getcwd(), self.config.app.profiles_location, f"{profile_name}.json")
        if not self.file.exists_locally(profile_path):
            return False
        self.file.delete(profile_path)
        return True

    def deploy_profile(self, profile_name: str) -> bool:
        currently_deployed_profile = self.get_active_profile()
        if currently_deployed_profile is not None:
            self.undeploy_profile(currently_deployed_profile.name)
        deploying_profile = self.get_profile(profile_name)
        for mod in deploying_profile.mods:
            mod_archive_path = self.mod.mod_archive_local_path(mod.id, mod.version)
            if mod_archive_path is None:
                mod_archive_path = self.mod.download_mod_version(mod.id, mod.version)
                #todo: signal that mod is downloaded.
            self.file.copy(
                mod_archive_path, 
                Path(self.cfg.game.folder_path, "mods")
            )
            #todo: signal mod is deployed.
        deploying_profile.active = True
        self.save(deploying_profile)
        print(f"Deployed profile {profile_name} with {len(deploying_profile.mods)} mods")
        return True
    
    def undeploy_profile(self, profile_name: str) -> bool:
        undeploy_profile = self.get_profile(profile_name)
        if not undeploy_profile.active: return True
        for mod in undeploy_profile.mods:
            deployed_archive_path = Path(getcwd(), self.cfg.game.folder_path, "mods", mod.archive_name)
            if self.file.delete(deployed_archive_path): 
                continue 
            else: return False #failed to remove for some reason (todo: raise exc here)
        self.save(undeploy_profile)
        return True

    def check_for_updates(profile_id=None):
        # get active profile
        # updateable = mod_manager.check_for_updates(profile.mods)
        # return updateable
        pass

    def add_mod_to_profile(self, profile_name: str, mod_id: int, mod_version: str):
        """ Downloads a mod archive and adds an entry to this profile with the path so it can be applied to the game. """
        profile = self.get_profile(profile_name)
        archive_path = self.mod.mod_archive_local_path(mod_id, mod_version)
        if not archive_path:
            archive_path = self.mod.download_mod_version(mod_id, mod_version)
        mod_info = self.mod.get_mod_info(mod_id)
        new_mod_entry = ProfileModEntry(
            id=mod_id,
            name=mod_info.name,
            tags=mod_info.tags,
            version=mod_version,
            archive_path=archive_path,
            archive_name=str(archive_path).split("/")[-1]
        )
        # todo: check mod already in profile, raise err if true
        for mod in profile.mods:
            if new_mod_entry.name == mod.name:
                # if versions match, give warning about double versions
                # todo: allow user to replace mod with newer automatically?
                print("Mod already exists in profile!")
                return
        profile.mods.append(new_mod_entry)
        self.save(profile)

    def remove_mod_from_profile(self, profile_name: str, mod_id: int, mod_version: str):
        """ Removes a mod archive from a profile, but does NOT delete the mod archive (In case other profiles rely on it. """
        selected_profile = self.get_profile(profile_name)
        for index, mod in enumerate(selected_profile.mods):
            if mod_id == mod.id and mod_version == mod.version:
                print("Mod removed from profile")
                selected_profile.mods.pop(index)
                self.save(selected_profile)

    def load_profiles_from_disk(self):
        """ Load the profiles from disk. """
        profile_folder = Path(getcwd(), self.cfg.app.profiles_location)
        json_files = [ f for f in listdir(profile_folder) if f.endswith("json") ]
        if len(json_files) == 0:
            # create a default empty profile if none exists in the directory
            default_profile = Profile(name="Default", desc="The default profile", mods=[], last_update=datetime.now(), active=True)
            self.profiles.append(default_profile)
            self.save(default_profile)
            return
        for json_file in json_files:
            json_file_path = Path(getcwd(), self.cfg.app.profiles_location, json_file)
            file_contents = self.file.read(json_file_path).decode('ascii')
            print(file_contents)
            profile = Profile(**json.loads(file_contents))
            self.profiles.append(profile)

    def save(self, profile: Profile) -> Path:
        """ Write a profile to disk in the profile directory using its name as the filename. """
        json_file_path =Path(getcwd(), self.cfg.app.profiles_location, f"{profile.name}.json")
        self.file.write(json_file_path, profile.json())

    def save_all(self):
        """ Save all profiles to disk. """
        for profile in self.profiles:
            json_file_path =Path(getcwd(), self.cfg.app.profiles_location, f"{profile}.json")
            self.file.write(json_file_path, profile.json())
