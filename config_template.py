# Shopify Configuration Template
# Copy this to config.py and fill in your actual values

SHOPIFY_CONFIG = {
    # Your Shopify store URL (e.g., 'https://your-store.myshopify.com')
    'SHOP_URL': 'https://YOUR-STORE.myshopify.com',
    
    # Your Shopify Admin API access token
    'ACCESS_TOKEN': 'YOUR_ACCESS_TOKEN_HERE',
    
    # API version (leave as is unless you need a specific version)
    'API_VERSION': '2023-10',
}

# To get your Shopify API credentials:
# 1. Go to your Shopify Admin → Settings → Apps and sales channels
# 2. Click "Develop apps for your store"  
# 3. Click "Create an app"
# 4. Give it a name like "Wine Importer"
# 5. Click "Configure Admin API scopes"
# 6. Enable these scopes:
#    - write_products
#    - read_products  
#    - write_product_listings
#    - read_product_listings
# 7. Save and install the app
# 8. Copy the Admin API access token here
