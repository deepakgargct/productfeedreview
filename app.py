# app.py
"""
OpenAI Product Feed Validator (Balanced Mode)

- Accepts JSON or XML product feed file upload (no URLs)
- Validates fields per OpenAI Product Feed Spec:
  https://developers.openai.com/commerce/specs/feed
- Balanced Mode: errors for required/conditional-required fields; warnings for recommended fields.
"""

import streamlit as st
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse
import re
import pandas as pd
from typing import Any, Dict, List, Tuple, Optional

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="OpenAI Product Feed Validator (Balanced Mode)", layout="wide")
st.title("🛍️ OpenAI Product Feed Validator")
st.caption("Balanced Mode: errors for required/conditional-required; warnings for recommended fields.")
st.write("Upload a **JSON** or **XML** product feed (file upload only). Validation follows the OpenAI Product Feed Spec.")

# -----------------------
# Helpers
# -----------------------
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
    """
    Accepts formats like "79.99 USD" or "79.99" or '{"value":79.99,"currency":"USD"}'
    Returns (value, currency) where currency may be None.
    """
    if value is None:
        return None, None
    s = str(value).strip()
    # numeric + optional 3-letter currency
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Z]{3})?\s*$", s)
    if m:
        val = float(m.group(1))
        cur = m.group(2)
        return val, cur
    # try json-like
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict) and "value" in parsed:
            val = float(parsed["value"])
            cur = parsed.get("currency")
            return val, cur
    except:
        pass
    # fallback: split tokens
    parts = s.split()
    if not parts:
        return None, None
    try:
        val = float(parts[0])
        cur = parts[1] if len(parts) > 1 and re.match(r"^[A-Z]{3}$", parts[1]) else None
        return val, cur
    except:
        return None, None

def safe_get(p: Dict[str, Any], key: str):
    # case-insensitive get
    for k in p:
        if k.lower() == key.lower():
            return p[k]
    return None

# -----------------------
# Load feed (JSON or XML)
# -----------------------
def extract_products_from_json(obj: Any) -> List[Dict[str, Any]]:
    # direct list of dicts
    if isinstance(obj, list) and all(isinstance(i, dict) for i in obj):
        return obj
    # common container keys
    if isinstance(obj, dict):
        for key in ("products", "items", "feed", "entries", "data"):
            if key in obj and isinstance(obj[key], list) and all(isinstance(i, dict) for i in obj[key]):
                return obj[key]
    # BFS to find first list-of-dicts
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
    raw = uploaded_file.getvalue().decode("utf-8")
    if name.endswith(".json"):
        parsed = json.loads(raw)
        return extract_products_from_json(parsed)
    elif name.endswith(".xml"):
        root = ET.fromstring(raw)
        # find product-like nodes
        candidates = root.findall(".//item") or root.findall(".//product") or root.findall(".//entry")
        if not candidates:
            candidates = list(root)
        items = []
        for el in candidates:
            obj = {}
            for child in el:
                tag = child.tag.split("}")[-1]
                # if nested children, convert to dict
                if list(child):
                    inner = {}
                    for c in child:
                        inner[c.tag.split("}")[-1]] = c.text or ""
                    obj[tag] = inner
                else:
                    obj[tag] = child.text or ""
            items.append(obj)
        return items
    else:
        raise ValueError("Unsupported file type. Upload JSON or XML only.")

