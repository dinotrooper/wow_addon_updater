import configparser
import os
import re
import json
from argparse import ArgumentParser
from wow_addons import GithubWowAddon

# TODO: Make appropriate functions private

class WowAddonUpdater:
    supported_sites = [
        "github",
    ]
    wow_install_dir = None
    addons = []
    def __init__(self, wow_install_conf, app_json, token_file_path="github_token"):
        self.setup(wow_install_conf, app_json, token_file_path)

    def setup(self, wow_install_conf, app_json, token_file_path):
        """ Wrapper for init - easier to unit test """
        self.token = self._get_github_token_from_file(token_file_path)
        self.wow_install_dir = self._get_classic_wow_addon_location(wow_install_conf)
        self.load_addons_from_text_file(app_json)
        self.update_addons()

    def _get_github_token_from_file(self, token_file_path):
        try:
            with open(token_file_path, "r") as file:
                return file.read().strip()
        except FileNotFoundError as error:
            text = f"""
Could not file named {token_file_path}. Please create this file and put your Github token here.
More infomation can be found here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
            """
            print(text)
            raise error

    @staticmethod
    def _get_classic_wow_addon_location(conf_file_name):
        if not os.path.exists(conf_file_name):
            raise FileNotFoundError(conf_file_name)
        config = configparser.ConfigParser()
        config.read(conf_file_name)
        return config["Classic"]["wow_install_dir"]

    def load_addons_from_text_file(self, json_path):
        with open(json_path, "r") as file_obj:
            file_contents = file_obj.readlines()
            for url in file_contents:
                if not url:
                    continue
                self.addons.append(self.load_addon(url))

    def load_addon(self, addon_url):
        site = self.get_site_from_url(addon_url)
        if site not in self.supported_sites:
            raise ValueError("Site %s not supported.", addon_url)
        if site == "github":
            return GithubWowAddon(addon_url, self.token)

    @staticmethod
    def get_site_from_url(url):
        patterns = [r'https:\/\/\w+\.(\w+)\.\w+\/.+', r'https:\/\/(\w+)\.\w+\/.+']
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).lower()
        return None

    def read_json_file(self, file_path):
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r") as file_obj:
            return json.load(file_obj)

    def update_addons(self):
        for addon in self.addons:
            try:
                addon.update(self.wow_install_dir)
            except Exception as error:
                print(f"Failed to update {addon.addon_name}.\n{error}\n")

    @staticmethod
    def write_json_utf8(json_obj, filepath):
        with open(filepath, mode="w+", encoding="utf-8") as file_obj:
            json.dump(json_obj, file_obj)

if __name__ == "__main__":
    parser = ArgumentParser(prog="addon_updater.py", description="Python script to update WoW addons.")
    parser.add_argument("wow_install_conf", help="file location of your wow installation configuration")
    parser.add_argument("addons_json", help="file location of your addon JSON file")
    args = parser.parse_args()
    WowAddonUpdater(args.wow_install_conf, args.addons_json)
