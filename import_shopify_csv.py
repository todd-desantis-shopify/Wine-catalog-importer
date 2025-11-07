#!/usr/bin/env python3
"""
Import Shopify CSV Format with Variants
Handles the standard Shopify CSV format with multiple rows per product for variants
"""

import csv
import requests
import time
import sys
from pathlib import Path
from collections import defaultdict

def load_shopify_credentials():
    """Load Shopify credentials"""
    try:
        import importlib.util
        config_path = Path(__file__).parent / 'config.py'
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config.SHOPIFY_CONFIG['SHOP_URL'], config.SHOPIFY_CONFIG['ACCESS_TOKEN']
    except Exception as e:
        print(f"❌ Could not load config: {e}")
        return None, None

def load_product_config(product_type: str):
    """Load product config for extra fields"""
    try:
        import yaml
        config_path = Path(__file__).parent / 'config' / 'products' / f'{product_type}.yaml'
        with open(config_path) as f:
            return yaml.safe_load(f)
    except:
        return {'extra_fields': []}

def parse_shopify_csv(csv_file: str):
    """Parse Shopify CSV and group variants by product"""
    products = defaultdict(lambda: {'variants': []})
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            handle = row.get('Handle', '')
            
            # First row of product has full data
            if not products[handle]['variants']:
                products[handle]['title'] = row.get('Title', '')
                products[handle]['body_html'] = row.get('Body HTML', '')
                products[handle]['vendor'] = row.get('Vendor', 'Citarella')
                products[handle]['product_type'] = row.get('Type', '')
                products[handle]['tags'] = row.get('Tags', '')
                products[handle]['image'] = row.get('Image Src', '')
                products[handle]['status'] = row.get('Status', 'active')
                
                # Extra fields (metafields)
                products[handle]['metafields'] = {}
                for key in row.keys():
                    if key not in ['Handle', 'Title', 'Variant SKU', 'Variant Price', 'Variant Compare At Price', 
                                   'Body HTML', 'Vendor', 'Type', 'Tags', 'Image Src', 'Option1 Name', 'Option1 Value', 'Status']:
                        if row.get(key):
                            products[handle]['metafields'][key] = row[key]
            
            # Add variant
            products[handle]['variants'].append({
                'sku': row.get('Variant SKU', ''),
                'price': row.get('Variant Price', '0'),
                'compare_at_price': row.get('Variant Compare At Price', ''),
                'option1': row.get('Option1 Value', '')
            })
    
    return dict(products)

def create_product_with_variants(shop_url: str, access_token: str, handle: str, product_data: dict, product_type: str):
    """Create product with variants in Shopify"""
    
    url = f"{shop_url}/admin/api/2025-07/products.json"
    headers = {'X-Shopify-Access-Token': access_token, 'Content-Type': 'application/json'}
    
    # Build variants
    variants = []
    for variant in product_data['variants']:
        var_data = {
            'sku': variant['sku'],
            'price': variant['price'],
            'option1': variant['option1']
        }
        if variant.get('compare_at_price'):
            var_data['compare_at_price'] = variant['compare_at_price']
        variants.append(var_data)
    
    # Build product
    product = {
        'product': {
            'title': product_data['title'],
            'body_html': product_data['body_html'],
            'vendor': product_data['vendor'],
            'product_type': product_data['product_type'],
            'tags': product_data['tags'],
            'status': product_data['status'],
            'variants': variants
        }
    }
    
    # Add options if variants have option values
    if variants[0].get('option1'):
        product['product']['options'] = [{'name': 'Size', 'values': [v['option1'] for v in variants]}]
    
    response = requests.post(url, headers=headers, json=product)
    
    if response.status_code == 201:
        result = response.json()['product']
        product_id = result['id']
        
        print(f"  ✅ Created: {product_data['title']} ({len(variants)} variant(s))")
        
        # Add image
        if product_data.get('image'):
            add_image(shop_url, access_token, product_id, product_data['image'])
        
        # Add metafields
        add_metafields(shop_url, access_token, product_id, product_data['metafields'], product_type)
        
        return True
    else:
        error_text = response.text
        if 'already exists' in error_text.lower():
            print(f"  ⏭️  Already exists: {product_data['title']}")
            return True
        else:
            print(f"  ❌ Failed: {product_data['title']} - {response.status_code}")
            return False

def add_image(shop_url: str, access_token: str, product_id: int, image_url: str):
    """Add product image"""
    if not image_url:
        return
    
    url = f"{shop_url}/admin/api/2025-07/products/{product_id}/images.json"
    headers = {'X-Shopify-Access-Token': access_token, 'Content-Type': 'application/json'}
    
    try:
        requests.post(url, headers=headers, json={'image': {'src': image_url}}, timeout=10)
        time.sleep(0.3)
    except:
        pass

def add_metafields(shop_url: str, access_token: str, product_id: int, metafields: dict, namespace: str):
    """Add metafields to product"""
    
    url = f"{shop_url}/admin/api/2025-07/products/{product_id}/metafields.json"
    headers = {'X-Shopify-Access-Token': access_token, 'Content-Type': 'application/json'}
    
    for key, value in metafields.items():
        if value and value != 'N/A':
            data = {
                'metafield': {
                    'namespace': namespace,
                    'key': key.lower().replace(' ', '_'),
                    'value': str(value),
                    'type': 'single_line_text_field'
                }
            }
            
            try:
                requests.post(url, headers=headers, json=data, timeout=10)
                time.sleep(0.3)
            except:
                pass

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Import Shopify CSV with Variants")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--product", required=True)
    
    args = parser.parse_args()
    
    print("📦 Shopify CSV Importer (with Variants)")
    print("=" * 40)
    
    shop_url, access_token = load_shopify_credentials()
    if not shop_url:
        return 1
    
    print(f"🏪 Store: {shop_url}")
    print(f"📂 CSV: {args.csv}")
    print(f"📦 Product Type: {args.product}\n")
    
    # Parse CSV
    products = parse_shopify_csv(args.csv)
    
    print(f"🚀 Importing {len(products)} products...")
    
    # Import each
    success = 0
    for i, (handle, product_data) in enumerate(products.items(), 1):
        print(f"[{i}/{len(products)}]", end=" ")
        if create_product_with_variants(shop_url, access_token, handle, product_data, args.product):
            success += 1
        time.sleep(0.5)
    
    print(f"\n✅ Import complete: {success}/{len(products)} products")
    return 0

if __name__ == "__main__":
    sys.exit(main())
