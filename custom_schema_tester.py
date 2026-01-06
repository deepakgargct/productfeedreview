import streamlit as st
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Custom Schema Tester",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .validation-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .validation-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .validation-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .validation-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


class SchemaValidator:
    """Validates product schema markup and provides recommendations."""
    
    # Required fields for product schema
    REQUIRED_FIELDS = {
        '@context': 'Schema.org context',
        '@type': 'Schema type',
        'name': 'Product name',
        'description': 'Product description',
        'image': 'Product image URL',
        'offers': 'Product offers/pricing'
    }
    
    # Recommended fields
    RECOMMENDED_FIELDS = {
        'sku': 'Stock Keeping Unit',
        'brand': 'Brand information',
        'aggregateRating': 'Aggregate ratings',
        'review': 'Product reviews',
        'availabilityStarts': 'Availability start date',
        'price': 'Price information',
        'priceCurrency': 'Currency code'
    }
    
    # Field-specific validators
    FIELD_VALIDATORS = {
        'url': lambda x: isinstance(x, str) and (x.startswith('http://') or x.startswith('https://')),
        'price': lambda x: str(x).replace('.', '').replace(',', '').isdigit(),
        'ratingValue': lambda x: 0 <= float(x) <= 5,
        'bestRating': lambda x: float(x) >= 1,
        'worstRating': lambda x: float(x) >= 0,
        'reviewCount': lambda x: int(x) >= 0,
    }
    
    def __init__(self, schema_data: Dict) -> None:
        self.schema = schema_data
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.suggestions: List[Dict] = []
        self.enhancements: List[Dict] = []
    
    def validate(self) -> Tuple[bool, Dict]:
        """Perform complete validation analysis."""
        self._validate_structure()
        self._validate_required_fields()
        self._validate_field_types()
        self._validate_field_values()
        self._generate_suggestions()
        self._generate_enhancements()
        
        return len(self.errors) == 0, self._compile_results()
    
    def _validate_structure(self) -> None:
        """Validate JSON structure."""
        if not isinstance(self.schema, dict):
            self.errors.append({
                'field': 'Structure',
                'message': 'Schema must be a JSON object',
                'severity': 'Critical'
            })
    
    def _validate_required_fields(self) -> None:
        """Check for required fields."""
        for field, description in self.REQUIRED_FIELDS.items():
            if field not in self.schema:
                self.errors.append({
                    'field': field,
                    'message': f'Missing required field: {description}',
                    'severity': 'Error'
                })
            elif not self.schema[field]:
                self.errors.append({
                    'field': field,
                    'message': f'Field "{field}" is empty',
                    'severity': 'Error'
                })
    
    def _validate_field_types(self) -> None:
        """Validate data types of fields."""
        type_rules = {
            'name': str,
            'description': str,
            'sku': str,
            'brand': (str, dict),
            'image': (str, list),
            'offers': (dict, list),
            'price': (str, int, float),
            'aggregateRating': dict,
            'review': (dict, list),
        }
        
        for field, expected_type in type_rules.items():
            if field in self.schema:
                if not isinstance(self.schema[field], expected_type):
                    self.warnings.append({
                        'field': field,
                        'message': f'Expected type {expected_type}, got {type(self.schema[field]).__name__}',
                        'severity': 'Warning'
                    })
    
    def _validate_field_values(self) -> None:
        """Validate specific field values."""
        # Validate URLs
        for url_field in ['image', 'url']:
            if url_field in self.schema:
                value = self.schema[url_field]
                if isinstance(value, str):
                    if not self.FIELD_VALIDATORS['url'](value):
                        self.warnings.append({
                            'field': url_field,
                            'message': f'{url_field} must be a valid URL',
                            'severity': 'Warning'
                        })
        
        # Validate rating values
        if 'aggregateRating' in self.schema:
            rating = self.schema['aggregateRating']
            if isinstance(rating, dict):
                if 'ratingValue' in rating:
                    try:
                        if not (0 <= float(rating['ratingValue']) <= 5):
                            self.errors.append({
                                'field': 'aggregateRating.ratingValue',
                                'message': 'Rating value must be between 0 and 5',
                                'severity': 'Error'
                            })
                    except (ValueError, TypeError):
                        self.errors.append({
                            'field': 'aggregateRating.ratingValue',
                            'message': 'Rating value must be numeric',
                            'severity': 'Error'
                        })
                
                if 'reviewCount' in rating:
                    try:
                        if int(rating['reviewCount']) < 0:
                            self.errors.append({
                                'field': 'aggregateRating.reviewCount',
                                'message': 'Review count cannot be negative',
                                'severity': 'Error'
                            })
                    except (ValueError, TypeError):
                        self.errors.append({
                            'field': 'aggregateRating.reviewCount',
                            'message': 'Review count must be numeric',
                            'severity': 'Error'
                        })
        
        # Validate offers
        if 'offers' in self.schema:
            offers = self.schema['offers']
            if isinstance(offers, dict):
                if 'price' in offers:
                    try:
                        float(str(offers['price']).replace(',', ''))
                    except ValueError:
                        self.errors.append({
                            'field': 'offers.price',
                            'message': 'Price must be numeric',
                            'severity': 'Error'
                        })
    
    def _generate_suggestions(self) -> None:
        """Generate suggestions for missing recommended fields."""
        for field, description in self.RECOMMENDED_FIELDS.items():
            if field not in self.schema:
                self.suggestions.append({
                    'field': field,
                    'message': f'Consider adding {description}',
                    'priority': 'Medium'
                })
    
    def _generate_enhancements(self) -> None:
        """Generate enhancement recommendations."""
        enhancements = []
        
        # Check for comprehensive offer details
        if 'offers' in self.schema:
            offers = self.schema['offers']
            if isinstance(offers, dict):
                if 'availability' not in offers:
                    enhancements.append({
                        'category': 'Offers',
                        'recommendation': 'Add availability status (InStock, OutOfStock, PreOrder, etc.)',
                        'impact': 'Improves e-commerce visibility'
                    })
        
        # Check for rich ratings
        if 'aggregateRating' not in self.schema:
            enhancements.append({
                'category': 'Credibility',
                'recommendation': 'Add aggregateRating with ratingValue and reviewCount',
                'impact': 'Increases user trust and CTR'
            })
        
        # Check for multiple images
        if 'image' in self.schema:
            image = self.schema['image']
            if isinstance(image, str):
                enhancements.append({
                    'category': 'Visual Content',
                    'recommendation': 'Use array of images for better rich snippets',
                    'impact': 'Allows multiple product images in search results'
                })
        
        # Check for structured reviews
        if 'review' not in self.schema and 'aggregateRating' in self.schema:
            enhancements.append({
                'category': 'Social Proof',
                'recommendation': 'Add individual review objects with author and datePublished',
                'impact': 'Enhances credibility and engagement'
            })
        
        # Check for product dimensions/weight
        if not any(field in self.schema for field in ['weight', 'height', 'width', 'depth']):
            enhancements.append({
                'category': 'Product Details',
                'recommendation': 'Add physical dimensions or weight for better product information',
                'impact': 'Helps users make informed purchasing decisions'
            })
        
        # Check for inventory tracking
        if 'offers' in self.schema:
            offers = self.schema['offers']
            if isinstance(offers, dict) and 'inventoryLevel' not in offers:
                enhancements.append({
                    'category': 'Inventory',
                    'recommendation': 'Track inventory levels for dynamic pricing strategies',
                    'impact': 'Enables inventory-based optimizations'
                })
        
        self.enhancements = enhancements
    
    def _compile_results(self) -> Dict:
        """Compile validation results."""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'enhancements': self.enhancements,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_suggestions': len(self.suggestions),
                'total_enhancements': len(self.enhancements),
                'timestamp': datetime.now().isoformat()
            }
        }


