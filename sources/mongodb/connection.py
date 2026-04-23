import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

from config import settings


def load_mongo_settings():
    env_file = settings.ROOT_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database = os.getenv("MONGO_DATABASE", "agricultural_price_monitoring")
    return uri, database


def get_mongo_client() -> MongoClient:
    uri, _ = load_mongo_settings()
    return MongoClient(uri)


def get_mongo_database():
    uri, database = load_mongo_settings()
    client = MongoClient(uri)
    return client[database]
