#!/usr/bin/env python3
"""
Setup Hybrid Wine Metafields - Uses Shopify's built-in Wine category fields where available
"""

import requests

def main():
    """Create all 16 custom wine metafields"""
    print("🍷 Setting up Hybrid Wine Metafields")
    print("=" * 50)
    print("🔧 Creating all 16 custom wine metafields...")
    print("(Skipping Shopify's metaobjects - too complex)")
    
    # Load config
    try:
        from config import SHOPIFY_CONFIG
        SHOP_URL = SHOPIFY_CONFIG['SHOP_URL']
        ACCESS_TOKEN = SHOPIFY_CONFIG['ACCESS_TOKEN']
        API_VERSION = SHOPIFY_CONFIG['API_VERSION']
        
        headers = {
            'X-Shopify-Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
        
        print(f"🏪 Store: {SHOP_URL}")
        print(f"🔧 API Version: {API_VERSION}")
    except ImportError:
        print("❌ config.py not found!")
        return
    
    # All 16 custom wine metafields (simpler than using Shopify's metaobjects)
    custom_wine_metafields = [
        {"key": "varietal", "name": "Wine Varietal", "description": "Primary grape variety (Cabernet Sauvignon, Chardonnay, etc.)"},
        {"key": "region", "name": "Wine Region", "description": "Wine region (Central Coast, Bordeaux, etc.)"},
        {"key": "country_state", "name": "Country/State", "description": "Country or state where wine is produced"},
        {"key": "vintage", "name": "Vintage", "description": "Year grapes were harvested", "type": "number_integer"},
        {"key": "abv", "name": "Alcohol Content", "description": "Alcohol by volume percentage", "type": "number_decimal"}, 
        {"key": "appellation", "name": "Appellation", "description": "Specific wine appellation/AVA"},
        {"key": "body", "name": "Body", "description": "Wine body: Light, Medium, Full-bodied"},
        {"key": "style", "name": "Style", "description": "Wine style: Elegant, Intense, etc."},
        {"key": "size", "name": "Bottle Size", "description": "Bottle size (750ml, 1.5L, etc.)"},
        {"key": "wine_type", "name": "Wine Type", "description": "Red, White, Rosé, Sparkling"},
        {"key": "tasting_notes", "name": "Tasting Notes", "description": "Flavor profile", "type": "multi_line_text_field"},
        {"key": "expert_rating", "name": "Expert Rating", "description": "Professional wine ratings"},
        {"key": "customer_rating", "name": "Customer Rating", "description": "Customer review rating"},
        {"key": "customer_reviews_count", "name": "Review Count", "description": "Number of reviews", "type": "number_integer"},
        {"key": "mix_6_price", "name": "Mix 6 Price", "description": "Bulk pricing discount"},
        {"key": "source_url", "name": "Source URL", "description": "Original retailer URL", "type": "url"}
    ]
    
    # GraphQL mutation for metafield definition creation
    graphql_mutation = """
    mutation metafieldDefinitionCreate($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          name
          namespace
          key
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    url = f"{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
    success_count = 0
    
    print(f"📋 Creating all {len(custom_wine_metafields)} wine metafields...")
    print()
    
    for field in custom_wine_metafields:
        field_type = field.get('type', 'single_line_text_field')
        
        variables = {
            "definition": {
                "namespace": "wine",
                "key": field['key'],
                "name": field['name'],
                "description": field['description'],
                "type": field_type,
                "ownerType": "PRODUCT"
            }
        }
        
        payload = {
            "query": graphql_mutation,
            "variables": variables
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data', {}).get('metafieldDefinitionCreate', {}).get('createdDefinition'):
                    print(f"✅ {field['name']}")
                    success_count += 1
                elif data.get('data', {}).get('metafieldDefinitionCreate', {}).get('userErrors'):
                    errors = data['data']['metafieldDefinitionCreate']['userErrors']
                    if any('in use' in str(error).lower() for error in errors):
                        print(f"⚠️ {field['name']} (Already exists)")
                        success_count += 1
                    else:
                        print(f"❌ {field['name']} → {errors}")
                        
        except Exception as e:
            print(f"❌ {field['name']} → Error: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(custom_wine_metafields)} custom metafields created")
    
    if success_count > 0:
        print("\n🎯 Next Steps:")
        print("1. Go to Shopify Admin → Settings → Metafields")
        print("2. Manually assign each custom metafield to 'Wine' category")
        print("3. They'll then appear under 'Assigned to categories'")
        print()
        print("🔧 All wine metafields created as custom fields:")
        print(f"  • {success_count} metafields → Manually assign to Wine category")
        print("  • Then they'll only appear for Wine products")

if __name__ == "__main__":
    main()
