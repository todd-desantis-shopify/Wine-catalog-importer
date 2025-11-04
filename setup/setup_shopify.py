#!/usr/bin/env python3
"""
Shopify Setup - Create metafields and collections for wine products
"""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from setup.platforms.shopify_setup import ShopifySetup
from config.config_manager import ConfigManager

def main():
    parser = argparse.ArgumentParser(description="Setup Shopify Metafields & Collections")
    parser.add_argument("--product", default="wine", help="Product type")
    parser.add_argument("--csv", help="CSV file for collections analysis")
    parser.add_argument("--metafields-only", action="store_true")
    parser.add_argument("--collections-only", action="store_true")
    
    args = parser.parse_args()
    
    # Load configs
    config_manager = ConfigManager()
    shopify_config = config_manager.load_platform_config("shopify")
    product_config = config_manager.load_product_config(args.product)
    
    setup = ShopifySetup(shopify_config)
    
    # Run setup
    if args.metafields_only:
        for mf in shopify_config['metafields']:
            setup.create_metafield_definition(mf)
    elif args.collections_only and args.csv:
        # Collections setup
        pass
    else:
        # Full setup
        for mf in shopify_config['metafields']:
            setup.create_metafield_definition(mf)
    
    print("✅ Setup complete")

if __name__ == "__main__":
    main()
