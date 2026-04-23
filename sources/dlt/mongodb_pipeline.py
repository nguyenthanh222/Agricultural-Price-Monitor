from sources.mongodb.connection import get_mongo_client


def sync_mongo_to_postgres():
    # Placeholder for the dbt/dlt pipeline that reads from MongoDB
    # and loads into a Postgres destination.
    print("🔄 Running MongoDB to Postgres sync pipeline")
    client = get_mongo_client()
    db = client["gold_price_monitoring"]
    collection_names = db.list_collection_names()
    print(f"Found MongoDB collections: {collection_names}")
    print("This step is a placeholder for the dlt/dbt ingestion flow.")


if __name__ == "__main__":
    sync_mongo_to_postgres()
