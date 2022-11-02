from abc import abstractmethod
import requests
import json
import configparser
import os
from zipfile import ZipFile
import re

#TODO: finish _get_current_version, _update_current_version 

class WowAddon:
    addon_name = None
    newest_version = None

    @abstractmethod
    def update(self):
        raise NotImplemented

class GithubWowAddon(WowAddon):
    def __init__(self, url, token, versions_dir="addon_versions"):
        user, addon_name = self._get_user_repo_from_url(url)
        self.user = user
        self.addon_name = addon_name
        self.token = token
        self.versions_dir = versions_dir
        self._get_current_version()

    self._get_current_version(self):
        # check for version file inside versions dir
        # file name is addon name
        # if there - read file and set file contents to current version
        # if not there - current version = None
        pass

    @staticmethod
    def _get_user_repo_from_url(url):
        pattern = r'https:\/\/github.com\/(\w+)\/(.+)'
        match = re.search(pattern, url)
        if not match:
            return None
        user = match.group(1)
        repo = match.group(2)
        return user, repo

    def _check_for_new_version(self)
        self._get_latest_release_json_from_repo()
        self.newest_version = self._get_newest_version()

    def _get_latest_release_json_from_repo(self):
        headers = {"accept":"application/vnd.github.v3+json", "Authorization":f"token {self.token}"}
        api_url = f"https://api.github.com/repos/{self.user}/{self.repo}/releases"
        response = requests.get(api_url, headers=headers)
        return json.loads(response.content)[0]

    def _get_newest_version(self):
        return self.info_json.get("tag_name")

    def update(self, wow_install_dir):
        if not self.does_addon_need_updating():
            return
        self.print_update_message()
        dl_url = self._get_zip_file_url_from_release_json(self.info_json)
        dl_filename = self.addon_name + "_" + self._get_file_name_from_url(dl_url)
        dl_file_path = self._create_download_file_path(dl_filename, wow_install_dir)
        self._download_file(dl_url, dl_file_path)
        self._unzip_file(dl_file_path, wow_install_dir)
        self._update_current_version()
        os.remove(dl_file_path)

    def does_addon_need_updating(self):
        self._check_for_new_version()
        if self.current_version is None:
            return True
        if self.newest_version != self.current_version:
            return True
        return False

    def print_update_message(self):
        print(f"Updating {self.addon_name} from version {self.current_version} to {self.newest_version}")

    @staticmethod
    def _get_zip_file_url_from_release_json(release_json):
        return release_json["assets"][0]["browser_download_url"]

    @staticmethod
    def _get_file_name_from_url(url):
        return url.split("/")[-1]

    @staticmethod
    def _create_download_file_path(filename, file_path):
        return os.path.join(file_path, filename)

    @staticmethod
    def _download_file(url, file_path):
        response = requests.get(url, stream=True)
        with open(file_path, "wb") as file_obj:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file_obj.write(chunk)

    @staticmethod
    def _unzip_file(zip_file_path, output_dir):
        with ZipFile(zip_file_path, 'r') as zip_obj:
            zip_obj.extractall(output_dir)

    def _update_current_version(self):
        # if versions dir does not exist - create it
        # current version = newest version
        # write current version to file inside versions dir
        # file name is addon name
