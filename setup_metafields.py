#!/usr/bin/env python3
"""
Setup Metafields - Run this ONCE to create all wine metafield definitions
"""

from shopify_wine_importer import ShopifyWineImporter

def main():
    """Create metafield definitions in Shopify (run once)"""
    print("🔧 Setting up Wine Metafields in Shopify")
    print("=" * 50)
    print("This script creates all 16 wine metafield definitions.")
    print("You only need to run this ONCE per Shopify store.")
    print()
    
    # Load config
    try:
        from config import SHOPIFY_CONFIG
        SHOP_URL = SHOPIFY_CONFIG['SHOP_URL']
        ACCESS_TOKEN = SHOPIFY_CONFIG['ACCESS_TOKEN']
        print("✅ Loaded configuration from config.py")
    except ImportError:
        print("❌ config.py not found!")
        print("1. Copy config_template.py to config.py")
        print("2. Add your Shopify store URL and access token")
        return
    
    # Check for placeholder values
    if SHOP_URL in ["https://YOUR-STORE.myshopify.com", "https://your-store.myshopify.com"] or ACCESS_TOKEN in ["YOUR_ACCESS_TOKEN_HERE", "your_access_token_here"]:
        print("❌ Please configure config.py with your real Shopify credentials:")
        print("   - SHOP_URL: https://your-store-name.myshopify.com") 
        print("   - ACCESS_TOKEN: Your Shopify Admin API token")
        return
    
    # Initialize importer
    importer = ShopifyWineImporter(SHOP_URL, ACCESS_TOKEN)
    
    print(f"\n🏪 Connecting to: {SHOP_URL}")
    print("📋 Creating metafield definitions...")
    print()
    
    # Create all metafield definitions
    success = importer.create_metafield_definitions()
    
    if success:
        print("\n🎉 Setup Complete!")
        print("All wine metafield definitions are now available in your Shopify store:")
        print()
        print("✅ wine.varietal          (Text)")
        print("✅ wine.vintage           (Number)")
        print("✅ wine.appellation       (Text)")
        print("✅ wine.region            (Text)")
        print("✅ wine.country_state     (Text)")
        print("✅ wine.abv               (Decimal)")
        print("✅ wine.body              (Text)")
        print("✅ wine.style             (Text)")
        print("✅ wine.tasting_notes     (Multi-line Text)")
        print("✅ wine.expert_rating     (Text)")
        print("✅ wine.customer_rating   (Text)")
        print("✅ wine.customer_reviews_count (Number)")
        print("✅ wine.mix_6_price       (Text)")
        print("✅ wine.source_url        (URL)")
        print("✅ wine.size              (Text)")
        print("✅ wine.wine_type         (Text)")
        print()
        print("🍷 You can now import wine products using:")
        print("   python3 import_wines.py")
    else:
        print("\n❌ Setup failed. Check your API credentials and try again.")

if __name__ == "__main__":
    main()
