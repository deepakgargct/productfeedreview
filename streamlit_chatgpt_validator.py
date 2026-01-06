import streamlit as st
import pandas as pd
import requests
from io import StringIO
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="Product Feed Validator", layout="wide")

# Title and description
st.title("📊 Product Feed Validator")
st.markdown("Validate and process product feeds from various sources with ChatGPT integration")

# Initialize session state
if 'feed_data' not in st.session_state:
    st.session_state.feed_data = None
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None
if 'loading_mode' not in st.session_state:
    st.session_state.loading_mode = None

def load_feed_from_url(url):
    """
    Load product feed from a given URL.
    
    Args:
        url (str): The URL of the feed to load
        
    Returns:
        pd.DataFrame or dict: Loaded feed data, or None if failed
        
    Raises:
        Exception: If the URL cannot be loaded or parsed
    """
    try:
        logger.info(f"Attempting to load feed from URL: {url}")
        
        # Add timeout and headers for better reliability
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Try to parse as JSON first
        try:
            data = response.json()
            logger.info(f"Successfully loaded JSON feed from {url}")
            
            # Convert to DataFrame if it's a list of objects
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # If it's a dict, try to find an array within it
                for key, value in data.items():
                    if isinstance(value, list):
                        return pd.DataFrame(value)
                return pd.DataFrame([data])
            return data
            
        except json.JSONDecodeError:
            # Try to parse as CSV
            logger.info(f"JSON parsing failed, attempting CSV parsing for {url}")
            df = pd.read_csv(StringIO(response.text))
            logger.info(f"Successfully loaded CSV feed from {url}")
            return df
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while loading feed from {url}")
        st.error(f"⏱️ Timeout: The URL took too long to respond. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while loading feed from {url}")
        st.error(f"🔌 Connection Error: Could not connect to the URL. Please check the URL and try again.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} while loading feed from {url}")
        st.error(f"❌ HTTP Error {e.response.status_code}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading feed from URL: {str(e)}")
        st.error(f"❌ Error loading feed: {str(e)}")
        return None

def load_feed_from_file(uploaded_file):
    """
    Load product feed from an uploaded file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pd.DataFrame or dict: Loaded feed data, or None if failed
    """
    try:
        logger.info(f"Loading feed from file: {uploaded_file.name}")
        
        if uploaded_file.type == "application/json":
            data = json.load(uploaded_file)
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        return pd.DataFrame(value)
                return pd.DataFrame([data])
            return data
        else:
            # Assume CSV format
            return pd.read_csv(uploaded_file)
            
    except Exception as e:
        logger.error(f"Error loading feed from file: {str(e)}")
        st.error(f"❌ Error loading file: {str(e)}")
        return None

def validate_feed_structure(feed_data):
    """
    Validate the structure of the feed data.
    
    Args:
        feed_data (pd.DataFrame): The feed data to validate
        
    Returns:
        dict: Validation results with status and details
    """
    try:
        if not isinstance(feed_data, pd.DataFrame) or feed_data.empty:
            return {
                "status": "error",
                "message": "Feed data is empty or invalid",
                "row_count": 0,
                "column_count": 0
            }
        
        results = {
            "status": "success",
            "message": "Feed structure is valid",
            "row_count": len(feed_data),
            "column_count": len(feed_data.columns),
            "columns": list(feed_data.columns),
            "missing_values": feed_data.isnull().sum().to_dict(),
            "duplicates": len(feed_data) - len(feed_data.drop_duplicates())
        }
        
        logger.info(f"Feed validation successful: {results['row_count']} rows, {results['column_count']} columns")
        return results
        
    except Exception as e:
        logger.error(f"Error validating feed structure: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# Main application layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Data Source")
    loading_mode = st.radio(
        "Select how to load your feed:",
        ["📂 Upload File", "🌐 Load from URL"],
        key="mode_selection"
    )

with col2:
    st.subheader("ℹ️ Info")
    st.info("Choose between uploading a local file or loading a feed directly from a URL")

# Handle different loading modes
if loading_mode == "📂 Upload File":
    uploaded_file = st.file_uploader(
        "Choose a CSV or JSON file",
        type=["csv", "json"],
        help="Upload your product feed file"
    )
    
    if uploaded_file is not None:
        with st.spinner("Loading file..."):
            st.session_state.feed_data = load_feed_from_file(uploaded_file)
            
elif loading_mode == "🌐 Load from URL":
    col1, col2 = st.columns([3, 1])
    
    with col1:
        feed_url = st.text_input(
            "Enter feed URL",
            placeholder="https://example.com/feed.json or https://example.com/feed.csv",
            help="Enter the complete URL to your product feed (JSON or CSV format)"
        )
    
    with col2:
        load_button = st.button("🔄 Load Feed", use_container_width=True)
    
    if load_button:
        if feed_url:
            with st.spinner("Loading feed from URL..."):
                st.session_state.feed_data = load_feed_from_url(feed_url)
        else:
            st.warning("⚠️ Please enter a valid URL")

# Display loaded data and validation
if st.session_state.feed_data is not None:
    st.success("✅ Feed loaded successfully!")
    
    # Validate feed structure
    validation_results = validate_feed_structure(st.session_state.feed_data)
    st.session_state.validation_results = validation_results
    
    # Display validation results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", validation_results.get("row_count", 0))
    with col2:
        st.metric("Columns", validation_results.get("column_count", 0))
    with col3:
        st.metric("Duplicate Rows", validation_results.get("duplicates", 0))
    with col4:
        st.metric("Status", "✅ Valid" if validation_results.get("status") == "success" else "⚠️ Invalid")
    
    # Display detailed info
    with st.expander("📋 Feed Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Columns:**")
            st.write(validation_results.get("columns", []))
        
        with col2:
            st.write("**Missing Values:**")
            st.json(validation_results.get("missing_values", {}))
    
    # Display sample data
    with st.expander("👀 Preview Data (First 10 rows)"):
        st.dataframe(st.session_state.feed_data.head(10), use_container_width=True)
    
    # Display full data
    with st.expander("📊 Full Data"):
        st.dataframe(st.session_state.feed_data, use_container_width=True)
    
    # Download option
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        csv = st.session_state.feed_data.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"feed_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = st.session_state.feed_data.to_json(orient="records", indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_data,
            file_name=f"feed_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 12px;'>
    Product Feed Validator | Built with Streamlit | Last Updated: 2026-01-06
    </div>
    """,
    unsafe_allow_html=True
)
