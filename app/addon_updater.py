from cgitb import text
import configparser
import os
import re
import json
from wow_addons import GithubWowAddon

class WowAddonUpdater:
    supported_sites = [
        "github",
    ]
    wow_install_dir = None
    addons = []
    addon_versions = {}
    addon_version_name = "addon_version.json"
    def __init__(self, wow_install_conf, text_file):
        self.wow_install_dir = self.get_classic_wow_addon_location(wow_install_conf)
        self.load_addons_from_text_file(text_file)
        self.get_addon_versions()

    @staticmethod
    def get_classic_wow_addon_location(conf_file_name):
        if not os.path.exists(conf_file_name):
            raise ValueError(f"File {conf_file_name} does not exist.")
        config = configparser.ConfigParser()
        config.read(conf_file_name)
        return config["Classic"]["wow_install_dir"]

    def load_addons_from_text_file(self, text_file):
        if not os.path.exists(text_file):
            raise ValueError(f"File {text_file} does not exist.")
        with open(text_file, "r") as file_obj:
            file_contents = file_obj.readlines()
            for url in file_contents:
                if not url:
                    continue
                self.addons.append(self.load_addon(url))

    def load_addon(self, addon_url):
        site = self.get_site_from_url(addon_url)
        if site not in self.supported_sites:
            raise ValueError("Site {site} not supported.")
        if site == "github": 
            return GithubWowAddon(addon_url)

    @staticmethod
    def get_site_from_url(url):
        pattern = r'[https:/]+www\.(\w+).\w+'
        match = re.search(pattern, url)
        if not match:
            return None
        return match.group(1).lower()

    def get_addon_versions(self):
        addon_version_json_fp = self.get_addon_version_json_fp()
        self.addon_versions = self.read_json_file(addon_version_json_fp)

    def get_addon_version_json_fp(self):
        return os.path.join(self.wow_install_dir, self.addon_version_name)

    def read_json_file(self, file_path):
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r") as file_obj:
            return json.load(file_obj)

    def update_addons(self):
        for addon in self.addons():
            if not self.does_addon_need_updating(addon):
                continue
            self.print_addon_update_message(addon)
            addon.update(self.wow_install_dir)
            self.addon_versions[addon.name] = addon.newest_version
        self.update_addon_version_json()

    def does_addon_need_updating(self, addon):
        local_version = self.addon_versions.get(addon.name)
        if local_version is None:
            return True
        if addon.newest_version != local_version: 
            return True
        return False

    def print_addon_update_message(self, addon):
        local_version = self.addon_versions.get(addon.name)
        print(f"Updating {addon.name} from version {local_version} to {addon.newest_version}")

    def update_addon_version_json(self):
        addon_version_json_fp = self.get_addon_version_json_fp()
        self.write_json_utf8(self.addon_versions, addon_version_json_fp)

    @staticmethod
    def write_json_utf8(json_obj, filepath):
        with open(filepath, mode="w+", encoding="utf-8") as file_obj:
            json.dump(json_obj, file_obj)
