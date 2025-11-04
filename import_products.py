#!/usr/bin/env python3
"""
Generic Shopify Product Importer
Works with any product type - just provide CSV and product config
"""

import csv
import json
import requests
import time
import argparse
import sys
from pathlib import Path
from typing import Dict, List

def load_shopify_credentials():
    """Load Shopify credentials from config"""
    try:
        import importlib.util
        config_path = Path(__file__).parent / 'config.py'
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config.SHOPIFY_CONFIG['SHOP_URL'], config.SHOPIFY_CONFIG['ACCESS_TOKEN']
    except Exception as e:
        print(f"❌ Could not load config.py: {e}")
        return None, None

def load_product_config(product_type: str) -> Dict:
    """Load product configuration"""
    try:
        import yaml
        config_path = Path(__file__).parent / 'config' / 'products' / f'{product_type}.yaml'
        with open(config_path) as f:
            return yaml.safe_load(f)
    except:
        return {'extra_fields': []}

def create_product(shop_url: str, access_token: str, product_data: Dict, extra_fields: List[str]) -> bool:
    """Create product in Shopify with GraphQL"""
    
    mutation = """
    mutation productCreate($input: ProductInput!) {
        productCreate(input: $input) {
            product {
                id
                title
                variants(first: 1) {
                    edges {
                        node {
                            id
                        }
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
    
    # Build product input
    variables = {
        "input": {
            "title": product_data.get('title', ''),
            "vendor": product_data.get('brand', ''),
            "productType": product_data.get('collection', ''),
            "descriptionHtml": product_data.get('description', ''),
            "tags": [product_data.get('collection', '')],
            "status": "ACTIVE",
        }
    }
    
    # Note: Variants are created automatically with product
    # We'll update pricing via REST API after product creation
    
    url = f"{shop_url}/admin/api/2025-07/graphql.json"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json={"query": mutation, "variables": variables})
    
    if response.status_code == 200:
        result = response.json()
        
        # Check for GraphQL errors
        if 'errors' in result:
            print(f"  ❌ GraphQL errors: {result['errors']}")
            return False
        
        if result.get('data', {}).get('productCreate', {}).get('product'):
            product = result['data']['productCreate']['product']
            product_id = product['id'].split('/')[-1]
            
            # Get variant ID
            variant_id = None
            if product.get('variants', {}).get('edges'):
                variant_id = product['variants']['edges'][0]['node']['id'].split('/')[-1]
            
            print(f"  ✅ Created: {product_data['title']}")
            
            # Update variant pricing
            if variant_id:
                update_variant_pricing(shop_url, access_token, variant_id, product_data)
            
            # Add image
            if product_data.get('image_url'):
                add_product_image(shop_url, access_token, product_id, product_data['image_url'])
            
            # Add metafields for extra fields
            add_metafields(shop_url, access_token, product_id, product_data, extra_fields, product_data.get('_product_type', 'generic'))
            
            return True
        else:
            errors = result.get('data', {}).get('productCreate', {}).get('userErrors', [])
            if any('already' in e.get('message', '').lower() for e in errors):
                print(f"  ⏭️  Already exists: {product_data['title']}")
                return True
            else:
                print(f"  ❌ Failed: {product_data['title']}")
                print(f"     Errors: {errors}")
                print(f"     Response: {result}")
                return False
    else:
        print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}")
        return False

def update_variant_pricing(shop_url: str, access_token: str, variant_id: str, product_data: Dict):
    """Update variant pricing via REST API"""
    
    url = f"{shop_url}/admin/api/2025-07/variants/{variant_id}.json"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    variant_update = {
        "variant": {
            "id": int(variant_id),
            "price": str(product_data.get('price', 0)),
            "sku": product_data.get('sku', ''),
        }
    }
    
    # Add compare at price if exists
    if product_data.get('msrp'):
        try:
            msrp = float(product_data['msrp'])
            if msrp > 0:
                variant_update["variant"]["compare_at_price"] = str(msrp)
        except:
            pass
    
    try:
        requests.put(url, headers=headers, json=variant_update, timeout=10)
        time.sleep(0.3)
    except:
        pass

def add_product_image(shop_url: str, access_token: str, product_id: str, image_url: str):
    """Add image to product"""
    if not image_url or not image_url.startswith('http'):
        return
    
    url = f"{shop_url}/admin/api/2025-07/products/{product_id}/images.json"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    data = {"image": {"src": image_url}}
    
    try:
        requests.post(url, headers=headers, json=data, timeout=10)
        time.sleep(0.3)
    except:
        pass

def add_metafields(shop_url: str, access_token: str, product_id: str, product_data: Dict, extra_fields: List[str], namespace: str):
    """Add metafields for extra product data"""
    
    url = f"{shop_url}/admin/api/2025-07/products/{product_id}/metafields.json"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    for field_name in extra_fields:
        value = product_data.get(field_name, '')
        if value:
            data = {
                "metafield": {
                    "namespace": namespace,
                    "key": field_name,
                    "value": str(value),
                    "type": "single_line_text_field"
                }
            }
            
            try:
                requests.post(url, headers=headers, json=data, timeout=10)
                time.sleep(0.3)
            except:
                pass

def import_products(csv_file: str, product_type: str):
    """Import products from CSV to Shopify"""
    
    print(f"📦 Generic Shopify Product Importer")
    print("=" * 40)
    
    # Load credentials
    shop_url, access_token = load_shopify_credentials()
    if not shop_url:
        return 1
    
    print(f"🏪 Store: {shop_url}")
    print(f"📂 CSV: {csv_file}")
    print(f"📦 Product Type: {product_type}")
    
    # Load product config
    product_config = load_product_config(product_type)
    extra_fields = product_config.get('extra_fields', [])
    
    print(f"🏷️  Extra fields: {', '.join(extra_fields) if extra_fields else 'none'}")
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = list(reader)
    
    print(f"\n🚀 Importing {len(products)} products...")
    
    # Import each product
    success_count = 0
    for i, product_data in enumerate(products, 1):
        print(f"[{i}/{len(products)}]", end=" ")
        product_data['_product_type'] = product_type
        
        if create_product(shop_url, access_token, product_data, extra_fields):
            success_count += 1
        
        time.sleep(0.5)
    
    print(f"\n✅ Import complete: {success_count}/{len(products)} products imported")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Generic Shopify Product Importer")
    parser.add_argument("--csv", required=True, help="CSV file to import")
    parser.add_argument("--product", required=True, help="Product type (e.g., fish, wine)")
    
    args = parser.parse_args()
    
    return import_products(args.csv, args.product)

if __name__ == "__main__":
    sys.exit(main())
