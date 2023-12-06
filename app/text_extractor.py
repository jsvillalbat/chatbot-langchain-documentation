import datetime
import json
import os
import re
from typing import Dict

import emoji
import requests
from termcolor import colored
from utils import create_dir, load_config, remove_existing_file
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def preprocess_text(text: str) -> str:
    """
    Preprocess text by removing emojis and URLs

    Args:
        text (str): Text to be preprocessed

    Returns:
        str: Preprocessed text
    """
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"http\S+|www.\S+", "", text)
    text = re.sub(r"Copyright.*", "", text)
    text = text.replace("\n", " ")
    text = emoji.demojize(text)
    text = re.sub(r":[a-z_&+-]+:", "", text)
    return text


def download_file(url: str, repo_info: dict, jsonl_file_name: str) -> None:
    """
    Download a file from an URL and save it as a JSONL file

    Args:
        url (str): URL of the file to be downloaded
        repo_info (dict): Information about the repository
        jsonl_file_name (str): Name of the JSONL file to be saved
    """
    response = requests.get(url)
    filename = url.split("/")[-1]
    text = response.text

    if text is not None and isinstance(text, str):
        text = preprocess_text(text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        file_dict = {
            "title": filename,
            "repo_owner": repo_info["owner"],
            "repo_name": repo_info["repo"],
            "text": text,
        }

        with open(jsonl_file_name, "a") as jsonl_file:
            jsonl_file.write(json.dumps(file_dict) + "\n")
    else:
        print(colored(f"Error: text not found in {url}", "red"))

def process_directory(
        path: str,
        repo_info: dict,
        headers: dict,
        jsonl_file_name: str,
    ) -> None:
    """
    Process a directory and download all files in it

    Args:
        path (str): Path to the directory to be processed
        repo_info (dict): Information about the repository
        headers (dict): Headers for the GitHub API
        jsonl_file_name (str): Name of the JSONL file to be saved
    """
    # If the name of the directory is 'zh', then we don't want to download and return inmediately
    # This feature is useful for repositories that have a lot of files in Chinese
    if os.path.basename(path) == "zh":
        print(colored("Skipping directory 'zh'", "yellow"))
        return
    
    base_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/contents/"
    print(
        colored(f"Processing directory {path} from repo: {repo_info['repo']}", "blue")
    )

    response = requests.get(base_url + path, headers=headers)

    if response.status_code == 200:
        files = response.json()
        for file in files:
            if file["type"] == "file" and (
                file["name"].endswith(".mdx") or file["name"].endswith(".md")
            ):
                print(colored(f"Downloading file {file['name']}", "green"))
                print(colored(f"URL: {file['download_url']}", "cyan"))
                download_file(file["download_url"], repo_info, jsonl_file_name)
            elif file["type"] == "dir":
                process_directory(
                    file["path"], repo_info, headers, jsonl_file_name
                )
        print(colored(f"Finished processing directory {path}", "green"))
    else:
        print(colored(f"Error: {response.status_code}. Please verify your Github Token and the repository details", "red"))


def main():
    """
    Main function that runs the initial script
    """
    config = load_config()
    github_token = os.getenv("GITHUB_TOKEN")

    if github_token is None:
        raise ValueError("Please set the GITHUB_TOKEN environment variable")
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.raw",
    }

    current_date = datetime.datetime.now().strftime("%Y_%m_%d")
    jsonl_file_name = f"data/docs_en_{current_date}.jsonl"

    create_dir("data/")
    remove_existing_file(jsonl_file_name)

    for repo_info in config["github"]["repos"]:
        process_directory(
            repo_info["path"],
            repo_info,
            headers,
            jsonl_file_name,
        )

if __name__ == "__main__":
    main()
