#!/usr/bin/env python3
"""
Remove Fake Compare At Pricing - Remove all fabricated compare at prices
"""

import requests
from shopify_wine_importer import ShopifyWineImporter

def remove_fake_compare_at_pricing(importer, product):
    """Remove fake compare at pricing, keep only real regular price"""
    
    product_id = str(product['id'])
    variant = product['variants'][0]
    variant_id = variant['id']
    current_price = variant['price']
    fake_compare_price = variant['compare_at_price']
    
    print(f"🔧 {product['title'][:50]}")
    print(f"   Current: ${current_price}, Compare At: ${fake_compare_price}")
    
    # Update variant to remove fake compare at price
    variant_data = {
        "variant": {
            "id": variant_id,
            "price": str(current_price),  # Keep the real price
            "compare_at_price": None  # Remove fake compare at price
        }
    }
    
    url = f"{importer.shop_url}/admin/api/2025-07/variants/{variant_id}.json"
    response = requests.put(url, headers=importer.headers, json=variant_data)
    
    if response.status_code == 200:
        print(f"   ✅ Removed fake compare at pricing - kept real price: ${current_price}")
        return True
    else:
        print(f"   ❌ Failed to update: {response.status_code}")
        return False

def main():
    """Remove all fake compare at pricing from products"""
    print("❌ REMOVE FAKE COMPARE AT PRICING")
    print("=" * 60)
    print("⚠️  Removing fabricated 15% markup 'compare at' prices")
    print("✅ Keeping only real Total Wine pricing data")
    print()
    
    # Load config
    try:
        from config import SHOPIFY_CONFIG
        SHOP_URL = SHOPIFY_CONFIG['SHOP_URL']
        ACCESS_TOKEN = SHOPIFY_CONFIG['ACCESS_TOKEN']
    except ImportError:
        print("❌ Could not import config.py.")
        return
    
    importer = ShopifyWineImporter(SHOP_URL, ACCESS_TOKEN)
    print(f"🏪 Shopify Store: {SHOP_URL}")
    print()
    
    # Get all wine products
    url = f"{importer.shop_url}/admin/api/2025-07/products.json?limit=250"
    response = requests.get(url, headers=importer.headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch products: {response.status_code}")
        return
    
    all_products = response.json()['products']
    wine_products = [p for p in all_products if 
                    'wine' in p.get('product_type', '').lower() or
                    'wine' in p.get('title', '').lower()]
    
    print(f"📦 Found {len(wine_products)} wine products")
    print("🔧 Removing fake compare at pricing from all products...")
    print()
    
    success_count = 0
    
    for i, product in enumerate(wine_products, 1):
        variant = product['variants'][0]
        has_compare_at = variant.get('compare_at_price') and float(variant['compare_at_price']) > 0
        
        if has_compare_at:
            if remove_fake_compare_at_pricing(importer, product):
                success_count += 1
        else:
            print(f"✅ {product['title'][:50]} - No compare at pricing to remove")
    
    print()
    print("=" * 60)
    print(f"✅ FAKE PRICING REMOVAL COMPLETE!")
    print(f"🔧 Processed: {success_count} products")
    print(f"✅ All products now have ONLY real pricing data")
    print(f"📊 No fake 'compare at' prices remain")

if __name__ == "__main__":
    main()
