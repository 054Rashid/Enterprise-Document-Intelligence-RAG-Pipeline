from app.database import init_db
from app.services.ingestion import ingest_directory


if __name__ == "__main__":
    init_db()
    result = ingest_directory("data/documents")
    print(result)
