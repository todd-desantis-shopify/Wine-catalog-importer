#!/usr/bin/env python3
"""
Shopify Product Importer
Handles Shopify-specific product import using GraphQL and REST APIs.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List, Optional
import logging
import re
from urllib.parse import urlparse

class ShopifyImporter:
    """Shopify-specific product importer"""
    
    def __init__(self, platform_config: Dict[str, Any], product_config: Dict[str, Any]):
        """Initialize Shopify importer"""
        self.platform_config = platform_config
        self.product_config = product_config
        
        # API configuration
        auth_config = platform_config.get('auth', {})
        self.shop_url = auth_config.get('shop_url', '').rstrip('/')
        self.access_token = auth_config.get('access_token', '')
        
        if not self.shop_url or not self.access_token:
            raise ValueError("Shopify shop_url and access_token are required")
        
        # API settings
        api_config = platform_config.get('api', {})
        self.api_version = platform_config.get('api_version', '2025-07')
        self.rate_limit = api_config.get('rate_limit', 0.5)
        self.max_retries = api_config.get('max_retries', 3)
        
        # Import settings
        import_config = platform_config.get('import', {})
        self.skip_duplicates = import_config.get('skip_duplicates', True)
        self.update_existing = import_config.get('update_existing', True)
        
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.last_request = 0
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit_wait(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        
        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request = time.time()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> aiohttp.ClientResponse:
        """Make API request with rate limiting and retry logic"""
        await self._rate_limit_wait()
        
        url = f"{self.shop_url}/admin/api/{self.api_version}/{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = await self.session.get(url, params=data)
                elif method.upper() == 'POST':
                    response = await self.session.post(url, json=data)
                elif method.upper() == 'PUT':
                    response = await self.session.put(url, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                return response
                
            except Exception as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    async def import_batch(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """Import a batch of products"""
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        async with self:
            for i, product in enumerate(products, 1):
                try:
                    result = await self.import_single_product(product)
                    results[result] += 1
                    
                    if result == 'success':
                        self.logger.info(f"✅ [{i}/{len(products)}] Imported: {product.get('title', 'Unknown')}")
                    elif result == 'skipped':
                        self.logger.info(f"⏭️  [{i}/{len(products)}] Skipped: {product.get('title', 'Unknown')}")
                    else:
                        self.logger.warning(f"❌ [{i}/{len(products)}] Failed: {product.get('title', 'Unknown')}")
                        
                except Exception as e:
                    self.logger.error(f"❌ [{i}/{len(products)}] Error importing product: {e}")
                    results['failed'] += 1
        
        return results
    
    async def import_single_product(self, product_data: Dict[str, Any]) -> str:
        """Import a single product"""
        # Check if product already exists
        existing_product = await self._find_existing_product(product_data)
        
        if existing_product:
            if self.skip_duplicates and not self.update_existing:
                return 'skipped'
            elif self.update_existing:
                return await self._update_product(existing_product, product_data)
        
        # Create new product
        return await self._create_product(product_data)
    
    async def _find_existing_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find existing product by title or SKU"""
        title = product_data.get('title', '')
        sku = product_data.get('variant.sku', '')
        
        if not title and not sku:
            return None
        
        try:
            # Search by title first
            if title:
                response = await self._make_request('GET', 'products.json', {'title': title, 'limit': 1})
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    if products:
                        return products[0]
            
            # Search by SKU if no title match
            if sku:
                response = await self._make_request('GET', 'products.json', {'limit': 250})
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    
                    for product in products:
                        for variant in product.get('variants', []):
                            if variant.get('sku') == sku:
                                return product
        
        except Exception as e:
            self.logger.debug(f"Error searching for existing product: {e}")
        
        return None
    
    async def _create_product(self, product_data: Dict[str, Any]) -> str:
        """Create a new product"""
        try:
            # Build product structure
            shopify_product = self._build_shopify_product(product_data)
            
            # Create product via API
            response = await self._make_request('POST', 'products.json', {'product': shopify_product})
            
            if response.status == 201:
                result = await response.json()
                product_id = result['product']['id']
                
                # Add metafields
                await self._add_metafields(product_id, product_data)
                
                # Add images
                if product_data.get('image_url'):
                    await self._add_product_image(product_id, product_data['image_url'])
                
                return 'success'
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to create product: {response.status} - {error_text}")
                return 'failed'
                
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return 'failed'
    
    async def _update_product(self, existing_product: Dict[str, Any], product_data: Dict[str, Any]) -> str:
        """Update an existing product"""
        try:
            product_id = existing_product['id']
            
            # Build updated product structure
            shopify_product = self._build_shopify_product(product_data, is_update=True)
            
            # Update product via API
            response = await self._make_request('PUT', f'products/{product_id}.json', {'product': shopify_product})
            
            if response.status == 200:
                # Update metafields
                await self._add_metafields(product_id, product_data)
                
                # Update images if needed
                if product_data.get('image_url') and not existing_product.get('images'):
                    await self._add_product_image(product_id, product_data['image_url'])
                
                return 'success'
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to update product: {response.status} - {error_text}")
                return 'failed'
                
        except Exception as e:
            self.logger.error(f"Error updating product: {e}")
            return 'failed'
    
    def _build_shopify_product(self, product_data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Build Shopify product structure from transformed data"""
        csv_data = product_data.get('_csv_data', {})
        defaults = self.platform_config.get('defaults', {})
        
        # Basic product fields
        product = {
            'title': product_data.get('title', csv_data.get('name', '')),
            'vendor': product_data.get('vendor', csv_data.get('brand', '')),
            'product_type': product_data.get('product_type', csv_data.get('wine_type', '')),
            'handle': product_data.get('handle', ''),
            'body_html': self._build_description(csv_data),
            'status': defaults.get('status', 'active'),
            'published': True,
            'tags': self._build_tags(csv_data)
        }
        
        # SEO fields
        if product_data.get('seo_title'):
            product['seo_title'] = product_data['seo_title']
        if product_data.get('seo_description'):
            product['seo_description'] = product_data['seo_description']
        
        # Variant (pricing and inventory)
        variant = {
            'price': str(csv_data.get('price', 0)),
            'sku': csv_data.get('sku', ''),
            'inventory_tracking': defaults.get('inventory_tracking', True),
            'inventory_quantity': defaults.get('inventory_quantity', 100),
            'inventory_policy': defaults.get('inventory_policy', 'deny'),
            'requires_shipping': defaults.get('requires_shipping', True),
            'taxable': defaults.get('taxable', True),
            'weight': defaults.get('weight', 1.5),
            'weight_unit': 'kg'
        }
        
        # Compare at price if available
        compare_at_price = csv_data.get('compare_at_price')
        if compare_at_price and float(compare_at_price) > 0:
            variant['compare_at_price'] = str(compare_at_price)
        
        if not is_update:
            product['variants'] = [variant]
        else:
            product['variants'] = [variant]  # Will update existing variant
        
        return product
    
    def _build_description(self, csv_data: Dict[str, Any]) -> str:
        """Build HTML description from product data"""
        description_parts = []
        
        # Product highlights
        highlights = csv_data.get('highlights', '').strip()
        if highlights:
            description_parts.append(f"<p>{highlights}</p>")
        
        # Wine details
        details = []
        if csv_data.get('country'):
            details.append(f"Country: {csv_data['country']}")
        if csv_data.get('region'):
            details.append(f"Region: {csv_data['region']}")
        if csv_data.get('varietal'):
            details.append(f"Varietal: {csv_data['varietal']}")
        if csv_data.get('abv'):
            details.append(f"ABV: {csv_data['abv']}%")
        
        if details:
            description_parts.append(f"<p>{' • '.join(details)}</p>")
        
        # Tasting notes
        taste_notes = csv_data.get('taste_notes', '').strip()
        if taste_notes:
            description_parts.append(f"<p><strong>Tasting Notes:</strong> {taste_notes}</p>")
        
        return '\n'.join(description_parts) if description_parts else ""
    
    def _build_tags(self, csv_data: Dict[str, Any]) -> str:
        """Build product tags from data"""
        tags = []
        
        # Wine type
        if csv_data.get('wine_type'):
            tags.append(csv_data['wine_type'])
        
        # Country and region
        if csv_data.get('country'):
            tags.append(csv_data['country'])
        if csv_data.get('region'):
            tags.append(csv_data['region'])
        
        # Varietal
        if csv_data.get('varietal'):
            tags.append(csv_data['varietal'])
        
        # Style and body
        if csv_data.get('style'):
            tags.append(csv_data['style'])
        if csv_data.get('body'):
            tags.append(csv_data['body'])
        
        # Price range tags
        try:
            price = float(csv_data.get('price', 0))
            if price < 25:
                tags.append('Under $25')
            elif price < 50:
                tags.append('$25-$50')
            else:
                tags.append('Premium ($50+)')
        except (ValueError, TypeError):
            pass
        
        return ', '.join(tags)
    
    async def _add_metafields(self, product_id: int, product_data: Dict[str, Any]):
        """Add metafields to product"""
        csv_data = product_data.get('_csv_data', {})
        metafield_mappings = self._get_metafield_mappings()
        
        for csv_field, metafield_key in metafield_mappings.items():
            value = csv_data.get(csv_field)
            if value:
                await self._create_metafield(product_id, metafield_key, value)
    
    def _get_metafield_mappings(self) -> Dict[str, str]:
        """Get CSV field to metafield mappings"""
        mappings = {}
        platform_name = self.platform_config.get('platform', '').lower()
        
        for field in self.product_config.get('fields', []):
            csv_field = field['name']
            metafield_key = f"{platform_name}_metafield"
            
            if metafield_key in field:
                mappings[csv_field] = field[metafield_key]
        
        return mappings
    
    async def _create_metafield(self, product_id: int, metafield_key: str, value: Any):
        """Create a metafield for a product"""
        if '.' not in metafield_key:
            return
        
        namespace, key = metafield_key.split('.', 1)
        
        # Determine value type
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                metafield_value = str(value)
                value_type = 'number_decimal'
            else:
                metafield_value = str(value)
                value_type = 'number_integer'
        else:
            metafield_value = str(value)
            value_type = 'single_line_text_field'
        
        metafield_data = {
            'metafield': {
                'namespace': namespace,
                'key': key,
                'value': metafield_value,
                'type': value_type
            }
        }
        
        try:
            response = await self._make_request('POST', f'products/{product_id}/metafields.json', metafield_data)
            if response.status != 201:
                error_text = await response.text()
                self.logger.debug(f"Failed to create metafield {metafield_key}: {error_text}")
        except Exception as e:
            self.logger.debug(f"Error creating metafield {metafield_key}: {e}")
    
    async def _add_product_image(self, product_id: int, image_url: str):
        """Add image to product"""
        if not image_url or not self._is_valid_image_url(image_url):
            return
        
        image_data = {
            'image': {
                'src': image_url,
                'alt': f"Product image"
            }
        }
        
        try:
            response = await self._make_request('POST', f'products/{product_id}/images.json', image_data)
            if response.status != 201:
                error_text = await response.text()
                self.logger.debug(f"Failed to add image: {error_text}")
        except Exception as e:
            self.logger.debug(f"Error adding product image: {e}")
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Validate image URL"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))
        except Exception:
            return False
