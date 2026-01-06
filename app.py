import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import re

st.set_page_config(
    page_title="Product Schema Generator - ChatGPT Shopping",
    page_icon="🛍️",
    layout="wide"
)

def extract_product_data(html_content, url):
    """Extract product data from HTML content according to ChatGPT Shopping specifications"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize product dictionary with all ChatGPT Shopping fields
    product = {
        # Required fields
        'enable_search': 'true',
        'enable_checkout': 'true',
        'id': '',
        'title': '',
        'description': '',
        'link': url,
        'condition': 'new',
        'product_category': '',
        'brand': '',
        'material': '',
        'weight': '',
        'image_link': '',
        'price': '',
        'availability': 'in_stock',
        'inventory_quantity': '',
        'shipping': '',
        'seller_name': '',
        'seller_url': '',
        'seller_privacy_policy': '',
        'seller_tos': '',
        'return_policy': '',
        'return_window': '',
        
        # Recommended fields
        'gtin': '',
        'mpn': '',
        'popularity_score': '',
        'return_rate': '',
        'product_review_count': '',
        'product_review_rating': '',
        
        # Optional but important fields
        'additional_image_link': '',
        'video_link': '',
        'model_3d_link': '',
        'sale_price': '',
        'sale_price_effective_date': '',
        'unit_pricing_measure': '',
        'base_measure': '',
        'pricing_trend': '',
        'availability_date': '',
        'expiration_date': '',
        'pickup_method': 'not_supported',
        'pickup_sla': '',
        'item_group_id': '',
        'item_group_title': '',
        'color': '',
        'size': '',
        'size_system': '',
        'gender': '',
        'age_group': '',
        'offer_id': '',
        'dimensions': '',
        'length': '',
        'width': '',
        'height': '',
        'delivery_estimate': '',
        'warning': '',
        'warning_url': '',
        'age_restriction': '',
        'store_review_count': '',
        'store_review_rating': '',
        'q_and_a': '',
        'raw_review_data': '',
        'related_product_id': '',
        'relationship_type': '',
        'geo_price': '',
        'geo_availability': '',
        'custom_variant1_category': '',
        'custom_variant1_option': '',
        'custom_variant2_category': '',
        'custom_variant2_option': '',
        'custom_variant3_category': '',
        'custom_variant3_option': ''
    }
    
    # Try to find existing JSON-LD schema
    existing_schema = None
    json_ld_script = soup.find('script', {'type': 'application/ld+json'})
    if json_ld_script:
        try:
            schema_text = json_ld_script.string
            existing_schema = json.loads(schema_text)
            # Handle array of schemas
            if isinstance(existing_schema, list):
                for schema in existing_schema:
                    if schema.get('@type') == 'Product':
                        existing_schema = schema
                        break
        except:
            pass
    
    # Extract ID/SKU (Required, max 100 chars)
    if existing_schema and 'sku' in existing_schema:
        product['id'] = str(existing_schema['sku'])[:100]
    else:
        sku_elem = soup.find(attrs={'itemprop': 'sku'})
        if sku_elem:
            product['id'] = sku_elem.get_text(strip=True)[:100] or sku_elem.get('content', '')[:100]
        else:
            product['id'] = f"PROD{int(datetime.now().timestamp())}"
    
    # Extract GTIN (Recommended, 8-14 digits)
    if existing_schema:
        for gtin_field in ['gtin', 'gtin13', 'gtin14', 'gtin8', 'gtin12']:
            if gtin_field in existing_schema:
                gtin_value = str(existing_schema[gtin_field])
                if gtin_value.isdigit() and 8 <= len(gtin_value) <= 14:
                    product['gtin'] = gtin_value
                    break
    
    if not product['gtin']:
        for attr in ['gtin', 'gtin13', 'gtin14', 'gtin8', 'gtin12']:
            gtin_elem = soup.find(attrs={'itemprop': attr})
            if gtin_elem:
                gtin_value = gtin_elem.get_text(strip=True)
                if gtin_value.isdigit() and 8 <= len(gtin_value) <= 14:
                    product['gtin'] = gtin_value
                    break
    
    # Extract MPN (Required if gtin missing, max 70 chars)
    if existing_schema and 'mpn' in existing_schema:
        product['mpn'] = str(existing_schema['mpn'])[:70]
    else:
        mpn_elem = soup.find(attrs={'itemprop': 'mpn'})
        if mpn_elem:
            product['mpn'] = mpn_elem.get_text(strip=True)[:70]
    
    # Extract Title (Required, max 150 chars)
    if existing_schema and 'name' in existing_schema:
        product['title'] = str(existing_schema['name'])[:150]
    else:
        h1 = soup.find('h1')
        if h1:
            product['title'] = h1.get_text(strip=True)[:150]
        else:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                product['title'] = og_title.get('content', '')[:150]
            else:
                title_tag = soup.find('title')
                if title_tag:
                    product['title'] = title_tag.get_text(strip=True)[:150]
    
    # Extract Description (Required, max 5000 chars, plain text only)
    if existing_schema and 'description' in existing_schema:
        product['description'] = str(existing_schema['description'])[:5000]
    else:
        desc_elem = soup.find(attrs={'itemprop': 'description'})
        if desc_elem:
            product['description'] = desc_elem.get_text(strip=True)[:5000]
        else:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                product['description'] = meta_desc.get('content', '')[:5000]
            else:
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    product['description'] = og_desc.get('content', '')[:5000]
    
    # Extract Brand (Required for most products, max 70 chars)
    if existing_schema and 'brand' in existing_schema:
        brand = existing_schema['brand']
        product['brand'] = (brand['name'] if isinstance(brand, dict) else str(brand))[:70]
    else:
        brand_elem = soup.find(attrs={'itemprop': 'brand'})
        if brand_elem:
            brand_name_elem = brand_elem.find(attrs={'itemprop': 'name'})
            product['brand'] = (brand_name_elem.get_text(strip=True) if brand_name_elem else brand_elem.get_text(strip=True))[:70]
        else:
            meta_brand = soup.find('meta', property='product:brand')
            if meta_brand:
                product['brand'] = meta_brand.get('content', '')[:70]
    
    # Extract Material (Required, max 100 chars)
    material_elem = soup.find(attrs={'itemprop': 'material'})
    if material_elem:
        product['material'] = material_elem.get_text(strip=True)[:100]
    
    # Extract Product Category (Required)
    breadcrumbs = soup.find_all(attrs={'itemprop': 'itemListElement'})
    categories = []
    for crumb in breadcrumbs:
        name_elem = crumb.find(attrs={'itemprop': 'name'})
        if name_elem:
            text = name_elem.get_text(strip=True)
            if text.lower() not in ['home', 'homepage']:
                categories.append(text)
    
    if categories:
        product['product_category'] = ' > '.join(categories)
    elif existing_schema and 'category' in existing_schema:
        product['product_category'] = str(existing_schema['category'])
    
    # Extract Image (Required, HTTPS preferred)
    if existing_schema and 'image' in existing_schema:
        image = existing_schema['image']
        product['image_link'] = image[0] if isinstance(image, list) else str(image)
    else:
        og_image = soup.find('meta', property='og:image')
        if og_image:
            product['image_link'] = og_image.get('content', '')
        else:
            img_elem = soup.find('img', attrs={'itemprop': 'image'})
            if img_elem:
                product['image_link'] = img_elem.get('src', '')
            else:
                # Try to find main product image
                main_img = soup.find('img', class_=re.compile(r'product|main', re.I))
                if main_img:
                    product['image_link'] = main_img.get('src', '')
    
    # Extract Price and Currency (Required, ISO 4217)
    price_value = ''
    currency = 'USD'
    
    if existing_schema and 'offers' in existing_schema:
        offers = existing_schema['offers']
        offer = offers[0] if isinstance(offers, list) else offers
        
        # Regular price
        price_value = str(offer.get('price', ''))
        currency = offer.get('priceCurrency', 'USD')
        product['price'] = f"{price_value} {currency}"
        
        # Sale price
        if 'priceSpecification' in offer and offer['priceSpecification'].get('price'):
            sale_value = str(offer['priceSpecification']['price'])
            product['sale_price'] = f"{sale_value} {currency}"
        
        # Availability
        avail = offer.get('availability', '').lower()
        if 'instock' in avail:
            product['availability'] = 'in_stock'
        elif 'outofstock' in avail:
            product['availability'] = 'out_of_stock'
        elif 'preorder' in avail:
            product['availability'] = 'preorder'
        
        # Inventory quantity
        if 'inventoryLevel' in offer:
            product['inventory_quantity'] = str(offer['inventoryLevel'])
        
        # Seller info
        if 'seller' in offer:
            seller = offer['seller']
            if isinstance(seller, dict):
                product['seller_name'] = seller.get('name', '')[:70]
                product['seller_url'] = seller.get('url', '')
    else:
        # Fallback price extraction
        price_elem = soup.find(attrs={'itemprop': 'price'})
        if not price_elem:
            price_elem = soup.find(class_=re.compile(r'price', re.I))
        
        if price_elem:
            price_text = price_elem.get_text() or price_elem.get('content', '')
            price_match = re.search(r'[\d,]+\.?\d*', price_text)
            currency_match = re.search(r'[A-Z]{3}', price_text)
            
            if price_match:
                price_value = price_match.group(0).replace(',', '')
                currency = currency_match.group(0) if currency_match else 'USD'
                product['price'] = f"{price_value} {currency}"
    
    # Extract Weight (Required with unit)
    weight_elem = soup.find(attrs={'itemprop': 'weight'})
    if weight_elem:
        weight_text = weight_elem.get_text(strip=True) or weight_elem.get('content', '')
        product['weight'] = weight_text
    
    # Extract Dimensions
    dimensions_elem = soup.find(attrs={'itemprop': 'depth'})
    if dimensions_elem:
        depth = dimensions_elem.get_text(strip=True)
        width_elem = soup.find(attrs={'itemprop': 'width'})
        height_elem = soup.find(attrs={'itemprop': 'height'})
        if width_elem and height_elem:
            width = width_elem.get_text(strip=True)
            height = height_elem.get_text(strip=True)
            product['dimensions'] = f"{depth}x{width}x{height}"
            product['length'] = depth
            product['width'] = width
            product['height'] = height
    
    # Extract additional images (Optional)
    all_images = soup.find_all('img')
    additional_images = []
    for img in all_images[:10]:  # Limit to first 10 images
        src = img.get('src') or img.get('data-src', '')
        if src and src != product['image_link'] and any(keyword in src.lower() for keyword in ['product', 'item', 'gallery']):
            additional_images.append(src)
            if len(additional_images) >= 10:
                break
    
    if additional_images:
        product['additional_image_link'] = ','.join(additional_images)
    
    # Extract video link (Optional)
    video_elem = soup.find('video')
    if video_elem:
        product['video_link'] = video_elem.get('src', '')
    else:
        youtube_elem = soup.find('iframe', src=re.compile(r'youtube|youtu\.be', re.I))
        if youtube_elem:
            product['video_link'] = youtube_elem.get('src', '')
    
    # Extract Age Group (Optional)
    age_elem = soup.find(attrs={'itemprop': 'audience'})
    if age_elem:
        age_text = age_elem.get_text(strip=True).lower()
        valid_ages = ['newborn', 'infant', 'toddler', 'kids', 'adult']
        for age in valid_ages:
            if age in age_text:
                product['age_group'] = age
                break
    
    # Extract Color (Recommended for apparel, max 40 chars)
    color_elem = soup.find(attrs={'itemprop': 'color'})
    if color_elem:
        product['color'] = color_elem.get_text(strip=True)[:40]
    
    # Extract Size (Recommended for apparel, max 20 chars)
    size_elem = soup.find(attrs={'itemprop': 'size'})
    if size_elem:
        product['size'] = size_elem.get_text(strip=True)[:20]
    
    # Extract Gender (Recommended for apparel)
    gender_elem = soup.find(attrs={'itemprop': 'gender'})
    if gender_elem:
        gender_text = gender_elem.get_text(strip=True).lower()
        if gender_text in ['male', 'female', 'unisex']:
            product['gender'] = gender_text
    
    # Extract Reviews (Recommended)
    if existing_schema and 'aggregateRating' in existing_schema:
        rating = existing_schema['aggregateRating']
        product['product_review_rating'] = str(rating.get('ratingValue', ''))
        product['product_review_count'] = str(rating.get('reviewCount', ''))
    else:
        rating_elem = soup.find(attrs={'itemprop': 'ratingValue'})
        if rating_elem:
            product['product_review_rating'] = rating_elem.get_text(strip=True) or rating_elem.get('content', '')
        
        count_elem = soup.find(attrs={'itemprop': 'reviewCount'})
        if count_elem:
            product['product_review_count'] = count_elem.get_text(strip=True) or count_elem.get('content', '')
    
    # Extract Condition (Required if not new)
    condition_elem = soup.find(attrs={'itemprop': 'itemCondition'})
    if condition_elem:
        condition_text = condition_elem.get_text(strip=True).lower()
        if 'refurbished' in condition_text:
            product['condition'] = 'refurbished'
        elif 'used' in condition_text:
            product['condition'] = 'used'
    
    # Extract Offer ID (Recommended)
    if product['id'] and product['price']:
        price_clean = product['price'].split()[0]
        product['offer_id'] = f"{product['id']}-{price_clean}"
        if product['color']:
            product['offer_id'] = f"{product['id']}-{product['color']}-{price_clean}"
    
    # Extract Return Policy URLs (Required)
    policy_links = soup.find_all('a', href=re.compile(r'return|refund|policy', re.I))
    for link in policy_links:
        href = link.get('href', '')
        if 'return' in href.lower():
            product['return_policy'] = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
        if 'privacy' in href.lower():
            product['seller_privacy_policy'] = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
        if 'terms' in href.lower() or 'tos' in href.lower():
            product['seller_tos'] = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
    
    # Set default return window (Required)
    product['return_window'] = '30'  # Default 30 days
    
    # Set seller URLs if not found
    if not product['seller_url']:
        product['seller_url'] = url
    if not product['seller_name']:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        product['seller_name'] = domain.replace('www.', '').split('.')[0].title()[:70]
    
    return product, price_value, currency

def generate_schema_markup(product_data, price_value, currency):
    """Generate comprehensive Schema.org JSON-LD markup"""
    availability_map = {
        'in_stock': 'https://schema.org/InStock',
        'out_of_stock': 'https://schema.org/OutOfStock',
        'preorder': 'https://schema.org/PreOrder'
    }
    
    condition_map = {
        'new': 'https://schema.org/NewCondition',
        'refurbished': 'https://schema.org/RefurbishedCondition',
        'used': 'https://schema.org/UsedCondition'
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
            "itemCondition": condition_map.get(product_data['condition'], condition_map['new'])
        }
    }
    
    # Add seller information to offers
    if product_data.get('seller_name'):
        schema['offers']['seller'] = {
            "@type": "Organization",
            "name": product_data['seller_name']
        }
        if product_data.get('seller_url'):
            schema['offers']['seller']['url'] = product_data['seller_url']
    
    # Add inventory quantity
    if product_data.get('inventory_quantity'):
        try:
            schema['offers']['inventoryLevel'] = int(product_data['inventory_quantity'])
        except:
            pass
    
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
    if product_data.get('material'):
        schema['material'] = product_data['material']
    if product_data.get('weight'):
        schema['weight'] = product_data['weight']
    if product_data.get('color'):
        schema['color'] = product_data['color']
    if product_data.get('size'):
        schema['size'] = product_data['size']
    
    # Add aggregate rating
    if product_data.get('product_review_rating') and product_data.get('product_review_count'):
        try:
            schema['aggregateRating'] = {
                "@type": "AggregateRating",
                "ratingValue": float(product_data['product_review_rating']),
                "reviewCount": int(product_data['product_review_count'])
            }
        except:
            pass
    
    return schema

# Streamlit UI
st.title("🛍️ Product Schema Markup Generator")
st.markdown("**ChatGPT Shopping Feed Compliant** - Extract product data and generate Schema.org markup")

# Add info about completeness
st.info("🎯 This tool extracts all required, recommended, and optional fields according to ChatGPT Shopping Feed specifications")

# URL input
url = st.text_input(
    "Enter Product Page URL",
    placeholder="https://example.com/product/123",
    help="Enter the full URL of the product page"
)

# Generate button
col1, col2 = st.columns([3, 1])
with col1:
    generate_btn = st.button("🚀 Generate Schema Markup", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 Clear", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if generate_btn:
    if not url:
        st.error("Please enter a valid URL")
    elif not url.startswith(('http://', 'https://')):
        st.error("URL must start with http:// or https://")
    else:
        with st.spinner("Extracting product data according to ChatGPT Shopping specifications..."):
            try:
                # Fetch the webpage
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Extract data
                product_data, price_value, currency = extract_product_data(response.text, url)
                schema_markup = generate_schema_markup(product_data, price_value, currency)
                
                # Store in session state
                st.session_state['product_data'] = product_data
                st.session_state['schema_markup'] = schema_markup
                st.session_state['url'] = url
                
                st.success("✅ Schema markup generated successfully!")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch website content: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

# Display results if available
if 'product_data' in st.session_state and 'schema_markup' in st.session_state:
    product_data = st.session_state['product_data']
    schema_markup = st.session_state['schema_markup']
    
    # Show completeness metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    required_fields = ['enable_search', 'enable_checkout', 'id', 'title', 'description', 'link', 
                       'condition', 'product_category', 'brand', 'material', 'weight', 
                       'image_link', 'price', 'availability', 'inventory_quantity', 'shipping',
                       'seller_name', 'seller_url', 'return_policy', 'return_window']
    
    recommended_fields = ['gtin', 'mpn', 'popularity_score', 'product_review_count', 'product_review_rating']
    
    required_filled = sum(1 for f in required_fields if product_data.get(f))
    recommended_filled = sum(1 for f in recommended_fields if product_data.get(f))
    total_fields = len([v for v in product_data.values() if v])
    
    col1.metric("Required Fields", f"{required_filled}/{len(required_fields)}")
    col2.metric("Recommended Fields", f"{recommended_filled}/{len(recommended_fields)}")
    col3.metric("Total Fields Populated", total_fields)
    col4.metric("Completion", f"{int((required_filled/len(required_fields))*100)}%")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Product Data", "🔖 Schema Markup", "💾 Downloads", "✅ Validation"])
    
    with tab1:
        st.subheader("Extracted Product Data (ChatGPT Shopping Format)")
        
        # Categorize fields
        required_data = {k: v for k, v in product_data.items() if k in required_fields}
        recommended_data = {k: v for k, v in product_data.items() if k in recommended_fields}
        optional_data = {k: v for k, v in product_data.items() if k not in required_fields and k not in recommended_fields}
        
        with st.expander("**Required Fields** (Must be present)", expanded=True):
            df_req = pd.DataFrame(list(required_data.items()), columns=['Field', 'Value'])
            df_req['Value'] = df_req['Value'].apply(lambda x: x if x else '⚠️ MISSING')
            st.dataframe(df_req, use_container_width=True, height=400)
        
        with st.expander("**Recommended Fields** (Should be present)"):
            df_rec = pd.DataFrame(list(recommended_data.items()), columns=['Field', 'Value'])
            df_rec['Value'] = df_rec['Value'].apply(lambda x: x if x else '—')
            st.dataframe(df_rec, use_container_width=True)
        
        with st.expander("**Optional Fields**"):
            df_opt = pd.DataFrame(list(optional_data.items()), columns=['Field', 'Value'])
            df_opt['Value'] = df_opt['Value'].apply(lambda x: x if x else '—')
            st.dataframe(df_opt, use_container_width=True, height=300)
    
    with tab2:
        st.subheader("Schema.org JSON-LD Markup")
        st.info("💡 Copy and paste this code into your website's `<head>` section")
        
        schema_html = f'<script type="application/ld+json">\n{json.dumps(schema_markup, indent=2)}\n</script>'
        st.code(schema_html, language='html')
        
        if st.button("📋 Copy to Clipboard"):
            st.code(schema_html, language='html')
            st.success("✅ Code is displayed above - select and copy using Ctrl+C or Cmd+C")
    
    with tab3:
        st.subheader("Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📄 Product Feed (CSV)**")
            st.caption("ChatGPT Shopping feed format")
            csv_data = pd.DataFrame([product_data]).to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                f"chatgpt_shopping_feed_{int(datetime.now().timestamp())}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("**🔖 Schema Markup (JSON)**")
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
            st.markdown("**🌐 HTML Code**")
            st.caption("Ready to paste in head tag")
            html_data = f'<script type="application/ld+json">\n{json.dumps(schema_markup, indent=2)}\n</script>'
            st.download_button(
                "📥 Download HTML",
                html_data,
                f"schema_markup_{int(datetime.now().timestamp())}.html",
                "text/html",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("**📋 Complete Feed (All Fields)**")
        
        # Create complete feed with all fields
        complete_feed = pd.DataFrame([product_data])
        complete_csv = complete_feed.to_csv(index=False)
        
        st.download_button(
            "📥 Download Complete Feed (All Fields)",
            complete_csv,
            f"complete_chatgpt_shopping_feed_{int(datetime.now().timestamp())}.csv",
            "text/csv",
            use_container_width=True,
            type="primary"
        )
    
    with tab4:
        st.subheader("ChatGPT Shopping Feed Validation")
        
        # Validation checks
        issues = []
        warnings = []
        successes = []
        
        # Check required fields
        for field in required_fields:
            if not product_data.get(field):
                issues.append(f"❌ Missing required field: **{field}**")
            else:
                successes.append(f"✅ Required field present: {field}")
        
        # Check field validations
        if product_data.get('id') and len(product_data['id']) > 100:
            issues.append("❌ ID exceeds 100 characters")
        
        if product_data.get('title') and len(product_data['title']) > 150:
            issues.append("❌ Title exceeds 150 characters")
        
        if product_data.get('description') and len(product_data['description']) > 5000:
            issues.append("❌ Description exceeds 5000 characters")
        
        if product_data.get('brand') and len(product_data['brand']) > 70:
            issues.append("❌ Brand exceeds 70 characters")
        
        if product_data.get('gtin'):
            gtin = product_data['gtin']
            if not gtin.isdigit() or not (8 <= len(gtin) <= 14):
                issues.append("❌ GTIN must be 8-14 digits")
        
        if not product_data.get('gtin') and not product_data.get('mpn'):
            warnings.append("⚠️ Either GTIN or MPN should be provided")
        
        if product_data.get('enable_search') != 'true':
            warnings.append("⚠️ enable_search should be 'true' for ChatGPT Shopping")
        
        if product_data.get('enable_checkout') == 'true' and product_data.get('enable_search') != 'true':
            issues.append("❌ enable_checkout requires enable_search to be true")
        
        if product_data.get('enable_checkout') == 'true':
            required_checkout = ['seller_privacy_policy', 'seller_tos']
            for field in required_checkout:
                if not product_data.get(field):
                    issues.append(f"❌ {field} required when enable_checkout is true")
        
        if product_data.get('availability') == 'preorder' and not product_data.get('availability_date'):
            issues.append("❌ availability_date required when availability is 'preorder'")
        
        if not product_data.get('image_link'):
            issues.append("❌ image_link is required")
        elif not product_data['image_link'].startswith('https'):
            warnings.append("⚠️ HTTPS preferred for image_link")
        
        # Check recommended fields
        for field in recommended_fields:
            if not product_data.get(field):
                warnings.append(f"⚠️ Recommended field missing: {field}")
        
        # Display validation results
        if issues:
            st.error(f"**{len(issues)} Critical Issues Found**")
            for issue in issues:
                st.markdown(issue)
        else:
            st.success("✅ **No critical issues found!**")
        
        if warnings:
            st.warning(f"**{len(warnings)} Warnings**")
            for warning in warnings:
                st.markdown(warning)
        
        if not issues and not warnings:
            st.balloons()
            st.success("🎉 **Perfect! Your product feed meets all ChatGPT Shopping requirements!**")
        
        # Show validation summary
        st.markdown("---")
        st.markdown("### Validation Summary")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        summary_col1.metric("✅ Passed", len(successes))
        summary_col2.metric("⚠️ Warnings", len(warnings))
        summary_col3.metric("❌ Issues", len(issues))

# Information sections
st.divider()

with st.expander("ℹ️ How it works"):
    st.markdown("""
    ### Step-by-Step Process
    
    1. **Enter Product URL** - Paste the URL of any product page
    2. **Automatic Extraction** - Tool scrapes and extracts all ChatGPT Shopping fields
    3. **Schema Generation** - Creates valid Schema.org JSON-LD markup
    4. **Validation** - Checks compliance with ChatGPT Shopping specifications
    5. **Export** - Download in CSV, JSON, or HTML format
    
    ### What Gets Extracted
    
    - ✅ **Required Fields** (20 fields) - Must be present for ChatGPT Shopping
    - 🎯 **Recommended Fields** (5 fields) - Should be present for better visibility
    - 📦 **Optional Fields** (40+ fields) - Additional product information
    
    ### Supported Field Types
    
    All field types per ChatGPT Shopping specifications:
    - String (text, alphanumeric, UTF-8)
    - Enum (predefined values)
    - Number (with units where applicable)
    - URL (RFC 1738 compliant)
    - Date (ISO 8601 format)
    """)

with st.expander("📋 ChatGPT Shopping Requirements"):
    st.markdown("""
    ### Required Fields (20)
    
    **Product Identification:**
    - enable_search, enable_checkout
    - id (SKU, max 100 chars)
    - gtin or mpn (universal identifier)
    
    **Product Information:**
    - title (max 150 chars)
    - description (max 5000 chars, plain text)
    - link (product page URL)
    - condition (new/refurbished/used)
    - product_category (with ">" separator)
    - brand (max 70 chars)
    - material (max 100 chars)
    - weight (with unit)
    
    **Imagery:**
    - image_link (HTTPS preferred)
    
    **Pricing & Availability:**
    - price (with ISO 4217 currency)
    - availability (in_stock/out_of_stock/preorder)
    - inventory_quantity (non-negative integer)
    
    **Seller & Policies:**
    - seller_name (max 70 chars)
    - seller_url
    - return_policy (URL)
    - return_window (days)
    - shipping (format: country:region:service:price)
    
    **Additional (for checkout):**
    - seller_privacy_policy (if enable_checkout=true)
    - seller_tos (if enable_checkout=true)
    
    ### Recommended Fields (5)
    
    - gtin (8-14 digits, no dashes/spaces)
    - mpn (max 70 chars)
    - product_review_count
    - product_review_rating (0-5 scale)
    - popularity_score
    
    ### Optional Fields (40+)
    
    Includes: additional images, videos, 3D models, sale prices, dimensions,
    variants (color, size, gender), reviews, Q&A, related products, and more.
    """)

with st.expander("🎯 Field Validation Rules"):
    st.markdown("""
    ### String Validation
    - **id**: Max 100 chars, alphanumeric, stable over time
    - **title**: Max 150 chars, avoid all-caps
    - **description**: Max 5000 chars, plain text only
    - **brand**: Max 70 chars
    - **material**: Max 100 chars
    - **color**: Max 40 chars
    - **size**: Max 20 chars
    
    ### Enum Validation
    - **enable_search/enable_checkout**: "true" or "false" (lowercase)
    - **condition**: "new", "refurbished", or "used"
    - **availability**: "in_stock", "out_of_stock", or "preorder"
    - **gender**: "male", "female", or "unisex"
    - **age_group**: "newborn", "infant", "toddler", "kids", or "adult"
    
    ### Number Validation
    - **gtin**: 8-14 digits, numeric only
    - **price**: Must include ISO 4217 currency code
    - **inventory_quantity**: Non-negative integer
    - **return_window**: Positive integer (days)
    - **weight**: Positive number with unit
    
    ### URL Validation
    - Must resolve with HTTP 200
    - HTTPS preferred
    - Must follow RFC 1738
    
    ### Dependencies
    - **mpn**: Required if gtin is missing
    - **enable_checkout**: Requires enable_search=true
    - **seller_privacy_policy**: Required if enable_checkout=true
    - **seller_tos**: Required if enable_checkout=true
    - **availability_date**: Required if availability=preorder
    - **sale_price_effective_date**: Required if sale_price provided
    """)

with st.expander("💡 Best Practices"):
    st.markdown("""
    ### For Better ChatGPT Shopping Results
    
    1. **Always provide GTIN or MPN** - Helps with product matching
    2. **Use high-quality images** - HTTPS URLs, JPEG/PNG format
    3. **Write clear descriptions** - Plain text, avoid HTML/special chars
    4. **Include review data** - Boosts product credibility
    5. **Set accurate inventory** - Update regularly
    6. **Provide complete variants** - Color, size for apparel
    7. **Add related products** - Cross-selling opportunities
    8. **Use proper categories** - Follow standard taxonomy
    9. **Keep URLs stable** - Don't change product URLs frequently
    10. **Update regularly** - Keep feed fresh (daily/weekly)
    
    ### Common Mistakes to Avoid
    
    - ❌ Using placeholder images
    - ❌ Incomplete product descriptions
    - ❌ Missing required policy URLs
    - ❌ Incorrect price formatting
    - ❌ All-caps titles
    - ❌ HTML in description field
    - ❌ Missing currency codes
    - ❌ Invalid GTIN format
    """)

# Footer
st.divider()
st.caption("Built with Streamlit • ChatGPT Shopping Feed Compliant • Schema Generator v2.0")
