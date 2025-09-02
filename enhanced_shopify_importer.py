#!/usr/bin/env python3
"""
Enhanced Shopify Wine Importer with Collections and Better Organization
"""

import requests
from shopify_wine_importer import ShopifyWineImporter, WineProduct
from typing import Dict, List, Any

class EnhancedWineImporter(ShopifyWineImporter):
    """Enhanced importer with Collections and better categorization"""
    
    def __init__(self, shop_url: str = None, access_token: str = None):
        super().__init__(shop_url, access_token)
        
        # Define wine collections we'll auto-create
        self.wine_collections = [
            # By Wine Type
            {"handle": "red-wines", "title": "Red Wines", "type": "manual"},
            {"handle": "white-wines", "title": "White Wines", "type": "manual"},
            {"handle": "rose-wines", "title": "Rosé Wines", "type": "manual"}, 
            {"handle": "sparkling-wines", "title": "Sparkling Wines", "type": "manual"},
            {"handle": "dessert-wines", "title": "Dessert Wines", "type": "manual"},
            
            # By Region (will be created dynamically)
            
            # By Price Range
            {"handle": "wines-under-20", "title": "Wines Under $20", "type": "automated", 
             "rules": [{"column": "variant_price", "relation": "less_than", "condition": "20"}]},
            {"handle": "wines-20-50", "title": "$20 - $50 Wines", "type": "automated",
             "rules": [
                 {"column": "variant_price", "relation": "greater_than", "condition": "19.99"},
                 {"column": "variant_price", "relation": "less_than", "condition": "50"}
             ]},
            {"handle": "wines-over-50", "title": "Premium Wines $50+", "type": "automated",
             "rules": [{"column": "variant_price", "relation": "greater_than", "condition": "49.99"}]},
             
            # By Rating 
            {"handle": "highly-rated-wines", "title": "Highly Rated Wines (90+ Points)", "type": "manual"}
        ]
        
        # Enhanced metafields with better categorization
        self.wine_metafields_enhanced = {
            'varietal': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'wine_details'},
            'vintage': {'type': 'number_integer', 'namespace': 'wine', 'category': 'wine_details'},
            'appellation': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'location'},
            'region': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'location'},
            'country_state': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'location'},
            'abv': {'type': 'number_decimal', 'namespace': 'wine', 'category': 'wine_details'},
            'body': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'tasting'},
            'style': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'tasting'},
            'tasting_notes': {'type': 'multi_line_text_field', 'namespace': 'wine', 'category': 'tasting'},
            'expert_rating': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'ratings'},
            'customer_rating': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'ratings'},
            'customer_reviews_count': {'type': 'number_integer', 'namespace': 'wine', 'category': 'ratings'},
            'mix_6_price': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'pricing'},
            'source_url': {'type': 'url', 'namespace': 'wine', 'category': 'reference'},
            'size': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'wine_details'},
            'wine_type': {'type': 'single_line_text_field', 'namespace': 'wine', 'category': 'wine_details'}
        }

    def create_collection(self, collection_data: Dict[str, Any]) -> bool:
        """Create a collection in Shopify"""
        if not self.shop_url or not self.access_token:
            return False
            
        url = f"{self.shop_url}/admin/api/2023-10/collections.json"
        
        payload = {"collection": collection_data}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 201:
                collection = response.json()['collection']
                print(f"✅ Created collection: {collection['title']} (ID: {collection['id']})")
                return True
            elif response.status_code == 422:
                print(f"⚠️ Collection already exists: {collection_data['title']}")
                return True
            else:
                print(f"❌ Failed to create collection: {collection_data['title']} - {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            return False

    def create_wine_collections(self) -> bool:
        """Create all wine collections"""
        print("🗂️ Creating wine collections...")
        success = True
        
        for collection_config in self.wine_collections:
            collection_data = {
                "title": collection_config["title"],
                "handle": collection_config["handle"],
                "published": True
            }
            
            # Add rules for automated collections
            if collection_config.get("type") == "automated" and "rules" in collection_config:
                collection_data["rules"] = collection_config["rules"]
                collection_data["sort_order"] = "best-selling"
            
            if not self.create_collection(collection_data):
                success = False
                
        return success

    def create_region_collection(self, region: str) -> bool:
        """Create a collection for a specific wine region"""
        if not region or region.lower() in ['', 'unknown', 'n/a']:
            return True
            
        handle = region.lower().replace(' ', '-').replace(',', '').replace('/', '-')
        collection_data = {
            "title": f"{region} Wines",
            "handle": f"{handle}-wines",
            "published": True,
            "body_html": f"Wine from the {region} region."
        }
        
        return self.create_collection(collection_data)

    def add_product_to_collections(self, product_id: int, wine: WineProduct) -> bool:
        """Add a wine product to appropriate collections"""
        if not self.shop_url or not self.access_token:
            return False
            
        collections_to_add = []
        
        # Add to wine type collection
        wine_type_lower = wine.wine_type.lower()
        if 'red' in wine_type_lower:
            collections_to_add.append('red-wines')
        elif 'white' in wine_type_lower:
            collections_to_add.append('white-wines')  
        elif 'rosé' in wine_type_lower or 'rose' in wine_type_lower:
            collections_to_add.append('rose-wines')
        elif 'sparkling' in wine_type_lower:
            collections_to_add.append('sparkling-wines')
        elif 'dessert' in wine_type_lower:
            collections_to_add.append('dessert-wines')
        
        # Add to region collection if it exists
        if wine.region:
            region_handle = f"{wine.region.lower().replace(' ', '-').replace(',', '').replace('/', '-')}-wines"
            collections_to_add.append(region_handle)
        
        # Add to rating collection if highly rated
        if wine.expert_rating and any(char.isdigit() for char in wine.expert_rating):
            # Extract number from rating
            numbers = ''.join(filter(str.isdigit, wine.expert_rating))
            if numbers and int(numbers[:2] if len(numbers) >= 2 else numbers) >= 90:
                collections_to_add.append('highly-rated-wines')
        
        # Actually add product to collections (manual collections only)
        success = True
        for collection_handle in collections_to_add:
            # Get collection ID first
            url = f"{self.shop_url}/admin/api/2023-10/collections.json?handle={collection_handle}"
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    collections = response.json().get('collections', [])
                    if collections:
                        collection_id = collections[0]['id']
                        
                        # Add product to collection
                        collect_url = f"{self.shop_url}/admin/api/2023-10/collects.json"
                        collect_data = {
                            "collect": {
                                "product_id": product_id,
                                "collection_id": collection_id
                            }
                        }
                        
                        collect_response = requests.post(collect_url, headers=self.headers, json=collect_data)
                        if collect_response.status_code == 201:
                            print(f"  ✅ Added to collection: {collection_handle}")
                        elif collect_response.status_code == 422:
                            print(f"  ⚠️ Already in collection: {collection_handle}")
                        else:
                            print(f"  ❌ Failed to add to collection: {collection_handle}")
                            success = False
            except Exception as e:
                print(f"  ❌ Error adding to collection {collection_handle}: {e}")
                success = False
                
        return success

    def create_product_with_collections(self, product_data: Dict[str, Any], wine: WineProduct) -> bool:
        """Create product and add to appropriate collections"""
        # First create the product
        if not super().create_product(product_data):
            return False
            
        # Get the product ID from the response (we need to modify create_product to return it)
        # For now, we'll get it by searching for the product by handle
        handle = product_data['product']['handle']
        url = f"{self.shop_url}/admin/api/2023-10/products.json?handle={handle}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                products = response.json().get('products', [])
                if products:
                    product_id = products[0]['id']
                    
                    # Create region collection if it doesn't exist
                    self.create_region_collection(wine.region)
                    
                    # Add product to collections
                    self.add_product_to_collections(product_id, wine)
                    
                    return True
        except Exception as e:
            print(f"❌ Error adding product to collections: {e}")
            
        return False

def main():
    """Test enhanced importer"""
    print("🍷 Enhanced Wine Importer with Collections")
    print("=" * 50)
    
    # Load config
    try:
        from config import SHOPIFY_CONFIG
        SHOP_URL = SHOPIFY_CONFIG['SHOP_URL']
        ACCESS_TOKEN = SHOPIFY_CONFIG['ACCESS_TOKEN']
    except ImportError:
        print("❌ config.py not found!")
        return
        
    # Initialize enhanced importer
    importer = EnhancedWineImporter(SHOP_URL, ACCESS_TOKEN)
    
    # Create collections first
    importer.create_wine_collections()
    
    # Then import wines (would use create_product_with_collections)
    print("✅ Enhanced setup complete!")

if __name__ == "__main__":
    main()