def render_validation_results(results: Dict) -> None:
    """Render validation results in the UI."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Errors", results['summary']['total_errors'], 
                 delta=-results['summary']['total_errors'] if results['summary']['total_errors'] > 0 else None,
                 delta_color="inverse")
    with col2:
        st.metric("Warnings", results['summary']['total_warnings'])
    with col3:
        st.metric("Suggestions", results['summary']['total_suggestions'])
    with col4:
        st.metric("Enhancements", results['summary']['total_enhancements'])
    
    st.divider()
    
    # Errors
    if results['errors']:
        st.markdown("### ❌ Errors")
        for error in results['errors']:
            st.markdown(f"""
            <div class="validation-error">
                <strong>{error['field']}</strong> - {error['message']}
            </div>
            """, unsafe_allow_html=True)
    
    # Warnings
    if results['warnings']:
        st.markdown("### ⚠️ Warnings")
        for warning in results['warnings']:
            st.markdown(f"""
            <div class="validation-warning">
                <strong>{warning['field']}</strong> - {warning['message']}
            </div>
            """, unsafe_allow_html=True)
    
    # Suggestions
    if results['suggestions']:
        st.markdown("### 💡 Suggestions")
        for suggestion in results['suggestions']:
            st.markdown(f"""
            <div class="validation-info">
                <strong>{suggestion['field']}</strong> - {suggestion['message']}
            </div>
            """, unsafe_allow_html=True)
    
    if not results['errors'] and not results['warnings'] and not results['suggestions']:
        st.markdown("""
        <div class="validation-success">
            <strong>✓ Schema looks good!</strong> No critical issues or warnings found.
        </div>
        """, unsafe_allow_html=True)


def render_enhancements(enhancements: List[Dict]) -> None:
    """Render enhancement recommendations."""
    if enhancements:
        st.markdown("### 🚀 Enhancement Recommendations")
        
        for enhancement in enhancements:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                **{enhancement['category']}**
                
                {enhancement['recommendation']}
                """)
            with col2:
                st.info(f"💫 {enhancement['impact']}")


