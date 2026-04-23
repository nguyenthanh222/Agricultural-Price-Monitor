import pandas as pd
from datetime import datetime
from pathlib import Path
from config import settings
import sys


# Thêm thư mục gốc project vào PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # sources/utils -> sources -> root
sys.path.insert(0, str(ROOT_DIR))

def build_daily_price_table():
    if not settings.SILVER_FILE.exists():
        print("❌ Không tìm thấy file silver.parquet")
        return

    df_silver = pd.read_parquet(settings.SILVER_FILE)

    df_gold = (
        df_silver
        [["date", "category", "product_normalized", "region", "unit_normalized", "price_number"]]
        .groupby(["date", "category", "product_normalized", "region", "unit_normalized"])
        .agg({"price_number": "mean"})
        .round(2)
        .reset_index()
        .rename(columns={"price_number": "avg_price"})
    )

    # === SỬA LỖI CHÍNH TẠI ĐÂY ===
    # Parse date với đúng format DD-MM-YYYY (từ scraper)
    df_gold["date"] = pd.to_datetime(
        df_gold["date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    # Nếu vẫn còn NaT, in ra để debug
    if df_gold["date"].isna().any():
        print("⚠️ Có một số date không chuyển được:")
        invalid_dates = df_silver[df_silver["date"].isna()]["date"].unique()
        print(invalid_dates)
        print("\nBắt đầu xóa các hàng có date không hợp lệ...")

    # Xóa các dòng có NaT date
    df_gold = df_gold.dropna(subset=["date"]).copy()

    # Lưu daily price
    settings.GOLD_DIR.mkdir(parents=True, exist_ok=True)
    df_gold.to_parquet(settings.GOLD_DAILY_FILE, index=False)
    print(f"✅ Đã lưu bảng giá ngày: {settings.GOLD_DAILY_FILE} ({len(df_gold)} rows)")

    # === Tính top biến động ===
    df_gold = df_gold.sort_values(["category", "product_normalized", "region", "date"])

    df_gold["prev_avg_price"] = (
        df_gold.groupby(["category", "product_normalized", "region"])["avg_price"]
        .shift(1)
    )

    df_gold["change_pct"] = (
        (df_gold["avg_price"] - df_gold["prev_avg_price"]) 
        / df_gold["prev_avg_price"] * 100
    ).round(2)

    latest_date = df_gold["date"].max()
    latest_date_str = latest_date.strftime("%Y%m%d")
    
    change_file = Path(str(settings.GOLD_CHANGE_FILE_TEMPLATE).format(date=latest_date_str))
    
    df_top = (
        df_gold.dropna(subset=["change_pct"])
        .nlargest(10, "change_pct")
        [["date", "category", "product_normalized", "region", "avg_price", "prev_avg_price", "change_pct"]]
    )
    
    df_top.to_parquet(change_file, index=False)
    print(f"✅ Đã lưu top 10 biến động: {change_file} ({len(df_top)} rows)")

    print(f"📅 Ngày mới nhất trong dữ liệu: {latest_date.date()}")


if __name__ == "__main__":
    build_daily_price_table()
