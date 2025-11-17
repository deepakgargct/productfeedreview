import streamlit as st
import pandas as pd
from utils.parse import load_feed
from validators import run_all_validations

st.set_page_config(page_title="Product Feed Validator (Full Spec Modular)", layout="wide")
st.title("🔎 Product Feed Validator — Full Spec (Modular)")

uploaded = st.file_uploader("Upload JSON or XML product feed (file upload only)", type=["json","xml"])
if not uploaded:
    st.info("Upload a .json or .xml file to begin validation.")
    st.stop()

try:
    products = load_feed(uploaded)
except Exception as e:
    st.error(f"Failed to parse file: {e}")
    st.stop()

st.success(f"Detected {len(products)} product records.")
results = []
for p in products:
    res = run_all_validations(p)
    results.append(res)

# Summary
total_errors = sum(len(r['errors']) for r in results)
total_warnings = sum(len(r['warnings']) for r in results)
c1, c2, c3 = st.columns(3)
c1.metric("Products", len(products))
c2.metric("Total errors", total_errors)
c3.metric("Total warnings", total_warnings)

# Top issues
issue_counts = {}
for r in results:
    for e in r['errors']:
        issue_counts[e] = issue_counts.get(e,0) + 1
    for w in r['warnings']:
        issue_counts[w] = issue_counts.get(w,0) + 1

if issue_counts:
    st.subheader("Top issues")
    df_issues = pd.DataFrame(sorted(issue_counts.items(), key=lambda x: -x[1]), columns=["Issue","Count"])
    st.dataframe(df_issues)

# Detailed per-product
st.subheader("Detailed product reports")
for idx, (p, r) in enumerate(zip(products, results), start=1):
    with st.expander(f"Product {idx} — ID: {p.get('id','(no id)')}"):
        df = pd.DataFrame(r['fields'])
        st.dataframe(df)
        if r['errors']:
            st.error("Errors:\n- " + "\n- ".join(r['errors']))
        if r['warnings']:
            st.warning("Warnings:\n- " + "\n- ".join(r['warnings']))
        if r['infos']:
            st.info("Info:\n- " + "\n- ".join(r['infos']))

# Download CSV summary
rows = []
for idx, (p, r) in enumerate(zip(products, results), start=1):
    rows.append({
        "index": idx,
        "id": p.get("id",""),
        "title": p.get("title",""),
        "price": p.get("price",""),
        "errors": " | ".join(r['errors']),
        "warnings": " | ".join(r['warnings'])
    })
df_report = pd.DataFrame(rows)
st.download_button("Download summary CSV", df_report.to_csv(index=False).encode('utf-8'), "validation_summary.csv", "text/csv")
