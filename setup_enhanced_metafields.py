#!/usr/bin/env python3
"""
Enhanced Metafield Setup - Creates wine metafields with category assignments
"""

import requests

def main():
    """Create wine metafields with proper category assignments"""
    print("🍷 Setting up Enhanced Wine Metafields with Categories")
    print("=" * 60)
    print("This creates wine metafields organized by logical categories.")
    print("Metafields will appear grouped in Shopify Admin.")
    print()
    
    # Load config
    try:
        from config import SHOPIFY_CONFIG
        SHOP_URL = SHOPIFY_CONFIG['SHOP_URL']
        ACCESS_TOKEN = SHOPIFY_CONFIG['ACCESS_TOKEN']
        API_VERSION = SHOPIFY_CONFIG.get('API_VERSION', '2024-10')
        
        headers = {
            'X-Shopify-Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
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
    
    print(f"🏪 Connecting to: {SHOP_URL}")
    print(f"🔧 Using API version: {API_VERSION}")
    print()
    
    # Enhanced metafield definitions with categories
    wine_metafields = [
        # 🍷 Wine Details Category
        {
            "namespace": "wine",
            "key": "varietal", 
            "name": "Varietal",
            "description": "Primary grape variety (e.g., Cabernet Sauvignon, Chardonnay)",
            "type": "single_line_text_field",
            "category": "Wine Details"
        },
        {
            "namespace": "wine",
            "key": "vintage",
            "name": "Vintage", 
            "description": "Year the grapes were harvested",
            "type": "number_integer",
            "category": "Wine Details"
        },
        {
            "namespace": "wine", 
            "key": "abv",
            "name": "Alcohol Content (ABV)",
            "description": "Alcohol by volume percentage",
            "type": "number_decimal",
            "category": "Wine Details"
        },
        {
            "namespace": "wine",
            "key": "body",
            "name": "Body",
            "description": "Wine body: Light, Medium, or Full-bodied", 
            "type": "single_line_text_field",
            "category": "Wine Details"
        },
        {
            "namespace": "wine",
            "key": "style", 
            "name": "Style",
            "description": "Wine style: Elegant, Intense, etc.",
            "type": "single_line_text_field",
            "category": "Wine Details"
        },
        {
            "namespace": "wine",
            "key": "size",
            "name": "Bottle Size",
            "description": "Bottle size (e.g., 750ml, 1.5L)",
            "type": "single_line_text_field", 
            "category": "Wine Details"
        },
        {
            "namespace": "wine",
            "key": "wine_type",
            "name": "Wine Type", 
            "description": "Type of wine: Red, White, Rosé, Sparkling",
            "type": "single_line_text_field",
            "category": "Wine Details"
        },
        
        # 🌍 Location Category
        {
            "namespace": "wine",
            "key": "appellation",
            "name": "Appellation",
            "description": "Specific wine region (e.g., Napa Valley, Bordeaux)",
            "type": "single_line_text_field",
            "category": "Location"
        },
        {
            "namespace": "wine",
            "key": "region",
            "name": "Region", 
            "description": "Broader wine region (e.g., California, Tuscany)",
            "type": "single_line_text_field",
            "category": "Location"
        },
        {
            "namespace": "wine",
            "key": "country_state",
            "name": "Country/State",
            "description": "Country or state where wine is produced",
            "type": "single_line_text_field",
            "category": "Location"
        },
        
        # 👃 Tasting Category
        {
            "namespace": "wine",
            "key": "tasting_notes",
            "name": "Tasting Notes",
            "description": "Flavor profile and tasting characteristics",
            "type": "multi_line_text_field", 
            "category": "Tasting"
        },
        
        # ⭐ Ratings Category
        {
            "namespace": "wine",
            "key": "expert_rating",
            "name": "Expert Rating",
            "description": "Professional wine ratings (e.g., '92 • Wine Spectator')",
            "type": "single_line_text_field",
            "category": "Ratings"
        },
        {
            "namespace": "wine",
            "key": "customer_rating", 
            "name": "Customer Rating",
            "description": "Customer review rating (e.g., '4.5/5')",
            "type": "single_line_text_field",
            "category": "Ratings"
        },
        {
            "namespace": "wine",
            "key": "customer_reviews_count",
            "name": "Review Count",
            "description": "Number of customer reviews",
            "type": "number_integer",
            "category": "Ratings"
        },
        
        # 💰 Pricing Category
        {
            "namespace": "wine",
            "key": "mix_6_price",
            "name": "Mix 6 Price", 
            "description": "Discounted price when buying 6+ bottles",
            "type": "single_line_text_field",
            "category": "Pricing"
        },
        
        # 🔗 Reference Category
        {
            "namespace": "wine",
            "key": "source_url",
            "name": "Source URL",
            "description": "Original product URL from wine retailer", 
            "type": "url",
            "category": "Reference"
        }
    ]
    
    print("📋 Creating enhanced metafield definitions...")
    print()
    
    success_count = 0
    current_category = None
    
    for field in wine_metafields:
        # Print category header when it changes
        if field['category'] != current_category:
            current_category = field['category']
            print(f"\n{get_category_emoji(current_category)} {current_category}:")
        
        # Create metafield definition with enhanced properties
        definition = {
            "metafield_definition": {
                "namespace": field["namespace"],
                "key": field["key"],
                "name": field["name"], 
                "description": field["description"],
                "type": field["type"],
                "owner_type": "PRODUCT",
                "access": {
                    "storefront": "PUBLIC_READ"
                }
            }
        }
        
        # Add category assignments for wine-related products
        # This helps organize metafields in the Shopify Admin
        if field.get("category"):
            definition["metafield_definition"]["category"] = field["category"]
        
        url = f"{SHOP_URL}/admin/api/{API_VERSION}/metafield_definitions.json"
        
        try:
            response = requests.post(url, headers=headers, json=definition)
            if response.status_code == 201:
                print(f"  ✅ {field['name']}")
                success_count += 1
            elif response.status_code == 422:
                print(f"  ⚠️ {field['name']} (Already exists)")
                success_count += 1
            else:
                print(f"  ❌ {field['name']} - Error {response.status_code}")
                if response.status_code == 400:
                    error_details = response.json().get('errors', {})
                    print(f"     Details: {error_details}")
        except Exception as e:
            print(f"  ❌ {field['name']} - {e}")
    
    print()
    print("📊 Enhanced Metafield Setup Summary:")
    print(f"✅ Successfully created/verified: {success_count}/{len(wine_metafields)}")
    
    if success_count == len(wine_metafields):
        print()
        print("🎉 Enhanced Wine Metafields Ready!")
        print()
        print("✨ Your metafields are now organized by category in Shopify Admin:")
        print("  🍷 Wine Details (7 fields)")
        print("  🌍 Location (3 fields)") 
        print("  👃 Tasting (1 field)")
        print("  ⭐ Ratings (3 fields)")
        print("  💰 Pricing (1 field)")
        print("  🔗 Reference (1 field)")
        print()
        print("🔄 Next steps:")
        print("  1. python3 setup_collections.py (create collections)")
        print("  2. python3 import_wines.py your_catalog.csv (import wines)")
    else:
        print()
        print("❌ Some metafields failed to create. Check your API credentials and try again.")

def get_category_emoji(category):
    """Get emoji for category"""
    emoji_map = {
        "Wine Details": "🍷",
        "Location": "🌍", 
        "Tasting": "👃",
        "Ratings": "⭐",
        "Pricing": "💰",
        "Reference": "🔗"
    }
    return emoji_map.get(category, "📋")

if __name__ == "__main__":
    main()
