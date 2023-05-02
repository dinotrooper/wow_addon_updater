""" Github Wow Addons """
import json
from abc import abstractmethod
import os
import re
from zipfile import ZipFile
import requests
from time import sleep

class WowAddon:
    """ Abstract class that represents any WoW Addon. """
    addon_name = None
    newest_version = None
    version_dir = None

    @abstractmethod
    def update(self):
        """ Update if a new verison of an addon exists. """
        raise NotImplementedError

class GithubWowAddon(WowAddon):
    release_json = None
    current_version = None
    """ A WoW Addon hosted on Github. Needs a Github token. """
    def __init__(self, url, token, versions_dir="addon_versions"):
        user, addon_name = self._get_user_repo_from_url(url)
        self._create_version_dir(versions_dir)
        self.version_file = os.path.join(self.versions_dir, addon_name)
        self.current_version = self._get_current_version()
        self.user = user
        self.addon_name = addon_name
        self.token = token

    @staticmethod
    def _get_user_repo_from_url(url):
        pattern = r'https:\/\/github\.com\/(.+)\/(.+)'
        match = re.search(pattern, url)
        if not match:
            return None
        user = match.group(1)
        repo = match.group(2)
        return user, repo

    def _create_version_dir(self, versions_dir):
        curr_dir = os.path.dirname(__file__)
        self.versions_dir = os.path.join(curr_dir, versions_dir)
        if not os.path.exists(self.versions_dir):
            os.mkdir(self.versions_dir)

    def _get_current_version(self):
        if not os.path.exists(self.version_file):
            return None
        return self._read_file_utf8(self.version_file)

    @staticmethod
    def _read_file_utf8(filename):
        with open(filename, "r", encoding="utf-8") as file_obj:
            return file_obj.read().strip()

    def update(self, wow_install_dir):
        """ Update an addon hosted on Github if they have a new release. """
        if not self._does_addon_need_updating():
            self._print_skip_message()
            return
        self._print_update_message()
        dl_url = self._get_zip_file_url_from_release_json(self.release_json)
        dl_filename = self.addon_name + "_" + self._get_file_name_from_url(dl_url)
        dl_file_path = self._create_download_file_path(dl_filename, wow_install_dir)
        self._download_file(dl_url, dl_file_path)
        self._unzip_file(dl_file_path, wow_install_dir)
        self._update_current_version()
        os.remove(dl_file_path)

    def _does_addon_need_updating(self):
        self._check_for_new_version()
        if self.current_version is None:
            return True
        if self.newest_version != self.current_version:
            return True
        return False

    def _print_skip_message(self):
        print(f"Skipping {self.addon_name}; addon's current version {self.current_version} matches newest version {self.newest_version}")

    def _check_for_new_version(self):
        self.release_json = self._get_latest_release_json_from_repo(self.token, self.user, self.addon_name)
        self.newest_version = self._get_newest_version()

    def _get_latest_release_json_from_repo(self, token, user, addon_name):
        headers = {"accept":"application/vnd.github.v3+json", "Authorization":f"token {token}"}
        api_url = f"https://api.github.com/repos/{user}/{addon_name}/releases"
        response = self.get_response_with_retries(api_url, headers, 60)
        return json.loads(response.content)[0]

    @staticmethod
    def get_response_with_retries(api_url, headers, timeout):
        max_retries = 5
        num_retries = 0
        try:
            return requests.get(api_url, headers=headers, timeout=timeout)
        except requests.exceptions.ConnectionError as error:
            if num_retries > max_retries:
                raise error
            sleep(.5 + num_retries)
            num_retries += 1

    def _get_newest_version(self):
        return self.release_json.get("tag_name")

    def _print_update_message(self):
        print(f"Updating {self.addon_name} from version {self.current_version} to {self.newest_version}")

    @staticmethod
    def _get_zip_file_url_from_release_json(release_json):
        assets = release_json["assets"]
        for asset in assets:
            if ".zip" in asset["name"]:
                return asset["browser_download_url"]
        return release_json["assets"][0]["browser_download_url"]

    @staticmethod
    def _get_file_name_from_url(url):
        return url.split("/")[-1]

    @staticmethod
    def _create_download_file_path(filename, file_path):
        return os.path.join(file_path, filename)

    @staticmethod
    def _download_file(url, file_path):
        response = requests.get(url, stream=True, timeout=60)
        with open(file_path, "wb") as file_obj:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file_obj.write(chunk)

    @staticmethod
    def _unzip_file(zip_file_path, output_dir):
        with ZipFile(zip_file_path, 'r') as zip_obj:
            zip_obj.extractall(output_dir)

    def _update_current_version(self):
        self._write_utf8(self.version_file, self.newest_version)
        self.current_version = self.newest_version

    @staticmethod
    def _write_utf8(filename, text):
        with open(filename, "w", encoding="utf-8") as file_obj:
            file_obj.write(text)
