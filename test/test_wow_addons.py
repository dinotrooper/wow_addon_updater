""" Tests for WoW Addons """
from unittest import TestCase
from unittest.mock import patch, MagicMock
import os
import json
import zipfile
import pytest
from app.wow_addons import GithubWowAddon

class TestGithubWowAddonUpdater(TestCase):
    """ Tests for Github WoW addons. """
    def setUp(self):
        url = "https://github.com/DeadlyBossMods/DBM-BCC"
        self.token = self._get_github_token_from_file()
        self.gh_wow_addon = GithubWowAddon(url, self.token)

    def _get_github_token_from_file(self, token_file_path = "github_token"):
        try:
            with open(token_file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError as error:
            text = f"""
Could not file named {token_file_path}. Please create this file and put your Github token here.
More infomation can be found here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
            """
            print(text)
            raise error

    def test_get_user_repo_from_url(self):
        url = "https://github.com/DeadlyBossMods/DBM-Classic"
        assert ("DeadlyBossMods", "DBM-Classic") == GithubWowAddon._get_user_repo_from_url(url)
        assert None is GithubWowAddon._get_user_repo_from_url("bad.url.com")

    def test_get_file_name_from_url(self):
        url = "http://www.award.com/home/resource/important.txt"
        assert GithubWowAddon._get_file_name_from_url(url) == "important.txt"

    def test_download_file(self):
        url = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.118.tar.xz"
        file_name = GithubWowAddon._get_file_name_from_url(url)
        assert file_name == "linux-5.10.118.tar.xz"
        file_path = GithubWowAddon._create_download_file_path(file_name, "/test/")
        assert file_path == "/test/linux-5.10.118.tar.xz"
        GithubWowAddon._download_file(url, file_path)
        assert os.path.exists(file_path)
        os.remove(file_path)

    def test_unzip_file(self):
        test_text_file_path = os.path.join("/test/", "test.txt")
        with open(test_text_file_path, "w", encoding="utf-8") as test_file:
            test_file.write("hello there!")
        assert os.path.exists(test_text_file_path)
        test_zip_file_path = os.path.join("/test/", "test.zip")
        with zipfile.ZipFile(test_zip_file_path, "w") as zip_file:
            zip_file.write(test_text_file_path)
        assert os.path.exists(test_zip_file_path)
        os.remove(test_text_file_path)
        GithubWowAddon._unzip_file(test_zip_file_path, "/")
        assert os.path.exists(test_text_file_path)
        os.remove(test_zip_file_path)
        os.remove(test_text_file_path)

    def test_get_latest_release_json_from_repo(self):
        user = self.gh_wow_addon.user
        addon_name = self.gh_wow_addon.addon_name
        test_json = self.gh_wow_addon._get_latest_release_json_from_repo(self.token, user, addon_name)
        print(json.dumps(test_json, indent=4, sort_keys=True))
        assets = test_json.get("assets")
        assert assets is not None
        first_asset = assets[0]
        assert first_asset != {}
        zip_file_url = first_asset.get("browser_download_url")
        assert zip_file_url is not None
        assert self.gh_wow_addon._get_zip_file_url_from_release_json(test_json) == zip_file_url

    def test_write_version(self):
        version = "2.5.40"
        self.gh_wow_addon.newest_version = "2.5.40"
        self.gh_wow_addon._update_current_version()
        with open(self.gh_wow_addon.version_file, "r", encoding="utf-8") as file_obj:
            assert file_obj.read() == version
        assert self.gh_wow_addon.current_version == version

    def test_get_current_version_from_file(self):
        test_version_file = "/test/VERSION"
        with open(test_version_file, "r", encoding="utf-8") as file_obj:
            self.gh_wow_addon.version_file = test_version_file
            assert self.gh_wow_addon._get_current_version() == file_obj.read().strip()

    @patch("app.wow_addons.GithubWowAddon._check_for_new_version", MagicMock())
    def test_does_addon_need_updating(self):
        self.gh_wow_addon.current_version = None
        assert self.gh_wow_addon._does_addon_need_updating()
        self.gh_wow_addon.current_version = "2.1.0"
        self.gh_wow_addon.newest_version = "2.1.0"
        assert not self.gh_wow_addon._does_addon_need_updating()
        self.gh_wow_addon.current_version = "2.0.0"
        self.gh_wow_addon.newest_version = "2.1.0"
        assert self.gh_wow_addon._does_addon_need_updating()

    def test_check_for_new_version(self):
        with patch("app.wow_addons.GithubWowAddon._get_latest_release_json_from_repo") as mock_get_json:
            test_version = "2.5.0"
            test_json = {"tag_name":test_version}
            mock_get_json.return_value=test_json
            self.gh_wow_addon._check_for_new_version()
            assert self.gh_wow_addon.newest_version == test_version

    @patch("app.wow_addons.GithubWowAddon._download_file", MagicMock())
    @patch("app.wow_addons.GithubWowAddon._unzip_file", MagicMock())
    @patch("app.wow_addons.GithubWowAddon._write_utf8", MagicMock())
    @patch("app.wow_addons.os", MagicMock())
    def test_upgrade(self):
        self.gh_wow_addon.update("/test/")

    @patch("app.wow_addons.GithubWowAddon._does_addon_need_updating", MagicMock(return_value=False))
    @patch("app.wow_addons.GithubWowAddon._write_utf8")
    def test_upgrade_when_not_needed(self, mock_write):
        self.gh_wow_addon.update("/test/")
        mock_write.assert_not_called()


