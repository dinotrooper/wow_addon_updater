""" Tests for Addon Updater """
from unittest.mock import patch, MagicMock
import os
import json
import zipfile
import pytest
from app.addon_updater import WowAddonUpdater
from test_common import TestGithubToken

class TestWowAddonUpdater(TestGithubToken):

    @patch("app.addon_updater.WowAddonUpdater.setup", new=MagicMock())
    def test_get_github_token(self):
        updater = self.get_test_updater()
        assert updater._get_github_token_from_file("test/github_token") == "aGVsbG8gdGhlcmUh"
        with pytest.raises(FileNotFoundError) as error:
            updater._get_github_token_from_file("does_not_exist")

    def get_test_updater(self):
        return WowAddonUpdater("test/test.conf", "test/test.json", "test/github_token")

    @patch("app.addon_updater.WowAddonUpdater.setup", new=MagicMock())
    def test_get_classic_wow_addon_location(self):
        updater = self.get_test_updater()
        assert updater._get_classic_wow_addon_location("test/test.conf") == "/path/to/wow/dir"
        with pytest.raises(FileNotFoundError) as error:
            updater._get_classic_wow_addon_location("does_not_exist")

    @patch("app.addon_updater.WowAddonUpdater.setup", new=MagicMock())
    @patch("app.addon_updater.WowAddonUpdater.load_addon")
    def test_load_addons_from_text_file(self, mock_load: MagicMock):
        test_addon_file = "test/addons.txt"
        with open(test_addon_file, "r") as text_file:
            num_addons = len(text_file.readlines())
        updater = self.get_test_updater()
        updater.load_addons_from_text_file(test_addon_file)
        assert len(updater.addons) == num_addons
        mock_load.call_count == num_addons