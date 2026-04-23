import pandas as pd
from pathlib import Path
from config import settings


def load_bronze_data():
    df_list = []
    for category in settings.CATEGORIES:
        for file in settings.BRONZE_DIR.glob(f"*_gia_{category}_raw.csv"):
            df = pd.read_csv(file, encoding="utf-8")
            df["category"] = category
            df_list.append(df)
    if not df_list:
        print("Không tìm thấy file bronze.")
        return pd.DataFrame()
    return pd.concat(df_list, ignore_index=True)


def normalize_product_name(category: str, name: str) -> str:
    name = name.lower().strip()
    if category == "lua_gao":
        if "gao" in name:
            return "gao"
        if "lua" in name:
            return "lua"
        return "lua_gao_khac"
    if category == "ca_phe":
        if "robusta" in name:
            return "ca_phe_robusta"
        if "arabica" in name:
            return "ca_phe_arabica"
        if "green" in name:
            return "ca_phe_green_bean"
        return "ca_phe_khac"
    if category == "rau_qua":
        if "rau an la" in name:
            return "rau_an_la"
        if "rau an cu" in name or "củ" in name:
            return "rau_an_cu"
        if "trai cay" in name or "qua" in name:
            return "trai_cay"
        return "rau_qua_khac"
    return "khac"


def normalize_unit(unit) -> str:
    """Xử lý an toàn khi unit là NaN hoặc float"""
    if pd.isna(unit) or unit is None:
        return "VND/kg"          # Giá trị mặc định hợp lý cho nông sản
    unit_str = str(unit).lower().strip()
    if "kg" in unit_str:
        return "VND/kg"
    if "tấn" in unit_str or "tan" in unit_str:
        return "VND/tấn"
    if unit_str == "":
        return "VND/kg"
    return unit_str


def clean_price(price) -> float:
    if pd.isna(price):
        return None
    cleaned = str(price).strip().replace(".", "").replace(",", "").replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def transform_to_silver():
    df = load_bronze_data()
    if df.empty:
        print("🚫 Không có dữ liệu bronze để transform.")
        return

    df_silver = df.copy()

    # Thêm cột category nếu chưa có (phòng trường hợp scrape nhiều file)
    if "category" not in df_silver.columns:
        df_silver["category"] = "lua_gao"   # hoặc detect từ tên file

    # Normalize
    df_silver["product_normalized"] = df_silver.apply(
        lambda row: normalize_product_name(row.get("category", "lua_gao"), row.get("product", "")),
        axis=1
    )
    
    df_silver["unit_normalized"] = df_silver["unit"].apply(normalize_unit)
    df_silver["price_number"] = df_silver["price"].apply(clean_price)

    # Xóa các dòng không có giá hợp lệ
    df_silver = df_silver.dropna(subset=["price_number"]).copy()
    df_silver = df_silver.drop_duplicates()

    # Parse date cột (format DD-MM-YYYY từ scraper)
    if "date" in df_silver.columns:
        df_silver["date"] = pd.to_datetime(
            df_silver["date"],
            format="%d-%m-%Y",
            errors="coerce"
        )
    else:
        # Nếu không có date cột, tạo với ngày hôm nay
        from datetime import datetime
        df_silver["date"] = datetime.today()

    settings.SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(settings.SILVER_FILE, index=False)
    
    print(f"✅ Transform thành công! Đã lưu {len(df_silver)} bản ghi vào silver: {settings.SILVER_FILE}")
    print(f"   → Số mặt hàng sau normalize: {df_silver['product_normalized'].nunique()}")


if __name__ == "__main__":
    transform_to_silver()
