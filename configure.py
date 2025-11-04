#!/usr/bin/env python3
"""
Configuration Setup Tool
Interactive tool to help users create configurations for new sites, products, and platforms.
"""

import argparse
import sys
from pathlib import Path
import yaml
import os

# Add config directory to path
sys.path.append(str(Path(__file__).parent))
from config.config_manager import ConfigManager

def create_site_config():
    """Interactive creation of site configuration"""
    print("🌐 Creating Site Configuration")
    print("=" * 40)
    
    site_name = input("Site name (e.g., 'amazon', 'ebay'): ").strip().lower()
    site_display_name = input("Site display name (e.g., 'Amazon'): ").strip()
    base_url = input("Base URL (e.g., 'https://www.amazon.com'): ").strip()
    
    rate_limit = input("Rate limit in seconds between requests [0.5]: ").strip()
    rate_limit = float(rate_limit) if rate_limit else 0.5
    
    print("\n🎯 CSS Selectors (leave blank if unknown, can be added later)")
    print("Note: You can use CSS selectors or text patterns like 'text*=\"Price\"'")
    
    config = {
        'site': {
            'name': site_display_name,
            'base_url': base_url,
            'rate_limit': rate_limit,
            'timeout': 30,
            'user_agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        },
        'selectors': {
            'product_name': input("Product name selector [h1]: ").strip() or "h1",
            'brand': input("Brand selector: ").strip(),
            'price': {
                'current': input("Current price selector: ").strip(),
                'compare_at': input("Compare at price selector: ").strip()
            }
        },
        'transformations': {
            'price': {
                'pattern': r'\$([0-9]+\.?[0-9]*)',
                'type': 'float'
            }
        },
        'error_handling': {
            'max_retries': 3,
            'retry_delay': 2,
            'skip_on_error': True,
            'log_errors': True
        }
    }
    
    # Save configuration
    config_path = Path(__file__).parent / "config" / "sites" / f"{site_name}.yaml"
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"\n✅ Site configuration saved to: {config_path}")
    print("💡 You can edit the file to add more detailed selectors")
    
    return config_path

def create_product_config():
    """Interactive creation of product configuration"""
    print("📦 Creating Product Configuration")
    print("=" * 40)
    
    product_type = input("Product type (e.g., 'electronics', 'clothing'): ").strip().lower()
    
    print(f"\n🏷️  Define fields for {product_type} products")
    print("Enter field names (press Enter on empty line to finish):")
    
    fields = []
    
    # Common fields
    common_fields = [
        {'name': 'name', 'type': 'string', 'required': True, 'shopify_field': 'title'},
        {'name': 'brand', 'type': 'string', 'required': True, 'shopify_field': 'vendor'},
        {'name': 'price', 'type': 'money', 'required': True, 'shopify_field': 'variant.price'},
        {'name': 'description', 'type': 'string', 'required': False, 'shopify_field': 'body_html'},
        {'name': 'sku', 'type': 'string', 'required': True, 'shopify_field': 'variant.sku'},
        {'name': 'image_url', 'type': 'string', 'required': False, 'shopify_field': 'images'}
    ]
    
    fields.extend(common_fields)
    
    # Custom fields
    while True:
        field_name = input(f"Field name: ").strip()
        if not field_name:
            break
        
        field_type = input(f"Field type [string]: ").strip() or "string"
        required = input(f"Required? [n]: ").strip().lower() in ['y', 'yes']
        metafield = input(f"Shopify metafield (e.g., 'custom.{field_name}'): ").strip()
        
        field = {
            'name': field_name,
            'type': field_type,
            'required': required
        }
        
        if metafield:
            field['shopify_metafield'] = metafield
        
        fields.append(field)
    
    config = {
        'product_type': product_type,
        'fields': fields,
        'collections': [
            {
                'name_pattern': '{brand} Products',
                'condition': 'brand',
                'type': 'automated'
            }
        ],
        'seo': {
            'title_pattern': '{name} | {brand}',
            'description_pattern': '{name} from {brand}',
            'handle_pattern': '{brand}-{name}'
        },
        'validation': {
            'price': {
                'min': 0.01,
                'max': 10000.00
            }
        }
    }
    
    # Save configuration
    config_path = Path(__file__).parent / "config" / "products" / f"{product_type}.yaml"
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"\n✅ Product configuration saved to: {config_path}")
    
    return config_path

