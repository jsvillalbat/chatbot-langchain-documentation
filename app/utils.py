import os
import sys

import jsonlines
import yaml
from langchain.schema import Document


class DocsJSONLLoader:
    """
    Class to load documents from a JSONL file
    
    Args:
        path (str): Path to the JSONL file
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def load(self) -> list[Document]:
        """
        Load the documents from the JSONL file
        
        Returns:
            list: List of documents
        """
        documents = []
        with jsonlines.open(self.file_path) as reader:
            for obj in reader:
                page_content = obj.get("text", "")
                metadata = {
                    "title": obj.get("title", ""),
                    "repo_owner": obj.get("repo_owner", ""),
                    "repo_name": obj.get("repo_name", ""),
                }
                documents.append(Document(page_content=page_content, metadata=metadata))
        return documents
    

def load_config():
    """
    Load the config of the application from the 'config.yaml' file

    Returns:
        dict: Dictionary with the config
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root_dir, "config.yaml")) as f:
        try:
             return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)

def get_open_api_key():
    """
    Get the OpenAI API key from the environment variable, if it does not exist, exit the application
    """
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    return openai_api_key

def get_cohere_api_key():
    """
    Get the Cohere API key from the environment variable, if it does not exist, request it to the user
    """
    cohere_api_key = os.environ.get("COHERE_API_KEY")
    if not cohere_api_key:
        cohere_api_key = input("Enter your Cohere API key: ")
    return cohere_api_key

def get_file_path():
    """
    Get the file path of the JSONL file specific in the config file

    Returns:
        file path of JSONL file
    """
    config = load_config()

    root_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.join(root_dir, "..")
    return os.path.join(parent_dir, config["jsonl_database_path"])


def get_query_from_user() -> str:
    """
    Get the query from the user

    Returns:
        str: Query entered by the user
    """
    try:
        query = input("Enter your query: ")
        return query
    except EOFError:
        print("EOFError: No query entered, please try again")
        return get_query_from_user()
    
def create_dir(path: str) -> None:
    """
    Create a directory if it does not exist

    Args:
        path (str): Path to the directory
    """
    if not os.path.exists(path):
        os.makedirs(path)

def remove_existing_file(file_path: str) -> None:
    """
    Remove a file if it exists

    Args:
        file_path (str): Path to the file
    """
    if os.path.exists(file_path):
        os.remove(file_path)
