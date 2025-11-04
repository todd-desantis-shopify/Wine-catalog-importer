#!/usr/bin/env python3
"""
Simple Collection Page Crawler for Shopify
Crawls collection/listing pages → extracts product URLs → crawls detail pages → outputs Shopify CSV
"""

import asyncio
import aiohttp
import csv
import argparse
import re
import ssl
from pathlib import Path
from typing import List, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config_manager import ConfigManager

async def crawl_collection_pages(collection_urls: List[str], site_config: dict, product_config: dict, output_file: str):
    """Crawl collection pages to find product URLs, then crawl products"""
    
    print(f"📋 Step 1: Extracting product URLs from {len(collection_urls)} collection page(s)...")
    
    # Extract product URLs from collection pages
    product_urls = await extract_product_urls_from_collections(collection_urls, site_config)
    
    if not product_urls:
        print("❌ No product URLs found on collection pages")
        return
    
    print(f"✅ Found {len(product_urls)} product URLs\n")
    print(f"📡 Step 2: Crawling {len(product_urls)} product detail pages...")
    
    # Crawl each product detail page
    products = await crawl_product_details(product_urls, site_config, product_config)
    
    # Write Shopify CSV
    if products:
        write_shopify_csv(products, output_file, product_config)
        print(f"\n✅ Saved {len(products)} products to {output_file}")
    else:
        print("\n❌ No products extracted")
    
    return products

async def extract_product_urls_from_collections(collection_urls: List[str], site_config: dict) -> Set[str]:
    """Extract product detail page URLs from collection pages"""
    
    # Setup SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {'User-Agent': site_config['site']['user_agent']}
    base_url = site_config['site']['base_url']
    
    product_urls = set()
    collection_config = site_config.get('collection_page', {})
    link_selector = collection_config.get('product_link_selector', "a[href*='/p/']")
    link_pattern = collection_config.get('product_link_pattern', "/p/\\d+")
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        for i, url in enumerate(collection_urls, 1):
            print(f"  [{i}/{len(collection_urls)}] Scanning collection: {url}")
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find all product links
                        links = soup.select(link_selector)
                        
                        for link in links:
                            href = link.get('href', '')
                            if re.search(link_pattern, href):
                                full_url = urljoin(base_url, href)
                                product_urls.add(full_url)
                        
                        print(f"     Found {len(links)} product links")
                    else:
                        print(f"     ❌ HTTP {response.status}")
                        
            except Exception as e:
                print(f"     ❌ Error: {e}")
            
            await asyncio.sleep(site_config['site']['rate_limit'])
    
    return product_urls

async def crawl_product_details(product_urls: List[str], site_config: dict, product_config: dict) -> List[dict]:
    """Crawl product detail pages and extract data"""
    
    # Setup SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {'User-Agent': site_config['site']['user_agent']}
    
    products = []
    product_urls_list = sorted(list(product_urls))
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        for i, url in enumerate(product_urls_list, 1):
            print(f"  [{i}/{len(product_urls_list)}] Crawling: {url}")
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        product = extract_product_data(html, url, site_config, product_config)
                        
                        if product.get('name'):
                            products.append(product)
                            print(f"      ✅ {product['name']}")
                        else:
                            print(f"      ⚠️  No data extracted")
                    else:
                        print(f"      ❌ HTTP {response.status}")
                        
            except Exception as e:
                print(f"      ❌ Error: {e}")
            
            await asyncio.sleep(site_config['site']['rate_limit'])
    
    return products

def extract_product_data(html: str, url: str, site_config: dict, product_config: dict) -> dict:
    """Extract product data from HTML based on enabled fields"""
    soup = BeautifulSoup(html, 'html.parser')
    selectors = site_config.get('selectors', {})
    
    product = {'url': url}
    
    # Get enabled fields from product config
    enabled_fields = [f['name'] for f in product_config['fields'] if f.get('enabled', True)]
    
    # Extract only enabled fields
    if 'name' in enabled_fields:
        h1 = soup.find('h1')
        product['name'] = h1.get_text(strip=True) if h1 else ''
    
    if 'sku' in enabled_fields:
        product['sku'] = extract_sku_from_url(url)
    
    if 'price' in enabled_fields:
        price_match = re.search(r'\$(\d+\.\d{2})', soup.get_text())
        product['price'] = price_match.group(1) if price_match else ''
    
    # Add more field extraction here based on selectors...
    # This is where site-specific CSS selectors would be used
    
    return product

def extract_sku_from_url(url: str) -> str:
    """Extract SKU from URL"""
    match = re.search(r'/p/([^/?]+)', url)
    return match.group(1) if match else ''

def write_shopify_csv(products: List[dict], output_file: str, product_config: dict):
    """Write Shopify-compatible CSV with only enabled fields"""
    
    # Get enabled field names
    enabled_fields = [f['name'] for f in product_config['fields'] if f.get('enabled', True)]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=enabled_fields, extrasaction='ignore')
        writer.writeheader()
        
        for product in products:
            # Only write enabled fields
            row = {k: v for k, v in product.items() if k in enabled_fields}
            writer.writerow(row)

async def main():
    parser = argparse.ArgumentParser(description="Simple Shopify Crawler - Collection Pages")
    parser.add_argument("--site", required=True, help="Site config name (e.g., 'totalwine')")
    parser.add_argument("--product", required=True, help="Product config name (e.g., 'wine')")
    parser.add_argument("--collections", required=True, help="File with collection page URLs")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    # Load configs
    config_manager = ConfigManager()
    site_config = config_manager.load_site_config(args.site)
    product_config = config_manager.load_product_config(args.product)
    
    # Load collection page URLs
    with open(args.collections, 'r') as f:
        collection_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"🕷️  Collection Page Crawler for Shopify")
    print(f"Site: {site_config['site']['name']}")
    print(f"Product Type: {product_config['product_type']}")
    print(f"Collection Pages: {len(collection_urls)}")
    print("=" * 50)
    
    # Crawl
    await crawl_collection_pages(collection_urls, site_config, product_config, args.output)

if __name__ == "__main__":
    asyncio.run(main())