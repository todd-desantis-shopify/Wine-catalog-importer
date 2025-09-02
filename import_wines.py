#!/usr/bin/env python3
"""
Import Wines - Import wine products using existing metafields
"""

import sys
import os
from shopify_wine_importer import ShopifyWineImporter

def main():
    """Import wine products from CSV file"""
    print("🍷 Wine Product Importer")
    print("=" * 50)
    
    # Check for CSV file argument
    if len(sys.argv) < 2:
        print("Usage: python3 import_wines.py <wine_catalog.csv>")
        print()
        print("Examples:")
        print("  python3 import_wines.py sample_wine_catalog.csv")
        print("  python3 import_wines.py red_wines_batch_1.csv")
        print("  python3 import_wines.py total_wine_cabernets.csv")
        print()
        print("Note: Make sure to run 'python3 setup_metafields.py' first!")
        return
    
    csv_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
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
        print("❌ Please configure config.py with your real Shopify credentials")
        return
    
    # Initialize importer
    importer = ShopifyWineImporter(SHOP_URL, ACCESS_TOKEN)
    
    print(f"📁 Importing from: {csv_file}")
    print(f"🏪 Shopify Store: {SHOP_URL}")
    print()
    
    # Read wine data
    wines = importer.read_wine_csv(csv_file)
    
    if not wines:
        print("❌ No wine data found in CSV file!")
        print("Make sure the CSV has the correct format with headers:")
        print("Name,Brand,Country_State,Region,Appellation,Wine_Type,Varietal...")
        return
    
    print(f"📊 Found {len(wines)} wines to import")
    
    # Transform to Shopify format
    print("🔄 Transforming wine data...")
    shopify_products = importer.transform_to_shopify_format(wines)
    
    # Import products (metafields should already exist)
    print("📦 Importing wine products...")
    success_count = 0
    
    for i, product_data in enumerate(shopify_products, 1):
        print(f"  [{i}/{len(shopify_products)}] {product_data['product']['title']}", end="... ")
        
        success = importer.create_product(product_data)
        if success:
            print("✅")
            success_count += 1
        else:
            print("❌")
            
            # Ask if they want to continue
            if i < len(shopify_products):
                response = input("    Continue importing? (y/n): ").lower()
                if response not in ['y', 'yes']:
                    break
    
    # Summary
    print()
    print("📋 Import Summary:")
    print(f"  ✅ Successfully imported: {success_count}")
    print(f"  ❌ Failed: {len(shopify_products) - success_count}")
    print(f"  📊 Total processed: {len(shopify_products)}")
    
    if success_count > 0:
        print()
        print("🎉 Import complete!")
        print(f"Check your Shopify admin to see the {success_count} new wine products!")
    
    # Generate CSV backup for manual import if there were failures
    if success_count < len(shopify_products):
        backup_file = f"shopify_import_backup_{csv_file.replace('.csv', '')}.csv"
        importer.generate_csv_for_manual_import(shopify_products, backup_file)
        print(f"📄 Generated backup CSV: {backup_file}")
        print("You can manually import this via Shopify Admin → Products → Import")

if __name__ == "__main__":
    main()
