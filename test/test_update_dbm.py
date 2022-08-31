from app.wow_addons import GithubWowAddon
import os
import zipfile
from unittest import TestCase
import json
from unittest.mock import patch

class TestGithubWowAddonUpdater(TestCase):

    def test_get_file_name_from_url(self):
        url = "http://www.award.com/home/resource/important.txt"
        assert GithubWowAddon.get_file_name_from_url(url) == "important.txt"

    def test_download_file(self):
        url = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.118.tar.xz"
        file_name = GithubWowAddon.get_file_name_from_url(url)
        file_path = GithubWowAddon.create_download_file_path(file_name, "/test/")
        GithubWowAddon.download_file(url, file_path)
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
        GithubWowAddon.unzip_file(test_zip_file_path, "/")
        assert os.path.exists(test_text_file_path)
        os.remove(test_zip_file_path)
        os.remove(test_text_file_path)

    def test_load_json(self):
        json_file_name = os.path.join("/test/", "test.json")
        json = GithubWowAddon.load_json(json_file_name)
        assert len(json) == 1
        assert json["hello there!"] == "general kenobi..."

    def test_get_classic_wow_addon_location(self):
        conf_file_name = os.path.join("/test/", "test.conf")
        assert GithubWowAddon.get_classic_wow_addon_location(conf_file_name) == "/path/to/wow/dir"

    def test_get_user_repo_from_url(self):
        url = "https://github.com/DeadlyBossMods/DBM-Classic"
        assert ("DeadlyBossMods", "DBM-Classic") == GithubWowAddon._get_user_repo_from_url(url)
        assert None == GithubWowAddon._get_user_repo_from_url("bad.url.com")

    def test_get_latest_release_json_from_repo(self):
        test_obj = GithubWowAddon("/test/test.conf", "/test/test.json")
        repo_url = "https://github.com/DeadlyBossMods/DBM-BCC"
        test_json = test_obj._get_latest_release_json_from_repo(repo_url)
        print(json.dumps(test_json, indent=4, sort_keys=True))
        assets = test_json.get("assets")
        assert assets is not None
        first_asset = assets[0]
        assert first_asset != {}
        zip_file_url = first_asset.get("browser_download_url")
        assert zip_file_url is not None
        assert test_obj.get_zip_file_url_from_release_json(test_json) == zip_file_url

    def test_write_json_utf8(self):
        test_json_fp = "/test/test_write_json_utf8"
        GithubWowAddon.write_json_utf8({"hello there!":"general kenobi"}, test_json_fp)
        with open(test_json_fp, "r") as file_obj:
            test_json_obj = json.load(file_obj)
            assert len(test_json_obj) == 1
            assert test_json_obj.get("hello there!") is not None
        os.remove(test_json_fp)


    @patch("app.wow_addons.GithubWowAddon._get_latest_release_json_from_repo")
    def test_get_addon_version_from_release_json(self, mock_get_release_json):
        with open("test/test_release.json", "r") as file_obj:
            test_release_json = json.load(file_obj) 
            mock_get_release_json.return_value = test_release_json
        assert GithubWowAddon("http://google.com") == "2.5.40"

    def test_write_version(self):
        addon_name = "test_addon"
        test_dir = "/test/"
        test_fp = os.path.join(test_dir, f"{addon_name}_version")
        version = "2.5.40"
        test_obj = GithubWowAddon("/test/test.conf", "/test/test.json")
        test_obj.write_version_to_addon_dir(version, test_dir, addon_name)
        with open(test_fp, "r") as file_obj:
            assert file_obj.read() == version