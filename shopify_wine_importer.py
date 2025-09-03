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
                    "namespace": "rating",
                    "key": "expert_rating",
                    "value": wine.expert_rating,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "rating",
                    "key": "customer_rating",
                    "value": wine.customer_rating,
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "rating",
                    "key": "review_count",
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
                    "namespace": "general",
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
                    # Assign to Wine category in Shopify's Standard Product Taxonomy
                    # Note: Verify this Wine category ID in your Shopify admin
                    "category": {
                        "id": "gid://shopify/TaxonomyCategory/fb-1-1-7"  # Wine category
                    },
                    "variants": [
                        {
                            "price": str(price),
                            "sku": wine.sku,
                            "inventory_management": "shopify",
                            "inventory_policy": "deny", 
                            "inventory_quantity": 100,
                            "weight": 1.5,
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
            
            url = f"{self.shop_url}/admin/api/2024-10/metafield_definitions.json"
            
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
        """Create a single product in Shopify using GraphQL"""
        if not self.shop_url or not self.access_token:
            print("⚠️ Shopify credentials not provided - skipping API calls")
            return False
        
        try:
            # Extract product info
            product_info = product_data['product']
            variant = product_info['variants'][0]
            
            # GraphQL mutation for product creation
            create_mutation = """
            mutation productCreate($input: ProductInput!) {
              productCreate(input: $input) {
                product {
                  id
                  title
                  category {
                    id
                    name
                  }
                }
                userErrors {
                  field
                  message
                }
              }
            }
            """
            
            # Convert product data to GraphQL format
            variables = {
                "input": {
                    "title": product_info['title'],
                    "descriptionHtml": product_info['body_html'],
                    "vendor": product_info['vendor'],
                    "productType": product_info['product_type'],
                    "handle": product_info['handle'],
                    "tags": product_info['tags'].split(', '),
                    "category": product_info['category']['id']
                }
            }
            
            # Create product using GraphQL
            url = f"{self.shop_url}/admin/api/2025-07/graphql.json"
            response = requests.post(url, headers=self.headers, json={"query": create_mutation, "variables": variables})
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data', {}).get('productCreate', {}).get('product'):
                    new_product = data['data']['productCreate']['product']
                    product_id_str = new_product['id'].split('/')[-1]  # Extract numeric ID
                    
                    print(f"✅ Created product: {new_product['title']} (ID: {product_id_str})")
                    print(f"   Category: {new_product.get('category', {}).get('name', 'None')}")
                    
                    # Now add metafields to the created product
                    metafields_success = self.add_metafields_to_product(product_id_str, product_info['metafields'])
                    
                    # Add wine bottle image (non-critical)
                    variant_sku = product_info['variants'][0]['sku']
                    image_success = self.add_wine_image(product_id_str, variant_sku)
                    
                    # Set inventory at all locations (non-critical)
                    inventory_success = self.set_product_inventory(product_id_str, 100)
                    
                    # Return success if product and metafields were created successfully
                    # Image and inventory failures are non-critical warnings
                    return metafields_success
                else:
                    errors = data.get('data', {}).get('productCreate', {}).get('userErrors', [])
                    # Check if it's just a duplicate handle (existing product)
                    if any("Handle" in str(error) and "already in use" in str(error) for error in errors):
                        print(f"⚠️ Product already exists, skipping: {product_info['title']}")
                        return True  # Return True to continue with next product
                    else:
                        print(f"❌ Failed to create product: {errors}")
                        return False
            else:
                print(f"❌ Failed to create product: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating product: {e}")
            return False
    
    def add_metafields_to_product(self, product_id: str, metafields: List[Dict[str, Any]]) -> bool:
        """Add metafields to an existing product"""
        success_count = 0
        
        print(f"🔧 Adding {len(metafields)} metafields...")
        
        for metafield in metafields:
            metafield_data = {
                "metafield": {
                    "namespace": metafield['namespace'],
                    "key": metafield['key'],
                    "value": metafield['value'],
                    "type": metafield['type']
                }
            }
            
            url = f"{self.shop_url}/admin/api/2025-07/products/{product_id}/metafields.json"
            response = requests.post(url, headers=self.headers, json=metafield_data)
            
            if response.status_code == 201:
                print(f"   ✅ {metafield['namespace']}.{metafield['key']}")
                success_count += 1
            else:
                print(f"   ❌ {metafield['namespace']}.{metafield['key']} - {response.status_code}")
        
        print(f"📊 Added {success_count}/{len(metafields)} metafields")
        return success_count == len(metafields)
    
    def add_wine_image(self, product_id: str, sku: str) -> bool:
        """Add wine bottle image to product using Total Wine image URL pattern"""
        try:
            import time
            
            # Construct Total Wine image URL from SKU
            base_sku = sku.split('-')[0] if '-' in sku else sku
            image_url = f"https://www.totalwine.com/images/{base_sku}/{base_sku}-1-fr.png"
            
            print(f"🖼️ Adding image: {image_url}")
            
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
            
            image_data = {
                "image": {
                    "src": image_url,
                    "alt": f"Wine bottle image",
                    "filename": f"{base_sku}.png"
                }
            }
            
            url = f"{self.shop_url}/admin/api/2025-07/products/{product_id}/images.json"
            response = requests.post(url, headers=self.headers, json=image_data)
            
            if response.status_code == 200:
                image_info = response.json()['image']
                print(f"   ✅ Image added (ID: {image_info['id']})")
                return True
            else:
                print(f"   ❌ Image upload failed: {response.status_code}")
                if response.text:
                    print(f"      Error details: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error adding image: {e}")
            return False
    
    def set_product_inventory(self, product_id: str, quantity: int) -> bool:
        """Set inventory tracking and quantity for product at all locations (following working JS approach)"""
        try:
            print(f"📦 Setting inventory to {quantity} units at all locations...")
            
            # Step 1: Get product variant and inventory item ID
            product_url = f"{self.shop_url}/admin/api/2025-07/products/{product_id}.json"
            product_response = requests.get(product_url, headers=self.headers)
            
            if product_response.status_code != 200:
                print(f"   ❌ Cannot read product")
                return False
                
            product_data = product_response.json()['product']
            variant_id = product_data['variants'][0]['id']
            inventory_item_id = product_data['variants'][0]['inventory_item_id']
            
            # Step 2: Enable inventory tracking
            inventory_item_data = {
                "inventory_item": {
                    "tracked": True
                }
            }
            
            inventory_url = f"{self.shop_url}/admin/api/2025-07/inventory_items/{inventory_item_id}.json"
            inventory_response = requests.put(inventory_url, headers=self.headers, json=inventory_item_data)
            
            if inventory_response.status_code == 200:
                print(f"   ✅ Inventory tracking enabled")
            else:
                print(f"   ❌ Failed to enable tracking: {inventory_response.status_code}")
                return False
            
            # Step 3: Get all locations
            locations_url = f"{self.shop_url}/admin/api/2025-07/locations.json"
            locations_response = requests.get(locations_url, headers=self.headers)
            
            if locations_response.status_code != 200:
                print(f"   ❌ Cannot read locations")
                return False
                
            locations = locations_response.json()['locations']
            print(f"   📍 Found {len(locations)} locations")
            
            # Step 4: Connect inventory item to all locations (like JS code)
            print(f"   🔗 Connecting inventory item to all locations...")
            for location in locations:
                # Check if already connected
                query_url = f"{self.shop_url}/admin/api/2025-07/inventory_levels.json?inventory_item_ids={inventory_item_id}&location_ids={location['id']}"
                query_response = requests.get(query_url, headers=self.headers)
                
                if query_response.status_code == 200:
                    inventory_levels = query_response.json().get('inventory_levels', [])
                    if not inventory_levels:
                        # Connect inventory item to this location
                        connect_url = f"{self.shop_url}/admin/api/2025-07/inventory_levels/connect.json"
                        connect_data = {
                            "inventory_item_id": inventory_item_id,
                            "location_id": location['id']
                        }
                        
                        connect_response = requests.post(connect_url, headers=self.headers, json=connect_data)
                        if connect_response.status_code == 200:
                            print(f"     ✅ Connected to {location['name']}")
                        else:
                            print(f"     ⚠️ Could not connect to {location['name']}")
                    else:
                        print(f"     ✅ Already connected to {location['name']}")
            
            # Step 5: Use GraphQL to set inventory at all locations (following JS approach)
            graphql_url = f"{self.shop_url}/admin/api/2025-07/graphql.json"
            
            # Build quantities array for all locations
            quantities = []
            for location in locations:
                quantities.append({
                    "inventoryItemId": f"gid://shopify/InventoryItem/{inventory_item_id}",
                    "locationId": f"gid://shopify/Location/{location['id']}",
                    "quantity": quantity
                })
            
            mutation = """
            mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
              inventorySetQuantities(input: $input) {
                inventoryAdjustmentGroup {
                  reason
                  changes {
                    name
                    delta
                  }
                }
                userErrors {
                  field
                  message
                }
              }
            }
            """
            
            variables = {
                "input": {
                    "name": "available",
                    "reason": "correction",
                    "ignoreCompareQuantity": True,
                    "quantities": quantities
                }
            }
            
            graphql_response = requests.post(graphql_url, headers=self.headers, json={"query": mutation, "variables": variables})
            
            if graphql_response.status_code == 200:
                data = graphql_response.json()
                
                if data.get('data', {}).get('inventorySetQuantities', {}).get('userErrors'):
                    errors = data['data']['inventorySetQuantities']['userErrors']
                    if errors:
                        print(f"   ❌ Inventory GraphQL errors: {errors}")
                        return False
                
                changes = data.get('data', {}).get('inventorySetQuantities', {}).get('inventoryAdjustmentGroup', {}).get('changes', [])
                if changes:
                    total_adjusted = sum(change.get('delta', 0) for change in changes)
                    print(f"   ✅ Inventory set at {len(locations)} locations (Total delta: {total_adjusted})")
                    return True
                else:
                    print(f"   ✅ Inventory set at {len(locations)} locations")
                    return True
            else:
                print(f"   ❌ GraphQL inventory update failed: {graphql_response.status_code}")
                print(f"   Response: {graphql_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error setting inventory: {e}")
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
            'metafields.rating.expert_rating', 'metafields.rating.customer_rating',
            'metafields.rating.review_count', 'metafields.wine.mix_6_price',
            'metafields.general.source_url', 'metafields.wine.size', 'metafields.wine.wine_type'
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
                    metafields_dict.get('metafields.rating.expert_rating', ''),
                    metafields_dict.get('metafields.rating.customer_rating', ''),
                    metafields_dict.get('metafields.rating.review_count', ''),
                    metafields_dict.get('metafields.wine.mix_6_price', ''),
                    metafields_dict.get('metafields.general.source_url', ''),
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
