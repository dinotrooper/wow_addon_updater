""" Tests for Addon Updater """
from unittest.mock import patch, MagicMock
from parameterized import parameterized
import sys
import json
import zipfile
import pytest
from addon_updater import WowAddonUpdater
from test_common import TestGithubToken

class TestWowAddonUpdater(TestGithubToken):

    @patch("addon_updater.WowAddonUpdater.setup", new=MagicMock())
    def test_get_github_token(self):
        updater = self.get_test_updater()
        assert updater._get_github_token_from_file("github_token") != ""
        with pytest.raises(FileNotFoundError) as error:
            updater._get_github_token_from_file("does_not_exist")

    def get_test_updater(self):
        return WowAddonUpdater("test/test.conf", "test/test.json", "github_token")

    @patch("addon_updater.WowAddonUpdater.setup", new=MagicMock())
    def test_get_classic_wow_addon_location(self):
        updater = self.get_test_updater()
        assert updater._get_classic_wow_addon_location("test/test.conf") == "/path/to/wow/dir"
        with pytest.raises(FileNotFoundError) as error:
            updater._get_classic_wow_addon_location("does_not_exist")

    @patch("addon_updater.WowAddonUpdater.setup", new=MagicMock())
    @patch("addon_updater.WowAddonUpdater.load_addon")
    def test_load_addons_from_text_file(self, mock_load: MagicMock):
        test_addon_file = "test/addons.txt"
        with open(test_addon_file, "r") as text_file:
            num_addons = len(text_file.readlines())
        updater = self.get_test_updater()
        updater.load_addons_from_text_file(test_addon_file)
        assert len(updater.addons) == num_addons
        mock_load.call_count == num_addons

    @parameterized.expand([
        ("github", "https://github.com/dinotrooper/wow_addon_updater", "github"),
        ("www_github", "https://www.github.com/dinotrooper/wow_addon_updater", "github"),
    ])
    def test_get_site_from_url(num, name, input, output):
        assert WowAddonUpdater.get_site_from_url(input) == output