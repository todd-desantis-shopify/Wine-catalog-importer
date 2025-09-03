#!/usr/bin/env python3
"""
Create smart wine collections with tag-based rules and sales channel assignments
"""

import requests

def main():
    """Create smart wine collections using GraphQL"""
    print("🗂️ Creating Smart Wine Collections")
    print("=" * 50)
    
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
    except ImportError:
        print("❌ config.py not found!")
        return
    
    # Smart collections with tag-based rules
    smart_collections = [
        {
            "handle": "red-wines",
            "title": "Red Wines", 
            "description": "Rich and bold red wines from around the world",
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "Red Wine"}
        },
        {
            "handle": "white-wines",
            "title": "White Wines",
            "description": "Crisp and refreshing white wines", 
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "White Wine"}
        },
        {
            "handle": "cabernet-sauvignon", 
            "title": "Cabernet Sauvignon",
            "description": "Bold and structured Cabernet Sauvignon wines",
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "Cabernet Sauvignon"}
        },
        {
            "handle": "chardonnay",
            "title": "Chardonnay", 
            "description": "Elegant Chardonnay wines from crisp to oaky",
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "Chardonnay"}
        },
        {
            "handle": "pinot-noir",
            "title": "Pinot Noir",
            "description": "Delicate and complex Pinot Noir wines", 
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "Pinot Noir"}
        },
        {
            "handle": "california-wines",
            "title": "California Wines",
            "description": "Exceptional wines from California's premier regions",
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "California"}
        },
        {
            "handle": "napa-valley",
            "title": "Napa Valley Wines", 
            "description": "World-renowned wines from Napa Valley",
            "rule": {"column": "TAG", "relation": "EQUALS", "condition": "Napa Valley"}
        }
    ]
    
    # GraphQL mutation for smart collection creation
    create_mutation = """
    mutation collectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          handle
          title
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
            }
          }
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
    
    print(f"📋 Creating {len(smart_collections)} smart wine collections with sales channels...")
    print()
    
    for collection_data in smart_collections:
        variables = {
            "input": {
                "handle": collection_data["handle"],
                "title": collection_data["title"],
                "descriptionHtml": collection_data["description"],
                "ruleSet": {
                    "appliedDisjunctively": False,
                    "rules": [collection_data["rule"]]
                }
            }
        }
        
        payload = {
            "query": create_mutation,
            "variables": variables
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data', {}).get('collectionCreate', {}).get('collection'):
                    new_collection = data['data']['collectionCreate']['collection']
                    rule_info = new_collection.get('ruleSet', {}).get('rules', [{}])[0]
                    print(f"✅ {new_collection['title']}")
                    print(f"   Rule: {rule_info.get('column')} {rule_info.get('relation')} '{rule_info.get('condition')}'")
                    success_count += 1
                elif data.get('data', {}).get('collectionCreate', {}).get('userErrors'):
                    errors = data['data']['collectionCreate']['userErrors']
                    if any('already exists' in str(error).lower() for error in errors):
                        print(f"⚠️ {collection_data['title']} (Already exists)")
                        success_count += 1
                    else:
                        print(f"❌ {collection_data['title']} → {errors}")
                else:
                    print(f"❌ {collection_data['title']} → Unexpected response")
            else:
                print(f"❌ {collection_data['title']} → HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {collection_data['title']} → Error: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(smart_collections)} smart collections created")
    
    if success_count == len(smart_collections):
        print("\n🎉 All smart wine collections created!")
        print("\n🎯 Next step: Manually publish to sales channels")
        print("  1. Go to each collection in Shopify Admin")
        print("  2. Edit → Sales channels → Check Online Store, Point of Sale, Shop")
        print("  3. Save")
        print()
        print("✨ Features:")
        print("  🏷️ Automatically populate based on product tags")
        print("  🔄 Products with matching tags will appear automatically")
        print()
        print("🍷 Your wine products should automatically appear in:")
        print("  • Red Wines (products tagged 'Red Wine')")
        print("  • Cabernet Sauvignon (products tagged 'Cabernet Sauvignon')")
        print("  • California Wines (products tagged 'California')")

if __name__ == "__main__":
    main()
