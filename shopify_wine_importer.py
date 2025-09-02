#!/usr/bin/env python3
"""
Wine Catalog to Shopify Importer
Transforms crawled wine data into Shopify format with metafields
"""

import csv
import json
import requests
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class WineProduct:
    """Wine product data structure"""
    name: str
    brand: str
    country_state: str
    region: str
    appellation: str
    wine_type: str
    varietal: str
    style: str
    abv: str
    taste_notes: str
    body: str
    sku: str
    size: str
    price: str
    mix_6_price: str
    customer_rating: str
    customer_reviews: str
    expert_rating: str
    url: str
    image_url: str
    product_highlights: str

class ShopifyWineImporter:
    """Handles transformation and import of wine data to Shopify"""
    
    def __init__(self, shop_url: str = None, access_token: str = None):
        self.shop_url = shop_url
        self.access_token = access_token
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        } if access_token else {}
        
        # Define wine metafields structure
        self.wine_metafields = {
            'varietal': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'vintage': {'type': 'number_integer', 'namespace': 'wine'},
            'appellation': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'region': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'country_state': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'abv': {'type': 'number_decimal', 'namespace': 'wine'},
            'body': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'style': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'tasting_notes': {'type': 'multi_line_text_field', 'namespace': 'wine'},
            'expert_rating': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'customer_rating': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'customer_reviews_count': {'type': 'number_integer', 'namespace': 'wine'},
            'mix_6_price': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'source_url': {'type': 'url', 'namespace': 'wine'},
            'size': {'type': 'single_line_text_field', 'namespace': 'wine'},
            'wine_type': {'type': 'single_line_text_field', 'namespace': 'wine'}
        }
    
    def read_wine_csv(self, file_path: str) -> List[WineProduct]:
        """Read wine data from CSV file"""
        wines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    wine = WineProduct(
                        name=row['Name'],
                        brand=row['Brand'],
                        country_state=row['Country_State'],
                        region=row['Region'],
                        appellation=row['Appellation'],
                        wine_type=row['Wine_Type'],
                        varietal=row['Varietal'],
                        style=row['Style'],
                        abv=row['ABV'],
                        taste_notes=row['Taste_Notes'],
                        body=row['Body'],
                        sku=row['SKU'],
                        size=row['Size'],
                        price=row['Price'],
                        mix_6_price=row['Mix_6_Price'],
                        customer_rating=row['Customer_Rating'],
                        customer_reviews=row['Customer_Reviews'],
                        expert_rating=row['Expert_Rating'],
                        url=row['URL'],
                        image_url=row['Image_URL'],
                        product_highlights=row['Product_Highlights']
                    )
                    wines.append(wine)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            
        return wines
    
    def extract_vintage_from_name(self, name: str) -> int:
        """Extract vintage year from wine name"""
        # Look for 4-digit year in the name
        match = re.search(r'\b(19|20)\d{2}\b', name)
        return int(match.group()) if match else None
    
    def clean_price(self, price_str: str) -> float:
        """Convert price string to float"""
        try:
            # Remove $ and convert to float
            return float(price_str.replace('$', '').replace(',', ''))
        except:
            return 0.0
    
    def clean_abv(self, abv_str: str) -> float:
        """Convert ABV string to float"""
        try:
            # Remove % and convert to float
            return float(abv_str.replace('%', ''))
        except:
            return 0.0
    
    def generate_handle(self, name: str) -> str:
        """Generate Shopify handle from product name"""
        # Convert to lowercase, replace spaces and special chars with hyphens
        handle = re.sub(r'[^\w\s-]', '', name.lower())
        handle = re.sub(r'[-\s]+', '-', handle)
        return handle.strip('-')
    
    def transform_to_shopify_format(self, wines: List[WineProduct]) -> List[Dict[str, Any]]:
        """Transform wine data to Shopify product format with metafields"""
        shopify_products = []
        
        for wine in wines:
            vintage = self.extract_vintage_from_name(wine.name)
            handle = self.generate_handle(wine.name)
            price = self.clean_price(wine.price)
            abv = self.clean_abv(wine.abv)
            
            # Build metafields
            metafields = [
                {
                    "namespace": "wine",
                    "key": "varietal",
                    "value": wine.varietal,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine", 
                    "key": "appellation",
                    "value": wine.appellation,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "region", 
                    "value": wine.region,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "country_state",
                    "value": wine.country_state,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "abv",
                    "value": str(abv),
                    "type": "number_decimal"
                },
                {
                    "namespace": "wine",
                    "key": "body",
                    "value": wine.body,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "style",
                    "value": wine.style,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "tasting_notes",
                    "value": wine.taste_notes,
                    "type": "multi_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "expert_rating",
                    "value": wine.expert_rating,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "customer_rating",
                    "value": wine.customer_rating,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "customer_reviews_count",
                    "value": wine.customer_reviews,
                    "type": "number_integer"
                },
                {
                    "namespace": "wine",
                    "key": "mix_6_price",
                    "value": wine.mix_6_price,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "source_url",
                    "value": wine.url,
                    "type": "url"
                },
                {
                    "namespace": "wine",
                    "key": "size",
                    "value": wine.size,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "wine",
                    "key": "wine_type",
                    "value": wine.wine_type,
                    "type": "single_line_text_field"
                }
            ]
            
            # Add vintage if found
            if vintage:
                metafields.append({
                    "namespace": "wine",
                    "key": "vintage",
                    "value": str(vintage),
                    "type": "number_integer"
                })
            
            # Build Shopify product
            shopify_product = {
                "product": {
                    "title": wine.name,
                    "body_html": wine.product_highlights,
                    "vendor": wine.brand,
                    "product_type": wine.wine_type,
                    "handle": handle,
                    "tags": f"{wine.varietal}, {wine.wine_type}, {wine.region}, {wine.appellation}",
                    "variants": [
                        {
                            "price": str(price),
                            "sku": wine.sku,
                            "inventory_management": "shopify",
                            "inventory_quantity": 100,  # Default stock
                            "weight": 1.5,  # Default weight for wine bottle
                            "weight_unit": "lb"
                        }
                    ],
                    "metafields": metafields
                }
            }
            
            shopify_products.append(shopify_product)
        
        return shopify_products
    
    def create_metafield_definitions(self) -> bool:
        """Create metafield definitions in Shopify"""
        if not self.shop_url or not self.access_token:
            print("⚠️ Shopify credentials not provided - skipping API calls")
            return False
        
        success = True
        
        for key, config in self.wine_metafields.items():
            definition = {
                "metafield_definition": {
                    "namespace": config['namespace'],
                    "key": key,
                    "name": key.replace('_', ' ').title(),
                    "type": config['type'],
                    "owner_type": "PRODUCT"
                }
            }
            
            url = f"{self.shop_url}/admin/api/2023-10/metafield_definitions.json"
            
            try:
                response = requests.post(url, headers=self.headers, json=definition)
                if response.status_code == 201:
                    print(f"✅ Created metafield definition: wine.{key}")
                elif response.status_code == 422:
                    print(f"⚠️ Metafield definition already exists: wine.{key}")
                else:
                    print(f"❌ Failed to create metafield definition: wine.{key} - {response.status_code}")
                    success = False
            except Exception as e:
                print(f"❌ Error creating metafield definition {key}: {e}")
                success = False
        
        return success
    
    def create_product(self, product_data: Dict[str, Any]) -> bool:
        """Create a single product in Shopify"""
        if not self.shop_url or not self.access_token:
            print("⚠️ Shopify credentials not provided - skipping API calls")
            return False
        
        url = f"{self.shop_url}/admin/api/2023-10/products.json"
        
        try:
            response = requests.post(url, headers=self.headers, json=product_data)
            if response.status_code == 201:
                product = response.json()['product']
                print(f"✅ Created product: {product['title']} (ID: {product['id']})")
                return True
            else:
                print(f"❌ Failed to create product: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error creating product: {e}")
            return False
    
    def generate_csv_for_manual_import(self, shopify_products: List[Dict[str, Any]], output_file: str):
        """Generate CSV file for manual Shopify import"""
        
        # Define CSV headers for Shopify import
        headers = [
            'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags',
            'Published', 'Option1 Name', 'Option1 Value', 'Variant Price', 'Variant SKU',
            'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Weight',
            'Variant Weight Unit', 'Image Src',
            # Metafields
            'metafields.wine.varietal', 'metafields.wine.vintage', 'metafields.wine.appellation',
            'metafields.wine.region', 'metafields.wine.country_state', 'metafields.wine.abv',
            'metafields.wine.body', 'metafields.wine.style', 'metafields.wine.tasting_notes',
            'metafields.wine.expert_rating', 'metafields.wine.customer_rating',
            'metafields.wine.customer_reviews_count', 'metafields.wine.mix_6_price',
            'metafields.wine.source_url', 'metafields.wine.size', 'metafields.wine.wine_type'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for product_data in shopify_products:
                product = product_data['product']
                variant = product['variants'][0]
                
                # Extract metafields into a dictionary
                metafields_dict = {}
                for mf in product.get('metafields', []):
                    key = f"metafields.{mf['namespace']}.{mf['key']}"
                    metafields_dict[key] = mf['value']
                
                row = [
                    product['handle'],
                    product['title'], 
                    product['body_html'],
                    product['vendor'],
                    'Wine',  # Product Category
                    product['product_type'],
                    product['tags'],
                    'TRUE',  # Published
                    'Title',  # Option1 Name
                    'Default Title',  # Option1 Value
                    variant['price'],
                    variant['sku'],
                    'shopify',
                    variant['inventory_quantity'],
                    variant['weight'],
                    variant['weight_unit'],
                    '',  # Image Src - we'll add this later
                    # Metafields
                    metafields_dict.get('metafields.wine.varietal', ''),
                    metafields_dict.get('metafields.wine.vintage', ''),
                    metafields_dict.get('metafields.wine.appellation', ''),
                    metafields_dict.get('metafields.wine.region', ''),
                    metafields_dict.get('metafields.wine.country_state', ''),
                    metafields_dict.get('metafields.wine.abv', ''),
                    metafields_dict.get('metafields.wine.body', ''),
                    metafields_dict.get('metafields.wine.style', ''),
                    metafields_dict.get('metafields.wine.tasting_notes', ''),
                    metafields_dict.get('metafields.wine.expert_rating', ''),
                    metafields_dict.get('metafields.wine.customer_rating', ''),
                    metafields_dict.get('metafields.wine.customer_reviews_count', ''),
                    metafields_dict.get('metafields.wine.mix_6_price', ''),
                    metafields_dict.get('metafields.wine.source_url', ''),
                    metafields_dict.get('metafields.wine.size', ''),
                    metafields_dict.get('metafields.wine.wine_type', '')
                ]
                
                writer.writerow(row)
        
        print(f"✅ Generated CSV for manual import: {output_file}")

def main():
    """Main execution function"""
    print("🍷 Wine Catalog to Shopify Importer")
    print("=" * 50)
    
    # Initialize importer (without API credentials for now)
    importer = ShopifyWineImporter()
    
    # Read wine data
    print("📖 Reading wine data from CSV...")
    wines = importer.read_wine_csv('sample_wine_catalog.csv')
    print(f"Found {len(wines)} wines to process")
    
    if not wines:
        print("❌ No wine data found!")
        return
    
    # Transform to Shopify format
    print("\n🔄 Transforming to Shopify format...")
    shopify_products = importer.transform_to_shopify_format(wines)
    
    # Generate CSV for manual import
    print("\n📄 Generating CSV for manual Shopify import...")
    importer.generate_csv_for_manual_import(shopify_products, 'shopify_wine_import.csv')
    
    # Display the transformed product
    print("\n📋 Preview of transformed product:")
    print("=" * 50)
    if shopify_products:
        product = shopify_products[0]['product']
        print(f"Title: {product['title']}")
        print(f"Handle: {product['handle']}")
        print(f"Vendor: {product['vendor']}")
        print(f"Price: ${product['variants'][0]['price']}")
        print(f"Tags: {product['tags']}")
        print(f"\nMetafields ({len(product['metafields'])}):")
        for mf in product['metafields'][:5]:  # Show first 5
            print(f"  - {mf['namespace']}.{mf['key']}: {mf['value']}")
        if len(product['metafields']) > 5:
            print(f"  ... and {len(product['metafields']) - 5} more")
    
    print("\n✅ Transformation complete!")
    print("\n📝 Next steps:")
    print("1. Review the generated 'shopify_wine_import.csv' file")
    print("2. Import it into Shopify via Admin → Products → Import")
    print("3. Or provide Shopify API credentials to auto-import")

if __name__ == "__main__":
    main()
