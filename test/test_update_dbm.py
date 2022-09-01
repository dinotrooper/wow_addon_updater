import sys
sys.path.append("../app")
from update_dbm import GithubWowAddonUpdater
import os
import zipfile
from unittest import TestCase
import json
from parameterized import parameterized

class TestGithubWowAddonUpdater(TestCase):

    def test_get_file_name_from_url(self):
        url = "http://www.award.com/home/resource/important.txt"
        assert GithubWowAddonUpdater.get_file_name_from_url(url) == "important.txt"

    def test_download_file(self):
        url = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.118.tar.xz"
        file_name = GithubWowAddonUpdater.get_file_name_from_url(url)
        file_path = GithubWowAddonUpdater.create_download_file_path(file_name, "/test/")
        GithubWowAddonUpdater.download_file(url, file_path)
        assert os.path.exists(file_path)
        os.remove(file_path)

    def test_unzip_file(self):
        test_text_file_path = os.path.join("/test/", "test.txt")
        with open(test_text_file_path, "w") as test_file:
            test_file.write("hello there!")
        assert os.path.exists(test_text_file_path)
        test_zip_file_path = os.path.join("/test/", "test.zip")
        with zipfile.ZipFile(test_zip_file_path, "w") as zip_file:
            zip_file.write(test_text_file_path)
        assert os.path.exists(test_zip_file_path)
        os.remove(test_text_file_path)
        GithubWowAddonUpdater.unzip_file(test_zip_file_path, "/")
        assert os.path.exists(test_text_file_path)
        os.remove(test_zip_file_path)
        os.remove(test_text_file_path)

    def test_load_json(self):
        json_file_name = os.path.join("/test/", "test.json")
        json = GithubWowAddonUpdater.load_json(json_file_name)
        assert len(json) == 1
        assert json["hello there!"] == "general kenobi..."

    def test_get_classic_wow_addon_location(self):
        conf_file_name = os.path.join("/test/", "test.conf")
        assert GithubWowAddonUpdater.get_classic_wow_addon_location(conf_file_name) == "/path/to/wow/dir"

    @parameterized.expand(
            [
                ("https://github.com/DeadlyBossMods/DBM-Classic",
                    ("DeadlyBossMods", "DBM-Classic")),
                ("https://github.com/max-ri/Guidelime",
                    ("max-ri", "Guidelime")),
                ("bad.url.com", None),
            ])
    def test_get_user_repo_from_url(self, url, expected):
        assert expected  == GithubWowAddonUpdater.get_user_repo_from_url(url)

    def test_get_latest_release_json_from_repo(self):
        test_obj = GithubWowAddonUpdater("/test/test.conf", "/test/test.json")
        repo_url = "https://github.com/DeadlyBossMods/DBM-BCC"
        test_json = test_obj.get_latest_release_json_from_repo(repo_url)
        assets = test_json.get("assets")
        assert assets is not None
        first_asset = assets[0]
        assert first_asset != {}
        zip_file_url = first_asset.get("browser_download_url")
        assert zip_file_url is not None
        assert test_obj.get_zip_file_url_from_release_json(test_json) == zip_file_url

    def test_get_url_from_release_body(self):
        test_url = "https://github.com/stuff/more_stuff/stuff.zip"
        body = f"Fixed stuff\r\n[stuff.zip]({test_url})\r\n"
        assert GithubWowAddonUpdater.get_url_from_release_json_body(body) == test_url

    def test_get_zip_file_with_no_assets(self):
        test_obj = GithubWowAddonUpdater("/test/test.conf", "/test/test.json")
        repo_url = "https://github.com/Vysci/LFG-Bulletin-Board"
        test_json = test_obj.get_latest_release_json_from_repo(repo_url)
        print(json.dumps(test_json, indent=4, sort_keys=True))
        assets = test_json.get("assets")
        assert len(assets) == 0
        zip_file_url = GithubWowAddonUpdater.get_url_from_release_json_body(test_json.get("body"))
        assert zip_file_url is not None
        assert test_obj.get_zip_file_url_from_release_json(test_json) == zip_file_url

    def test_write_json_utf8(self):
        test_json_fp = "/test/test_write_json_utf8"
        GithubWowAddonUpdater.write_json_utf8({"hello there!":"general kenobi"}, test_json_fp)
        with open(test_json_fp, "r") as file_obj:
            test_json_obj = json.load(file_obj)
            assert len(test_json_obj) == 1
            assert test_json_obj.get("hello there!") is not None
        os.remove(test_json_fp)

    def test_get_addon_version_from_release_json(self):
        with open("test/test_release.json", "r") as file_obj:
            test_release_json = json.load(file_obj)
        version = GithubWowAddonUpdater.get_addon_version_from_release_json(test_release_json)
        assert version == "2.5.42"

    def test_write_version(self):
        addon_name = "test_addon"
        test_dir = "/test/"
        test_fp = os.path.join(test_dir, f"{addon_name}_version")
        version = "2.5.40"
        test_obj = GithubWowAddonUpdater("/test/test.conf", "/test/test.json")
        test_obj.write_version_to_addon_dir(version, test_dir, addon_name)
        with open(test_fp, "r") as file_obj:
            assert file_obj.read() == version