def create_platform_config():
    """Interactive creation of platform configuration"""
    print("🏪 Creating Platform Configuration")
    print("=" * 40)
    
    platform_name = input("Platform name (e.g., 'shopify', 'woocommerce'): ").strip().lower()
    
    if platform_name == 'shopify':
        config = {
            'platform': 'shopify',
            'api_version': '2025-07',
            'auth': {
                'shop_url': '${SHOPIFY_SHOP_URL}',
                'access_token': '${SHOPIFY_ACCESS_TOKEN}'
            },
            'api': {
                'rate_limit': 0.5,
                'timeout': 30,
                'max_retries': 3,
                'batch_size': 250
            },
            'defaults': {
                'status': 'active',
                'inventory_tracking': True,
                'inventory_quantity': 100,
                'inventory_policy': 'deny',
                'requires_shipping': True,
                'taxable': True
            },
            'import': {
                'batch_size': 50,
                'concurrent_requests': 3,
                'skip_duplicates': True,
                'update_existing': True
            },
            'error_handling': {
                'continue_on_error': True,
                'log_errors': True,
                'skip_invalid_data': True,
                'validate_before_import': True
            }
        }
    else:
        print(f"❌ Platform '{platform_name}' not yet supported")
        print("Currently supported: shopify")
        return None
    
    # Save configuration
    config_path = Path(__file__).parent / "config" / "platforms" / f"{platform_name}.yaml"
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"\n✅ Platform configuration saved to: {config_path}")
    
    if platform_name == 'shopify':
        print("\n💡 Environment Variables Required:")
        print("   export SHOPIFY_SHOP_URL='https://your-store.myshopify.com'")
        print("   export SHOPIFY_ACCESS_TOKEN='your_access_token'")
    
    return config_path

def list_configurations():
    """List all available configurations"""
    config_manager = ConfigManager()
    
    print("📋 Available Configurations")
    print("=" * 40)
    
    print("🌐 Sites:")
    sites = config_manager.get_available_sites()
    for site in sites:
        print(f"   • {site}")
    
    print("\n📦 Products:")
    products = config_manager.get_available_products()
    for product in products:
        print(f"   • {product}")
    
    print("\n🏪 Platforms:")
    platforms = config_manager.get_available_platforms()
    for platform in platforms:
        print(f"   • {platform}")
    
    if not sites and not products and not platforms:
        print("   No configurations found.")

def test_configuration():
    """Test loading configurations"""
    config_manager = ConfigManager()
    
    print("🧪 Testing Configurations")
    print("=" * 40)
    
    # Test sites
    sites = config_manager.get_available_sites()
    for site in sites:
        try:
            config_manager.load_site_config(site)
            print(f"✅ Site '{site}' loads successfully")
        except Exception as e:
            print(f"❌ Site '{site}' failed to load: {e}")
    
    # Test products
    products = config_manager.get_available_products()
    for product in products:
        try:
            config_manager.load_product_config(product)
            print(f"✅ Product '{product}' loads successfully")
        except Exception as e:
            print(f"❌ Product '{product}' failed to load: {e}")
    
    # Test platforms
    platforms = config_manager.get_available_platforms()
    for platform in platforms:
        try:
            config_manager.load_platform_config(platform)
            print(f"✅ Platform '{platform}' loads successfully")
        except Exception as e:
            print(f"❌ Platform '{platform}' failed to load: {e}")

def main():
    """Main configuration function"""
    parser = argparse.ArgumentParser(description="Configuration Setup Tool")
    parser.add_argument("--create-site", action="store_true", help="Create site configuration")
    parser.add_argument("--create-product", action="store_true", help="Create product configuration")
    parser.add_argument("--create-platform", action="store_true", help="Create platform configuration")
    parser.add_argument("--list", action="store_true", help="List all configurations")
    parser.add_argument("--test", action="store_true", help="Test configurations")
    
    args = parser.parse_args()
    
    if args.create_site:
        create_site_config()
    elif args.create_product:
        create_product_config()
    elif args.create_platform:
        create_platform_config()
    elif args.list:
        list_configurations()
    elif args.test:
        test_configuration()
    else:
        print("🛠️  Generic E-commerce Catalog System - Configuration Tool")
        print("=" * 60)
        print()
        print("Available commands:")
        print("  --create-site      Create new site configuration")
        print("  --create-product   Create new product configuration")
        print("  --create-platform  Create new platform configuration")
        print("  --list             List existing configurations")
        print("  --test             Test configuration loading")
        print()
        print("Example workflow:")
        print("  1. python configure.py --create-site")
        print("  2. python configure.py --create-product")
        print("  3. python configure.py --create-platform")
        print("  4. python configure.py --test")

if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("❌ Missing required package: pyyaml")
        print("Install with: pip install pyyaml")
        exit(1)
    
    main()