def render_sample_schema() -> None:
    """Render sample schema template."""
    sample_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Premium Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
        "image": [
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg"
        ],
        "brand": {
            "@type": "Brand",
            "name": "TechBrand"
        },
        "sku": "TH-001-BLK",
        "offers": {
            "@type": "Offer",
            "url": "https://example.com/wireless-headphones",
            "priceCurrency": "USD",
            "price": "199.99",
            "availability": "https://schema.org/InStock",
            "inventoryLevel": 100
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.5",
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": "248",
            "reviewCount": "48"
        },
        "review": [
            {
                "@type": "Review",
                "author": "John Doe",
                "datePublished": "2025-12-15",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5",
                    "worstRating": "1"
                },
                "reviewBody": "Excellent product with great sound quality!"
            }
        ]
    }
    
    st.markdown("#### Sample Product Schema")
    st.json(sample_schema)
    
    if st.button("📋 Copy Sample to Input", key="copy_sample"):
        st.session_state.schema_input = json.dumps(sample_schema, indent=2)
        st.rerun()


# Initialize session state
if 'schema_input' not in st.session_state:
    st.session_state.schema_input = ''
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None


# Main UI
st.title("🧪 Custom Schema Tester")
st.markdown("""
Test and validate your custom product schema markup with detailed analysis, 
validation errors, and actionable enhancement recommendations.
""")

st.divider()

