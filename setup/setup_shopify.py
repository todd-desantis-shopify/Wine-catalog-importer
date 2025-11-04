#!/usr/bin/env python3
"""
Shopify Setup - Auto-create collections from CSV data
"""

import argparse
import csv
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

def load_shopify_credentials():
    """Load Shopify credentials from config"""
    try:
        config_path = Path(__file__).parent.parent / 'config.py'
        if not config_path.exists():
            print("❌ config.py not found")
            return None, None
        
        # Import config module
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        return config.SHOPIFY_CONFIG['SHOP_URL'], config.SHOPIFY_CONFIG['ACCESS_TOKEN']
    except Exception as e:
        print(f"❌ Could not load config.py: {e}")
        return None, None

def analyze_csv_for_collections(csv_file: str) -> set:
    """Auto-detect what collections to create from CSV data"""
    
    collections = set()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Add collection from collection column
            if row.get('collection'):
                collections.add(row['collection'])
            
            # Add price-based collections
            try:
                price = float(row.get('price', 0))
                if price < 25:
                    collections.add("Under $25")
                elif price < 50:
                    collections.add("$25-$50")
                else:
                    collections.add("Premium ($50+)")
            except:
                pass
    
    return collections

def create_collection(shop_url: str, access_token: str, collection_name: str):
    """Create a smart collection in Shopify"""
    
    url = f"{shop_url}/admin/api/2025-07/custom_collections.json"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    data = {
        "custom_collection": {
            "title": collection_name,
            "published": True
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"  ✅ Created: {collection_name}")
        return True
    elif 'already exists' in response.text.lower():
        print(f"  ⏭️  Already exists: {collection_name}")
        return True
    else:
        print(f"  ❌ Failed: {collection_name} - {response.status_code}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup Shopify Collections from CSV")
    parser.add_argument("--csv", required=True, help="CSV file to analyze")
    
    args = parser.parse_args()
    
    print("🏗️  Shopify Collections Setup")
    print("=" * 40)
    
    # Load credentials
    shop_url, access_token = load_shopify_credentials()
    if not shop_url:
        return 1
    
    print(f"🏪 Store: {shop_url}")
    
    # Analyze CSV
    print(f"📊 Analyzing: {args.csv}")
    collections = analyze_csv_for_collections(args.csv)
    
    print(f"\n📋 Found {len(collections)} collections to create:")
    for c in collections:
        print(f"   • {c}")
    
    print(f"\n🚀 Creating collections...")
    
    # Create collections
    success_count = 0
    for collection_name in collections:
        if create_collection(shop_url, access_token, collection_name):
            success_count += 1
    
    print(f"\n✅ Setup complete: {success_count}/{len(collections)} collections ready")
    return 0

if __name__ == "__main__":
    sys.exit(main())