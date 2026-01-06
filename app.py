import React, { useState } from 'react';
import { Download, AlertCircle, CheckCircle, Loader2, Copy } from 'lucide-react';

const ProductSchemaGenerator = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [productData, setProductData] = useState(null);
  const [schemaMarkup, setSchemaMarkup] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('data');
  const [copied, setCopied] = useState(false);

  const extractProductData = (htmlContent, url) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    const getText = (selector) => {
      const el = doc.querySelector(selector);
      return el ? el.textContent.trim() : '';
    };
    
    const getAttr = (selector, attr) => {
      const el = doc.querySelector(selector);
      return el ? el.getAttribute(attr) : '';
    };
    
    // Try to find existing JSON-LD schema
    let existingSchema = null;
    const jsonLdScript = doc.querySelector('script[type="application/ld+json"]');
    if (jsonLdScript) {
      try {
        existingSchema = JSON.parse(jsonLdScript.textContent);
      } catch (e) {
        console.log('Could not parse existing schema');
      }
    }
    
    const product = {
      enable_search: 'true',
      enable_checkout: 'true',
      id: '',
      title: '',
      description: '',
      link: url,
      condition: 'new',
      brand: '',
      image_link: '',
      price: '',
      availability: 'in_stock'
    };
    
    // Extract ID/SKU
    product.id = existingSchema?.sku || 
                getAttr('[itemprop="sku"]', 'content') ||
                getText('[itemprop="sku"]') ||
                `PROD${Date.now()}`;
    
    // Extract Title
    product.title = existingSchema?.name ||
                   getText('h1') ||
                   getText('[itemprop="name"]') ||
                   getAttr('meta[property="og:title"]', 'content') || '';
    
    // Extract Description
    product.description = existingSchema?.description ||
                         getText('[itemprop="description"]') ||
                         getAttr('meta[name="description"]', 'content') ||
                         getAttr('meta[property="og:description"]', 'content') || '';
    
    // Extract Brand
    if (existingSchema?.brand) {
      product.brand = typeof existingSchema.brand === 'object' ? 
                     existingSchema.brand.name : existingSchema.brand;
    } else {
      product.brand = getText('[itemprop="brand"]') ||
                     getAttr('meta[property="product:brand"]', 'content') || '';
    }
    
    // Extract Image
    product.image_link = existingSchema?.image?.[0] || existingSchema?.image ||
                        getAttr('meta[property="og:image"]', 'content') ||
                        getAttr('[itemprop="image"]', 'src') || '';
    
    // Extract Price
    let priceValue = '';
    let currency = 'USD';
    
    if (existingSchema?.offers) {
      const offer = Array.isArray(existingSchema.offers) ? 
                   existingSchema.offers[0] : existingSchema.offers;
      priceValue = offer.price || '';
      currency = offer.priceCurrency || 'USD';
      product.price = `${priceValue} ${currency}`;
      
      const avail = (offer.availability || '').toLowerCase();
      if (avail.includes('instock')) product.availability = 'in_stock';
      else if (avail.includes('outofstock')) product.availability = 'out_of_stock';
      else if (avail.includes('preorder')) product.availability = 'preorder';
    } else {
      const priceEl = doc.querySelector('[itemprop="price"]') || 
                     doc.querySelector('.price');
      if (priceEl) {
        const priceText = priceEl.textContent || priceEl.getAttribute('content') || '';
        const priceMatch = priceText.match(/[\d,.]+/);
        const currencyMatch = priceText.match(/[A-Z]{3}/);
        if (priceMatch) {
          priceValue = priceMatch[0];
          currency = currencyMatch ? currencyMatch[0] : 'USD';
          product.price = `${priceValue} ${currency}`;
        }
      }
    }
    
    // Extract additional images
    const images = Array.from(doc.querySelectorAll('img'))
      .map(img => img.src || img.getAttribute('data-src'))
      .filter(src => src && src !== product.image_link && src.includes('product'))
      .slice(0, 3);
    
    if (images.length > 0) {
      product.additional_image_link = images.join(',');
    }
    
    // Extract category
    const breadcrumbs = Array.from(doc.querySelectorAll('[itemprop="itemListElement"]'))
      .map(el => {
        const name = el.querySelector('[itemprop="name"]');
        return name ? name.textContent.trim() : '';
      })
      .filter(text => text && text.toLowerCase() !== 'home');
    
    if (breadcrumbs.length > 0) {
      product.product_category = breadcrumbs.join(' > ');
    }
    
    // Extract GTIN
    const gtin = getText('[itemprop="gtin"]') || 
                getText('[itemprop="gtin13"]') || 
                getText('[itemprop="gtin14"]');
    if (gtin) product.gtin = gtin;
    
    // Extract MPN
    const mpn = getText('[itemprop="mpn"]');
    if (mpn) product.mpn = mpn;
    
    return { product, priceValue, currency };
  };

  const generateSchemaMarkup = (productData, priceValue, currency) => {
    const availabilityMap = {
      'in_stock': 'https://schema.org/InStock',
      'out_of_stock': 'https://schema.org/OutOfStock',
      'preorder': 'https://schema.org/PreOrder'
    };
    
    const schema = {
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": productData.title,
      "description": productData.description,
      "sku": productData.id,
      "brand": {
        "@type": "Brand",
        "name": productData.brand
      },
      "offers": {
        "@type": "Offer",
        "url": productData.link,
        "priceCurrency": currency,
        "price": priceValue.replace(',', ''),
        "availability": availabilityMap[productData.availability],
        "itemCondition": "https://schema.org/NewCondition"
      }
    };
    
    if (productData.image_link) {
      const images = [productData.image_link];
      if (productData.additional_image_link) {
        images.push(...productData.additional_image_link.split(','));
      }
      schema.image = images;
    }
    
    if (productData.gtin) schema.gtin = productData.gtin;
    if (productData.mpn) schema.mpn = productData.mpn;
    if (productData.product_category) schema.category = productData.product_category;
    
    return schema;
  };

  const handleGenerate = async () => {
    if (!url) {
      setError('Please enter a valid URL');
      return;
    }
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URL must start with http:// or https://');
      return;
    }
    
    setLoading(true);
    setError(null);
    setProductData(null);
    setSchemaMarkup(null);
    
    try {
      const response = await fetch(`https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch website content');
      }
      
      const html = await response.text();
      const { product, priceValue, currency } = extractProductData(html, url);
      const schema = generateSchemaMarkup(product, priceValue, currency);
      
      setProductData(product);
      setSchemaMarkup(schema);
      setActiveTab('data');
    } catch (err) {
      setError(err.message || 'Failed to generate schema. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    const headers = Object.keys(productData).join(',');
    const values = Object.values(productData).map(v => `"${v || ''}"`).join(',');
    const csv = `${headers}\n${values}`;
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `product_feed_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadJSON = () => {
    const json = JSON.stringify(schemaMarkup, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schema_markup_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadHTML = () => {
    const html = `<script type="application/ld+json">\n${JSON.stringify(schemaMarkup, null, 2)}\n</script>`;
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schema_markup_${Date.now()}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    const html = `<script type="application/ld+json">\n${JSON.stringify(schemaMarkup, null, 2)}\n</script>`;
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              🛍️ Product Schema Markup Generator
            </h1>
            <p className="text-gray-600">
              Extract product data and generate Schema.org markup for ChatGPT Shopping
            </p>
          </div>

          <div className="space-y-4 mb-8">
            <div className="flex gap-3">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/product/123"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                disabled={loading}
              />
              <button
                onClick={handleGenerate}
                disabled={loading || !url}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Extracting...
                  </>
                ) : (
                  '🚀 Generate'
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-medium text-red-800">Error</h3>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {productData && schemaMarkup && (
            <div>
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-medium text-green-800">Success!</h3>
                  <p className="text-green-600 text-sm mt-1">Schema markup generated successfully</p>
                </div>
              </div>

              <div className="border-b border-gray-200 mb-6">
                <div className="flex gap-4">
                  <button
                    onClick={() => setActiveTab('data')}
                    className={`pb-3 px-2 font-medium transition-colors ${
                      activeTab === 'data'
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    📊 Product Data
                  </button>
                  <button
                    onClick={() => setActiveTab('schema')}
                    className={`pb-3 px-2 font-medium transition-colors ${
                      activeTab === 'schema'
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    🔖 Schema Markup
                  </button>
                  <button
                    onClick={() => setActiveTab('downloads')}
                    className={`pb-3 px-2 font-medium transition-colors ${
                      activeTab === 'downloads'
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    💾 Downloads
                  </button>
                </div>
              </div>

              {activeTab === 'data' && (
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <h3 className="font-semibold text-gray-800 mb-4 text-lg">Extracted Product Data</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {Object.entries(productData).map(([key, value]) => (
                      <div key={key} className="flex gap-4">
                        <span className="font-medium text-gray-700 min-w-[200px]">{key}:</span>
                        <span className="text-gray-600 break-all">{value || '—'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'schema' && (
                <div>
                  <div className="mb-4">
                    <p className="text-gray-600 mb-3">
                      Copy and paste this code into your website's <code className="bg-gray-100 px-2 py-1 rounded">&lt;head&gt;</code> section:
                    </p>
                    <button
                      onClick={copyToClipboard}
                      className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      {copied ? 'Copied!' : 'Copy to Clipboard'}
                    </button>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-green-400 text-sm">
                      <code>{`<script type="application/ld+json">\n${JSON.stringify(schemaMarkup, null, 2)}\n</script>`}</code>
                    </pre>
                  </div>
                  <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      💡 This Schema.org markup helps search engines and ChatGPT understand your product data.
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'downloads' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-gray-800 mb-2">Product Feed (CSV)</h4>
                    <p className="text-sm text-gray-600 mb-4">For product catalogs and feeds</p>
                    <button
                      onClick={downloadCSV}
                      className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download CSV
                    </button>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-gray-800 mb-2">Schema Markup (JSON)</h4>
                    <p className="text-sm text-gray-600 mb-4">Pure JSON-LD format</p>
                    <button
                      onClick={downloadJSON}
                      className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download JSON
                    </button>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-gray-800 mb-2">HTML Code</h4>
                    <p className="text-sm text-gray-600 mb-4">Ready to paste in head tag</p>
                    <button
                      onClick={downloadHTML}
                      className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download HTML
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="mt-12 pt-8 border-t border-gray-200">
            <details className="mb-4">
              <summary className="font-semibold text-gray-800 cursor-pointer hover:text-blue-600">
                ℹ️ How it works
              </summary>
              <div className="mt-3 text-gray-600 text-sm space-y-2 ml-6">
                <p><strong>1.</strong> Enter the product page URL</p>
                <p><strong>2.</strong> The tool scrapes and extracts product information</p>
                <p><strong>3.</strong> Generates proper Schema.org JSON-LD markup</p>
                <p><strong>4.</strong> Download in multiple formats or copy directly to your website</p>
              </div>
            </details>
            
            <details>
              <summary className="font-semibold text-gray-800 cursor-pointer hover:text-blue-600">
                📋 ChatGPT Shopping Requirements
              </summary>
              <div className="mt-3 text-gray-600 text-sm ml-6">
                <p className="font-medium mb-2">Required Fields:</p>
                <ul className="list-disc ml-5 space-y-1">
                  <li>enable_search, enable_checkout</li>
                  <li>id, title, description, link</li>
                  <li>condition, brand, image_link</li>
                  <li>price, availability</li>
                </ul>
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductSchemaGenerator;
