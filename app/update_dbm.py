import requests
import json
import configparser
import os
from zipfile import ZipFile
import re

def download_file(url, file_path):
    response = requests.get(url, stream=True)
    with open(file_path, "wb") as file_obj:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file_obj.write(chunk)

def unzip_file(zip_file_path, output_dir):
    with ZipFile(zip_file_path, 'r') as zip_obj:
        zip_obj.extractall(output_dir)

def get_file_name_from_url(url):
    return url.split("/")[-1]

def load_json(filename):
    with open(filename, "r") as file_obj:
        return json.loads(file_obj.read())

def get_classic_wow_addon_location(conf_file_name):
    config = configparser.ConfigParser()
    config.read(conf_file_name)
    return config["Classic"]["wow_install_dir"]

def create_download_file_path(filename, file_path):
    return os.path.join(file_path, filename)

def main():
    wow_install_dir = get_classic_wow_addon_location("wow_install.conf")
    json_contents = load_json("addons.json")
    for addon_name, repo_url in json_contents.items():
        dl_url = get_latest_release_dl_url_from_repo_url(repo_url)
        dl_filename = addon_name + "_" + get_file_name_from_url(dl_url) 
        dl_file_path = create_download_file_path(dl_filename, wow_install_dir)
        download_file(dl_url, dl_file_path)
        unzip_file(dl_file_path, wow_install_dir)
        os.remove(dl_file_path)

def get_user_repo_from_url(url):
    pattern = r'https:\/\/github.com\/(\w+)\/(.+)'
    match = re.search(pattern, url)
    if not match:
        return None
    user = match.group(1)
    repo = match.group(2)
    return user, repo 

def get_latest_release_dl_url_from_repo_url(repo_url):
    release_info_json = get_latest_release_json_from_repo(repo_url)
    return get_zip_file_url_from_release_json(release_info_json)

def get_latest_release_json_from_repo(url):
    headers = {"accept":"application/vnd.github.v3+json"}
    user, repo = get_user_repo_from_url(url)
    api_url = f"https://api.github.com/repos/{user}/{repo}/releases"
    response = requests.get(api_url, headers=headers)
    return json.loads(response.content)[0]

def get_zip_file_url_from_release_json(release_json):
    return release_json["assets"][0]["browser_download_url"]

if __name__ == "__main__":
    main()
