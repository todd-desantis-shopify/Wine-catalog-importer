#!/usr/bin/env python3
"""
Simple Web Crawler for Shopify - Outputs Shopify-compatible CSV format
"""

import asyncio
import aiohttp
import csv
import time
import argparse
import logging
import re
import ssl
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config_manager import ConfigManager

async def crawl_urls(urls: List[str], site_config: dict, product_config: dict, output_file: str):
    """Crawl URLs and output Shopify CSV format"""
    
    # Setup SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {'User-Agent': site_config['site']['user_agent']}
    
    products = []
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Crawling: {url}")
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        product = extract_product_data(html, url, site_config)
                        if product.get('name'):
                            products.append(product)
                            print(f"  ✅ {product['name']}")
                        else:
                            print(f"  ⚠️  No data extracted")
                    else:
                        print(f"  ❌ HTTP {response.status}")
                        
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            await asyncio.sleep(site_config['site']['rate_limit'])
    
    # Write Shopify CSV
    if products:
        write_shopify_csv(products, output_file, product_config)
        print(f"\n✅ Saved {len(products)} products to {output_file}")
    else:
        print("\n❌ No products extracted")
    
    return products

def extract_product_data(html: str, url: str, site_config: dict) -> dict:
    """Extract product data from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    selectors = site_config.get('selectors', {})
    
    # Basic extraction with BeautifulSoup
    product = {
        'name': '',
        'brand': '',
        'price': 0,
        'sku': extract_sku_from_url(url),
        'url': url
    }
    
    # Extract h1 title
    h1 = soup.find('h1')
    if h1:
        product['name'] = h1.get_text(strip=True)
    
    # Try to extract price (look for price patterns)
    price_text = soup.get_text()
    price_match = re.search(r'\$(\d+\.\d{2})', price_text)
    if price_match:
        product['price'] = float(price_match.group(1))
    
    return product

def extract_sku_from_url(url: str) -> str:
    """Extract SKU from URL pattern"""
    match = re.search(r'/p/([^/]+)', url)
    return match.group(1) if match else ''

def write_shopify_csv(products: List[dict], output_file: str, product_config: dict):
    """Write Shopify-compatible CSV"""
    
    # Shopify CSV columns
    shopify_columns = [field['name'] for field in product_config['fields']]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=shopify_columns, extrasaction='ignore')
        writer.writeheader()
        
        for product in products:
            writer.writerow(product)

async def main():
    parser = argparse.ArgumentParser(description="Simple Shopify Crawler")
    parser.add_argument("--site", required=True)
    parser.add_argument("--product", required=True)
    parser.add_argument("--urls", required=True, help="File with URLs")
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    # Load configs
    config_manager = ConfigManager()
    site_config = config_manager.load_site_config(args.site)
    product_config = config_manager.load_product_config(args.product)
    
    # Load URLs
    with open(args.urls, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # Crawl
    await crawl_urls(urls, site_config, product_config, args.output)

if __name__ == "__main__":
    asyncio.run(main())
