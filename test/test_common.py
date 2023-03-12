""" Common test objects """
from unittest import TestCase

class TestGithubToken(TestCase):
    """ Class with function to get GitHub token """
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
