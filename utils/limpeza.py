from datetime import datetime, timedelta, timezone

def limpar_antigos(collection):
    limite = datetime.now(timezone.utc) - timedelta(hours=1)
    collection.delete_many({
        "timestamp_datetime": {"$lt": limite}
    })
