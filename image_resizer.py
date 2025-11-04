#!/usr/bin/env python3
"""
Shopify Product Image Resizer
Downloads existing product images, checks dimensions, and resizes canvas to 750px if width < 400px
"""

import os
import requests
import json
from PIL import Image
from io import BytesIO
import time
from typing import Dict, List, Any, Tuple
from config import SHOPIFY_CONFIG

class ShopifyImageResizer:
    """Handles downloading, resizing, and re-uploading Shopify product images"""
    
    def __init__(self):
        self.shop_url = SHOPIFY_CONFIG['SHOP_URL']
        self.access_token = SHOPIFY_CONFIG['ACCESS_TOKEN']
        self.api_version = SHOPIFY_CONFIG['API_VERSION']
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        # Create folders for images
        os.makedirs('images/original', exist_ok=True)
        os.makedirs('images/resized', exist_ok=True)
        
        self.processed_count = 0
        self.resized_count = 0
        self.total_products = 0
        
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Fetch all products from Shopify store"""
        print("🔍 Fetching all products from Shopify...")
        
        all_products = []
        page_info = None
        page = 1
        
        while True:
            # Use REST API with limit and page_info for pagination
            url = f"{self.shop_url}/admin/api/{self.api_version}/products.json?limit=50&fields=id,title,images,handle,product_type"
            
            if page_info:
                url += f"&page_info={page_info}"
                
            try:
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('products', [])
                    all_products.extend(products)
                    
                    print(f"   📄 Page {page}: {len(products)} products")
                    
                    # Check for next page
                    link_header = response.headers.get('Link', '')
                    if 'next' in link_header:
                        # Extract page_info from Link header
                        import re
                        next_match = re.search(r'<[^>]*[?&]page_info=([^&>]*)>', link_header)
                        if next_match:
                            page_info = next_match.group(1)
                            page += 1
                        else:
                            break
                    else:
                        break
                else:
                    print(f"❌ Error fetching products: {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Exception fetching products: {e}")
                break
        
        self.total_products = len(all_products)
        print(f"✅ Found {self.total_products} total products")
        return all_products
    
    def download_image(self, image_url: str, filename: str) -> Tuple[bool, int, int]:
        """Download image and return success status with dimensions"""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # Save original image
                original_path = f"images/original/{filename}"
                with open(original_path, 'wb') as f:
                    f.write(response.content)
                
                # Get dimensions
                image = Image.open(BytesIO(response.content))
                width, height = image.size
                
                return True, width, height
            else:
                print(f"   ❌ Failed to download image: {response.status_code}")
                return False, 0, 0
                
        except Exception as e:
            print(f"   ❌ Error downloading image: {e}")
            return False, 0, 0
    
    def resize_image_canvas(self, original_path: str, resized_path: str, target_width: int = 750) -> bool:
        """Resize image canvas to target width with transparent background (like sips command)"""
        try:
            # Open original image
            image = Image.open(original_path)
            original_width, original_height = image.size
            
            # If image already meets width requirement, no need to resize
            if original_width >= 400:
                print(f"   ✅ Image width ({original_width}px) already sufficient, skipping resize")
                return False
            
            # Create new canvas with target width, keeping original height
            new_image = Image.new('RGBA', (target_width, original_height), (0, 0, 0, 0))
            
            # Center the original image on the new canvas
            x_offset = (target_width - original_width) // 2
            new_image.paste(image, (x_offset, 0))
            
            # Save resized image
            new_image.save(resized_path, 'PNG')
            print(f"   ✅ Resized: {original_width}x{original_height} → {target_width}x{original_height}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error resizing image: {e}")
            return False
    
    def upload_image_to_shopify(self, product_id: str, image_path: str, original_image_id: str = None) -> bool:
        """Upload resized image to Shopify product and replace original if specified"""
        try:
            # Read the resized image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64 for Shopify API
            import base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            filename = os.path.basename(image_path)
            
            # If we're replacing an existing image
            if original_image_id:
                # Update existing image
                url = f"{self.shop_url}/admin/api/{self.api_version}/products/{product_id}/images/{original_image_id}.json"
                image_data_obj = {
                    "image": {
                        "attachment": image_b64,
                        "filename": filename
                    }
                }
                
                response = requests.put(url, headers=self.headers, json=image_data_obj)
            else:
                # Add new image
                url = f"{self.shop_url}/admin/api/{self.api_version}/products/{product_id}/images.json"
                image_data_obj = {
                    "image": {
                        "attachment": image_b64,
                        "filename": filename
                    }
                }
                
                response = requests.post(url, headers=self.headers, json=image_data_obj)
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Image uploaded to Shopify successfully")
                return True
            else:
                print(f"   ❌ Failed to upload image: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Error uploading image: {e}")
            return False
    
    def process_product_images(self, product: Dict[str, Any]) -> None:
        """Process all images for a single product"""
        product_id = str(product['id'])
        product_title = product['title']
        images = product.get('images', [])
        
        print(f"\n🍷 Processing: {product_title}")
        print(f"   Product ID: {product_id}")
        print(f"   Images: {len(images)}")
        
        if not images:
            print("   ⚠️ No images found, skipping")
            return
        
        for idx, image in enumerate(images):
            image_id = str(image['id'])
            image_url = image['src']
            
            print(f"\n   🖼️ Image {idx + 1}/{len(images)} (ID: {image_id})")
            
            # Generate filename
            filename = f"{product_id}_{image_id}.png"
            original_path = f"images/original/{filename}"
            resized_path = f"images/resized/{filename}"
            
            # Download image
            success, width, height = self.download_image(image_url, filename)
            
            if not success:
                continue
                
            print(f"   📏 Original size: {width}x{height}px")
            
            # Check if resize is needed
            if width < 400:
                print(f"   🔧 Width < 400px, resizing canvas to 750px...")
                
                # Resize the image canvas
                if self.resize_image_canvas(original_path, resized_path, 750):
                    self.resized_count += 1
                    
                    # Upload resized image back to Shopify
                    print(f"   ⬆️ Uploading resized image...")
                    if self.upload_image_to_shopify(product_id, resized_path, image_id):
                        print(f"   ✅ Successfully replaced image in Shopify")
                    else:
                        print(f"   ❌ Failed to upload resized image")
                else:
                    print(f"   ❌ Failed to resize image")
            else:
                print(f"   ✅ Width sufficient ({width}px), no resize needed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        self.processed_count += 1
        print(f"   📊 Progress: {self.processed_count}/{self.total_products} products")
    
    def filter_wine_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter products to only include wine-related items"""
        wine_products = []
        
        for product in products:
            product_type = product.get('product_type', '').lower()
            if 'wine' in product_type:
                wine_products.append(product)
        
        return wine_products
    
    def run(self, test_mode=False, test_limit=5, wine_only=False):
        """Main execution function"""
        print("🖼️ Shopify Product Image Resizer")
        print("=" * 50)
        print(f"Target: Resize images < 400px wide to 750px canvas")
        print(f"Store: {self.shop_url}")
        
        if test_mode:
            print(f"🧪 TEST MODE: Processing only first {test_limit} products")
        
        if wine_only:
            print(f"🍷 WINE FILTER: Only processing products with 'wine' in category")
        
        print()
        
        # Get all products
        products = self.get_all_products()
        
        if not products:
            print("❌ No products found!")
            return
        
        # Filter for wine products if requested
        if wine_only:
            original_count = len(products)
            products = self.filter_wine_products(products)
            print(f"🍷 Filtered to {len(products)} wine products (from {original_count} total)")
        
        # Limit products for test mode
        if test_mode:
            products = products[:test_limit]
            print(f"🧪 Limited to {len(products)} products for testing")
        
        print(f"\n🚀 Starting image processing for {len(products)} products...")
        
        # Process each product
        for product in products:
            try:
                self.process_product_images(product)
            except KeyboardInterrupt:
                print("\n⚠️ Process interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error processing product {product.get('title', 'Unknown')}: {e}")
                continue
        
        # Final summary
        print("\n" + "=" * 50)
        print("📊 FINAL SUMMARY")
        print("=" * 50)
        print(f"✅ Products processed: {self.processed_count}/{self.total_products}")
        print(f"🔧 Images resized: {self.resized_count}")
        print(f"📁 Original images saved to: images/original/")
        print(f"📁 Resized images saved to: images/resized/")
        
        if self.resized_count > 0:
            print(f"\n✅ Successfully processed {self.resized_count} images!")
        else:
            print(f"\n ℹ️ No images needed resizing (all were >= 400px wide)")

def main():
    """Main entry point"""
    import sys
    
    # Check command line arguments
    args = [arg.lower() for arg in sys.argv[1:]]
    test_mode = 'test' in args
    wine_only = 'wine' in args or 'wines' in args
    
    try:
        resizer = ShopifyImageResizer()
        resizer.run(test_mode=test_mode, wine_only=wine_only)
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
