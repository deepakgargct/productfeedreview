import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import csv
import io
from typing import List, Dict, Tuple, Any
import hashlib
from collections import defaultdict

# Page configuration
st.set_page_config(
    page_title="Product Feed Validator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
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
    }
    .warning-badge {
        background-color: #ffc107;
        color: black;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    .error-badge {
        background-color: #dc3545;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    .info-badge {
        background-color: #17a2b8;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


class ProductFeedValidator:
    """Comprehensive product feed validator with compliance scoring."""
    
    # Define required and recommended fields
    REQUIRED_FIELDS = {
        'id': 'string',
        'title': 'string',
        'description': 'string',
        'price': 'numeric',
        'availability': 'string',
        'image_link': 'url'
    }
    
    RECOMMENDED_FIELDS = {
        'brand': 'string',
        'category': 'string',
        'product_type': 'string',
        'condition': 'string',
        'mpn': 'string',
        'gtin': 'string'
    }
    
    AVAILABILITY_OPTIONS = ['in_stock', 'out_of_stock', 'preorder', 'available', 'unavailable']
    CONDITION_OPTIONS = ['new', 'refurbished', 'used']
    
    def __init__(self):
        self.validation_results = {}
        self.issues = []
        self.compliance_score = 0
    
    def validate_feed(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate entire product feed."""
        self.issues = []
        validation_report = {
            'total_rows': len(df),
            'valid_rows': 0,
            'invalid_rows': 0,
            'issues': [],
            'field_analysis': {},
            'compliance_score': 0,
            'recommendations': []
        }
        
        # Check required fields
        missing_fields = self._check_required_fields(df)
        if missing_fields:
            validation_report['issues'].extend(missing_fields)
        
        # Validate each row
        valid_count = 0
        for idx, row in df.iterrows():
            row_issues = self._validate_row(row, idx)
            if not row_issues:
                valid_count += 1
            else:
                validation_report['issues'].extend(row_issues)
        
        validation_report['valid_rows'] = valid_count
        validation_report['invalid_rows'] = len(df) - valid_count
        
        # Analyze fields
        validation_report['field_analysis'] = self._analyze_fields(df)
        
        # Calculate compliance score
        validation_report['compliance_score'] = self._calculate_compliance_score(
            df, 
            validation_report
        )
        
        # Generate recommendations
        validation_report['recommendations'] = self._generate_recommendations(
            df,
            validation_report
        )
        
        return validation_report
    
    def _check_required_fields(self, df: pd.DataFrame) -> List[str]:
        """Check if all required fields are present."""
        issues = []
        missing = [field for field in self.REQUIRED_FIELDS.keys() if field not in df.columns]
        
        if missing:
            issues.append({
                'type': 'error',
                'field': 'structure',
                'message': f"Missing required fields: {', '.join(missing)}",
                'row': 'all'
            })
        
        return issues
    
    def _validate_row(self, row: pd.Series, row_idx: int) -> List[Dict]:
        """Validate a single row."""
        issues = []
        
        # Check required fields have values
        for field in self.REQUIRED_FIELDS.keys():
            if field not in row.index or pd.isna(row[field]) or str(row[field]).strip() == '':
                issues.append({
                    'type': 'error',
                    'field': field,
                    'message': f'Required field is empty',
                    'row': row_idx + 2  # +2 for header and 1-based indexing
                })
        
        # Validate specific fields
        if 'price' in row.index and not pd.isna(row['price']):
            if not self._is_valid_price(row['price']):
                issues.append({
                    'type': 'error',
                    'field': 'price',
                    'message': f"Invalid price format: {row['price']}",
                    'row': row_idx + 2
                })
        
        if 'image_link' in row.index and not pd.isna(row['image_link']):
            if not self._is_valid_url(str(row['image_link'])):
                issues.append({
                    'type': 'warning',
                    'field': 'image_link',
                    'message': f"Invalid image URL format",
                    'row': row_idx + 2
                })
        
        if 'availability' in row.index and not pd.isna(row['availability']):
            if str(row['availability']).lower() not in self.AVAILABILITY_OPTIONS:
                issues.append({
                    'type': 'warning',
                    'field': 'availability',
                    'message': f"Non-standard availability value: {row['availability']}",
                    'row': row_idx + 2
                })
        
        if 'condition' in row.index and not pd.isna(row['condition']):
            if str(row['condition']).lower() not in self.CONDITION_OPTIONS:
                issues.append({
                    'type': 'warning',
                    'field': 'condition',
                    'message': f"Non-standard condition value: {row['condition']}",
                    'row': row_idx + 2
                })
        
        # Check for duplicate IDs
        if 'id' in row.index and not pd.isna(row['id']):
            product_id = str(row['id'])
            if product_id in [r.get('id') for r in self.validation_results.values()]:
                issues.append({
                    'type': 'error',
                    'field': 'id',
                    'message': f"Duplicate product ID: {product_id}",
                    'row': row_idx + 2
                })
        
        return issues
    
    def _is_valid_price(self, price: Any) -> bool:
        """Validate price format."""
        try:
            price_val = float(str(price).replace('$', '').replace(',', ''))
            return price_val >= 0
        except (ValueError, AttributeError):
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        url = str(url).strip()
        return url.startswith(('http://', 'https://')) and len(url) > 10
    
    def _analyze_fields(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze field completeness and quality."""
        analysis = {}
        
        for col in df.columns:
            non_empty = df[col].notna().sum()
            completeness = (non_empty / len(df)) * 100 if len(df) > 0 else 0
            
            analysis[col] = {
                'present': non_empty,
                'missing': len(df) - non_empty,
                'completeness': round(completeness, 2),
                'is_required': col in self.REQUIRED_FIELDS,
                'is_recommended': col in self.RECOMMENDED_FIELDS
            }
        
        return analysis
    
    def _calculate_compliance_score(self, df: pd.DataFrame, report: Dict) -> int:
        """Calculate overall compliance score (0-100)."""
        score = 100
        
        # Deduct for missing required fields
        if report['issues']:
            error_count = len([i for i in report['issues'] if i['type'] == 'error'])
            warning_count = len([i for i in report['issues'] if i['type'] == 'warning'])
            score -= min(50, error_count * 5)
            score -= min(30, warning_count * 2)
        
        # Deduct for low completeness on required fields
        for field, analysis in report['field_analysis'].items():
            if field in self.REQUIRED_FIELDS:
                if analysis['completeness'] < 100:
                    score -= (100 - analysis['completeness']) * 0.3
        
        # Bonus for recommended fields
        recommended_present = sum(
            1 for field in df.columns 
            if field in self.RECOMMENDED_FIELDS
        )
        bonus = (recommended_present / len(self.RECOMMENDED_FIELDS)) * 10
        score += bonus
        
        return max(0, min(100, int(score)))
    
    def _generate_recommendations(self, df: pd.DataFrame, report: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for missing recommended fields
        recommended_fields = set(self.RECOMMENDED_FIELDS.keys())
        present_recommended = set(col for col in df.columns if col in recommended_fields)
        missing_recommended = recommended_fields - present_recommended
        
        if missing_recommended:
            recommendations.append(
                f"Add recommended fields for better feed quality: {', '.join(missing_recommended)}"
            )
        
        # Check for low completeness
        for field, analysis in report['field_analysis'].items():
            if field in self.REQUIRED_FIELDS and analysis['completeness'] < 100:
                recommendations.append(
                    f"Improve completeness of '{field}' (current: {analysis['completeness']}%)"
                )
        
        # Data quality recommendations
        if report['invalid_rows'] > 0:
            invalid_pct = (report['invalid_rows'] / report['total_rows']) * 100
            recommendations.append(
                f"Fix validation issues in {report['invalid_rows']} rows ({invalid_pct:.1f}% of feed)"
            )
        
        if report['compliance_score'] < 70:
            recommendations.append(
                "Consider a complete feed audit to improve overall data quality"
            )
        
        return recommendations


def load_sample_data() -> pd.DataFrame:
    """Load sample product feed data."""
    sample_data = {
        'id': ['001', '002', '003', '004', '005'],
        'title': [
            'Premium Wireless Headphones',
            'USB-C Cable 10ft',
            'Laptop Stand',
            'Mechanical Keyboard',
            'Monitor Light Bar'
        ],
        'description': [
            'High-quality wireless headphones with noise cancellation',
            'Fast charging USB-C cable with durable nylon braiding',
            'Adjustable aluminum laptop stand',
            'RGB mechanical keyboard with hot-swap switches',
            'Auto-dimming monitor light bar'
        ],
        'price': ['149.99', '12.99', '39.99', '89.99', '79.99'],
        'availability': ['in_stock', 'in_stock', 'out_of_stock', 'in_stock', 'in_stock'],
        'image_link': [
            'https://example.com/headphones.jpg',
            'https://example.com/cable.jpg',
            'https://example.com/stand.jpg',
            'https://example.com/keyboard.jpg',
            'https://example.com/lightbar.jpg'
        ],
        'brand': ['TechBrand', 'CableCo', 'StandMaster', 'KeyPro', 'LightTech'],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories'],
        'condition': ['new', 'new', 'new', 'new', 'new']
    }
    return pd.DataFrame(sample_data)


def main():
    """Main Streamlit application."""
    
    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        validation_mode = st.radio(
            "Select Mode",
            ["📤 Single File Upload", "📦 Batch Validation", "📊 Sample Data"],
            help="Choose how to validate your product feed"
        )
        
        st.divider()
        
        st.subheader("About")
        st.info(
            """
            **Product Feed Validator**
            
            Comprehensive validation tool for product feeds with:
            - File upload support (CSV, Excel, JSON)
            - Batch validation processing
            - Compliance scoring
            - Field analysis
            - Actionable recommendations
            """
        )
    
    # Main content
    st.title("📋 Product Feed Validator")
    st.markdown("Validate and optimize your product feeds with comprehensive compliance scoring")
    
    # Initialize session state
    if 'validation_report' not in st.session_state:
        st.session_state.validation_report = None
    if 'uploaded_df' not in st.session_state:
        st.session_state.uploaded_df = None
    
    validator = ProductFeedValidator()
    
    # Mode selection
    if validation_mode == "📤 Single File Upload":
        st.header("Upload Product Feed")
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['csv', 'xlsx', 'json'],
                help="Upload CSV, Excel, or JSON file"
            )
        
        with col2:
            file_format = st.selectbox(
                "File Format",
                ["CSV", "Excel", "JSON"],
                help="Specify the file format"
            )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == 'text/csv':
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.type == 'application/json':
                    df = pd.read_json(uploaded_file)
                else:
                    st.error("Unsupported file format")
                    return
                
                st.session_state.uploaded_df = df
                st.success(f"✓ File loaded successfully ({len(df)} rows, {len(df.columns)} columns)")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                return
        
        if st.session_state.uploaded_df is not None:
            df = st.session_state.uploaded_df
            
            if st.button("🔍 Validate Feed", use_container_width=True, type="primary"):
                with st.spinner("Validating feed..."):
                    st.session_state.validation_report = validator.validate_feed(df)
    
    elif validation_mode == "📦 Batch Validation":
        st.header("Batch Validation")
        
        st.info("Upload multiple files for batch processing")
        
        uploaded_files = st.file_uploader(
            "Choose multiple files",
            type=['csv', 'xlsx', 'json'],
            accept_multiple_files=True,
            help="Upload multiple files for batch validation"
        )
        
        if uploaded_files:
            batch_results = []
            
            for uploaded_file in uploaded_files:
                try:
                    if uploaded_file.type == 'text/csv':
                        df = pd.read_csv(uploaded_file)
                    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                        df = pd.read_excel(uploaded_file)
                    elif uploaded_file.type == 'application/json':
                        df = pd.read_json(uploaded_file)
                    else:
                        continue
                    
                    report = validator.validate_feed(df)
                    batch_results.append({
                        'filename': uploaded_file.name,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'report': report
                    })
                
                except Exception as e:
                    batch_results.append({
                        'filename': uploaded_file.name,
                        'error': str(e)
                    })
            
            if batch_results:
                st.session_state.validation_report = {
                    'batch': True,
                    'results': batch_results
                }
    
    elif validation_mode == "📊 Sample Data":
        st.header("Sample Data Validation")
        
        st.info("Validate with pre-loaded sample data")
        
        df = load_sample_data()
        st.session_state.uploaded_df = df
        
        st.subheader("Sample Data Preview")
        st.dataframe(df, use_container_width=True)
        
        if st.button("🔍 Validate Sample Feed", use_container_width=True, type="primary"):
            with st.spinner("Validating sample feed..."):
                st.session_state.validation_report = validator.validate_feed(df)
    
    # Display validation results
    if st.session_state.validation_report:
        report = st.session_state.validation_report
        
        if isinstance(report, dict) and report.get('batch'):
            st.divider()
            st.header("📊 Batch Validation Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_files = len(report['results'])
            successful_files = sum(1 for r in report['results'] if 'error' not in r)
            failed_files = total_files - successful_files
            avg_score = np.mean([r['report']['compliance_score'] for r in report['results'] if 'error' not in r])
            
            with col1:
                st.metric("Total Files", total_files)
            with col2:
                st.metric("Successful", successful_files, f"{(successful_files/total_files*100):.0f}%")
            with col3:
                st.metric("Failed", failed_files)
            with col4:
                st.metric("Avg Score", f"{avg_score:.0f}/100")
            
            # Detailed results
            st.subheader("Detailed Results")
            for result in report['results']:
                if 'error' in result:
                    st.error(f"❌ {result['filename']}: {result['error']}")
                else:
                    with st.expander(f"📄 {result['filename']}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows", result['rows'])
                        with col2:
                            st.metric("Columns", result['columns'])
                        with col3:
                            st.metric("Score", f"{result['report']['compliance_score']}/100")
                        
                        st.write("**Issues Found:**")
                        if result['report']['issues']:
                            for issue in result['report']['issues'][:5]:
                                st.write(f"- [{issue['type'].upper()}] {issue['field']}: {issue['message']}")
                            if len(result['report']['issues']) > 5:
                                st.write(f"- ... and {len(result['report']['issues']) - 5} more issues")
                        else:
                            st.success("No issues found!")
        
        else:
            st.divider()
            st.header("📊 Validation Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Rows",
                    report['total_rows'],
                    f"{report['valid_rows']} valid"
                )
            
            with col2:
                validity = (report['valid_rows'] / report['total_rows'] * 100) if report['total_rows'] > 0 else 0
                st.metric(
                    "Validity Rate",
                    f"{validity:.1f}%",
                    f"{report['invalid_rows']} invalid"
                )
            
            with col3:
                st.metric(
                    "Issues Found",
                    len(report['issues']),
                    f"{len([i for i in report['issues'] if i['type'] == 'error'])} errors"
                )
            
            with col4:
                score_color = "🟢" if report['compliance_score'] >= 80 else "🟡" if report['compliance_score'] >= 60 else "🔴"
                st.metric(
                    "Compliance Score",
                    f"{score_color} {report['compliance_score']}/100"
                )
            
            # Compliance score gauge
            st.subheader("Compliance Score Breakdown")
            col1, col2 = st.columns([2, 1])
            with col1:
                score = report['compliance_score']
                st.progress(score / 100)
                st.markdown(f"**Overall Score: {score}/100**")
            with col2:
                if score >= 80:
                    st.success("Excellent")
                elif score >= 60:
                    st.warning("Good")
                elif score >= 40:
                    st.error("Fair")
                else:
                    st.error("Poor")
            
            st.divider()
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["Issues", "Field Analysis", "Recommendations", "Data Preview"])
            
            with tab1:
                st.subheader("Validation Issues")
                
                if report['issues']:
                    # Separate issues by type
                    errors = [i for i in report['issues'] if i['type'] == 'error']
                    warnings = [i for i in report['issues'] if i['type'] == 'warning']
                    infos = [i for i in report['issues'] if i['type'] == 'info']
                    
                    if errors:
                        st.subheader("❌ Errors", divider="red")
                        for issue in errors:
                            st.error(
                                f"**Row {issue['row']}** | Field: `{issue['field']}`\n\n"
                                f"{issue['message']}"
                            )
                    
                    if warnings:
                        st.subheader("⚠️ Warnings", divider="orange")
                        for issue in warnings:
                            st.warning(
                                f"**Row {issue['row']}** | Field: `{issue['field']}`\n\n"
                                f"{issue['message']}"
                            )
                    
                    if infos:
                        st.subheader("ℹ️ Info", divider="blue")
                        for issue in infos:
                            st.info(
                                f"**Row {issue['row']}** | Field: `{issue['field']}`\n\n"
                                f"{issue['message']}"
                            )
                else:
                    st.success("✓ No issues found! Your feed is valid.")
            
            with tab2:
                st.subheader("Field Analysis")
                
                analysis_df = pd.DataFrame(report['field_analysis']).T
                analysis_df = analysis_df.reset_index().rename(columns={'index': 'field'})
                
                # Color code by required/recommended
                def format_field_name(field):
                    if field in validator.REQUIRED_FIELDS:
                        return f"⭐ {field}"
                    elif field in validator.RECOMMENDED_FIELDS:
                        return f"✨ {field}"
                    else:
                        return f"📌 {field}"
                
                analysis_df['field'] = analysis_df['field'].apply(format_field_name)
                
                st.dataframe(
                    analysis_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.caption("⭐ Required | ✨ Recommended | 📌 Optional")
            
            with tab3:
                st.subheader("Recommendations")
                
                if report['recommendations']:
                    for i, rec in enumerate(report['recommendations'], 1):
                        st.info(f"{i}. {rec}")
                else:
                    st.success("✓ No specific recommendations. Your feed looks great!")
            
            with tab4:
                st.subheader("Data Preview")
                
                if st.session_state.uploaded_df is not None:
                    df = st.session_state.uploaded_df
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        preview_rows = st.slider("Rows to display", 1, len(df), min(10, len(df)))
                    
                    st.dataframe(
                        df.head(preview_rows),
                        use_container_width=True
                    )
                    
                    # Download options
                    st.subheader("Download Options")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv_data,
                            file_name=f"validated_feed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        json_data = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_data,
                            file_name=f"validated_feed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col3:
                        report_json = json.dumps(report, indent=2, default=str)
                        st.download_button(
                            label="📥 Download Report",
                            data=report_json,
                            file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.85em;'>
        <p>Product Feed Validator | Version 1.0 | Last updated: 2026-01-06</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
