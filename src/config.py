import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot Configuration"""

    PORT = 3978
    APP_ID = os.environ.get("BOT_ID")
    APP_PASSWORD = os.environ.get("BOT_PASSWORD")

    AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"] # Azure OpenAI API key
    AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = os.environ["AZURE_OPENAI_MODEL_DEPLOYMENT_NAME"] # Azure OpenAI model deployment name
    AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"] # Azure OpenAI endpoint
    AZURE_OPENAI_VERSION = os.environ["AZURE_OPENAI_VERSION"] # Azure OpenAI version

    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] # Azure OpenAI embedding deployment
    AZURE_SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"] # Azure Search key
    AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"] # Azure Search endpoint
    INDEX_NAME = os.environ["INDEX_NAME"] # Index of our knowledge base

    LANGUAGE_KEY = os.environ["LANGUAGE_KEY"]
    LANGUAGE_ENDPOINT = os.environ["LANGUAGE_ENDPOINT"]
