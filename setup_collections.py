#!/usr/bin/env python3
"""
Setup Collections - Create wine collections for better organization
"""

import requests

def main():
    """Create wine collections in Shopify"""
    print("🗂️ Setting up Wine Collections in Shopify")
    print("=" * 50)
    
    # Load config
    try:
        from config import SHOPIFY_CONFIG
        SHOP_URL = SHOPIFY_CONFIG['SHOP_URL']
        ACCESS_TOKEN = SHOPIFY_CONFIG['ACCESS_TOKEN']
        headers = {
            'X-Shopify-Access-Token': ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
    except ImportError:
        print("❌ config.py not found!")
        return
        
    # Check credentials
    if SHOP_URL in ["https://YOUR-STORE.myshopify.com", "https://your-store.myshopify.com"] or ACCESS_TOKEN in ["YOUR_ACCESS_TOKEN_HERE", "your_access_token_here"]:
        print("❌ Please configure config.py with real Shopify credentials")
        return
    
    # Define collections to create
    collections = [
        # By Wine Type (Manual - you'll add products manually)
        {
            "title": "Red Wines",
            "handle": "red-wines", 
            "body_html": "Rich and bold red wines from around the world.",
            "published": True
        },
        {
            "title": "White Wines",
            "handle": "white-wines",
            "body_html": "Crisp and refreshing white wines.",
            "published": True
        },
        {
            "title": "Rosé Wines", 
            "handle": "rose-wines",
            "body_html": "Perfect pink wines for any occasion.",
            "published": True
        },
        {
            "title": "Sparkling Wines",
            "handle": "sparkling-wines",
            "body_html": "Celebrate with our sparkling wine selection.",
            "published": True
        },
        
        # By Price Range (Automated - products auto-added by price)
        {
            "title": "Wines Under $20",
            "handle": "wines-under-20",
            "body_html": "Great value wines under $20.",
            "published": True,
            "rules": [
                {
                    "column": "variant_price",
                    "relation": "less_than", 
                    "condition": "20"
                }
            ],
            "sort_order": "price-ascending"
        },
        {
            "title": "Premium Wines $20-$50",
            "handle": "wines-20-50",
            "body_html": "Premium wines from $20 to $50.",
            "published": True,
            "rules": [
                {
                    "column": "variant_price",
                    "relation": "greater_than",
                    "condition": "19.99"
                },
                {
                    "column": "variant_price", 
                    "relation": "less_than",
                    "condition": "50"
                }
            ],
            "sort_order": "price-ascending"
        },
        {
            "title": "Luxury Wines $50+",
            "handle": "wines-over-50", 
            "body_html": "Our finest luxury wines over $50.",
            "published": True,
            "rules": [
                {
                    "column": "variant_price",
                    "relation": "greater_than",
                    "condition": "49.99"
                }
            ],
            "sort_order": "price-descending"
        },
        
        # By Varietal (Automated - products auto-added by tags)
        {
            "title": "Cabernet Sauvignon",
            "handle": "cabernet-sauvignon",
            "body_html": "Bold and structured Cabernet Sauvignon wines.",
            "published": True,
            "rules": [
                {
                    "column": "tag",
                    "relation": "equals",
                    "condition": "Cabernet Sauvignon"
                }
            ],
            "sort_order": "best-selling"
        },
        {
            "title": "Chardonnay", 
            "handle": "chardonnay",
            "body_html": "Elegant Chardonnay wines from crisp to oaky.",
            "published": True,
            "rules": [
                {
                    "column": "tag",
                    "relation": "equals", 
                    "condition": "Chardonnay"
                }
            ],
            "sort_order": "best-selling"
        },
        {
            "title": "Pinot Noir",
            "handle": "pinot-noir",
            "body_html": "Delicate and complex Pinot Noir wines.",
            "published": True,
            "rules": [
                {
                    "column": "tag",
                    "relation": "equals",
                    "condition": "Pinot Noir"
                }
            ],
            "sort_order": "best-selling"
        },
        
        # By Region (Automated)
        {
            "title": "California Wines",
            "handle": "california-wines",
            "body_html": "Exceptional wines from California's premier regions.",
            "published": True,
            "rules": [
                {
                    "column": "tag",
                    "relation": "equals",
                    "condition": "California"
                }
            ],
            "sort_order": "best-selling"
        },
        {
            "title": "Napa Valley Wines",
            "handle": "napa-valley-wines", 
            "body_html": "World-renowned wines from Napa Valley.",
            "published": True,
            "rules": [
                {
                    "column": "tag",
                    "relation": "equals",
                    "condition": "Napa Valley"
                }
            ],
            "sort_order": "best-selling"
        }
    ]
    
    print(f"Creating {len(collections)} collections...")
    print()
    
    success_count = 0
    
    for collection_data in collections:
        url = f"{SHOP_URL}/admin/api/2023-10/collections.json"
        payload = {"collection": collection_data}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                collection = response.json()['collection']
                collection_type = "Automated" if "rules" in collection_data else "Manual"
                print(f"✅ {collection['title']} ({collection_type})")
                success_count += 1
            elif response.status_code == 422:
                print(f"⚠️ {collection_data['title']} (Already exists)")
                success_count += 1
            else:
                print(f"❌ {collection_data['title']} - Error {response.status_code}")
        except Exception as e:
            print(f"❌ {collection_data['title']} - {e}")
    
    print()
    print("📊 Collection Setup Summary:")
    print(f"✅ Successfully created/verified: {success_count}/{len(collections)}")
    
    if success_count == len(collections):
        print()
        print("🎉 All collections ready!")
        print()
        print("📋 Your wine store now has:")
        print("  🍷 Wine Type collections (Red, White, Rosé, Sparkling)")
        print("  💰 Price Range collections (Under $20, $20-50, $50+)")  
        print("  🍇 Varietal collections (Cabernet, Chardonnay, Pinot Noir)")
        print("  🌍 Region collections (California, Napa Valley)")
        print()
        print("🔄 Automated collections will populate as you import wines!")
        print("🗂️ Manual collections can be organized in Shopify Admin")

if __name__ == "__main__":
    main()
