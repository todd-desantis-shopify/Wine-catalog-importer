#!/usr/bin/env python3
"""
Setup Wine Metafields - Creates metafields assigned to Wine product category
"""

import requests

def main():
    """Create wine metafields assigned to the Wine category in Shopify taxonomy"""
    print("🍷 Setting up Wine Metafields with Proper Category Assignment")
    print("=" * 60)
    print("This creates wine metafields assigned to the 'Wine' category.")
    print("Metafields will only appear for products categorized as Wine.")
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
    
    # Wine metafield definitions assigned to Wine product category
    wine_metafields = [
        {
            "namespace": "wine",
            "key": "varietal", 
            "name": "Varietal",
            "description": "Primary grape variety (e.g., Cabernet Sauvignon, Chardonnay)",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "vintage",
            "name": "Vintage", 
            "description": "Year the grapes were harvested",
            "type": "number_integer"
        },
        {
            "namespace": "wine", 
            "key": "abv",
            "name": "Alcohol Content (ABV)",
            "description": "Alcohol by volume percentage",
            "type": "number_decimal"
        },
        {
            "namespace": "wine",
            "key": "body",
            "name": "Body",
            "description": "Wine body: Light, Medium, or Full-bodied", 
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "style", 
            "name": "Style",
            "description": "Wine style: Elegant, Intense, etc.",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "size",
            "name": "Bottle Size",
            "description": "Bottle size (e.g., 750ml, 1.5L)",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "wine_type",
            "name": "Wine Type", 
            "description": "Type of wine: Red, White, Rosé, Sparkling",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "appellation",
            "name": "Appellation",
            "description": "Specific wine region (e.g., Napa Valley, Bordeaux)",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "region",
            "name": "Region", 
            "description": "Broader wine region (e.g., California, Tuscany)",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "country_state",
            "name": "Country/State",
            "description": "Country or state where wine is produced",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "tasting_notes",
            "name": "Tasting Notes",
            "description": "Flavor profile and tasting characteristics",
            "type": "multi_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "expert_rating",
            "name": "Expert Rating",
            "description": "Professional wine ratings (e.g., '92 • Wine Spectator')",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "customer_rating", 
            "name": "Customer Rating",
            "description": "Customer review rating (e.g., '4.5/5')",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "customer_reviews_count",
            "name": "Review Count",
            "description": "Number of customer reviews",
            "type": "number_integer"
        },
        {
            "namespace": "wine",
            "key": "mix_6_price",
            "name": "Mix 6 Price", 
            "description": "Discounted price when buying 6+ bottles",
            "type": "single_line_text_field"
        },
        {
            "namespace": "wine",
            "key": "source_url",
            "name": "Source URL",
            "description": "Original product URL from wine retailer", 
            "type": "url"
        }
    ]
    
    print("📋 Creating wine metafields assigned to Wine category...")
    print()
    
    success_count = 0
    
    for field in wine_metafields:
        # Create metafield definition assigned to Wine category
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
                },
                # This assigns the metafield to Wine products in Shopify's taxonomy
                "category_assignments": [
                    "gid://shopify/TaxonomyCategory/aa-2-2-2"  # Wine category ID
                ]
            }
        }
        
        url = f"{SHOP_URL}/admin/api/{API_VERSION}/metafield_definitions.json"
        
        try:
            response = requests.post(url, headers=headers, json=definition)
            if response.status_code == 201:
                print(f"✅ {field['name']} → assigned to Wine category")
                success_count += 1
            elif response.status_code == 422:
                error_details = response.json().get('errors', {})
                if 'already exists' in str(error_details).lower():
                    print(f"⚠️ {field['name']} → already exists")
                    success_count += 1
                else:
                    print(f"❌ {field['name']} → {error_details}")
            else:
                print(f"❌ {field['name']} → Error {response.status_code}")
                if response.text:
                    print(f"   Details: {response.text}")
        except Exception as e:
            print(f"❌ {field['name']} → {e}")
    
    print()
    print("📊 Wine Metafield Setup Summary:")
    print(f"✅ Successfully created/verified: {success_count}/{len(wine_metafields)}")
    
    if success_count == len(wine_metafields):
        print()
        print("🎉 Wine Category Metafields Ready!")
        print()
        print("✨ Your metafields are now:")
        print("  🍷 Assigned to the Wine product category")
        print("  📋 Will only appear for Wine products")
        print("  🔍 Available on storefront via API")
        print("  🏪 Organized in Shopify Admin")
        print()
        print("🍇 Metafields created:")
        for field in wine_metafields:
            print(f"  • wine.{field['key']}")
        print()
        print("🔄 Next steps:")
        print("  1. Assign your products to 'Wine' category in Shopify taxonomy")
        print("  2. python3 setup_collections.py (create collections)")
        print("  3. python3 import_wines.py your_catalog.csv (import wines)")
        print()
        print("💡 Note: Products must be categorized as 'Wine' to use these metafields!")
    else:
        print()
        print("❌ Some metafields failed. Check API credentials and try again.")

if __name__ == "__main__":
    main()
