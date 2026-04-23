#!/usr/bin/env python3
"""
Helper script để inspect VNSAT form fields và table structure.
Giúp extract tên control từ HTML form.
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import os

# Fix Unicode encoding for Windows console
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def inspect_form_fields(url: str):
    """Extract tất cả input fields từ form."""
    print(f"\n📋 Inspecting form fields from {url}...\n")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Tìm tất cả input fields
        print("=" * 80)
        print("INPUT FIELDS:")
        print("=" * 80)
        for inp in soup.find_all("input"):
            name = inp.get("name", "")
            type_ = inp.get("type", "")
            value = inp.get("value", "")[:50]  # First 50 chars
            if name:
                print(f"  name='{name}' type='{type_}' value='{value}'")
        
        # Tìm tất cả select (dropdown)
        print("\n" + "=" * 80)
        print("SELECT DROPDOWNS:")
        print("=" * 80)
        for sel in soup.find_all("select"):
            name = sel.get("name", "")
            if name:
                options = [opt.get_text(strip=True) for opt in sel.find_all("option")]
                print(f"  name='{name}'")
                for opt in options[:10]:  # First 10 options
                    print(f"    - {opt}")
                if len(options) > 10:
                    print(f"    ... and {len(options) - 10} more")
        
        # Tìm tất cả tables
        print("\n" + "=" * 80)
        print("TABLES:")
        print("=" * 80)
        for i, tbl in enumerate(soup.find_all("table"), 1):
            id_ = tbl.get("id", "")
            class_ = " ".join(tbl.get("class", []))
            rows = len(tbl.find_all("tr"))
            cols = len(tbl.find("tr").find_all(["td", "th"])) if tbl.find("tr") else 0
            print(f"  Table {i}:")
            if id_:
                print(f"    id='{id_}'")
            if class_:
                print(f"    class='{class_}'")
            print(f"    rows={rows}, cols={cols}")
            
            # Print first few headers
            header = tbl.find("tr")
            if header:
                headers = [th.get_text(strip=True) for th in header.find_all(["th", "td"])]
                print(f"    headers: {headers[:5]}")
        
        # Tìm form submit button
        print("\n" + "=" * 80)
        print("SUBMIT BUTTONS:")
        print("=" * 80)
        for btn in soup.find_all(["button", "input"]):
            if btn.get("type") in ["submit", "image"]:
                name = btn.get("name", "")
                value = btn.get("value", "")
                print(f"  name='{name}' value='{value}'")
        
        # Tìm ViewState
        print("\n" + "=" * 80)
        print("VIEWSTATE & VALIDATION:")
        print("=" * 80)
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})
        eventval = soup.find("input", {"name": "__EVENTVALIDATION"})
        print(f"  __VIEWSTATE: {'✓ Found' if viewstate else '✗ Not found'}")
        print(f"  __EVENTVALIDATION: {'✓ Found' if eventval else '✗ Not found'}")
        
        print("\n" + "=" * 80)
        print("✅ Inspection complete!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def inspect_post_response(url: str, form_data: dict):
    """Inspect response từ form submission."""
    print(f"\n📤 Submitting form to {url}...\n")
    
    try:
        session = requests.Session()
        response = session.post(url, data=form_data, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")
        
        print(f"✅ POST successful. Response contains {len(tables)} tables\n")
        
        for i, tbl in enumerate(tables, 1):
            id_ = tbl.get("id", "")
            class_ = " ".join(tbl.get("class", []))
            rows = len(tbl.find_all("tr"))
            
            print(f"Table {i}: id='{id_}' class='{class_}' rows={rows}")
            
            # Print first 3 rows
            for j, tr in enumerate(tbl.find_all("tr")[:3], 1):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                print(f"  Row {j}: {cells}")
        
        print("\n✅ Inspection complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    url = "https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx"
    
    # Bước 1: Inspect form fields
    inspect_form_fields(url)
    
    # Bước 2: (Optional) Nếu bạn biết form data, submit và inspect response
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        form_data = {
            "__VIEWSTATE": "...",  # Thay bằng ViewState thực tế
            # ... các fields khác
        }
        inspect_post_response(url, form_data)
