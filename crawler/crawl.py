#!/usr/bin/env python3
"""
Universal Web Crawler for E-commerce Sites
Configuration-driven crawler that can extract product data from any e-commerce website.
"""

import asyncio
import aiohttp
import csv
import time
import argparse
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
import yaml
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.config_manager import ConfigManager

@dataclass
class ProductData:
    """Data class for extracted product information"""
    name: str = ""
    brand: str = ""
    country: str = ""
    region: str = ""
    appellation: str = ""
    wine_type: str = ""
    varietal: str = ""
    style: str = ""
    abv: float = 0.0
    taste_notes: str = ""
    body: str = ""
    price: float = 0.0
    compare_at_price: float = 0.0
    mix_6_price: float = 0.0
    customer_rating: float = 0.0
    customer_reviews: int = 0
    expert_rating: str = ""
    sku: str = ""
    size: str = "750ml"
    url: str = ""
    image_url: str = ""
    highlights: str = ""

class UniversalCrawler:
    """Universal web crawler for e-commerce sites"""
    
    def __init__(self, site_config: Dict[str, Any], product_config: Dict[str, Any]):
        """Initialize crawler with site and product configurations"""
        self.site_config = site_config
        self.product_config = product_config
        self.session = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.rate_limit = site_config.get('site', {}).get('rate_limit', 1.0)
        self.last_request = 0
        
        # Error handling settings
        error_config = site_config.get('error_handling', {})
        self.max_retries = error_config.get('max_retries', 3)
        self.retry_delay = error_config.get('retry_delay', 2)
        self.skip_on_error = error_config.get('skip_on_error', True)
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(
            total=self.site_config.get('site', {}).get('timeout', 30)
        )
        
        headers = {
            'User-Agent': self.site_config.get('site', {}).get('user_agent', 
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
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
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page with retry logic"""
        await self._rate_limit_wait()
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.warning(f"HTTP {response.status} for {url}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    if self.skip_on_error:
                        self.logger.warning(f"Skipping {url} after {self.max_retries + 1} attempts")
                        return None
                    else:
                        raise
        
        return None
    
    def extract_data_from_html(self, html: str, url: str) -> ProductData:
        """Extract product data from HTML using BeautifulSoup"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        product = ProductData()
        product.url = url
        
        # Extract data using selectors from config
        selectors = self.site_config.get('selectors', {})
        transformations = self.site_config.get('transformations', {})
        
        # Basic product information
        product.name = self._extract_text(soup, selectors.get('product_name', ''))
        product.brand = self._extract_text(soup, selectors.get('brand', ''))
        
        # Pricing
        price_text = self._extract_text(soup, selectors.get('price', {}).get('current', ''))
        product.price = self._transform_data(price_text, transformations.get('price', {}))
        
        compare_price_text = self._extract_text(soup, selectors.get('price', {}).get('compare_at', ''))
        if compare_price_text:
            product.compare_at_price = self._transform_data(compare_price_text, transformations.get('price', {}))
        
        mix6_text = self._extract_text(soup, selectors.get('mix_6_price', ''))
        if mix6_text:
            product.mix_6_price = self._transform_data(mix6_text, transformations.get('price', {}))
        
        # Wine details
        details = selectors.get('details', {})
        product.country = self._extract_text(soup, details.get('country', ''))
        product.region = self._extract_text(soup, details.get('region', ''))
        product.appellation = self._extract_text(soup, details.get('appellation', ''))
        product.wine_type = self._extract_text(soup, details.get('wine_type', ''))
        product.varietal = self._extract_text(soup, details.get('varietal', ''))
        product.style = self._extract_text(soup, details.get('style', ''))
        product.body = self._extract_text(soup, details.get('body', ''))
        
        # ABV
        abv_text = self._extract_text(soup, details.get('abv', ''))
        product.abv = self._transform_data(abv_text, transformations.get('abv', {}))
        
        # Ratings
        rating_text = self._extract_text(soup, selectors.get('customer_rating', ''))
        product.customer_rating = self._transform_data(rating_text, transformations.get('rating', {}))
        
        reviews_text = self._extract_text(soup, selectors.get('customer_reviews', ''))
        if reviews_text:
            # Extract number from reviews text like "165 Reviews"
            reviews_match = re.search(r'(\d+)', reviews_text)
            if reviews_match:
                product.customer_reviews = int(reviews_match.group(1))
        
        product.expert_rating = self._extract_text(soup, selectors.get('expert_rating', ''))
        
        # Additional fields
        product.highlights = self._extract_text(soup, selectors.get('highlights', ''))
        product.taste_notes = self._extract_text(soup, selectors.get('tasting_notes', ''))
        
        # SKU (try multiple methods)
        product.sku = self._extract_sku(soup, url, selectors.get('sku', ''))
        
        # Image
        product.image_url = self._extract_image_url(soup, selectors.get('main_image', ''), url)
        
        return product
    
    def _extract_text(self, soup, selector: str) -> str:
        """Extract text using CSS selector or text pattern"""
        if not selector:
            return ""
            
        try:
            # Handle text pattern matching (e.g., "text*='Price'")
            if 'text*=' in selector:
                pattern = selector.split("text*=")[1].strip("'\"")
                elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
                if elements:
                    # Find the parent element and get its text
                    parent = elements[0].parent
                    return parent.get_text(strip=True) if parent else ""
            
            # Handle CSS selectors with + sibling combinator
            elif '+' in selector:
                parts = selector.split('+')
                first_elem = soup.select_one(parts[0].strip())
                if first_elem:
                    sibling = first_elem.find_next_sibling()
                    if sibling:
                        return sibling.get_text(strip=True)
            
            # Regular CSS selector
            else:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
                    
        except Exception as e:
            self.logger.debug(f"Error extracting with selector '{selector}': {e}")
        
        return ""
    
    def _extract_sku(self, soup, url: str, selector: str) -> str:
        """Extract SKU from page or URL"""
        # Try selector first
        sku = self._extract_text(soup, selector)
        if sku:
            return sku
        
        # Try to extract from URL pattern
        url_path = urlparse(url).path
        # Look for pattern like /p/123456789
        sku_match = re.search(r'/p/([^/]+)', url_path)
        if sku_match:
            return sku_match.group(1)
        
        # Look for general number patterns
        number_match = re.search(r'(\d{6,})', url_path)
        if number_match:
            return number_match.group(1)
        
        return ""
    
    def _extract_image_url(self, soup, selector: str, base_url: str) -> str:
        """Extract image URL"""
        try:
            if selector:
                img_element = soup.select_one(selector)
                if img_element:
                    img_url = img_element.get('src') or img_element.get('data-src')
                    if img_url:
                        return urljoin(base_url, img_url)
        except Exception as e:
            self.logger.debug(f"Error extracting image: {e}")
        
        return ""
    
    def _transform_data(self, text: str, transform_config: Dict[str, Any]) -> Any:
        """Transform extracted text using transformation rules"""
        if not text or not transform_config:
            return text
        
        pattern = transform_config.get('pattern', '')
        data_type = transform_config.get('type', 'string')
        
        if pattern:
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                
                if data_type == 'float':
                    try:
                        return float(value)
                    except ValueError:
                        return 0.0
                elif data_type == 'int':
                    try:
                        return int(value)
                    except ValueError:
                        return 0
                else:
                    return value
        
        return text if data_type == 'string' else 0
    
    async def crawl_products(self, urls: List[str]) -> List[ProductData]:
        """Crawl multiple product URLs and extract data"""
        products = []
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Crawling product {i}/{len(urls)}: {url}")
            
            html = await self.fetch_page(url)
            if html:
                try:
                    product = self.extract_data_from_html(html, url)
                    if product.name:  # Only add if we got basic data
                        products.append(product)
                        self.logger.info(f"✅ Extracted: {product.name}")
                    else:
                        self.logger.warning(f"⚠️  No product name found for {url}")
                except Exception as e:
                    self.logger.error(f"❌ Error processing {url}: {e}")
            else:
                self.logger.warning(f"⚠️  Failed to fetch {url}")
        
        return products
    
    def save_to_csv(self, products: List[ProductData], output_file: str):
        """Save extracted products to CSV file"""
        if not products:
            self.logger.warning("No products to save")
            return
        
        # Get field names from product config
        field_names = [field['name'] for field in self.product_config.get('fields', [])]
        
        # Fallback to dataclass fields if config doesn't specify
        if not field_names:
            field_names = list(asdict(products[0]).keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            
            for product in products:
                product_dict = asdict(product)
                # Only write fields that are in the config
                filtered_dict = {k: v for k, v in product_dict.items() if k in field_names}
                writer.writerow(filtered_dict)
        
        self.logger.info(f"✅ Saved {len(products)} products to {output_file}")

async def main():
    """Main crawler function"""
    parser = argparse.ArgumentParser(description="Universal E-commerce Crawler")
    parser.add_argument("--site", required=True, help="Site configuration name")
    parser.add_argument("--product", required=True, help="Product configuration name")
    parser.add_argument("--urls", required=True, help="File containing URLs to crawl")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    # Load configurations
    config_manager = ConfigManager()
    
    try:
        site_config = config_manager.load_site_config(args.site)
        product_config = config_manager.load_product_config(args.product)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Load URLs from file
    try:
        with open(args.urls, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading URLs file: {e}")
        return 1
    
    # Run crawler
    async with UniversalCrawler(site_config, product_config) as crawler:
        products = await crawler.crawl_products(urls)
        crawler.save_to_csv(products, args.output)
    
    print(f"✅ Crawling complete! Extracted {len(products)} products")
    return 0

if __name__ == "__main__":
    # Install required packages check
    try:
        import aiohttp
        from bs4 import BeautifulSoup
        import yaml
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Install with: pip install aiohttp beautifulsoup4 pyyaml")
        exit(1)
    
    asyncio.run(main())
