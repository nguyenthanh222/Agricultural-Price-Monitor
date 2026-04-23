# Scraper Setup Guide - VNSAT Form-Based Website

## Hiện tượng
Website VNSAT (https://thitruongnongsan.gov.vn) sử dụng **ASP.NET WebForms** với form tra cứu:
- Form có khoảng thời gian (từ ngày - đến ngày)
- Dropdown "Xem theo", "Nhóm theo các trường"
- Bảng giá chỉ xuất hiện sau khi submit form (postback)

## Cách cấu hình

### 1. Inspect trang website
1. Mở https://thitruongnongsan.gov.vn/vn/tm.aspx
2. Mở Developer Tools (`F12`)
3. Vào tab **Network**
4. Điền form và nhấn nút "Tìm kiếm" / submit
5. Tìm request **POST** trong Network tab
6. Xem **Request payload** để lấy tên các form fields

### 2. Cấu hình Form Fields trong scraper.py

Tìm đoạn này trong `scraper.py`:

```python
form_data = {
    "__VIEWSTATE": viewstate,
    "__EVENTVALIDATION": eventvalidation,
    # Điều chỉnh các field names sau khi inspect trang thực tế:
    # "ctl00$maincontent$txtFromDate": from_date,  # Ví dụ
    # "ctl00$maincontent$txtToDate": to_date,
    # "ctl00$maincontent$ddCategory": category,  # dropdown
    # "ctl00$maincontent$btnSearch": "Tìm kiếm",  # submit button
}
```

Thay thế các field names bằng tên thực tế từ bước 1. Ví dụ:

```python
form_data = {
    "__VIEWSTATE": viewstate,
    "__EVENTVALIDATION": eventvalidation,
    "ctl00$ContentPlaceHolder1$FromDate": from_date,
    "ctl00$ContentPlaceHolder1$ToDate": to_date,
    "ctl00$ContentPlaceHolder1$Category": category,
    "ctl00$ContentPlaceHolder1$btnSearch": "Search",
}
```

### 3. Điều chỉnh Table Selector

Tìm đoạn này:

```python
price_table = (
    soup.find("table", {"id": re.compile(r"GridView|grvPrice", re.I)})
    or soup.find("table", {"class": re.compile(r"price|data", re.I)})
    or soup.find("table")  # Fallback: table đầu tiên
)
```

Nếu cần, thay regex hoặc ID/class cụ thể:

```python
price_table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_grvData"})
```

### 4. Kiểm tra cột dữ liệu

Trong phần extract data, đảm bảo thứ tự cột khớp với bảng thực tế:

```python
if len(cells) >= 4:
    rows.append({
        "date": today_str,
        "category": category,
        "product": cells[0],      # Cột 1: Mặt hàng
        "region": cells[1],       # Cột 2: Địa điểm
        "unit": cells[2],         # Cột 3: Đơn vị
        "price": cells[3],        # Cột 4: Giá
    })
```

## Thử nghiệm

### Chạy scraper với ngày cụ thể
```powershell
python -m sources.scraper.scraper lua_gao "01/04/2026" "20/04/2026"
```

### Xem logs để debug
```powershell
# Logs sẽ in trên console khi chạy
python -m sources.scraper.scraper lua_gao
```

## Troubleshooting

### ViewState không thể extract
- Kiểm tra URL có đúng không
- Website có thay đổi cấu trúc HTML không?
- Thử dùng `requests.Session()` với cookies

### Bảng không xuất hiện
- Kiểm tra form fields có đúng không (step 2)
- Thử inspect Network tab xem request/response có gì khác
- Bảng có thể nằm trong AJAX response - cần xử lý khác

### Giá extract sai
- Kiểm tra lại thứ tự cột (step 4)
- In ra `cells` để debug:
```python
print(f"DEBUG: cells = {cells}")
```

## Notes
- `__VIEWSTATE` và `__EVENTVALIDATION` là bắt buộc cho ASP.NET WebForms
- Session/cookies được tự động quản lý bởi `requests.Session()`
- Timeout = 15 giây, có thể tăng nếu server chậm
