from abc import abstractmethod
import requests
import json
import configparser
import os
from zipfile import ZipFile
import re

#TODO: add dir for addon_versions, check version before updating

class WowAddon:
    addon_name = None
    newest_version = None

    @abstractmethod
    def update(self):
        raise NotImplemented

class GithubWowAddon(WowAddon):
    def __init__(self, url):
        user, addon_name = self._get_user_repo_from_url(url)
        self.addon_name = addon_name
        self.info_json = self._get_latest_release_json_from_repo(user, addon_name)
        self.newest_version = self._get_newest_version()

    @staticmethod
    def _get_user_repo_from_url(url):
        pattern = r'https:\/\/github.com\/(\w+)\/(.+)'
        match = re.search(pattern, url)
        if not match:
            return None
        user = match.group(1)
        repo = match.group(2)
        return user, repo

    def _get_latest_release_json_from_repo(self, user, repo):
        headers = {"accept":"application/vnd.github.v3+json"}
        api_url = f"https://api.github.com/repos/{user}/{repo}/releases"
        response = requests.get(api_url, headers=headers)
        return json.loads(response.content)[0]

    def _get_newest_version(self):
        return self.info_json.get("tag_name")

    def update(self, wow_install_dir):
        dl_url = self.get_zip_file_url_from_release_json(self.info_json)
        dl_filename = self.addon_name + "_" + self.get_file_name_from_url(dl_url) 
        dl_file_path = self.create_download_file_path(dl_filename, wow_install_dir)
        self.download_file(dl_url, dl_file_path)
        self.unzip_file(dl_file_path, wow_install_dir)
        os.remove(dl_file_path)

    @staticmethod
    def get_zip_file_url_from_release_json(release_json):
        return release_json["assets"][0]["browser_download_url"]

    @staticmethod
    def get_file_name_from_url(url):
        return url.split("/")[-1]

    @staticmethod
    def create_download_file_path(filename, file_path):
        return os.path.join(file_path, filename)

    @staticmethod
    def download_file(url, file_path):
        response = requests.get(url, stream=True)
        with open(file_path, "wb") as file_obj:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file_obj.write(chunk)

    @staticmethod
    def unzip_file(zip_file_path, output_dir):
        with ZipFile(zip_file_path, 'r') as zip_obj:
            zip_obj.extractall(output_dir)
