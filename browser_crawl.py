#!/usr/bin/env python3
"""
Browser-based Smart Crawler - Uses real browser to bypass bot protection
Works inside Cursor with browser MCP
"""

import csv
import re
from typing import List, Dict
from urllib.parse import urljoin, urlparse

class BrowserCrawler:
    """Crawler that uses browser MCP tools"""
    
    def __init__(self, product_type: str = "generic"):
        self.product_type = product_type
        self.base_url = ""
        self.extra_fields = []
        
        # Load extra fields from config if exists
        try:
            import yaml
            from pathlib import Path
            config_path = Path(__file__).parent / "config" / "products" / f"{product_type}.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    self.extra_fields = config.get('extra_fields', [])
        except:
            pass
    
    def extract_product_links_from_snapshot(self, snapshot_yaml: str, base_url: str) -> List[str]:
        """Extract product links from browser snapshot"""
        
        product_urls = []
        
        # Parse snapshot to find links
        # Snapshot contains lines like:
        #   - link "Product Name" [ref=s1e123]:
        #     - /url: /products/product-name
        
        lines = snapshot_yaml.split('\n')
        current_url = None
        
        for line in lines:
            # Look for URL lines
            if '/url:' in line:
                url_match = re.search(r'/url:\s*(.+)', line)
                if url_match:
                    current_url = url_match.group(1).strip()
                    
                    # Check if it's a product URL
                    if self._is_product_url(current_url):
                        full_url = urljoin(base_url, current_url)
                        if full_url not in product_urls:
                            product_urls.append(full_url)
        
        return product_urls
    
    def _is_product_url(self, url: str) -> bool:
        """Check if URL is a product detail page"""
        product_patterns = [
            r'/p/\d+',
            r'/dp/[A-Z0-9]+',
            r'/products/[\w-]+',
            r'/item/\d+',
            r'/shop/[\w-]+/[\w-]+/[\w-]+-\d+',
        ]
        
        return any(re.search(pattern, url) for pattern in product_patterns)
    
    def extract_product_data_from_snapshot(self, snapshot_yaml: str, url: str) -> Dict:
        """Extract product data from browser snapshot"""
        
        product = {}
        
        # Extract from snapshot structure
        # The snapshot has text content we can parse
        
        lines = snapshot_yaml.split('\n')
        all_text = '\n'.join(lines)
        
        # Title - look for heading or og:title-like patterns
        product['title'] = self._extract_title_from_snapshot(lines)
        
        # Price - look for $ patterns
        product['price'] = self._extract_price_from_snapshot(all_text, 'current')
        product['msrp'] = self._extract_price_from_snapshot(all_text, 'compare')
        
        # SKU
        product['sku'] = self._extract_sku_from_snapshot(all_text, url)
        
        # Brand
        product['brand'] = self._extract_brand_from_snapshot(all_text)
        
        # Image
        product['image_url'] = self._extract_image_from_snapshot(lines, url)
        
        # Description
        product['description'] = self._extract_description_from_snapshot(all_text)
        
        # Collection
        product['collection'] = self._extract_collection_from_snapshot(all_text, url)
        
        # Extra fields
        for field_name in self.extra_fields:
            product[field_name] = self._extract_field_from_snapshot(all_text, field_name)
        
        return product
    
    def _extract_title_from_snapshot(self, lines: List[str]) -> str:
        """Extract title from snapshot"""
        for line in lines:
            # Look for heading levels
            if 'heading' in line and '[level=1]' in line:
                # Next line usually has the text
                title_match = re.search(r'heading\s+"([^"]+)"', line)
                if title_match:
                    return title_match.group(1)
        
        return ''
    
    def _extract_price_from_snapshot(self, text: str, price_type: str) -> str:
        """Extract price from snapshot text"""
        if price_type == 'current':
            price_match = re.search(r'\$(\d+\.\d{2})', text)
            return price_match.group(1) if price_match else ''
        else:
            patterns = [
                r'(?:was|originally|list|msrp|previously).*?\$(\d+\.\d{2})',
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        return ''
    
    def _extract_sku_from_snapshot(self, text: str, url: str) -> str:
        """Extract SKU"""
        patterns = [
            r'/p/([^/?]+)', r'/dp/([^/?]+)', r'/products/[\w-]+-(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        sku_match = re.search(r'SKU[:\s]+([A-Z0-9-]+)', text, re.IGNORECASE)
        return sku_match.group(1) if sku_match else ''
    
    def _extract_brand_from_snapshot(self, text: str) -> str:
        """Extract brand"""
        brand_match = re.search(r'Brand[:\s]+([A-Za-z0-9\s&-]+)', text)
        return brand_match.group(1).strip() if brand_match else ''
    
    def _extract_image_from_snapshot(self, lines: List[str], url: str) -> str:
        """Extract image URL"""
        for line in lines:
            if 'img' in line and ('src=' in line or 'data-src=' in line):
                img_match = re.search(r'(?:src|data-src)="([^"]+)"', line)
                if img_match:
                    img_url = img_match.group(1)
                    if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        return urljoin(url, img_url)
        return ''
    
    def _extract_description_from_snapshot(self, text: str) -> str:
        """Extract description"""
        # Look for description-like text
        desc_match = re.search(r'(?:description|about|details)[:\s]+([^\n]{50,500})', text, re.IGNORECASE)
        return desc_match.group(1).strip() if desc_match else ''
    
    def _extract_collection_from_snapshot(self, text: str, url: str) -> str:
        """Extract collection"""
        path_parts = urlparse(url).path.split('/')
        if len(path_parts) > 2:
            return path_parts[-1].replace('-', ' ').title()
        return ''
    
    def _extract_field_from_snapshot(self, text: str, field_name: str) -> str:
        """Extract custom field"""
        pattern = rf'{field_name}[:\s]+([^\n]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ''

# This will be called from Cursor with browser MCP access
def extract_from_browser(snapshot_yaml: str, url: str, product_type: str = "generic") -> Dict:
    """Helper function to extract data from browser snapshot"""
    crawler = BrowserCrawler(product_type)
    return crawler.extract_product_data_from_snapshot(snapshot_yaml, url)

if __name__ == "__main__":
    print("This crawler is designed to be used within Cursor with browser MCP access")
    print("Use: Have Cursor navigate to pages and extract data using the browser tools")
