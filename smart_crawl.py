#!/usr/bin/env python3
"""
Smart Crawler - Automatically figures out site structure and extracts product data
Just give it a collection page URL, it does the rest.
"""

import asyncio
import aiohttp
import csv
import re
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict
import argparse

class SmartCrawler:
    """Intelligent crawler that auto-detects site structure"""
    
    def __init__(self, product_type: str = "generic"):
        self.product_type = product_type
        self.base_url = ""
        
        # Load extra fields from config if exists
        try:
            import yaml
            from pathlib import Path
            config_path = Path(__file__).parent / "config" / "products" / f"{product_type}.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    self.extra_fields = config.get('extra_fields', [])
            else:
                self.extra_fields = []
        except:
            self.extra_fields = []
        
        # SSL setup
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def crawl(self, collection_url: str) -> List[Dict]:
        """Main crawl function - collection page → products → CSV data"""
        
        self.base_url = f"{urlparse(collection_url).scheme}://{urlparse(collection_url).netloc}"
        
        print(f"🕷️  Smart Crawler - Auto-detecting site structure")
        print(f"Collection: {collection_url}")
        print("=" * 60)
        
        # Step 1: Extract product URLs from collection page
        print("\n📋 Step 1: Finding product links...")
        product_urls = await self.extract_product_urls(collection_url)
        
        if not product_urls:
            print("❌ No product URLs found")
            return []
        
        print(f"✅ Found {len(product_urls)} products")
        
        # Step 2: Crawl each product
        print(f"\n📡 Step 2: Crawling {len(product_urls)} products...")
        products = await self.crawl_products(list(product_urls))
        
        print(f"\n✅ Extracted {len(products)} products with data")
        return products
    
    async def extract_product_urls(self, collection_url: str) -> Set[str]:
        """Auto-detect product links on collection page"""
        
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(collection_url) as response:
                if response.status != 200:
                    print(f"❌ Failed to load collection page: {response.status}")
                    return set()
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Smart detection: find links that look like product detail pages
                product_urls = set()
                
                # Common patterns for product detail URLs
                product_patterns = [
                    r'/p/\d+',           # Total Wine: /p/123456
                    r'/dp/[A-Z0-9]+',    # Amazon: /dp/B07ABC123
                    r'/products/[\w-]+', # Shopify stores: /products/product-name
                    r'/item/\d+',        # eBay: /item/123456
                ]
                
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link['href']
                    
                    # Check if it matches any product pattern
                    for pattern in product_patterns:
                        if re.search(pattern, href):
                            full_url = urljoin(self.base_url, href)
                            # Avoid duplicates from different URLs pointing to same product
                            product_urls.add(full_url.split('?')[0])  # Remove query params
                            break
                
                return product_urls
    
    async def crawl_products(self, product_urls: List[str]) -> List[Dict]:
        """Crawl product detail pages and extract data"""
        
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        products = []
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i, url in enumerate(product_urls, 1):
                print(f"  [{i}/{len(product_urls)}] {url}")
                
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            product = self.extract_product_data(html, url)
                            
                            if product.get('title'):
                                products.append(product)
                                print(f"      ✅ {product['title']}")
                            else:
                                print(f"      ⚠️  No title found")
                        else:
                            print(f"      ❌ HTTP {response.status}")
                            
                except Exception as e:
                    print(f"      ❌ {e}")
                
                await asyncio.sleep(0.5)  # Rate limiting
        
        return products
    
    def extract_product_data(self, html: str, url: str) -> Dict:
        """Smart extraction - auto-detects where data is on the page"""
        
        soup = BeautifulSoup(html, 'html.parser')
        product = {}
        
        # STANDARD FIELDS (auto-detected)
        
        # Title - usually the first h1 or largest heading
        product['title'] = self.auto_extract_title(soup)
        
        # Price - look for $ patterns
        product['price'] = self.auto_extract_price(soup, 'current')
        
        # MSRP/Compare At Price - "was", "originally", "list price"
        product['msrp'] = self.auto_extract_price(soup, 'compare')
        
        # SKU - from URL or page
        product['sku'] = self.auto_extract_sku(soup, url)
        
        # Brand - common patterns
        product['brand'] = self.auto_extract_brand(soup)
        
        # Image - first large product image
        product['image_url'] = self.auto_extract_image(soup, url)
        
        # Description - product description text
        product['description'] = self.auto_extract_description(soup)
        
        # Collection - from URL or breadcrumbs
        product['collection'] = self.auto_extract_collection(soup, url)
        
        # EXTRA FIELDS (product-specific)
        for field_name in self.extra_fields:
            product[field_name] = self.auto_extract_field(soup, field_name)
        
        return product
    
    def auto_extract_title(self, soup) -> str:
        """Auto-detect product title"""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '').strip()
        
        return ''
    
    def auto_extract_price(self, soup, price_type: str) -> str:
        """Auto-detect price - current or compare/msrp"""
        
        text = soup.get_text()
        
        if price_type == 'current':
            # Look for price near "price", "now", or standalone
            price_match = re.search(r'\$(\d+\.\d{2})', text)
            return price_match.group(1) if price_match else ''
        else:
            # Look for "was", "originally", "list", "msrp", "compare"
            compare_patterns = [
                r'(?:was|originally|list price|msrp|previously|compare at).*?\$(\d+\.\d{2})',
                r'\$(\d+\.\d{2}).*?(?:was|originally|list)',
            ]
            
            for pattern in compare_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return ''
    
    def auto_extract_sku(self, soup, url: str) -> str:
        """Auto-detect SKU"""
        # Try URL first
        patterns = [
            r'/p/([^/?]+)',      # Total Wine
            r'/dp/([^/?]+)',     # Amazon
            r'/item/(\d+)',      # eBay
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try page text
        sku_match = re.search(r'SKU[:\s]+([A-Z0-9-]+)', soup.get_text(), re.IGNORECASE)
        if sku_match:
            return sku_match.group(1)
        
        return ''
    
    def auto_extract_brand(self, soup) -> str:
        """Auto-detect brand/vendor"""
        # Try meta tags
        meta_brand = soup.find('meta', property='og:brand')
        if meta_brand:
            return meta_brand.get('content', '').strip()
        
        # Try links with "brand" in them
        brand_link = soup.find('a', href=re.compile(r'/brand/', re.I))
        if brand_link:
            return brand_link.get_text(strip=True)
        
        # Try text pattern
        brand_match = re.search(r'Brand[:\s]+([A-Za-z0-9\s&-]+)', soup.get_text())
        if brand_match:
            return brand_match.group(1).strip()
        
        return ''
    
    def auto_extract_image(self, soup, url: str) -> str:
        """Auto-detect main product image"""
        # Look for large images (likely product images)
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src') or img.get('data-src')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                # Skip tiny images (logos, icons)
                if 'logo' not in src.lower() and 'icon' not in src.lower():
                    return urljoin(url, src)
        
        return ''
    
    def auto_extract_description(self, soup) -> str:
        """Auto-detect product description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try common description containers
        desc_containers = soup.find_all(['div', 'p'], class_=re.compile(r'description|details|about', re.I))
        if desc_containers:
            return desc_containers[0].get_text(strip=True)[:500]  # First 500 chars
        
        return ''
    
    def auto_extract_collection(self, soup, url: str) -> str:
        """Auto-detect collection from URL or breadcrumbs"""
        # Try breadcrumbs
        breadcrumbs = soup.find('nav', attrs={'aria-label': re.compile(r'breadcrumb', re.I)})
        if breadcrumbs:
            links = breadcrumbs.find_all('a')
            if len(links) > 1:
                return links[-1].get_text(strip=True)
        
        # Try URL path
        path_parts = urlparse(url).path.split('/')
        if len(path_parts) > 2:
            return path_parts[2].replace('-', ' ').title()
        
        return ''
    
    def auto_extract_field(self, soup, field_name: str) -> str:
        """Auto-detect custom fields by name pattern matching"""
        text = soup.get_text()
        
        # Try pattern: "Field Name: Value"
        pattern = rf'{field_name}[:\s]+([^\n]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return ''

async def main():
    parser = argparse.ArgumentParser(description="Smart Crawler - Auto-detects site structure")
    parser.add_argument("--url", required=True, help="Collection page URL to crawl")
    parser.add_argument("--product", default="generic", help="Product type (optional)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    parser.add_argument("--limit", type=int, help="Max products to crawl (optional)")
    
    args = parser.parse_args()
    
    # Create smart crawler
    crawler = SmartCrawler(args.product)
    
    # Crawl
    products = await crawler.crawl(args.url)
    
    if args.limit:
        products = products[:args.limit]
    
    # Save to CSV
    if products:
        # Standard fields
        standard_fields = ['title', 'price', 'collection', 'description', 'msrp', 'brand', 'sku', 'image_url']
        all_fields = standard_fields + crawler.extra_fields
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(products)
        
        print(f"\n✅ Saved {len(products)} products to {args.output}")
        print(f"📊 Fields: {', '.join(all_fields)}")
    else:
        print("\n❌ No products extracted")

if __name__ == "__main__":
    asyncio.run(main())
