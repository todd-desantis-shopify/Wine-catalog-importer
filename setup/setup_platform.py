#!/usr/bin/env python3
"""
Platform Setup Tool - Collections and Metafields
Automatically sets up collections and metafields for any e-commerce platform based on configuration.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Any, List, Set
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.config_manager import ConfigManager
from setup.platforms.shopify_setup import ShopifySetup

class PlatformSetupManager:
    """Manages platform setup for collections and metafields"""
    
    def __init__(self, platform_config: Dict[str, Any], product_config: Dict[str, Any]):
        """Initialize setup manager"""
        self.platform_config = platform_config
        self.product_config = product_config
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform-specific setup
        platform_name = platform_config.get('platform', '').lower()
        if platform_name == 'shopify':
            self.platform_setup = ShopifySetup(platform_config)
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")
    
    def setup_metafields(self) -> bool:
        """Create metafield definitions"""
        self.logger.info("🏷️  Setting up metafields...")
        
        metafields = self.platform_config.get('metafields', [])
        if not metafields:
            self.logger.warning("No metafields defined in configuration")
            return True
        
        success_count = 0
        for metafield in metafields:
            try:
                if self.platform_setup.create_metafield_definition(metafield):
                    success_count += 1
                    self.logger.info(f"✅ Created metafield: {metafield['namespace']}.{metafield['key']}")
                else:
                    self.logger.warning(f"⚠️  Metafield already exists: {metafield['namespace']}.{metafield['key']}")
            except Exception as e:
                self.logger.error(f"❌ Failed to create metafield {metafield['namespace']}.{metafield['key']}: {e}")
        
        self.logger.info(f"✅ Metafields setup complete: {success_count}/{len(metafields)} created")
        return success_count > 0
    
    def analyze_csv_for_collections(self, csv_file: str) -> Dict[str, Set[str]]:
        """Analyze CSV data to determine what collections to create"""
        self.logger.info(f"📊 Analyzing CSV data: {csv_file}")
        
        collections_data = {}
        collection_rules = self.product_config.get('collections', [])
        
        if not collection_rules:
            self.logger.warning("No collection rules defined in product config")
            return collections_data
        
        # Read CSV data
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            return collections_data
        
        # Analyze data for each collection rule
        for rule in collection_rules:
            condition = rule.get('condition', '')
            name_pattern = rule.get('name_pattern', '')
            
            if not condition or not name_pattern:
                continue
            
            # Simple field-based collections
            if condition in rows[0].keys():
                unique_values = set()
                for row in rows:
                    value = row.get(condition, '').strip()
                    if value:
                        unique_values.add(value)
                
                # Generate collection names
                for value in unique_values:
                    collection_name = name_pattern.format(**{condition: value})
                    if collection_name not in collections_data:
                        collections_data[collection_name] = set()
                    collections_data[collection_name].add(value)
            
            # Price-based collections (smart collections)
            elif 'price' in condition:
                collection_name = name_pattern
                if collection_name not in collections_data:
                    collections_data[collection_name] = set(['price_rule'])
        
        self.logger.info(f"📋 Found {len(collections_data)} collections to create")
        return collections_data
    
    def setup_collections(self, csv_file: str) -> bool:
        """Create collections based on CSV data analysis"""
        self.logger.info("📚 Setting up collections...")
        
        # Analyze CSV to determine collections
        collections_data = self.analyze_csv_for_collections(csv_file)
        
        if not collections_data:
            self.logger.warning("No collections to create")
            return True
        
        # Get collection templates from platform config
        templates = self.platform_config.get('collection_templates', {})
        collection_rules = self.product_config.get('collections', [])
        
        success_count = 0
        
        for collection_name, values in collections_data.items():
            try:
                # Find matching rule
                rule_type = self._find_rule_type(collection_name, collection_rules)
                
                # Create collection
                if self.platform_setup.create_collection(collection_name, rule_type, templates, values):
                    success_count += 1
                    self.logger.info(f"✅ Created collection: {collection_name}")
                else:
                    self.logger.warning(f"⚠️  Collection already exists: {collection_name}")
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to create collection {collection_name}: {e}")
        
        self.logger.info(f"✅ Collections setup complete: {success_count}/{len(collections_data)} created")
        return success_count > 0
    
    def _find_rule_type(self, collection_name: str, collection_rules: List[Dict[str, Any]]) -> str:
        """Find the rule type for a collection name"""
        for rule in collection_rules:
            name_pattern = rule.get('name_pattern', '')
            rule_type = rule.get('type', 'automated')
            
            # Simple pattern matching
            if any(placeholder in name_pattern for placeholder in ['{wine_type}', '{varietal}', '{country}', '{region}']):
                if any(word in collection_name.lower() for word in ['wine', 'red', 'white', 'rosé', 'rose']):
                    return rule_type
            elif 'price' in name_pattern.lower() or '$' in name_pattern:
                if any(word in collection_name.lower() for word in ['under', '$', 'premium', 'price']):
                    return 'smart'
        
        return 'automated'  # Default
    
    def setup_all(self, csv_file: str = None) -> bool:
        """Run complete platform setup"""
        self.logger.info("🚀 Starting platform setup...")
        
        success = True
        
        # Setup metafields
        if not self.setup_metafields():
            success = False
        
        # Setup collections if CSV provided
        if csv_file:
            if not self.setup_collections(csv_file):
                success = False
        else:
            self.logger.info("ℹ️  No CSV file provided, skipping collections setup")
        
        if success:
            self.logger.info("✅ Platform setup completed successfully!")
        else:
            self.logger.warning("⚠️  Platform setup completed with some errors")
        
        return success

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Platform Setup Tool")
    parser.add_argument("--platform", required=True, help="Platform configuration name")
    parser.add_argument("--product", required=True, help="Product configuration name")
    parser.add_argument("--csv", help="CSV file to analyze for collections (optional)")
    parser.add_argument("--metafields-only", action="store_true", help="Setup metafields only")
    parser.add_argument("--collections-only", action="store_true", help="Setup collections only")
    
    args = parser.parse_args()
    
    # Load configurations
    config_manager = ConfigManager()
    
    try:
        platform_config = config_manager.load_platform_config(args.platform)
        product_config = config_manager.load_product_config(args.product)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Initialize setup manager
    try:
        setup_manager = PlatformSetupManager(platform_config, product_config)
    except Exception as e:
        print(f"❌ Setup manager initialization error: {e}")
        return 1
    
    # Run setup based on arguments
    success = True
    
    if args.metafields_only:
        success = setup_manager.setup_metafields()
    elif args.collections_only:
        if not args.csv:
            print("❌ CSV file required for collections setup")
            return 1
        success = setup_manager.setup_collections(args.csv)
    else:
        success = setup_manager.setup_all(args.csv)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
