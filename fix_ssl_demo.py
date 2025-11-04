#!/usr/bin/env python3
"""
Quick SSL fix demo - shows how to test the crawler with SSL bypass
"""

import ssl
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def test_crawler_with_ssl_fix():
    """Test the crawler with SSL bypass"""
    
    print("🔧 Testing Crawler with SSL Fix")
    print("=" * 40)
    
    # Create SSL context that bypasses verification (development only)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout, 
        headers=headers
    ) as session:
        
        url = "https://www.totalwine.com/wine/red-wine/sangiovese/tenuta-di-renieri-chianti-classico-riserva/p/113708750"
        
        print(f"🌐 Testing URL: {url}")
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Test extraction
                    title_elem = soup.select_one('h1')
                    title = title_elem.get_text(strip=True) if title_elem else "Not found"
                    
                    print(f"✅ Connection successful!")
                    print(f"📄 Page title: {title}")
                    print(f"📊 HTML size: {len(html):,} characters")
                    
                    return True
                else:
                    print(f"❌ HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_crawler_with_ssl_fix())
