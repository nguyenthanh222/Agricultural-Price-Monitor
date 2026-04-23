# config/settings.py

import os
from pathlib import Path

# Đường dẫn project (tự động tính theo thư mục gốc)
ROOT_DIR = Path(__file__).parent.parent

DATA_DIR   = ROOT_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR   = DATA_DIR / "gold"

# URL VNSAT (cơ sở dữ liệu giá)
VNSAT_BASE = "https://thitruongnongsan.gov.vn"
VNSAT_PRICES_URL = f"{VNSAT_BASE}/vn/nguonwmy.aspx"

# Định dạng ngày cho tên file
FILE_DATE_FORMAT = "%Y%m%d"

# Danh sách ngành hàng chính
CATEGORIES = [
    "lua_gao",      # lúa gạo
    "ca_phe",       # cà phê
    "rau_qua",      # rau quả
]

# Tên file mẫu bronze
def get_bronze_path(date_str: str, category: str):
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    return BRONZE_DIR / f"{date_str}_gia_{category}_raw.csv"

# Tên file silver/gold chung
SILVER_FILE = SILVER_DIR / "gia_nong_san_clean.parquet"
GOLD_DAILY_FILE = GOLD_DIR / "daily_price_by_product_region.parquet"
GOLD_CHANGE_FILE_TEMPLATE = GOLD_DIR / "{date}_top_10_change.parquet"
