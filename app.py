import streamlit as st
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse
import re
import pandas as pd

# -----------------------------------------------------------
# Helper validation functions
# -----------------------------------------------------------

def is_url(s):
    try:
        p = urlparse(s)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except:
        return False

def is_iso8601_date(s):
    try:
        datetime.fromisoformat(s)
        return True
    except:
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except:
            return False

def parse_iso_date(s):
    try:
        return datetime.fromisoformat(s)
    except:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except:
            return None

def is_positive_integer_str(s):
    try:
        return int(s) >= 0
    except:
        return False

def extract_price_and_currency(value):
    if not value:
        return None, None
    value = str(value).strip()

    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Z]{3})?\s*$", value)
    if m:
        return float(m.group(1)), m.group(2)
    return None, None


# -----------------------------------------------------------
# Load JSON or XML feed
# -----------------------------------------------------------
def load_feed(file):
    name = file.name.lower()

    if name.endswith(".json"):
        data = json.load(file)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for k in ("products", "items", "feed"):
                if k in data and isinstance(data[k], list):
                    return data[k]
            return [data]

    elif name.endswith(".xml"):
        tree = ET.parse(file)
        root = tree.getroot()

        items = []
        candidates = root.findall(".//item") or root.findall(".//product") or list(root)
        if not candidates:
            candidates = list(root)

        for el in candidates:
            obj = {}
            for child in el:
                tag = child.tag.split("}", 1)[-1]
                obj[tag] = child.text or ""
            items.append(obj)
        return items

    else:
        st.error("Unsupported file type. Upload JSON or XML only.")
        return None


# -----------------------------------------------------------
# Product Validation Logic
# -----------------------------------------------------------
def validate_product(p, idx):
    errors = []
    warnings = []

    def get(key):
        for k in p:
            if k.lower() == key.lower():
                return p[k]
        return None

    required = ["id", "title", "description", "link", "price",
                "availability", "inventory_quantity",
                "image_link", "enable_search", "enable_checkout"]

    for f in required:
        if get(f) in (None, ""):
            if f in ("enable_search", "enable_checkout"):
                warnings.append(f"Missing flag '{f}', recommended by spec.")
            else:
                errors.append(f"Missing required field '{f}'.")

    # URL checks
    if get("link") and not is_url(get("link")):
        errors.append("Invalid URL in 'link'.")
    if get("image_link") and not is_url(get("image_link")):
        errors.append("Invalid URL in 'image_link'.")

    # Price
    price_val, price_cur = extract_price_and_currency(get("price"))
    if price_val is None:
        errors.append("Invalid price format (expected 'number CUR').")

    # Sale price
    sale = get("sale_price")
    if sale:
        sale_val, _ = extract_price_and_currency(sale)
        if sale_val is None:
            errors.append("sale_price not parseable.")
        elif price_val and sale_val > price_val:
            errors.append("sale_price must be less than price.")

    # Availability
    availability = get("availability")
    if availability not in ("in_stock", "out_of_stock", "preorder"):
        errors.append("availability must be in 'in_stock|out_of_stock|preorder'.")

    if availability == "preorder":
        a_date = get("availability_date")
        if not a_date:
            errors.append("availability_date required for preorder.")
        elif not is_iso8601_date(a_date):
            errors.append("availability_date must be ISO 8601.")
        else:
            dt = parse_iso_date(a_date)
            if dt and dt <= datetime.now(timezone.utc):
                errors.append("availability_date must be future for preorder.")

    # Inventory
    inv = get("inventory_quantity")
    if not is_positive_integer_str(inv):
        errors.append("inventory_quantity must be a non-negative integer.")

    # GTIN / MPN Check
    gtin = get("gtin")
    mpn = get("mpn")
    if not gtin and not mpn:
        errors.append("Either gtin or mpn must be present.")

    return errors, warnings


# -----------------------------------------------------------
# Streamlit App UI
# -----------------------------------------------------------

st.set_page_config(page_title="OpenAI Product Feed Validator", layout="wide")
st.title("🛍️ OpenAI Product Feed Validator")
st.write("Upload a **JSON or XML** feed to validate it against the **OpenAI Product Feed Spec**.")

uploaded = st.file_uploader("Upload JSON or XML feed", type=["json", "xml"])

if uploaded:
    with st.spinner("Parsing feed..."):
        products = load_feed(uploaded)

    if products:
        st.success(f"Loaded {len(products)} product records!")

        report = []
        total_errors = 0
        total_warnings = 0

    for idx, p in enumerate(products, start=1):

    errors = product_results[idx - 1]["errors_list"]
    warnings = product_results[idx - 1]["warnings_list"]
    infos = product_results[idx - 1]["infos_list"]

    with st.expander(f"Product {idx} — ID: {p.get('id', '(no id)')}"):

        # ===== FIELD-LEVEL TABLE =====
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

            # Match field to error message
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

        # ===== ERRORS / WARNINGS / INFO =====
        if errors:
            st.error("Errors:\n- " + "\n- ".join(errors))
        if warnings:
            st.warning("Warnings:\n- " + "\n- ".join(warnings))
        if infos:
            st.info("Info:\n- " + "\n- ".join(infos))


        # Downloadable CSV
        df = pd.DataFrame(report)
        st.download_button(
            "Download Report as CSV",
            df.to_csv(index=False).encode("utf-8"),
            "product_feed_report.csv",
            "text/csv"
        )

else:
    st.info("Please upload a feed file to start validation.")