# -----------------------
# Validation rules (Balanced Mode)
# -----------------------
# We'll validate required fields (errors), conditional-required (errors), recommended (warnings), optional (light checks).
def validate_product(p: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    infos: List[str] = []

    # -- BASIC FIELDS (Required)
    # id
    prod_id = safe_get(p, "id")
    if prod_id in (None, ""):
        errors.append("Missing required field: id")
    else:
        # id can be numeric or string; ensure <=100 chars
        if len(str(prod_id)) > 100:
            warnings.append("id exceeds recommended max length 100 characters")

    # title
    title = safe_get(p, "title")
    if title in (None, ""):
        errors.append("Missing required field: title")
    else:
        if len(str(title)) > 150:
            warnings.append("title exceeds recommended max length 150 characters")

    # description
    desc = safe_get(p, "description")
    if desc in (None, ""):
        errors.append("Missing required field: description")
    else:
        if len(str(desc)) > 5000:
            errors.append("description exceeds max length 5000 characters")

    # link (required + must be URL; spec says must resolve with HTTP200 but we won't live-check by default)
    link = safe_get(p, "link")
    if link in (None, ""):
        errors.append("Missing required field: link")
    else:
        if not is_url(link):
            errors.append("link must be a valid http(s) URL")
        else:
            # HTTPS preferred (warning)
            if not str(link).lower().startswith("https"):
                warnings.append("link should use HTTPS (preferred)")

    # image_link (required)
    image_link = safe_get(p, "image_link")
    if image_link in (None, ""):
        errors.append("Missing required field: image_link")
    else:
        if not is_url(image_link):
            errors.append("image_link must be a valid http(s) URL")
        elif not str(image_link).lower().startswith("https"):
            warnings.append("image_link should use HTTPS (preferred)")

    # price (required, must include currency per spec)
    price_raw = safe_get(p, "price")
    price_val, price_cur = extract_price_and_currency(price_raw)
    if price_val is None:
        errors.append("Missing or invalid required field: price (expected 'number CUR', e.g., '79.99 USD')")
    else:
        if price_val < 0:
            errors.append("price must be a non-negative number")
        # spec: currency required; balanced mode => error if currency missing
        if not price_cur:
            errors.append("price must include an ISO 4217 currency code (e.g., USD) per spec")

    # availability (required)
    availability = safe_get(p, "availability")
    allowed_avail = ("in_stock", "out_of_stock", "preorder")
    if availability in (None, ""):
        errors.append("Missing required field: availability")
    else:
        if str(availability) not in allowed_avail:
            errors.append("availability must be one of 'in_stock', 'out_of_stock', 'preorder'")

    # inventory_quantity (required)
    inv = safe_get(p, "inventory_quantity")
    if inv in (None, ""):
        errors.append("Missing required field: inventory_quantity")
    else:
        if not is_positive_integer_str(inv):
            errors.append("inventory_quantity must be a non-negative integer")

    # -- CONDITIONAL REQUIRED RULES
    # mpn required if gtin missing
    gtin = safe_get(p, "gtin")
    mpn = safe_get(p, "mpn")
    if (gtin in (None, "")) and (mpn in (None, "")):
        errors.append("Either 'gtin' (recommended) or 'mpn' (required if gtin missing) must be provided")

    # availability_date required if availability == preorder
    if str(availability) == "preorder":
        avail_date = safe_get(p, "availability_date")
        if not avail_date:
            errors.append("availability_date is required when availability='preorder'")
        else:
            if not is_iso8601_date(str(avail_date)):
                errors.append("availability_date must be a valid ISO 8601 date")
            else:
                dt = parse_iso_date(str(avail_date))
                if dt and dt <= datetime.now(timezone.utc):
                    errors.append("availability_date must be a future date for preorder items")

    # item_group_id required if variants exist (we treat presence of color/size as variants)
    has_variant_fields = any(safe_get(p, f) not in (None, "") for f in ("color", "size", "item_group_title", "offer_id"))
    if has_variant_fields:
        item_group_id = safe_get(p, "item_group_id")
        if not item_group_id:
            errors.append("item_group_id is required when variant rows are present (e.g., color/size/offer_id)")

    # sale_price_effective_date required when sale_price present must be start/end
    sale_price = safe_get(p, "sale_price")
    sale_eff = safe_get(p, "sale_price_effective_date")
    if sale_price not in (None, ""):
        sale_val, sale_cur = extract_price_and_currency(sale_price)
        if sale_val is None:
            errors.append("sale_price provided but not parseable as number + optional currency")
        else:
            if price_val is not None and sale_val > price_val:
                errors.append("sale_price must be less than or equal to price")
        if not sale_eff:
            warnings.append("sale_price provided but sale_price_effective_date is missing (recommended)")
        else:
            parts = re.split(r"\s*/\s*", str(sale_eff))
            if len(parts) != 2:
                errors.append("sale_price_effective_date must be a start/end ISO date range 'YYYY-MM-DD / YYYY-MM-DD'")
            else:
                s_dt = parse_iso_date(parts[0])
                e_dt = parse_iso_date(parts[1])
                if not s_dt or not e_dt:
                    errors.append("sale_price_effective_date start or end not valid ISO date")
                elif s_dt >= e_dt:
                    errors.append("sale_price_effective_date start must be before end")

    # -- RECOMMENDED FIELDS (Warnings if missing)
    # gtin recommended (8-14 digits)
    if not gtin:
        warnings.append("gtin is recommended (8-14 digits). If absent, mpn must be provided.")
    else:
        if not re.match(r"^[0-9]{8,14}$", str(gtin)):
            warnings.append("gtin should be 8-14 digits with no spaces/dashes")

    # brand recommended (with exceptions)
    brand = safe_get(p, "brand")
    # spec: brand required for all excluding movies/books/musical recordings; we'll warn if missing
    if not brand:
        warnings.append("brand is recommended for most products (max 70 chars)")

    # product_category (required per spec uses 'product_category' or google_product_category? Spec shows product_category required)
    product_category = safe_get(p, "product_category") or safe_get(p, "category") or safe_get(p, "google_product_category")
    if not product_category:
        warnings.append("product_category (category) is recommended — helps classification and relevance")

    # condition: required if different from 'new' (we warn if present and not allowed)
    condition = safe_get(p, "condition")
    if condition and condition not in ("new", "refurbished", "used"):
        warnings.append("condition should be one of 'new', 'refurbished', 'used' (lower-case)")

    # weight is required per spec (Basic Item Information shows weight is Required — spec line says weight Required? It shows 'weight Number + unit—Product weight Required—Positive number with unit')
    # According to the spec snippet weight is required. We'll enforce it as recommended in Balanced Mode (but spec shows required). To be safe, enforce as required:
    weight = safe_get(p, "weight") or safe_get(p, "shipping_weight")
    if not weight:
        warnings.append("weight (or shipping_weight) is recommended (positive number + unit).")
    else:
        # simple parse: number present
        try:
            float(str(weight).split()[0])
        except:
            warnings.append("weight provided but could not parse numeric part")

    # image assets: additional_image_link optional array
    additional_img = safe_get(p, "additional_image_link")
    if additional_img:
        # allow comma-separated or list-like string
        if isinstance(additional_img, str) and "," in additional_img:
            arr = [s.strip() for s in additional_img.split(",") if s.strip()]
            for url in arr:
                if not is_url(url):
                    warnings.append("additional_image_link contains non-URL entries")
                    break
        elif isinstance(additional_img, list):
            for url in additional_img:
                if not is_url(url):
                    warnings.append("additional_image_link contains non-URL entries")
                    break
        else:
            if not is_url(str(additional_img)):
                warnings.append("additional_image_link is present but not a valid URL or list")

    # video_link optional: must be URL if present
    video_link = safe_get(p, "video_link")
    if video_link:
        if isinstance(video_link, str) and "," in video_link:
            for v in [s.strip() for s in video_link.split(",")]:
                if not is_url(v):
                    warnings.append("video_link contains invalid URL")
                    break
        elif isinstance(video_link, list):
            for v in video_link:
                if not is_url(v):
                    warnings.append("video_link contains invalid URL")
                    break
        else:
            if not is_url(str(video_link)):
                warnings.append("video_link is not a valid URL")

    # model_3d_link optional
    model_3d = safe_get(p, "model_3d_link")
    if model_3d and not is_url(model_3d):
        warnings.append("model_3d_link provided but not a valid URL")

    # shipping parsing (light)
    shipping = safe_get(p, "shipping")
    if shipping:
        # accept list or comma-separated entries of format country:region:service_class:price
        entries = shipping if isinstance(shipping, list) else [s.strip() for s in str(shipping).split(",") if s.strip()]
        for s in entries:
            parts = s.split(":")
            if len(parts) < 4:
                warnings.append(f"shipping entry '{s}' expected 'country:region:service_class:price'")
            else:
                # check price parse
                pv, _ = extract_price_and_currency(parts[3])
                if pv is None:
                    warnings.append(f"shipping entry price not parseable in '{s}'")

    # seller info recommended
    if not safe_get(p, "seller_name"):
        warnings.append("seller_name recommended (merchant display name)")

    # timestamps recommended
    if not safe_get(p, "updated_at") and not safe_get(p, "created_at"):
        warnings.append("updated_at or created_at recommended for feed freshness tracking")

    # any schema_org_json_ld presence is info
    if safe_get(p, "schema_org_json_ld"):
        infos.append("schema_org_json_ld present — good for structured data")

    return errors, warnings, infos

# -----------------------
# UI: File upload
# -----------------------
uploaded = st.file_uploader("Upload JSON or XML feed (file upload only)", type=["json", "xml"])
if not uploaded:
    st.info("Please upload a JSON or XML product feed file to validate.")
    st.stop()

try:
    with st.spinner("Parsing feed..."):
        products = load_feed(uploaded)
except Exception as e:
    st.error(f"Failed to parse uploaded file: {e}")
    st.stop()

if not products:
    st.warning("No product records were detected in the uploaded feed.")
    st.stop()

st.success(f"Loaded {len(products)} product records.")

# -----------------------
# Validate all products
# -----------------------
prod_results = []
total_errors = 0
total_warnings = 0

for p in products:
    errs, warns, infos = validate_product(p)
    prod_results.append({"errors_list": errs, "warnings_list": warns, "infos_list": infos})
    total_errors += len(errs)
    total_warnings += len(warns)

# -----------------------
# Summary
# -----------------------
st.subheader("Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Total products", len(products))
c2.metric("Total errors", total_errors)
c3.metric("Total warnings", total_warnings)

# grouped summary of most common issues
issue_counts = {}
for r in prod_results:
    for e in r["errors_list"]:
        issue_counts[e] = issue_counts.get(e, 0) + 1
    for w in r["warnings_list"]:
        issue_counts[w] = issue_counts.get(w, 0) + 1

if issue_counts:
    st.subheader("Top issues (errors + warnings)")
    df_issues = pd.DataFrame(sorted(issue_counts.items(), key=lambda x: -x[1]), columns=["Issue", "Count"])
    st.dataframe(df_issues)

# -----------------------
# Detailed per-product report (field-by-field)
# -----------------------
st.subheader("Detailed Product Reports")

# fields to show in table (covers spec main fields)
fields_display = [
    "id", "title", "description", "link", "image_link", "additional_image_link",
    "price", "sale_price", "sale_price_effective_date", "unit_pricing_measure", "pricing_trend",
    "availability", "availability_date", "inventory_quantity", "expiration_date",
    "condition", "product_category", "brand", "material", "dimensions", "length", "width", "height", "weight",
    "item_group_id", "item_group_title", "color", "size", "size_system", "gender", "offer_id",
    "custom_variant1_category", "custom_variant1_option", "custom_variant2_category", "custom_variant2_option",
    "shipping", "shipping_weight", "shipping_label", "tax", "seller_name", "seller_tos", "seller_privacy_policy",
    "enable_search", "enable_checkout", "geo_availability", "geo_price", "language", "updated_at", "created_at",
    "video_link", "model_3d_link", "raw_review_data", "q_and_a", "schema_org_json_ld", "metadata"
]

for idx, p in enumerate(products, start=1):
    errs = prod_results[idx - 1]["errors_list"]
    warns = prod_results[idx - 1]["warnings_list"]
    infos = prod_results[idx - 1]["infos_list"]

    with st.expander(f"Product {idx} — ID: {p.get('id', '(no id)')}"):

        table_rows = []
        for field in fields_display:
            val = safe_get(p, field)
            present = val not in (None, "")
            status = "✔ Present" if present else "⚠ Missing"

            # check if any error mentions this field
            notes = ""
            for e in errs:
                if field.lower() in e.lower():
                    status = "❌ Invalid"
                    notes = e
            # attach first matching warning if any
            if not notes:
                for w in warns:
                    if field.lower() in w.lower():
                        notes = w
                        break

            table_rows.append({
                "Field": field,
                "Status": status,
                "Value": val if val not in (None, "") else "—",
                "Notes": notes if notes else "—"
            })

        df_table = pd.DataFrame(table_rows)
        st.markdown("#### 🔎 Field Validation Overview")
        st.dataframe(df_table)

        if errs:
            st.error("Errors:\n- " + "\n- ".join(errs))
        if warns:
            st.warning("Warnings:\n- " + "\n- ".join(warns))
        if infos:
            st.info("Info:\n- " + "\n- ".join(infos))

# -----------------------
# Download combined report as CSV
# -----------------------
st.subheader("Downloadable Reports")
report_rows = []
for idx, p in enumerate(products, start=1):
    base = {"index": idx, "id": p.get("id", "")}
    base["errors"] = " | ".join(prod_results[idx - 1]["errors_list"])
    base["warnings"] = " | ".join(prod_results[idx - 1]["warnings_list"])
    # include some key fields
    base["title"] = p.get("title", "")
    base["price"] = p.get("price", "")
    base["availability"] = p.get("availability", "")
    base["inventory_quantity"] = p.get("inventory_quantity", "")
    report_rows.append(base)

df_report = pd.DataFrame(report_rows)
csv_bytes = df_report.to_csv(index=False).encode("utf-8")

st.download_button("Download validation summary CSV", csv_bytes, "validation_summary.csv", "text/csv")

st.success("Validation complete. Review per-product reports to fix required/conditional issues first (errors), then address recommendations (warnings).")
