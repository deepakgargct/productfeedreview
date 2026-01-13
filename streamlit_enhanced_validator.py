"""
Enhanced ChatGPT Product Feed Validator with Compliance Scoring
Streamlit UI with API integration, compliance metrics, and batch processing
"""

import streamlit as st
import pandas as pd
import json
import io
import requests
from datetime import datetime
from typing import Dict, List, Any

# Set page configuration
st.set_page_config(
    page_title="ChatGPT Product Feed Validator",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    .compliance-score {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .score-excellent {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .score-good {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .score-fair {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
    }
    .score-poor {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #333;
    }
    .critical-issue {
        background-color: #fee;
        border-left: 4px solid #f00;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .warning-issue {
        background-color: #ffc;
        border-left: 4px solid #ff0;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .recommendation {
        background-color: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .action-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:5000"

def call_validate_api(product_data: Dict) -> Dict:
    """Call the /api/validate endpoint for single product validation"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/validate",
            json=product_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the API server is running on http://localhost:5000")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP Error {e.response.status_code}: {e.response.reason}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The server took too long to respond.")
        return None
    except Exception as e:
        st.error(f"❌ Error calling API: {str(e)}")
        return None

def call_validate_feed_api(products: List[Dict] = None, file_data = None) -> Dict:
    """Call the /api/validate-feed endpoint for batch validation"""
    try:
        if file_data:
            # Upload file
            files = {'file': file_data}
            response = requests.post(
                f"{API_BASE_URL}/api/validate-feed",
                files=files,
                timeout=60
            )
        else:
            # Send JSON
            response = requests.post(
                f"{API_BASE_URL}/api/validate-feed",
                json=products,
                timeout=60
            )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the API server is running on http://localhost:5000")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP Error {e.response.status_code}: {e.response.reason}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The server took too long to respond.")
        return None
    except Exception as e:
        st.error(f"❌ Error calling API: {str(e)}")
        return None

def display_compliance_score(score: float, percentage: str):
    """Display compliance score with color coding"""
    if score >= 90:
        css_class = "score-excellent"
        status = "🌟 Excellent"
    elif score >= 70:
        css_class = "score-good"
        status = "✅ Good"
    elif score >= 50:
        css_class = "score-fair"
        status = "⚠️ Fair"
    else:
        css_class = "score-poor"
        status = "❌ Poor"
    
    st.markdown(f"""
        <div class="compliance-score {css_class}">
            <div style="font-size: 0.6em; margin-bottom: 10px;">{status}</div>
            <div>{percentage}</div>
            <div style="font-size: 0.4em; margin-top: 10px;">Compliance Score</div>
        </div>
    """, unsafe_allow_html=True)

def display_critical_issues(issues: List[Dict]):
    """Display critical issues with red highlighting"""
    if not issues:
        st.success("✅ No critical issues found!")
        return
    
    st.markdown("### 🔴 Critical Issues")
    st.markdown(f"**Found {len(issues)} critical issue(s) that must be fixed:**")
    
    for idx, issue in enumerate(issues, 1):
        st.markdown(f"""
            <div class="critical-issue">
                <strong>#{idx}: {issue['field']}</strong><br/>
                ❌ {issue['message']}<br/>
                💡 <em>Suggestion: {issue.get('suggestion', 'Please fix this issue')}</em>
            </div>
        """, unsafe_allow_html=True)

def display_warnings(warnings: List[Dict]):
    """Display warnings"""
    if not warnings:
        return
    
    st.markdown("### ⚠️ Warnings")
    st.markdown(f"**Found {len(warnings)} warning(s):**")
    
    for idx, warning in enumerate(warnings, 1):
        st.markdown(f"""
            <div class="warning-issue">
                <strong>#{idx}: {warning['field']}</strong><br/>
                ⚠️ {warning['message']}<br/>
                💡 <em>Suggestion: {warning.get('suggestion', 'Consider addressing this')}</em>
            </div>
        """, unsafe_allow_html=True)

def display_recommendations(recommendations: List[Dict]):
    """Display actionable recommendations"""
    if not recommendations:
        return
    
    st.markdown("### 💡 Recommendations")
    st.markdown(f"**{len(recommendations)} improvement(s) suggested:**")
    
    for idx, rec in enumerate(recommendations, 1):
        action = rec.get('action', rec.get('suggestion', 'Review and update'))
        st.markdown(f"""
            <div class="recommendation">
                <strong>#{idx}: {rec['field']}</strong><br/>
                📝 {rec['message']}<br/>
                🎯 <strong>Action:</strong> <em>{action}</em>
            </div>
        """, unsafe_allow_html=True)

def main():
    """Main application"""
    # Header
    st.markdown("# ✅ ChatGPT Product Feed Validator")
    st.markdown("**Validate product feeds against ChatGPT specifications with compliance scoring**")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Navigation")
        page = st.radio(
            "Select Mode:",
            ["Single Product Validation", "Batch Feed Validation", "API Info"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.info("""
        This tool validates product feeds against ChatGPT product specifications:
        
        - ✅ Compliance scoring (0-100%)
        - 🔴 Critical issue detection
        - 💡 Actionable recommendations
        - 📦 CSV/JSON batch processing
        """)
    
    if page == "Single Product Validation":
        single_product_page()
    elif page == "Batch Feed Validation":
        batch_feed_page()
    else:
        api_info_page()

def single_product_page():
    """Single product validation page"""
    st.markdown("## 🔍 Single Product Validation")
    st.markdown("Validate a single product and get instant compliance feedback")
    
    # Input method
    input_method = st.radio(
        "Input Method:",
        ["Manual Entry", "JSON Paste", "Sample Product"],
        horizontal=True
    )
    
    product_data = None
    
    if input_method == "Manual Entry":
        st.markdown("### Enter Product Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_id = st.text_input("Product ID *", help="Unique product identifier")
            title = st.text_input("Title *", help="Product title (10-150 characters)")
            price = st.number_input("Price *", min_value=0.01, value=99.99, step=0.01)
            currency = st.selectbox("Currency *", ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "INR"])
            
        with col2:
            category = st.text_input("Category *", help="Product category")
            availability = st.selectbox("Availability *", ["in_stock", "out_of_stock", "preorder"])
            brand = st.text_input("Brand", help="Product brand")
            image_url = st.text_input("Image URL", help="Product image URL (HTTPS)")
        
        description = st.text_area("Description *", help="Product description (20-5000 characters)")
        product_url = st.text_input("Product URL", help="Product landing page URL")
        
        if st.button("✅ Validate Product", type="primary", use_container_width=True):
            if not all([product_id, title, price, currency, category, availability, description]):
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                product_data = {
                    "product_id": product_id,
                    "title": title,
                    "description": description,
                    "price": price,
                    "currency": currency,
                    "category": category,
                    "availability": availability
                }
                if brand:
                    product_data["manufacturer"] = brand
                if image_url:
                    product_data["image_url"] = image_url
                if product_url:
                    product_data["product_url"] = product_url
    
    elif input_method == "JSON Paste":
        st.markdown("### Paste Product JSON")
        json_input = st.text_area(
            "Product JSON:",
            height=300,
            placeholder='{\n  "product_id": "PROD001",\n  "title": "Product Name",\n  ...\n}'
        )
        
        if st.button("✅ Validate JSON", type="primary", use_container_width=True):
            try:
                product_data = json.loads(json_input)
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {str(e)}")
    
    else:  # Sample Product
        st.markdown("### Using Sample Product Data")
        if st.button("📦 Load Sample & Validate", type="primary", use_container_width=True):
            product_data = {
                "product_id": "SAMPLE001",
                "title": "Premium Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with active noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers and professionals.",
                "price": 149.99,
                "currency": "USD",
                "category": "electronics",
                "availability": "in_stock",
                "image_url": "https://example.com/images/headphones.jpg",
                "product_url": "https://example.com/products/headphones",
                "manufacturer": "AudioPro",
                "rating": 4.5,
                "review_count": 1250
            }
            st.code(json.dumps(product_data, indent=2), language="json")
    
    # Validate if we have product data
    if product_data:
        with st.spinner("🔄 Validating product..."):
            result = call_validate_api(product_data)
        
        if result:
            st.markdown("---")
            display_validation_results(result)

def batch_feed_page():
    """Batch feed validation page"""
    st.markdown("## 📦 Batch Feed Validation")
    st.markdown("Upload CSV or JSON files to validate multiple products at once")
    
    # File upload
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Product Feed",
            type=['csv', 'json'],
            help="Upload a CSV or JSON file containing multiple products"
        )
    
    with col2:
        st.markdown("### 📋 Format Requirements")
        st.info("""
        **CSV:** Must include headers
        **JSON:** Array of products or {products: [...]}
        """)
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Preview file
        with st.expander("👀 Preview File"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df.head(10), use_container_width=True)
                    uploaded_file.seek(0)  # Reset file pointer
                elif uploaded_file.name.endswith('.json'):
                    content = uploaded_file.read().decode('utf-8')
                    data = json.loads(content)
                    st.json(data if isinstance(data, list) else data.get('products', [data]))
                    uploaded_file.seek(0)  # Reset file pointer
            except Exception as e:
                st.error(f"❌ Error previewing file: {str(e)}")
        
        if st.button("✅ Validate Feed", type="primary", use_container_width=True):
            with st.spinner("🔄 Validating feed..."):
                result = call_validate_feed_api(file_data=uploaded_file)
            
            if result:
                st.markdown("---")
                display_batch_results(result)

def display_validation_results(result: Dict):
    """Display single product validation results"""
    st.markdown("## 📊 Validation Results")
    
    # Compliance Score
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        display_compliance_score(
            result.get('compliance_score', 0),
            result.get('compliance_percentage', '0%')
        )
    
    with col2:
        st.metric(
            "Status",
            "✅ Valid" if result.get('is_compliant', False) else "❌ Invalid",
            help="Product validation status"
        )
        st.metric(
            "Product ID",
            result.get('product_id', 'N/A'),
            help="Validated product identifier"
        )
    
    with col3:
        summary = result.get('summary', {})
        st.metric("Critical Issues", summary.get('total_critical', 0), help="Must be fixed")
        st.metric("Warnings", summary.get('total_warnings', 0), help="Should be addressed")
        st.metric("Recommendations", summary.get('total_recommendations', 0), help="For improvement")
    
    st.markdown("---")
    
    # Display issues, warnings, and recommendations
    critical_issues = result.get('critical_issues', [])
    warnings = result.get('warnings', [])
    recommendations = result.get('recommendations', [])
    
    if critical_issues:
        display_critical_issues(critical_issues)
        st.markdown("---")
    
    if warnings:
        display_warnings(warnings)
        st.markdown("---")
    
    if recommendations:
        display_recommendations(recommendations)
    
    # Export results
    st.markdown("---")
    st.markdown("### 📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        json_export = json.dumps(result, indent=2)
        st.download_button(
            "📄 Download JSON Report",
            json_export,
            file_name=f"validation_{result.get('product_id', 'product')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Create CSV summary
        csv_data = pd.DataFrame([{
            'Product ID': result.get('product_id'),
            'Valid': result.get('is_compliant'),
            'Compliance Score': result.get('compliance_score'),
            'Critical Issues': summary.get('total_critical', 0),
            'Warnings': summary.get('total_warnings', 0),
            'Recommendations': summary.get('total_recommendations', 0),
            'Timestamp': result.get('timestamp')
        }])
        st.download_button(
            "📊 Download CSV Summary",
            csv_data.to_csv(index=False),
            file_name=f"validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def display_batch_results(result: Dict):
    """Display batch validation results"""
    st.markdown("## 📊 Batch Validation Results")
    
    batch_summary = result.get('batch_summary', {})
    
    # Overall metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Products", batch_summary.get('total_products', 0))
    with col2:
        st.metric("Compliant", batch_summary.get('compliant_products', 0), help="Valid products")
    with col3:
        st.metric("Non-Compliant", batch_summary.get('non_compliant_products', 0), help="Invalid products")
    with col4:
        st.metric("Compliance Rate", batch_summary.get('compliance_rate', '0%'))
    with col5:
        st.metric("Avg Score", batch_summary.get('average_compliance_score', 0))
    
    st.markdown("---")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Critical Issues", batch_summary.get('total_critical_issues', 0), help="Across all products")
    with col2:
        st.metric("Total Warnings", batch_summary.get('total_warnings', 0))
    with col3:
        st.metric("Total Recommendations", batch_summary.get('total_recommendations', 0))
    
    st.markdown("---")
    
    # Product-by-product results
    st.markdown("### 📋 Detailed Product Results")
    
    products = result.get('products', [])
    
    # Create summary table
    summary_data = []
    for product in products:
        summary_data.append({
            'Product ID': product.get('product_id'),
            'Status': '✅ Valid' if product.get('valid') else '❌ Invalid',
            'Compliance': product.get('compliance_percentage'),
            'Score': product.get('compliance_score'),
            'Critical': product.get('summary', {}).get('total_critical', 0),
            'Warnings': product.get('summary', {}).get('total_warnings', 0),
            'Recommendations': product.get('summary', {}).get('total_recommendations', 0)
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # Detailed view for each product
    st.markdown("### 🔍 Product Details")
    
    for idx, product in enumerate(products):
        with st.expander(f"📦 Product: {product.get('product_id')} - {product.get('compliance_percentage')}"):
            display_validation_results(product)
    
    # Export batch results
    st.markdown("---")
    st.markdown("### 📥 Export Batch Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        json_export = json.dumps(result, indent=2)
        st.download_button(
            "📄 Download Full JSON Report",
            json_export,
            file_name=f"batch_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            "📊 Download Summary CSV",
            df_summary.to_csv(index=False),
            file_name=f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def api_info_page():
    """API information page"""
    st.markdown("## 📡 API Information")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            
            st.success("✅ API Server is running!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Service Information")
                st.json({
                    'Service': info.get('service'),
                    'Version': info.get('version'),
                    'Timestamp': info.get('timestamp')
                })
            
            with col2:
                st.markdown("### Available Endpoints")
                endpoints = info.get('endpoints', {})
                for endpoint, description in endpoints.items():
                    st.markdown(f"- **{endpoint}**: {description}")
            
            st.markdown("### Features")
            features = info.get('features', [])
            for feature in features:
                st.markdown(f"✅ {feature}")
        else:
            st.error("❌ API Server returned an error")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server")
        st.markdown("""
        **To start the API server:**
        
        ```bash
        cd /path/to/productfeedreview
        python api_server.py
        ```
        
        The server will start on `http://localhost:5000`
        """)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
