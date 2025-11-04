#!/usr/bin/env python3
"""
Create Shopify Metafield Definitions from Product Config
"""

import argparse
import requests
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

def load_shopify_credentials():
    """Load Shopify credentials"""
    try:
        import importlib.util
        config_path = Path(__file__).parent.parent / 'config.py'
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config.SHOPIFY_CONFIG['SHOP_URL'], config.SHOPIFY_CONFIG['ACCESS_TOKEN']
    except Exception as e:
        print(f"❌ Could not load config: {e}")
        return None, None

def get_metafields_for_product_type(product_type: str) -> list:
    """Get metafield definitions based on product type"""
    
    # Load product config
    try:
        import yaml
        config_path = Path(__file__).parent.parent / 'config' / 'products' / f'{product_type}.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
            extra_fields = config.get('extra_fields', [])
    except:
        print(f"❌ Could not load product config for {product_type}")
        return []
    
    # Create metafield definitions
    metafields = []
    
    for field in extra_fields:
        metafields.append({
            'namespace': product_type,
            'key': field,
            'name': field.replace('_', ' ').title(),
            'type': 'single_line_text_field'  # Default type
        })
    
    return metafields

def create_metafield_definition(shop_url: str, access_token: str, metafield: dict):
    """Create a metafield definition in Shopify"""
    
    mutation = """
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
    
    variables = {
        "definition": {
            "name": metafield['name'],
            "namespace": metafield['namespace'],
            "key": metafield['key'],
            "type": metafield['type'],
            "ownerType": "PRODUCT"
        }
    }
    
    url = f"{shop_url}/admin/api/2025-07/graphql.json"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json={"query": mutation, "variables": variables})
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('data', {}).get('metafieldDefinitionCreate', {}).get('createdDefinition'):
            print(f"  ✅ Created: {metafield['namespace']}.{metafield['key']}")
            return True
        else:
            errors = result.get('data', {}).get('metafieldDefinitionCreate', {}).get('userErrors', [])
            if errors:
                # Check if already exists
                if any('already exists' in e.get('message', '').lower() for e in errors):
                    print(f"  ⏭️  Already exists: {metafield['namespace']}.{metafield['key']}")
                    return True
                else:
                    print(f"  ❌ Failed: {metafield['namespace']}.{metafield['key']} - {errors}")
            return False
    else:
        print(f"  ❌ HTTP {response.status_code}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Shopify Metafields")
    parser.add_argument("--product", required=True, help="Product type (e.g., fish, wine)")
    
    args = parser.parse_args()
    
    print("🏷️  Shopify Metafields Setup")
    print("=" * 40)
    
    # Load credentials
    shop_url, access_token = load_shopify_credentials()
    if not shop_url:
        return 1
    
    print(f"🏪 Store: {shop_url}")
    print(f"📦 Product Type: {args.product}")
    
    # Get metafields for product type
    metafields = get_metafields_for_product_type(args.product)
    
    if not metafields:
        print("❌ No metafields to create")
        return 1
    
    print(f"\n📋 Creating {len(metafields)} metafield definitions...")
    
    # Create each metafield
    success_count = 0
    for mf in metafields:
        if create_metafield_definition(shop_url, access_token, mf):
            success_count += 1
    
    print(f"\n✅ Metafields setup complete: {success_count}/{len(metafields)} ready")
    return 0

if __name__ == "__main__":
    sys.exit(main())
