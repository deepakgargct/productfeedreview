import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import re

st.set_page_config(
    page_title="Product Schema Generator",
    page_icon="🛍️",
    layout="wide"
)

def extract_product_data(html_content, url):
    """Extract product data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize product dictionary
    product = {
        'enable_search': 'true',
        'enable_checkout': 'true',
        'id': '',
        'title': '',
        'description': '',
        'link': url,
        'condition': 'new',
        'brand': '',
        'image_link': '',
        'price': '',
        'availability': 'in_stock'
    }
    
    # Try to find existing JSON-LD schema
    existing_schema = None
    json_ld_script = soup.find('script', {'type': 'application/ld+json'})
    if json_ld_script:
        try:
            existing_schema = json.loads(json_ld_script.string)
        except:
            pass
    
    # Extract ID/SKU
    if existing_schema and 'sku' in existing_schema:
        product['id'] = existing_schema['sku']
    else:
        sku_elem = soup.find(attrs={'itemprop': 'sku'})
        if sku_elem:
            product['id'] = sku_elem.get_text(strip=True) or sku_elem.get('content', '')
        else:
            product['id'] = f"PROD{int(datetime.now().timestamp())}"
    
    # Extract Title
    if existing_schema and 'name' in existing_schema:
        product['title'] = existing_schema['name']
    else:
        h1 = soup.find('h1')
        if h1:
            product['title'] = h1.get_text(strip=True)
        else:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                product['title'] = og_title.get('content', '')
    
    # Extract Description
    if existing_schema and 'description' in existing_schema:
        product['description'] = existing_schema['description']
    else:
        desc_elem = soup.find(attrs={'itemprop': 'description'})
        if desc_elem:
            product['description'] = desc_elem.get_text(strip=True)
        else:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                product['description'] = meta_desc.get('content', '')
            else:
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    product['description'] = og_desc.get('content', '')
    
    # Extract Brand
    if existing_schema and 'brand' in existing_schema:
        brand = existing_schema['brand']
        product['brand'] = brand['name'] if isinstance(brand, dict) else brand
    else:
        brand_elem = soup.find(attrs={'itemprop': 'brand'})
        if brand_elem:
            product['brand'] = brand_elem.get_text(strip=True)
    
    # Extract Image
    if existing_schema and 'image' in existing_schema:
        image = existing_schema['image']
        product['image_link'] = image[0] if isinstance(image, list) else image
    else:
        og_image = soup.find('meta', property='og:image')
        if og_image:
            product['image_link'] = og_image.get('content', '')
        else:
            img_elem = soup.find('img', attrs={'itemprop': 'image'})
            if img_elem:
                product['image_link'] = img_elem.get('src', '')
    
    # Extract Price
    price_value = ''
    currency = 'USD'
    
    if existing_schema and 'offers' in existing_schema:
        offers = existing_schema['offers']
        offer = offers[0] if isinstance(offers, list) else offers
        price_value = str(offer.get('price', ''))
        currency = offer.get('priceCurrency', 'USD')
        product['price'] = f"{price_value} {currency}"
        
        # Extract availability
        avail = offer.get('availability', '').lower()
        if 'instock' in avail:
            product['availability'] = 'in_stock'
        elif 'outofstock' in avail:
            product['availability'] = 'out_of_stock'
        elif 'preorder' in avail:
            product['availability'] = 'preorder'
    else:
        price_elem = soup.find(attrs={'itemprop': 'price'})
        if not price_elem:
            price_elem = soup.find(class_='price')
        
        if price_elem:
            price_text = price_elem.get_text() or price_elem.get('content', '')
            price_match = re.search(r'[\d,.]+', price_text)
            currency_match = re.search(r'[A-Z]{3}', price_text)
            
            if price_match:
                price_value = price_match.group(0)
                currency = currency_match.group(0) if currency_match else 'USD'
                product['price'] = f"{price_value} {currency}"
    
    # Extract additional images
    all_images = soup.find_all('img')
    additional_images = []
    for img in all_images:
        src = img.get('src') or img.get('data-src', '')
        if src and src != product['image_link'] and 'product' in src.lower():
            additional_images.append(src)
            if len(additional_images) >= 3:
                break
    
    if additional_images:
        product['additional_image_link'] = ','.join(additional_images)
    
    # Extract category from breadcrumbs
    breadcrumbs = soup.find_all(attrs={'itemprop': 'itemListElement'})
    categories = []
    for crumb in breadcrumbs:
        name_elem = crumb.find(attrs={'itemprop': 'name'})
        if name_elem:
            text = name_elem.get_text(strip=True)
            if text.lower() != 'home':
                categories.append(text)
    
    if categories:
        product['product_category'] = ' > '.join(categories)
    
    # Extract GTIN
    gtin_elem = soup.find(attrs={'itemprop': ['gtin', 'gtin13', 'gtin14']})
    if gtin_elem:
        product['gtin'] = gtin_elem.get_text(strip=True)
    
    # Extract MPN
    mpn_elem = soup.find(attrs={'itemprop': 'mpn'})
    if mpn_elem:
        product['mpn'] = mpn_elem.get_text(strip=True)
    
    return product, price_value, currency

def generate_schema_markup(product_data, price_value, currency):
    """Generate Schema.org JSON-LD markup"""
    availability_map = {
        'in_stock': 'https://schema.org/InStock',
        'out_of_stock': 'https://schema.org/OutOfStock',
        'preorder': 'https://schema.org/PreOrder'
    }
    
    schema = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product_data['title'],
        "description": product_data['description'],
        "sku": product_data['id'],
        "brand": {
            "@type": "Brand",
            "name": product_data['brand']
        },
        "offers": {
            "@type": "Offer",
            "url": product_data['link'],
            "priceCurrency": currency,
            "price": price_value.replace(',', ''),
            "availability": availability_map.get(product_data['availability'], availability_map['in_stock']),
            "itemCondition": "https://schema.org/NewCondition"
        }
    }
    
    # Add images
    if product_data.get('image_link'):
        images = [product_data['image_link']]
        if product_data.get('additional_image_link'):
            images.extend(product_data['additional_image_link'].split(','))
        schema['image'] = images
    
    # Add optional fields
    if product_data.get('gtin'):
        schema['gtin'] = product_data['gtin']
    if product_data.get('mpn'):
        schema['mpn'] = product_data['mpn']
    if product_data.get('product_category'):
        schema['category'] = product_data['product_category']
    
    return schema

# Streamlit UI
st.title("🛍️ Product Schema Markup Generator")
st.markdown("Extract product data and generate Schema.org markup for ChatGPT Shopping")

# URL input
url = st.text_input(
    "Enter Product Page URL",
    placeholder="https://example.com/product/123",
    help="Enter the full URL of the product page"
)

# Generate button
if st.button("🚀 Generate", type="primary", use_container_width=True):
    if not url:
        st.error("Please enter a valid URL")
    elif not url.startswith(('http://', 'https://')):
        st.error("URL must start with http:// or https://")
    else:
        with st.spinner("Extracting product data..."):
            try:
                # Fetch the webpage
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Extract data
                product_data, price_value, currency = extract_product_data(response.text, url)
                schema_markup = generate_schema_markup(product_data, price_value, currency)
                
                # Store in session state
                st.session_state['product_data'] = product_data
                st.session_state['schema_markup'] = schema_markup
                
                st.success("✅ Schema markup generated successfully!")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch website content: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Display results if available
if 'product_data' in st.session_state and 'schema_markup' in st.session_state:
    product_data = st.session_state['product_data']
    schema_markup = st.session_state['schema_markup']
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Product Data", "🔖 Schema Markup", "💾 Downloads"])
    
    with tab1:
        st.subheader("Extracted Product Data")
        # Display as a clean table
        df = pd.DataFrame(list(product_data.items()), columns=['Field', 'Value'])
        df['Value'] = df['Value'].fillna('—')
        st.dataframe(df, use_container_width=True, height=400)
    
    with tab2:
        st.subheader("Schema Markup")
        st.info("💡 Copy and paste this code into your website's `<head>` section")
        
        schema_html = f'<script type="application/ld+json">\n{json.dumps(schema_markup, indent=2)}\n</script>'
        st.code(schema_html, language='html')
        
        if st.button("📋 Copy to Clipboard"):
            st.code(schema_html, language='html')
            st.success("Code is displayed above - use your browser's copy function")
    
    with tab3:
        st.subheader("Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Product Feed (CSV)**")
            st.caption("For product catalogs and feeds")
            csv_data = pd.DataFrame([product_data]).to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                f"product_feed_{int(datetime.now().timestamp())}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("**Schema Markup (JSON)**")
            st.caption("Pure JSON-LD format")
            json_data = json.dumps(schema_markup, indent=2)
            st.download_button(
                "📥 Download JSON",
                json_data,
                f"schema_markup_{int(datetime.now().timestamp())}.json",
                "application/json",
                use_container_width=True
            )
        
        with col3:
            st.markdown("**HTML Code**")
            st.caption("Ready to paste in head tag")
            html_data = f'<script type="application/ld+json">\n{json.dumps(schema_markup, indent=2)}\n</script>'
            st.download_button(
                "📥 Download HTML",
                html_data,
                f"schema_markup_{int(datetime.now().timestamp())}.html",
                "text/html",
                use_container_width=True
            )

# Information sections
st.divider()

with st.expander("ℹ️ How it works"):
    st.markdown("""
    1. **Enter the product page URL**
    2. **The tool scrapes and extracts product information**
    3. **Generates proper Schema.org JSON-LD markup**
    4. **Download in multiple formats or copy directly to your website**
    """)

with st.expander("📋 ChatGPT Shopping Requirements"):
    st.markdown("""
    **Required Fields:**
    - enable_search, enable_checkout
    - id, title, description, link
    - condition, brand, image_link
    - price, availability
    """)

# Footer
st.divider()
st.caption("Built with Streamlit • Product Schema Generator v1.0")
