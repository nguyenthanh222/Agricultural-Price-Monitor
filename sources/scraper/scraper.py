import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from pathlib import Path
import re
import logging

from config import settings

# Setup logger
logger = logging.getLogger(__name__)


def extract_viewstate(html: str) -> str:
    """Extract ViewState từ ASP.NET WebForms form."""
    soup = BeautifulSoup(html, "html.parser")
    viewstate_input = soup.find("input", {"name": "__VIEWSTATE"})
    if viewstate_input:
        return viewstate_input.get("value", "")
    return ""


def extract_form_fields(html: str) -> dict:
    """Extract tất cả fields từ form ASP.NET WebForms để giữ nguyên payload ban đầu."""
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", {"id": "aspnetForm"}) or soup.find("form")
    data = {}
    if not form:
        return data

    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        typ = inp.get("type", "text").lower()
        if typ in ("checkbox", "radio"):
            if inp.has_attr("checked"):
                data[name] = inp.get("value", "on")
            continue
        if typ in ("submit", "image"):
            continue
        data[name] = inp.get("value", "")

    for sel in form.find_all("select"):
        name = sel.get("name")
        if not name:
            continue
        selected = sel.find("option", selected=True)
        if selected:
            data[name] = selected.get("value", "")
        else:
            first_option = sel.find("option")
            data[name] = first_option.get("value", "") if first_option else ""

    return data


def fetch_vnsat_prices(category: str, from_date: str = None, to_date: str = None):
    today = datetime.datetime.today()
    today_str = today.strftime(settings.FILE_DATE_FORMAT)
    
    if from_date is None:
        from_date = today.strftime("%d/%m/%Y")
    if to_date is None:
        to_date = today.strftime("%d/%m/%Y")

    category_map = {
        "lua_gao": "Lúa gạo",
        "ca_phe": "Cà phê",
        "rau_qua": "Rau, quả"
    }
    category_vn = category_map.get(category, "Lúa gạo")

    url = settings.VNSAT_PRICES_URL
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    })

    try:
        logger.info(f"Fetching initial form from {url}")
        response = session.get(url, timeout=20)
        response.raise_for_status()

        form_data = extract_form_fields(response.text)

        # Override fields
        form_data["__EVENTTARGET"] = ""
        form_data["__EVENTARGUMENT"] = ""
        form_data["ctl00$maincontent$tu_ngay"] = from_date
        form_data["ctl00$maincontent$den_ngay"] = to_date
        form_data["ctl00$maincontent$Ngành_hàng"] = category_vn
        form_data["ctl00$maincontent$Theo_thời_gian"] = "Ngày"
        form_data["ctl00$maincontent$Xem"] = "Xem"

        # Xóa checkbox thừa
        for key in list(form_data.keys()):
            if "hiện_các_trường" in key or (key.endswith("$Xem") and key != "ctl00$maincontent$Xem"):
                form_data.pop(key, None)

        logger.info(f"Submitting form → {category_vn} | {from_date} → {to_date}")
        response = session.post(url, data=form_data, timeout=25)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # === LƯU DEBUG FILE (rất quan trọng) ===
        debug_file = Path(f"debug_response_{category}_{today_str}.html")
        debug_file.write_text(response.text, encoding="utf-8")
        logger.info(f"Debug HTML saved to: {debug_file}")

        # Tìm bảng
        price_table = (
            soup.find("table", {"id": "ctl00_maincontent_GridView1"}) or
            soup.find("table", id=re.compile(r"GridView", re.I)) or
            max(soup.find_all("table"), key=lambda t: len(t.find_all("tr")), default=None)
        )

        if not price_table:
            logger.error("Không tìm thấy table nào")
            return False

        rows_count = len(price_table.find_all("tr"))
        logger.info(f"Found table with {rows_count} rows")

        # Extract dữ liệu - phiên bản debug chi tiết
        data_rows = []
        header_found = False

        for i, tr in enumerate(price_table.find_all("tr")):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if not cells:
                continue

            row_text = " | ".join(cells[:6])  # lấy 6 cột đầu để debug
            logger.info(f"Row {i}: {row_text[:200]}...")   # in log để xem cấu trúc

            first_cell_lower = cells[0].lower().strip() if cells else ""

            # Skip các dòng header
            if any(keyword in first_cell_lower for keyword in ["tên mặt hàng", "mặt hàng", "sản phẩm", "ngày", "khu vực", "giá"]):
                header_found = True
                continue

            # Chỉ lấy dòng có ít nhất 3-4 cột dữ liệu thực
            if len(cells) >= 3 and not first_cell_lower.startswith("--"):
                data_rows.append({
                    "date": cells[2] if len(cells) > 2 else from_date,
                    "category": category,
                    "product": cells[0],
                    "region": cells[1] if len(cells) > 1 else "",
                    "unit": cells[3] if len(cells) > 3 else "",
                    "price": cells[3] if len(cells) > 3 else cells[-1],
                })

        logger.info(f"Extracted {len(data_rows)} data rows (after skipping headers)")

        if not data_rows:
            print(f"⚠️ Không có dữ liệu cho {category_vn} trong khoảng {from_date} - {to_date}")
            print(f"   → Kiểm tra file: {debug_file.name}")
            print("   → Có thể ngày hôm nay chưa có dữ liệu, hoặc form submit chưa đúng.")
            return False

        # Lưu dữ liệu
        df = pd.DataFrame(data_rows)
        output_path = settings.get_bronze_path(today_str, category)
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"Saved {len(data_rows)} rows to {output_path}")
        print(f"✅ Thành công! Đã lưu {len(data_rows)} hàng dữ liệu {category}")
        return True

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Lỗi: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Thiết lập logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    if len(sys.argv) < 2:
        print("Usage: python -m sources.scraper.scraper <category> [from_date] [to_date]")
        print("  category: lua_gao|ca_phe|rau_qua")
        print("  from_date: optional, format DD/MM/YYYY (default: today)")
        print("  to_date: optional, format DD/MM/YYYY (default: today)")
        sys.exit(1)
    
    category = sys.argv[1]
    if category not in settings.CATEGORIES:
        print(f"❌ Category không hợp lệ. Chọn một trong: {settings.CATEGORIES}")
        sys.exit(1)
    
    from_date = sys.argv[2] if len(sys.argv) > 2 else None
    to_date = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = fetch_vnsat_prices(category, from_date, to_date)
    sys.exit(0 if success else 1)
