#!/usr/bin/env python3
"""
Generic Product Importer
Multi-platform product import system that can import to Shopify, WooCommerce, and other platforms.
"""

import argparse
import csv
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.config_manager import ConfigManager
from importer.platforms.shopify_importer import ShopifyImporter

class ProductImportManager:
    """Generic product import manager"""
    
    def __init__(self, platform_config: Dict[str, Any], product_config: Dict[str, Any]):
        """Initialize import manager"""
        self.platform_config = platform_config
        self.product_config = product_config
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform-specific importer
        platform_name = platform_config.get('platform', '').lower()
        if platform_name == 'shopify':
            self.platform_importer = ShopifyImporter(platform_config, product_config)
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")
    
    def load_products_from_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """Load products from CSV file"""
        self.logger.info(f"📂 Loading products from: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                products = list(reader)
                
            self.logger.info(f"📊 Loaded {len(products)} products from CSV")
            return products
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {e}")
            raise
    
    def validate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate product data against configuration rules"""
        self.logger.info("🔍 Validating product data...")
        
        valid_products = []
        validation_rules = self.product_config.get('validation', {})
        required_fields = [field['name'] for field in self.product_config.get('fields', []) if field.get('required', False)]
        
        for i, product in enumerate(products, 1):
            is_valid = True
            errors = []
            
            # Check required fields
            for field in required_fields:
                if not product.get(field):
                    errors.append(f"Missing required field: {field}")
                    is_valid = False
            
            # Validate field values
            for field_name, rules in validation_rules.items():
                value = product.get(field_name)
                if value:
                    try:
                        if field_name == 'price':
                            price = float(value)
                            if price < rules.get('min', 0) or price > rules.get('max', 10000):
                                errors.append(f"Price {price} outside valid range")
                                is_valid = False
                        elif field_name == 'abv':
                            abv = float(value)
                            if abv < rules.get('min', 0) or abv > rules.get('max', 100):
                                errors.append(f"ABV {abv} outside valid range")
                                is_valid = False
                        elif field_name == 'customer_rating':
                            rating = float(value)
                            if rating < rules.get('min', 1) or rating > rules.get('max', 5):
                                errors.append(f"Rating {rating} outside valid range")
                                is_valid = False
                    except ValueError:
                        errors.append(f"Invalid {field_name} value: {value}")
                        is_valid = False
            
            if is_valid:
                valid_products.append(product)
            else:
                self.logger.warning(f"⚠️  Product {i} validation failed: {'; '.join(errors)}")
        
        self.logger.info(f"✅ Validation complete: {len(valid_products)}/{len(products)} products valid")
        return valid_products
    
    def transform_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform product data for platform import"""
        self.logger.info("🔄 Transforming product data...")
        
        transformed_products = []
        field_mapping = self._get_field_mapping()
        defaults = self.platform_config.get('defaults', {})
        seo_config = self.product_config.get('seo', {})
        
        for product in products:
            transformed = {}
            
            # Map fields according to configuration
            for csv_field, platform_field in field_mapping.items():
                value = product.get(csv_field, '')
                if value:
                    transformed[platform_field] = value
            
            # Apply defaults
            for key, value in defaults.items():
                if key not in transformed:
                    transformed[key] = value
            
            # Generate SEO fields
            if seo_config:
                transformed.update(self._generate_seo_fields(product, seo_config))
            
            # Store original CSV data for reference
            transformed['_csv_data'] = product
            
            transformed_products.append(transformed)
        
        self.logger.info(f"✅ Transformed {len(transformed_products)} products")
        return transformed_products
    
    def _get_field_mapping(self) -> Dict[str, str]:
        """Get field mapping between CSV and platform"""
        field_mapping = {}
        platform_name = self.platform_config.get('platform', '').lower()
        
        for field in self.product_config.get('fields', []):
            csv_field = field['name']
            
            # Check for platform-specific mapping
            platform_field_key = f"{platform_name}_field"
            metafield_key = f"{platform_name}_metafield"
            
            if platform_field_key in field:
                field_mapping[csv_field] = field[platform_field_key]
            elif metafield_key in field:
                field_mapping[csv_field] = field[metafield_key]
        
        return field_mapping
    
    def _generate_seo_fields(self, product: Dict[str, Any], seo_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO fields from product data"""
        seo_fields = {}
        
        # Generate title
        title_pattern = seo_config.get('title_pattern', '{name}')
        try:
            seo_fields['seo_title'] = title_pattern.format(**product)
        except KeyError:
            seo_fields['seo_title'] = product.get('name', '')
        
        # Generate description
        desc_pattern = seo_config.get('description_pattern', '{name}')
        try:
            seo_fields['seo_description'] = desc_pattern.format(**product)
        except KeyError:
            seo_fields['seo_description'] = product.get('highlights', '')
        
        # Generate handle
        handle_pattern = seo_config.get('handle_pattern', '{name}')
        try:
            handle = handle_pattern.format(**product)
            # Clean handle for URL safety
            seo_fields['handle'] = self._clean_handle(handle)
        except KeyError:
            seo_fields['handle'] = self._clean_handle(product.get('name', ''))
        
        return seo_fields
    
    def _clean_handle(self, text: str) -> str:
        """Clean text for use as URL handle"""
        import re
        
        # Convert to lowercase
        handle = text.lower()
        
        # Replace spaces and special chars with hyphens
        handle = re.sub(r'[^a-z0-9]+', '-', handle)
        
        # Remove leading/trailing hyphens
        handle = handle.strip('-')
        
        # Limit length
        return handle[:100]
    
    async def import_products(self, products: List[Dict[str, Any]], batch_size: Optional[int] = None) -> Dict[str, int]:
        """Import products to platform"""
        self.logger.info(f"🚀 Starting product import...")
        
        if batch_size is None:
            batch_size = self.platform_config.get('import', {}).get('batch_size', 50)
        
        results = {
            'total': len(products),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Process in batches
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(products) + batch_size - 1) // batch_size
            
            self.logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} products)")
            
            batch_results = await self.platform_importer.import_batch(batch)
            
            # Update results
            results['success'] += batch_results.get('success', 0)
            results['failed'] += batch_results.get('failed', 0)
            results['skipped'] += batch_results.get('skipped', 0)
            
            # Log batch results
            self.logger.info(f"✅ Batch {batch_num} complete: {batch_results}")
        
        return results
    
    async def run_full_import(self, csv_file: str) -> Dict[str, int]:
        """Run complete import process"""
        self.logger.info("🎯 Starting full product import process...")
        
        try:
            # Load products
            products = self.load_products_from_csv(csv_file)
            
            # Validate products
            if self.platform_config.get('error_handling', {}).get('validate_before_import', True):
                products = self.validate_products(products)
            
            # Transform products
            products = self.transform_products(products)
            
            # Import products
            results = await self.import_products(products)
            
            # Log final results
            self.logger.info("=" * 60)
            self.logger.info("📊 IMPORT COMPLETE!")
            self.logger.info(f"Total Products: {results['total']}")
            self.logger.info(f"✅ Successful: {results['success']}")
            self.logger.info(f"❌ Failed: {results['failed']}")
            self.logger.info(f"⏭️  Skipped: {results['skipped']}")
            self.logger.info(f"📈 Success Rate: {(results['success']/results['total']*100):.1f}%")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Import process failed: {e}")
            raise

async def main():
    """Main import function"""
    parser = argparse.ArgumentParser(description="Generic Product Importer")
    parser.add_argument("--platform", required=True, help="Platform configuration name")
    parser.add_argument("--product", required=True, help="Product configuration name")
    parser.add_argument("--csv", required=True, help="CSV file containing product data")
    parser.add_argument("--batch-size", type=int, help="Batch size for import (overrides config)")
    parser.add_argument("--dry-run", action="store_true", help="Validate and transform only, don't import")
    
    args = parser.parse_args()
    
    # Load configurations
    config_manager = ConfigManager()
    
    try:
        platform_config = config_manager.load_platform_config(args.platform)
        product_config = config_manager.load_product_config(args.product)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Initialize import manager
    try:
        import_manager = ProductImportManager(platform_config, product_config)
    except Exception as e:
        print(f"❌ Import manager initialization error: {e}")
        return 1
    
    # Run import
    try:
        if args.dry_run:
            # Validation and transformation only
            products = import_manager.load_products_from_csv(args.csv)
            products = import_manager.validate_products(products)
            products = import_manager.transform_products(products)
            print(f"✅ Dry run complete: {len(products)} products ready for import")
        else:
            # Full import
            results = await import_manager.run_full_import(args.csv)
            success_rate = results['success'] / results['total'] * 100 if results['total'] > 0 else 0
            
            if success_rate >= 90:
                print("✅ Import completed successfully!")
                return 0
            elif success_rate >= 50:
                print("⚠️  Import completed with some issues")
                return 0
            else:
                print("❌ Import completed with significant failures")
                return 1
                
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