# Sidebar for options
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    validation_mode = st.radio(
        "Validation Mode",
        ["Validate JSON", "Edit & Validate", "View Samples"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📚 Quick Help")
    st.info("""
    **Getting Started:**
    1. Paste your product schema JSON
    2. Click "Validate Schema"
    3. Review results and recommendations
    4. Implement suggested enhancements
    """)


# Main content tabs
tab1, tab2, tab3 = st.tabs(["📊 Validator", "📋 Schema Editor", "📖 Templates"])

with tab1:
    st.markdown("### Paste Your Schema")
    
    schema_input = st.text_area(
        "Schema JSON Input",
        value=st.session_state.schema_input,
        height=300,
        placeholder='{\n  "@context": "https://schema.org",\n  "@type": "Product",\n  ...\n}',
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("✓ Validate Schema", type="primary", use_container_width=True):
            if schema_input.strip():
                try:
                    schema_data = json.loads(schema_input)
                    validator = SchemaValidator(schema_data)
                    is_valid, results = validator.validate()
                    st.session_state.validation_results = results
                    st.success("Validation complete!")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")
            else:
                st.warning("Please enter a schema to validate")
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.schema_input = ''
            st.session_state.validation_results = None
            st.rerun()
    
    # Display results
    if st.session_state.validation_results:
        st.divider()
        render_validation_results(st.session_state.validation_results)
        
        st.divider()
        render_enhancements(st.session_state.validation_results['enhancements'])
        
        # Export results
        st.divider()
        st.markdown("### 📥 Export Results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download as JSON",
                data=json.dumps(st.session_state.validation_results, indent=2),
                file_name=f"schema_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            csv_data = pd.DataFrame(st.session_state.validation_results['errors'] + 
                                   st.session_state.validation_results['warnings'])
            if not csv_data.empty:
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_data.to_csv(index=False),
                    file_name=f"schema_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )


with tab2:
    st.markdown("### Edit Your Schema")
    
    editor_input = st.text_area(
        "Edit Schema JSON",
        value=st.session_state.schema_input,
        height=400,
        placeholder='{\n  "@context": "https://schema.org",\n  "@type": "Product",\n  ...\n}',
        label_visibility="collapsed"
    )
    
    if editor_input != st.session_state.schema_input:
        st.session_state.schema_input = editor_input
    
    # Visual editor options
    st.markdown("#### Field Templates")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Offers"):
            st.info("""
            ```json
            "offers": {
              "@type": "Offer",
              "price": "199.99",
              "priceCurrency": "USD",
              "availability": "https://schema.org/InStock"
            }
            ```
            """)
    
    with col2:
        if st.button("⭐ Add Rating"):
            st.info("""
            ```json
            "aggregateRating": {
              "@type": "AggregateRating",
              "ratingValue": "4.5",
              "ratingCount": "100"
            }
            ```
            """)
    
    with col3:
        if st.button("👤 Add Review"):
            st.info("""
            ```json
            "review": {
              "@type": "Review",
              "author": "User Name",
              "reviewRating": {"ratingValue": "5"}
            }
            ```
            """)


with tab3:
    st.markdown("### Schema Templates")
    
    template_choice = st.selectbox(
        "Select a template",
        ["Basic Product", "E-commerce Product", "Product with Reviews", "Local Business Product"],
        label_visibility="collapsed"
    )
    
    if template_choice == "Basic Product":
        render_sample_schema()
    
    elif template_choice == "E-commerce Product":
        sample = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Product Name",
            "description": "Detailed product description",
            "image": ["https://example.com/image1.jpg"],
            "sku": "SKU-001",
            "offers": {
                "@type": "Offer",
                "url": "https://example.com/product",
                "priceCurrency": "USD",
                "price": "99.99",
                "availability": "https://schema.org/InStock",
                "inventoryLevel": 50,
                "seller": {
                    "@type": "Organization",
                    "name": "Store Name"
                }
            }
        }
        st.json(sample)
        if st.button("📋 Copy E-commerce Template", key="copy_ecom"):
            st.session_state.schema_input = json.dumps(sample, indent=2)
            st.rerun()
    
    elif template_choice == "Product with Reviews":
        sample = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Premium Product",
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.5",
                "ratingCount": "1000"
            },
            "review": [
                {
                    "@type": "Review",
                    "author": "Reviewer Name",
                    "datePublished": "2025-01-01",
                    "reviewRating": {"ratingValue": "5"},
                    "reviewBody": "Great product!"
                }
            ]
        }
        st.json(sample)
        if st.button("📋 Copy Reviews Template", key="copy_reviews"):
            st.session_state.schema_input = json.dumps(sample, indent=2)
            st.rerun()
    
    elif template_choice == "Local Business Product":
        sample = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Local Product",
            "seller": {
                "@type": "LocalBusiness",
                "name": "Business Name",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "123 Main St",
                    "addressLocality": "City",
                    "addressRegion": "State",
                    "postalCode": "12345"
                }
            }
        }
        st.json(sample)
        if st.button("📋 Copy Local Business Template", key="copy_local"):
            st.session_state.schema_input = json.dumps(sample, indent=2)
            st.rerun()


# Footer
st.divider()
st.markdown("""
---
**Custom Schema Tester** | Validate and enhance your product schema markup
| [Schema.org Reference](https://schema.org/Product) | [Google Rich Results Test](https://search.google.com/test/rich-results)
""")
