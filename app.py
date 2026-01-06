import streamlit as st
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Product Schema Generator",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .success-box {
            padding: 1rem;
            background-color: #d4edda;
            border-radius: 0.5rem;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }
        .error-box {
            padding: 1rem;
            background-color: #f8d7da;
            border-radius: 0.5rem;
            border-left: 4px solid #dc3545;
            margin: 1rem 0;
        }
        .info-box {
            padding: 1rem;
            background-color: #d1ecf1;
            border-radius: 0.5rem;
            border-left: 4px solid #17a2b8;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

class SchemaExtractor:
    """Extract structured data and schemas from web pages"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None
    
    def extract_json_ld(self, html: str, url: str) -> List[Dict]:
        """Extract JSON-LD structured data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            schemas = []
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    schemas.append(data)
                except json.JSONDecodeError:
                    continue
            
            return schemas
        except Exception as e:
            logger.error(f"Error extracting JSON-LD: {str(e)}")
            return []
    
    def extract_og_tags(self, html: str) -> Dict[str, str]:
        """Extract Open Graph meta tags"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            og_data = {}
            
            og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
            for tag in og_tags:
                property_name = tag.get('property', '').replace('og:', '')
                content = tag.get('content', '')
                og_data[property_name] = content
            
            return og_data
        except Exception as e:
            logger.error(f"Error extracting OG tags: {str(e)}")
            return {}
    
    def extract_meta_tags(self, html: str) -> Dict[str, str]:
        """Extract standard meta tags"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            meta_data = {}
            
            meta_tags = soup.find_all('meta', attrs={'name': True})
            for tag in meta_tags:
                name = tag.get('name', '').lower()
                content = tag.get('content', '')
                if name and content:
                    meta_data[name] = content
            
            return meta_data
        except Exception as e:
            logger.error(f"Error extracting meta tags: {str(e)}")
            return {}
    
    def extract_product_data(self, html: str, url: str) -> Dict:
        """Extract product-specific data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            product_data = {}
            
            # Extract title
            title = soup.find('title')
            if title:
                product_data['title'] = title.string
            
            # Extract price (common patterns)
            price_patterns = [
                soup.find(class_=re.compile(r'price', re.I)),
                soup.find(id=re.compile(r'price', re.I)),
                soup.find('span', class_=re.compile(r'price', re.I))
            ]
            for elem in price_patterns:
                if elem:
                    product_data['price'] = elem.get_text(strip=True)
                    break
            
            # Extract rating/reviews
            rating_patterns = [
                soup.find(class_=re.compile(r'rating|review', re.I)),
                soup.find(id=re.compile(r'rating|review', re.I))
            ]
            for elem in rating_patterns:
                if elem:
                    product_data['rating'] = elem.get_text(strip=True)
                    break
            
            # Extract images
            images = []
            img_tags = soup.find_all('img', limit=5)
            for img in img_tags:
                src = img.get('src', '')
                if src and not src.endswith(('.gif', '.svg')):
                    images.append(urljoin(url, src))
            if images:
                product_data['images'] = images
            
            return product_data
        except Exception as e:
            logger.error(f"Error extracting product data: {str(e)}")
            return {}
    
    def validate_schema(self, schema: Dict) -> Tuple[bool, List[str]]:
        """Validate schema structure"""
        errors = []
        
        if not isinstance(schema, dict):
            errors.append("Schema must be a dictionary")
            return False, errors
        
        if '@type' not in schema:
            errors.append("Missing required '@type' field")
        
        if '@context' not in schema:
            errors.append("Missing recommended '@context' field")
        
        return len(errors) == 0, errors
    
    def create_product_schema(self, data: Dict) -> Dict:
        """Create a valid Product schema.org schema"""
        schema = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": data.get('name', 'Product Name'),
            "description": data.get('description', ''),
            "url": data.get('url', ''),
            "image": data.get('image', []),
            "brand": {
                "@type": "Brand",
                "name": data.get('brand', '')
            },
            "offers": {
                "@type": "Offer",
                "price": data.get('price', '0'),
                "priceCurrency": data.get('currency', 'USD'),
                "availability": data.get('availability', 'https://schema.org/InStock'),
                "url": data.get('url', '')
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": data.get('rating_value', '0'),
                "reviewCount": data.get('review_count', '0')
            }
        }
        return schema

class SchemaValidator:
    """Validate and test schemas"""
    
    @staticmethod
    def validate_json_structure(json_str: str) -> Tuple[bool, str, Optional[Dict]]:
        """Validate JSON structure"""
        try:
            data = json.loads(json_str)
            return True, "Valid JSON", data
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}", None
    
    @staticmethod
    def validate_schema_type(schema: Dict) -> Tuple[bool, List[str]]:
        """Validate schema type and required fields"""
        errors = []
        
        schema_type = schema.get('@type', '')
        
        # Product schema validation
        if schema_type == 'Product':
            required_fields = ['name', 'offers']
            for field in required_fields:
                if field not in schema:
                    errors.append(f"Missing required field for Product: {field}")
            
            if 'offers' in schema:
                if not isinstance(schema['offers'], dict):
                    errors.append("'offers' must be an object")
                elif 'price' not in schema['offers']:
                    errors.append("'offers' must contain 'price'")
        
        # Organization schema validation
        elif schema_type == 'Organization':
            if 'name' not in schema:
                errors.append("Organization requires 'name' field")
        
        # LocalBusiness schema validation
        elif schema_type == 'LocalBusiness':
            required_fields = ['name', 'address']
            for field in required_fields:
                if field not in schema:
                    errors.append(f"Missing required field for LocalBusiness: {field}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def test_schema_compliance(schema: Dict) -> Dict:
        """Test schema compliance"""
        results = {
            'has_context': '@context' in schema,
            'has_type': '@type' in schema,
            'type': schema.get('@type', 'Unknown'),
            'field_count': len(schema),
            'nested_objects': sum(1 for v in schema.values() if isinstance(v, dict)),
            'arrays': sum(1 for v in schema.values() if isinstance(v, list))
        }
        return results

def main():
    """Main application"""
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    mode = st.sidebar.radio(
        "Select Mode",
        ["📥 URL Extraction", "✏️ Manual Schema Creation", "🧪 Schema Testing", "📊 Batch Processing"]
    )
    
    st.markdown("""
        <div class="header">
            <h1>🏷️ Product Schema Generator</h1>
            <p>Extract, create, and validate structured data schemas</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'schemas' not in st.session_state:
        st.session_state.schemas = []
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = {}
    
    # Mode: URL Extraction
    if mode == "📥 URL Extraction":
        st.header("Extract Schemas from URLs")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            url = st.text_input(
                "Enter URL",
                placeholder="https://example.com/product",
                help="Full URL including https://"
            )
        with col2:
            extract_btn = st.button("🔍 Extract", use_container_width=True)
        
        if extract_btn and url:
            if not url.startswith(('http://', 'https://')):
                st.error("❌ URL must start with http:// or https://")
            else:
                with st.spinner("Extracting schemas..."):
                    extractor = SchemaExtractor()
                    html = extractor.fetch_page(url)
                    
                    if html:
                        st.markdown('<div class="success-box">✅ Page fetched successfully</div>', unsafe_allow_html=True)
                        
                        # Create tabs for different extraction types
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "JSON-LD Schemas",
                            "Open Graph Tags",
                            "Meta Tags",
                            "Product Data"
                        ])
                        
                        with tab1:
                            st.subheader("JSON-LD Structured Data")
                            json_ld = extractor.extract_json_ld(html, url)
                            
                            if json_ld:
                                for i, schema in enumerate(json_ld):
                                    st.json(schema)
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button(f"✅ Save Schema {i+1}", key=f"save_{i}"):
                                            st.session_state.schemas.append(schema)
                                            st.success(f"Schema {i+1} saved!")
                                    with col2:
                                        if st.button(f"📋 Copy JSON {i+1}", key=f"copy_{i}"):
                                            st.code(json.dumps(schema, indent=2))
                            else:
                                st.info("ℹ️ No JSON-LD schemas found on this page")
                        
                        with tab2:
                            st.subheader("Open Graph Metadata")
                            og_data = extractor.extract_og_tags(html)
                            
                            if og_data:
                                df_og = pd.DataFrame(list(og_data.items()), columns=['Property', 'Content'])
                                st.dataframe(df_og, use_container_width=True)
                            else:
                                st.info("ℹ️ No Open Graph tags found")
                        
                        with tab3:
                            st.subheader("Meta Tags")
                            meta_data = extractor.extract_meta_tags(html)
                            
                            if meta_data:
                                df_meta = pd.DataFrame(list(meta_data.items()), columns=['Name', 'Content'])
                                st.dataframe(df_meta, use_container_width=True)
                            else:
                                st.info("ℹ️ No meta tags found")
                        
                        with tab4:
                            st.subheader("Extracted Product Data")
                            product_data = extractor.extract_product_data(html, url)
                            
                            if product_data:
                                st.json(product_data)
                            else:
                                st.info("ℹ️ No product-specific data found")
                    else:
                        st.markdown('<div class="error-box">❌ Failed to fetch the page. Check URL and try again.</div>', unsafe_allow_html=True)
    
    # Mode: Manual Schema Creation
    elif mode == "✏️ Manual Schema Creation":
        st.header("Create Custom Schema")
        
        col1, col2 = st.columns(2)
        with col1:
            schema_type = st.selectbox(
                "Schema Type",
                ["Product", "Organization", "LocalBusiness", "Article", "BlogPosting", "Custom"]
            )
        with col2:
            st.write("")
        
        schema_data = {}
        
        if schema_type == "Product":
            col1, col2 = st.columns(2)
            with col1:
                schema_data['name'] = st.text_input("Product Name *")
                schema_data['description'] = st.text_area("Description")
                schema_data['brand'] = st.text_input("Brand Name")
            with col2:
                schema_data['url'] = st.text_input("Product URL")
                schema_data['price'] = st.number_input("Price", min_value=0.0, step=0.01)
                schema_data['currency'] = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR"])
            
            col1, col2 = st.columns(2)
            with col1:
                schema_data['rating_value'] = st.slider("Rating", 0.0, 5.0, 4.5)
                schema_data['review_count'] = st.number_input("Review Count", min_value=0)
            with col2:
                schema_data['image'] = st.text_area("Image URLs (one per line)").split('\n') if st.text_area("Image URLs (one per line)", key="img") else []
        
        elif schema_type == "Organization":
            col1, col2 = st.columns(2)
            with col1:
                schema_data['name'] = st.text_input("Organization Name *")
                schema_data['url'] = st.text_input("Website URL")
                schema_data['email'] = st.text_input("Email")
            with col2:
                schema_data['telephone'] = st.text_input("Telephone")
                schema_data['location'] = st.text_input("Location")
        
        elif schema_type == "LocalBusiness":
            col1, col2 = st.columns(2)
            with col1:
                schema_data['name'] = st.text_input("Business Name *")
                schema_data['address'] = st.text_input("Address *")
                schema_data['telephone'] = st.text_input("Telephone")
            with col2:
                schema_data['email'] = st.text_input("Email")
                schema_data['latitude'] = st.number_input("Latitude")
                schema_data['longitude'] = st.number_input("Longitude")
        
        else:
            # Custom schema with JSON editor
            schema_json = st.text_area(
                "Enter Schema JSON",
                value='{"@context": "https://schema.org/", "@type": "CustomType"}',
                height=300
            )
        
        if st.button("✅ Create Schema", use_container_width=True):
            if schema_type == "Custom":
                validator = SchemaValidator()
                is_valid, msg, parsed = validator.validate_json_structure(schema_json)
                if is_valid:
                    schema_data = parsed
                else:
                    st.error(f"Invalid JSON: {msg}")
                    return
            else:
                extractor = SchemaExtractor()
                schema_data = extractor.create_product_schema(schema_data)
            
            st.session_state.schemas.append(schema_data)
            st.success("✅ Schema created and saved!")
            st.json(schema_data)
    
    # Mode: Schema Testing
    elif mode == "🧪 Schema Testing":
        st.header("Test and Validate Schemas")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Custom Schema Input")
            schema_input = st.text_area(
                "Paste Schema JSON",
                height=300,
                placeholder='{\n  "@context": "https://schema.org/",\n  "@type": "Product"\n}'
            )
        
        with col2:
            st.subheader("Validation Results")
            
            if schema_input:
                validator = SchemaValidator()
                is_valid, msg, parsed_schema = validator.validate_json_structure(schema_input)
                
                if is_valid:
                    st.markdown('<div class="success-box">✅ Valid JSON Structure</div>', unsafe_allow_html=True)
                    
                    # Type validation
                    is_type_valid, type_errors = validator.validate_schema_type(parsed_schema)
                    if is_type_valid:
                        st.markdown('<div class="success-box">✅ Schema Type Valid</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">⚠️ Schema Type Errors</div>', unsafe_allow_html=True)
                        for error in type_errors:
                            st.write(f"• {error}")
                    
                    # Compliance test
                    compliance = validator.test_schema_compliance(parsed_schema)
                    st.subheader("Compliance Report")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Schema Type", compliance['type'])
                        st.metric("Total Fields", compliance['field_count'])
                    with col2:
                        st.metric("Nested Objects", compliance['nested_objects'])
                        st.metric("Arrays", compliance['arrays'])
                    
                    # Detailed view
                    st.subheader("Schema Details")
                    st.json(parsed_schema)
                    
                    # Export options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("💾 Save Schema", use_container_width=True):
                            st.session_state.schemas.append(parsed_schema)
                            st.success("Schema saved!")
                    with col2:
                        json_str = json.dumps(parsed_schema, indent=2)
                        st.download_button(
                            "📥 Download JSON",
                            data=json_str,
                            file_name="schema.json",
                            mime="application/json"
                        )
                    with col3:
                        html_str = f"<script type='application/ld+json'>\n{json_str}\n</script>"
                        st.download_button(
                            "🌐 Download HTML",
                            data=html_str,
                            file_name="schema.html",
                            mime="text/html"
                        )
                else:
                    st.markdown(f'<div class="error-box">❌ {msg}</div>', unsafe_allow_html=True)
    
    # Mode: Batch Processing
    elif mode == "📊 Batch Processing":
        st.header("Batch Process Schemas")
        
        tab1, tab2 = st.tabs(["Upload CSV", "Manage Schemas"])
        
        with tab1:
            st.subheader("Upload Product Data")
            uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.write("📊 Preview:")
                    st.dataframe(df.head())
                    
                    if st.button("🔄 Generate Schemas from CSV"):
                        extractor = SchemaExtractor()
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df.iterrows():
                            schema_data = row.to_dict()
                            schema = extractor.create_product_schema(schema_data)
                            st.session_state.schemas.append(schema)
                            
                            progress = (idx + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.text(f"Processed {idx + 1}/{len(df)} rows")
                        
                        st.success(f"✅ Generated {len(df)} schemas!")
                
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
        
        with tab2:
            st.subheader("Saved Schemas")
            
            if st.session_state.schemas:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Schemas", len(st.session_state.schemas))
                
                for i, schema in enumerate(st.session_state.schemas):
                    with st.expander(f"Schema {i+1}: {schema.get('@type', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.json(schema)
                        with col2:
                            json_str = json.dumps(schema, indent=2)
                            st.download_button(
                                "📥 Download",
                                data=json_str,
                                file_name=f"schema_{i+1}.json",
                                mime="application/json",
                                key=f"download_{i}"
                            )
                
                # Export all
                if st.button("📦 Export All Schemas"):
                    all_schemas = json.dumps(st.session_state.schemas, indent=2)
                    st.download_button(
                        "Download All",
                        data=all_schemas,
                        file_name="all_schemas.json",
                        mime="application/json"
                    )
                
                # Clear all
                if st.button("🗑️ Clear All Schemas"):
                    st.session_state.schemas = []
                    st.rerun()
            else:
                st.info("ℹ️ No schemas saved yet. Create or extract schemas to see them here.")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: gray; margin-top: 2rem;">
            <p>Product Schema Generator v1.0 | Created on 2026-01-06</p>
            <p>Supports schema.org structured data for SEO optimization</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
