import requests
import json
import configparser
import os
from zipfile import ZipFile
import re

#TODO: add dir for addon_versions, check version before updating

class GithubWowAddonUpdater:
    def __init__(self, wow_install_conf, json_contents):
        self.wow_install_dir = self.get_classic_wow_addon_location(wow_install_conf)
        self.json_contents = self.load_json(json_contents)

    @staticmethod
    def get_classic_wow_addon_location(conf_file_name):
        if not os.path.exists(conf_file_name):
            raise ValueError(f"File {conf_file_name} does not exist.")
        config = configparser.ConfigParser()
        config.read(conf_file_name)
        return config["Classic"]["wow_install_dir"]

    @staticmethod
    def load_json(filename):
        with open(filename, "r") as file_obj:
            return json.loads(file_obj.read())

    def update_addons_in_json(self):
        for addon_name, repo_url in self.json_contents.items():
            self.update_addon(addon_name, repo_url)
            print(f"Done")

    def update_addon(self, addon_name, repo_url):
        release_info_json = self.get_latest_release_json_from_repo(repo_url)
        version = self.get_addon_version_from_release_json(release_info_json)
        print(f"Updating {addon_name} to version {version}")
        dl_url = self.get_latest_release_dl_url_from_release_json(release_info_json)
        dl_filename = addon_name + "_" + self.get_file_name_from_url(dl_url) 
        print(f"dl_filename = {dl_filename}")
        dl_file_path = self.create_download_file_path(dl_filename, self.wow_install_dir)
        self.download_file(dl_url, dl_file_path)
        self.unzip_file(dl_file_path, self.wow_install_dir)
        self.write_version_to_addon_dir(version, self.wow_install_dir, addon_name)
        os.remove(dl_file_path)

    def get_latest_release_json_from_repo(self, url):
        headers = {"accept":"application/vnd.github.v3+json"}
        user, repo = self.get_user_repo_from_url(url)
        api_url = f"https://api.github.com/repos/{user}/{repo}/releases"
        response = requests.get(api_url, headers=headers)
        return json.loads(response.content)[0]

    @staticmethod
    def get_addon_version_from_release_json(release_json):
        return release_json.get("tag_name")

    @staticmethod
    def get_user_repo_from_url(url):
        pattern = r'https:\/\/github.com\/([a-zA-z\-]+)/(.+)'
        match = re.search(pattern, url)
        if not match:
            return None
        user = match.group(1)
        repo = match.group(2)
        return user, repo 

    @staticmethod
    def write_json_utf8(json_obj, filepath):
        with open(filepath, mode="w+", encoding="utf-8") as file_obj:
            json.dump(json_obj, file_obj, indent=4, sort_keys=True)

    def get_latest_release_dl_url_from_release_json(self, release_info_json):
        return self.get_zip_file_url_from_release_json(release_info_json)

    def get_zip_file_url_from_release_json(self, release_json):
        if len(release_json["assets"]) == 0:
            return self.get_url_from_release_json_body(release_json["body"])
        return release_json["assets"][0]["browser_download_url"]

    @staticmethod
    def get_url_from_release_json_body(body):
        pattern = r'.+(https:\/\/github.com\/.+\.zip).+'
        match = re.search(pattern, body)
        if not match:
            return None
        return match.group(1)

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

    def write_version_to_addon_dir(self, version, addon_dir, addon_name):
        version_fp = os.path.join(addon_dir, f"{addon_name}_version")
        self.write_utf8(version_fp, version)

    @staticmethod
    def write_utf8(filepath, contents):
        with open(filepath, mode="w+", encoding="utf-8") as file_obj:
            file_obj.write(contents)

if __name__ == "__main__":
    dbm_updater = GithubWowAddonUpdater("wow_install.conf", "addons.json")
    dbm_updater.update_addons_in_json()
