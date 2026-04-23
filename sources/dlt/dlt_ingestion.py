import glob
from pathlib import Path
import pandas as pd
import sys

from config import settings
from sources.mongodb.connection import get_mongo_client


def find_latest_bronze_file(category: str):
    pattern = settings.BRONZE_DIR / f"*_gia_{category}_raw.csv"
    files = sorted(glob.glob(str(pattern)))
    return Path(files[-1]) if files else None


def ingest_latest_bronze(category: str = "lua_gao"):
    bronze_file = find_latest_bronze_file(category)
    if not bronze_file or not bronze_file.exists():
        print(f"❌ Không tìm thấy file bronze cho category={category}")
        print(f"   Hãy chạy scraper trước: python -m sources.scraper.scraper {category}")
        return False

    try:
        df = pd.read_csv(bronze_file, encoding="utf-8")
        print(f"📥 Đã đọc {len(df)} hàng từ {bronze_file}")

        client = get_mongo_client()
        db = client["agricultural_price_monitoring"]
        collection = db[f"bronze_{category}"]
        records = df.to_dict(orient="records")
        if records:
            collection.insert_many(records)
            print(f"✅ Đã ghi {len(records)} bản ghi vào MongoDB: bronze_{category}")
            return True
        else:
            print(f"⚠️ File {bronze_file} trống")
            return False
    except Exception as e:
        print(f"❌ Lỗi khi ingest {category}: {e}")
        return False


def ingest_all_categories():
    """Ingest tất cả 3 category: lua_gao, ca_phe, rau_qua"""
    results = {}
    for category in settings.CATEGORIES:
        print(f"\n{'='*60}")
        print(f"Ingesting {category}...")
        print(f"{'='*60}")
        results[category] = ingest_latest_bronze(category)
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    for category, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{category}: {status}")
    
    return all(results.values())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Ingest specific category
        category = sys.argv[1]
        if category not in settings.CATEGORIES:
            print(f"❌ Category không hợp lệ. Chọn một trong: {settings.CATEGORIES}")
            sys.exit(1)
        success = ingest_latest_bronze(category)
        sys.exit(0 if success else 1)
    else:
        # Ingest all categories
        success = ingest_all_categories()
        sys.exit(0 if success else 1)

