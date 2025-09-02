#!/usr/bin/env python3
"""
Test API Import - Demo how to import wine data directly to Shopify
"""

from shopify_wine_importer import ShopifyWineImporter

def main():
    """Test API import with credentials"""
    print("🧪 Testing API Import (Demo Mode)")
    print("=" * 50)
    
    # For demo purposes - normally you'd import from config.py
    SHOP_URL = "https://your-store.myshopify.com" 
    ACCESS_TOKEN = "your_access_token_here"
    
    # Initialize importer with API credentials
    importer = ShopifyWineImporter(SHOP_URL, ACCESS_TOKEN)
    
    # Read wine data
    print("📖 Reading wine data...")
    wines = importer.read_wine_csv('sample_wine_catalog.csv')
    
    if not wines:
        print("❌ No wine data found!")
        return
    
    print(f"Found {len(wines)} wines to import")
    
    # Transform to Shopify format
    print("\n🔄 Transforming data...")
    shopify_products = importer.transform_to_shopify_format(wines)
    
    # Step 1: Create metafield definitions
    print("\n🔧 Creating metafield definitions...")
    if SHOP_URL == "https://your-store.myshopify.com":
        print("⚠️ Demo mode - API credentials not configured")
        print("To actually create metafields and products:")
        print("1. Copy config_template.py to config.py")
        print("2. Fill in your Shopify store URL and access token")  
        print("3. Run this script again")
    else:
        importer.create_metafield_definitions()
        
        # Step 2: Create products
        print("\n📦 Creating products...")
        for product_data in shopify_products:
            success = importer.create_product(product_data)
            if not success:
                break
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
