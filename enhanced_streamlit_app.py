"""
Enhanced Streamlit Application for Product Feed Validation
Integrates batch processing, API endpoints, and advanced validation with dashboard
"""

import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import re
import plotly.express as px
import plotly.graph_objects as go
from batch_processor import (
    BatchProcessingManager, BatchConfig, FeedFormat, 
    CSVBatchProcessor, JSONBatchProcessor, DefaultValidator
)
from validators.basic import validate_basic
from validators.media import validate_media
from validators.availability import validate_availability
from validators.geo import validate_geo
from validators.reviews import validate_reviews
from validators.returns import validate_returns
from validators.flags import validate_flags

# Page configuration
st.set_page_config(
    page_title="Advanced Product Feed Validator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .error-badge {
        background-color: #dc3545;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .warning-badge {
        background-color: #ffc107;
        color: black;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)


class ComprehensiveValidator:
    """Comprehensive product feed validator using modular validators"""
    
    def __init__(self):
        self.validators = [
            validate_basic,
            validate_media,
            validate_availability,
            validate_geo,
            validate_reviews,
            validate_returns,
            validate_flags
        ]
        self.all_errors = []
        self.all_warnings = []
        self.validation_details = []

    def validate_product(self, product: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate single product using all validators"""
        product_errors = []
        product_warnings = []
        product_rows = []

        for validator_func in self.validators:
            try:
                errors, warnings, rows = validator_func(product)
                product_errors.extend(errors)
                product_warnings.extend(warnings)
                product_rows.extend(rows)
            except Exception as e:
                product_errors.append(f"Validator error: {str(e)}")

        return {
            'index': index,
            'errors': product_errors,
            'warnings': product_warnings,
            'rows': product_rows,
            'is_valid': len(product_errors) == 0
        }

    def validate_feed(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate entire feed"""
        results = {
            'products': [],
            'summary': {},
            'health_score': 0.0,
            'recommendations': []
        }

        valid_count = 0
        total_errors = 0
        total_warnings = 0

        for idx, product in enumerate(products):
            validation_result = self.validate_product(product, idx)
            results['products'].append(validation_result)
            
            if validation_result['is_valid']:
                valid_count += 1
            
            total_errors += len(validation_result['errors'])
            total_warnings += len(validation_result['warnings'])

        # Calculate health score
        if len(products) > 0:
            health_score = (valid_count / len(products)) * 100
        else:
            health_score = 0.0

        results['summary'] = {
            'total_products': len(products),
            'valid_products': valid_count,
            'invalid_products': len(products) - valid_count,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'error_rate': ((len(products) - valid_count) / len(products) * 100) if len(products) > 0 else 0
        }

        results['health_score'] = health_score
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        summary = results['summary']
        if summary['error_rate'] > 20:
            recommendations.append("🔴 Critical: Fix errors in more than 20% of products")
        
        if summary['total_warnings'] > 0:
            recommendations.append("⚠️ Address warnings to improve data quality")
        
        if summary['total_products'] == 0:
            recommendations.append("ℹ️ No products in feed")
        
        if summary['total_products'] > 0 and summary['valid_products'] == summary['total_products']:
            recommendations.append("✅ All products passed validation!")

        return recommendations


def create_dashboard(results: Dict[str, Any]):
    """Create comprehensive dashboard with visualizations"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Health Score",
            f"{results['health_score']:.1f}%",
            delta="Feed Quality"
        )
    
    with col2:
        st.metric(
            "Valid Products",
            f"{results['summary']['valid_products']}/{results['summary']['total_products']}"
        )
    
    with col3:
        st.metric(
            "Total Errors",
            results['summary']['total_errors'],
            delta="To Fix"
        )
    
    with col4:
        st.metric(
            "Total Warnings",
            results['summary']['total_warnings'],
            delta="To Review"
        )

    # Visualizations
    st.markdown("---")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Pie chart for product validity
        valid_counts = [
            results['summary']['valid_products'],
            results['summary']['invalid_products']
        ]
        fig = px.pie(
            values=valid_counts,
            names=['Valid', 'Invalid'],
            title='Product Validity Distribution',
            color_discrete_map={'Valid': '#28a745', 'Invalid': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with viz_col2:
        # Error/Warning distribution
        summary_data = {
            'Type': ['Errors', 'Warnings'],
            'Count': [
                results['summary']['total_errors'],
                results['summary']['total_warnings']
            ]
        }
        fig = px.bar(
            summary_data,
            x='Type',
            y='Count',
            title='Errors vs Warnings',
            color='Type',
            color_discrete_map={'Errors': '#dc3545', 'Warnings': '#ffc107'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    if results['recommendations']:
        st.markdown("### 💡 Recommendations")
        for rec in results['recommendations']:
            st.info(rec)


def display_detailed_results(results: Dict[str, Any]):
    """Display detailed validation results"""
    
    st.markdown("### 📋 Detailed Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Products with Issues",
        "Error Details",
        "Field Analysis",
        "Summary Table"
    ])

    with tab1:
        problematic = [p for p in results['products'] if not p['is_valid']]
        if problematic:
            st.markdown(f"**Products with issues:** {len(problematic)}")
            for product in problematic[:20]:
                with st.expander(f"Product #{product['index']} - {len(product['errors'])} errors"):
                    for error in product['errors']:
                        st.error(f"• {error}")
                    if product['warnings']:
                        st.warning("**Warnings:**")
                        for warning in product['warnings']:
                            st.write(f"• {warning}")
        else:
            st.success("✅ No products with errors!")

    with tab2:
        errors_list = []
        for product in results['products']:
            for error in product['errors']:
                errors_list.append({
                    'Product #': product['index'],
                    'Error': error
                })
        
        if errors_list:
            df_errors = pd.DataFrame(errors_list)
            st.dataframe(df_errors, use_container_width=True, hide_index=True)
        else:
            st.info("No errors found in feed")

    with tab3:
        all_fields = {}
        for product in results['products']:
            for row in product['rows']:
                field = row['Field']
                if field not in all_fields:
                    all_fields[field] = {'values': [], 'count': 0}
                all_fields[field]['values'].append(row['Value'])
                all_fields[field]['count'] += 1
        
        field_stats = []
        for field, data in all_fields.items():
            non_empty = sum(1 for v in data['values'] if v is not None and v != '')
            field_stats.append({
                'Field': field,
                'Present': non_empty,
                'Missing': data['count'] - non_empty,
                'Coverage': f"{(non_empty/data['count']*100):.1f}%"
            })
        
        df_fields = pd.DataFrame(field_stats)
        st.dataframe(df_fields, use_container_width=True, hide_index=True)

    with tab4:
        summary_data = []
        for product in results['products']:
            summary_data.append({
                'Product #': product['index'],
                'Errors': len(product['errors']),
                'Warnings': len(product['warnings']),
                'Status': '✗ Invalid' if product['errors'] else '✓ Valid'
            })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)


def main():
    """Main application"""
    
    st.markdown("# 🚀 Advanced Product Feed Validator")
    st.markdown("Professional tool for validating, analyzing, and optimizing product feeds")

    # Sidebar
    with st.sidebar:
        st.markdown("## 📂 Menu")
        page = st.radio(
            "Select page:",
            [
                "Dashboard",
                "Batch Processing",
                "Manual Validation",
                "Analytics",
                "Settings",
                "Help"
            ]
        )

    if page == "Dashboard":
        dashboard_page()
    elif page == "Batch Processing":
        batch_processing_page()
    elif page == "Manual Validation":
        manual_validation_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Settings":
        settings_page()
    else:
        help_page()


def dashboard_page():
    """Dashboard page"""
    st.markdown("## 📊 Dashboard")
    
    st.info("""
    Welcome to the Advanced Product Feed Validator Dashboard.
    Use the sidebar to navigate to different features.
    """)

    # Quick stats
    st.markdown("### Quick Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Validators", 7, "Active")
    with col2:
        st.metric("Feed Formats", 2, "CSV, JSON")
    with col3:
        st.metric("Export Formats", 3, "JSON, CSV, TXT")


def batch_processing_page():
    """Batch processing page"""
    st.markdown("## 📦 Batch Processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload CSV or JSON file",
            type=['csv', 'json']
        )
    
    with col2:
        st.markdown("### Options")
        validate_data = st.checkbox("Validate data", value=True)
        skip_on_error = st.checkbox("Skip on error", value=True)
        deduplicate = st.checkbox("Remove duplicates", value=True)

    if uploaded_file:
        # Determine file format
        file_format = FeedFormat.CSV if uploaded_file.name.endswith('.csv') else FeedFormat.JSON
        
        # Read file
        if file_format == FeedFormat.CSV:
            df = pd.read_csv(uploaded_file)
            feed_data = df.to_dict('records')
        else:
            feed_data = json.load(uploaded_file)
            if not isinstance(feed_data, list):
                feed_data = [feed_data]

        st.markdown(f"### File: {uploaded_file.name}")
        st.metric("Total Records", len(feed_data))

        # Process button
        if st.button("▶ Start Processing", use_container_width=True, type="primary"):
            with st.spinner("Processing feed..."):
                config = BatchConfig(
                    validate_data=validate_data,
                    skip_on_error=skip_on_error,
                    deduplicate=deduplicate
                )
                
                validator = ComprehensiveValidator()
                results = validator.validate_feed(feed_data)
                
                # Display results
                create_dashboard(results)
                display_detailed_results(results)

                # Export options
                st.markdown("---")
                st.markdown("### 📥 Export Results")
                
                exp_col1, exp_col2, exp_col3 = st.columns(3)
                
                with exp_col1:
                    if st.button("📄 Download JSON", use_container_width=True):
                        json_str = json.dumps(results, indent=2)
                        st.download_button(
                            label="Download",
                            data=json_str,
                            file_name=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with exp_col2:
                    if st.button("📊 Download CSV", use_container_width=True):
                        df_export = pd.DataFrame([
                            {
                                'Product #': p['index'],
                                'Valid': '✓' if p['is_valid'] else '✗',
                                'Errors': len(p['errors']),
                                'Warnings': len(p['warnings'])
                            }
                            for p in results['products']
                        ])
                        csv_str = df_export.to_csv(index=False)
                        st.download_button(
                            label="Download",
                            data=csv_str,
                            file_name=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                with exp_col3:
                    st.info("More export formats coming soon")


def manual_validation_page():
    """Manual validation page"""
    st.markdown("## ✏️ Manual Validation")
    
    st.markdown("### Enter JSON data manually")
    
    json_input = st.text_area(
        "Paste JSON (single object or array):",
        height=300,
        placeholder='[{"id": "1", "title": "Product", ...}]'
    )

    if json_input and st.button("▶ Validate", use_container_width=True, type="primary"):
        try:
            feed_data = json.loads(json_input)
            if not isinstance(feed_data, list):
                feed_data = [feed_data]
            
            with st.spinner("Validating..."):
                validator = ComprehensiveValidator()
                results = validator.validate_feed(feed_data)
                
                create_dashboard(results)
                display_detailed_results(results)
        
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {str(e)}")


def analytics_page():
    """Analytics page"""
    st.markdown("## 📈 Analytics")
    
    st.info("Analytics features coming soon")
    
    st.markdown("""
    Features planned:
    - Historical validation trends
    - Field quality metrics
    - Error pattern analysis
    - Processing performance metrics
    """)


def settings_page():
    """Settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### Validation Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Batch Processing")
        batch_size = st.number_input("Batch size", 100, 10000, 1000)
        max_retries = st.number_input("Max retries", 1, 10, 3)
    
    with col2:
        st.markdown("#### Data Processing")
        validate_data = st.checkbox("Validate data", value=True)
        skip_errors = st.checkbox("Skip on error", value=True)
        deduplicate = st.checkbox("Deduplicate", value=True)

    if st.button("Save Settings", use_container_width=True):
        st.success("Settings saved!")


def help_page():
    """Help page"""
    st.markdown("## ❓ Help & Documentation")
    
    st.markdown("""
    ### Getting Started
    
    1. **Upload a Feed**: Go to "Batch Processing" and upload your CSV or JSON file
    2. **Validate**: Click the "Start Processing" button
    3. **Review Results**: Check the dashboard and detailed analysis
    4. **Export**: Download results in your preferred format
    
    ### Supported Formats
    
    - **CSV**: Comma-separated values with headers
    - **JSON**: Array of objects or single object
    
    ### Validation Rules
    
    The validator checks:
    - Required fields presence
    - Data type compliance
    - URL format validation
    - Inventory constraints
    - Review data integrity
    - Return policy validation
    - And more...
    
    ### Tips
    
    - Always validate before importing to production
    - Fix errors before warnings
    - Use batch processing for large feeds
    - Export results for record keeping
    """)


if __name__ == "__main__":
    main()
