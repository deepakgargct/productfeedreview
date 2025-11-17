import streamlit as st
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse
import re
import pandas as pd
import requests
from typing import Any, Dict, List, Tuple, Optional

# =========================================================
# Streamlit Page Setup
# =========================================================
st.set_page_config(page_title="OpenAI Product Feed Validator", layout="wide")
st.title("🛍️ OpenAI Product Feed Validator")
st.write("Upload a **JSON or XML feed** to validate it against OpenAI's Product Feed Specification.")


# =========================================================
# Helper Functions
# =========================================================
def is_url(s: Optional[str]) -> bool:
    if not s:
        return False
    try:
        p = urlparse(str(s))
        return p.scheme in ("http", "https") and bool(p.netloc)
    except:
        return False


def is_iso8601_date(s: Optional[str]) -> bool:
    if not s:
        return False
    try:
        datetime.fromisoformat(str(s))
        return True
    except:
        try:
            datetime.strptime(str(s), "%Y-%m-%d")
            return True
        except:
            return False


def parse_iso_date(s: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(s)
    except:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except:
            return None


def is_positive_integer_str(s: Any) -> bool:
    try:
        return int(s) >= 0
    except:
        return False


def extract_price_and_currency(value: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    if value is None:
        return None, None

    s = str(value).strip()
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Z]{3})?\s*$", s)
    if m:
        return float(m.group(1)), m.group(2)

    # Try JSON-like price structure
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict) and "value" in parsed:
            return float(parsed["value"]), parsed.get("currency")
    except:
        pass

    # Fallback token parse
    parts = s.split()
    if len(parts) == 0:
        return None, None
    try:
        val = float(parts[0])
        cur = parts[1] if len(parts) > 1 else None
        return val, cur
    except:
        return None, None


# =========================================================
# Feed Loading (JSON + XML)
# =========================================================
def extract_products_from_json(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, list) and all(isinstance(i, dict) for i in obj):
        return obj

    if isinstance(obj, dict):
        for key in ("products", "items", "feed", "entries", "data"):
            if key in obj and isinstance(obj[key], list):
                return obj[key]

    # BFS fallback search for list-of-dicts
    queue = [obj]
    seen = set()
    while queue:
        cur = queue.pop(0)
        if id(cur) in seen:
            continue
        seen.add(id(cur))

        if isinstance(cur, list):
            if cur and all(isinstance(i, dict) for i in cur):
                return cur
            for item in cur:
                queue.append(item)

        elif isinstance(cur, dict):
            for v in cur.values():
                queue.append(v)

    if isinstance(obj, dict):
        return [obj]

    return []


def load_feed(uploaded_file) -> List[Dict[str, Any]]:
    name = uploaded_file.name.lower()
    text = uploaded_file.getvalue().decode("utf-8")

    if name.endswith(".json"):
        parsed = json.loads(text)
        return extract_products_from_json(parsed)

    elif name.endswith(".xml"):
        root = ET.fromstring(text)
        items = []
        candidates = root.findall(".//item") or root.findall(".//product") or root.findall(".//entry")

        if not candidates:
            candidates = list(root)

        for el in candidates:
            obj = {}
            for child in el:
                tag = child.tag.split("}")[-1]
                obj[tag] = child.text or ""
            items.append(obj)

        return items

    else:
        raise ValueError("Unsupported file type – upload JSON or XML only.")


# =========================================================
# Validation Logic
# =========================================================
def validate_product(p: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
    errors = []
    warnings = []
    infos = []

    def get(key: str):
        for k in p:
            if k.lower() == key.lower():
                return p[k]
        return None

    required_fields = [
        "id", "title", "description", "link", "price",
        "availability", "inventory_quantity", "image_link"
    ]

    for f in required_fields:
        if get(f) in (None, ""):
            errors.append(f"Missing required field: {f}")

    # URL fields
    for field in ("link", "image_link"):
        val = get(field)
        if val:
            if not is_url(val):
                errors.append(f"{field} is not a valid URL")
            elif not val.lower().startswith("https"):
                warnings.append(f"{field} should use HTTPS")

    # Price
    price_val, price_cur = extract_price_and_currency(get("price"))
    if price_val is None:
        errors.append("Invalid price format (expected 'number CUR')")

    # Sale price
    sale = get("sale_price")
    if sale:
        sale_val, sale_cur = extract_price_and_currency(sale)
        if sale_val is None:
            errors.append("sale_price not parseable")
        elif price_val and sale_val > price_val:
            errors.append("sale_price must be <= price")

    # Availability
    availability = get("availability")
    if availability not in ("in_stock", "out_of_stock", "preorder"):
        errors.append("availability must be in 'in_stock|out_of_stock|preorder'")

    # Inventory
    inv = get("inventory_quantity")
    if not is_positive_integer_str(inv):
        errors.append("inventory_quantity must be a non-negative integer")

    # GTIN / MPN
    gtin = get("gtin")
    mpn = get("mpn")
    if not gtin and not mpn:
        errors.append("Either gtin or mpn must be present")

    return errors, warnings, infos


# =========================================================
# File Upload UI
# =========================================================
uploaded = st.file_uploader("Upload JSON or XML feed", type=["json", "xml"])

if not uploaded:
    st.info("Please upload a feed file to start validation.")
    st.stop()

# Parse file
with st.spinner("Parsing feed..."):
    products = load_feed(uploaded)

st.success(f"Loaded {len(products)} product records.")


# =========================================================
# Validate All Products
# =========================================================
product_results = []
total_errors = 0
total_warnings = 0

for p in products:
    errors, warnings, infos = validate_product(p)

    total_errors += len(errors)
    total_warnings += len(warnings)

    product_results.append({
        "errors_list": errors,
        "warnings_list": warnings,
        "infos_list": infos
    })


# =========================================================
# Summary Section
# =========================================================
st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Products", len(products))
col2.metric("Total Errors", total_errors)
col3.metric("Total Warnings", total_warnings)


# =========================================================
# Detailed Report with Field-by-Field Table
# =========================================================
st.subheader("Detailed Report")

for idx, p in enumerate(products, start=1):
    errors = product_results[idx - 1]["errors_list"]
    warnings = product_results[idx - 1]["warnings_list"]
    infos = product_results[idx - 1]["infos_list"]

    with st.expander(f"Product {idx} — ID: {p.get('id', '(no id)')}"):

        required_and_optional_fields = [
            "id", "title", "description", "link", "image_link", "price",
            "sale_price", "sale_price_effective_date",
            "availability", "availability_date",
            "inventory_quantity", "gtin", "mpn",
            "brand", "category", "google_product_category",
            "shipping", "weight",
            "enable_search", "enable_checkout"
        ]

        table_rows = []

        for field in required_and_optional_fields:
            value = p.get(field, None)
            present = value not in (None, "")

            status = "✔ Present" if present else "⚠ Missing"
            notes = ""

            for e in errors:
                if field.lower() in e.lower():
                    status = "❌ Invalid"
                    notes = e

            for w in warnings:
                if field.lower() in w.lower() and not notes:
                    notes = w

            table_rows.append({
                "Field": field,
                "Status": status,
                "Value": value if value not in (None, "") else "—",
                "Notes": notes if notes else "—",
            })

        st.markdown("### 🔎 Field Validation Overview")
        st.dataframe(pd.DataFrame(table_rows))

        # Error sections
        if errors:
            st.error("Errors:\n- " + "\n- ".join(errors))
        if warnings:
            st.warning("Warnings:\n- " + "\n- ".join(warnings))
        if infos:
            st.info("Info:\n- " + "\n- ".join(infos))
