import sys
from turtle import update
sys.path.append("../app")
import update_dbm
import os
import zipfile
from unittest.mock import patch

def test_get_file_name_from_url():
    url = "http://www.award.com/home/resource/important.txt"
    assert update_dbm.get_file_name_from_url(url) == "important.txt"

def test_download_file():
    url = "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.10.118.tar.xz"
    file_name = update_dbm.get_file_name_from_url(url)
    file_path = update_dbm.create_download_file_path(file_name, "/test/")
    update_dbm.download_file(url, file_path)
    assert os.path.exists(file_path)
    os.remove(file_path)

def test_unzip_file():
    test_text_file_path = os.path.join("/test/", "test.txt")
    with open(test_text_file_path, "w") as test_file:
        test_file.write("hello there!")
    assert os.path.exists(test_text_file_path)
    test_zip_file_path = os.path.join("/test/", "test.zip")
    with zipfile.ZipFile(test_zip_file_path, "w") as zip_file:
        zip_file.write(test_text_file_path)
    assert os.path.exists(test_zip_file_path)
    os.remove(test_text_file_path)
    update_dbm.unzip_file(test_zip_file_path, "/")
    assert os.path.exists(test_text_file_path)
    os.remove(test_zip_file_path)
    os.remove(test_text_file_path)

def test_load_json():
    json_file_name = os.path.join("/test/", "test.json")
    json = update_dbm.load_json(json_file_name)
    assert len(json) == 1
    assert json["hello there!"] == "general kenobi..."

def test_get_classic_wow_addon_location():
    conf_file_name = os.path.join("/test/", "test.conf")
    assert update_dbm.get_classic_wow_addon_location(conf_file_name) == "/path/to/wow/dir"

def test_get_user_repo_from_url():
    url = "https://github.com/DeadlyBossMods/DBM-Classic"
    assert ("DeadlyBossMods", "DBM-Classic") == update_dbm.get_user_repo_from_url(url)
    assert None == update_dbm.get_user_repo_from_url("bad.url.com")