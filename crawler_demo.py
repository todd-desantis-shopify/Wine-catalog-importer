#!/usr/bin/env python3
"""
Crawler Demo - Shows how the Universal Crawler extracts data
"""

import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from config.config_manager import ConfigManager

def demo_crawler_output():
    """Demonstrate what the crawler would extract"""
    
    # Load configurations (same as real crawler)
    config_manager = ConfigManager()
    site_config = config_manager.load_site_config("totalwine")
    product_config = config_manager.load_product_config("wine")
    
    print("🕷️  Universal Crawler Demo")
    print("=" * 50)
    
    # Show loaded configs
    print(f"✅ Site Config: {site_config['site']['name']}")
    print(f"✅ Product Fields: {len(product_config['fields'])} configured")
    print(f"✅ Rate Limit: {site_config['site']['rate_limit']} seconds")
    
    # Demo extraction (simulated)
    print("\n🔍 Simulated Data Extraction:")
    print("URL: https://www.totalwine.com/.../tenuta-di-renieri.../p/113708750")
    
    extracted_data = {
        "name": "Tenuta di Renieri Chianti Classico Riserva, 2020",
        "brand": "Tenuta di Renieri", 
        "country": "Italy",
        "region": "Tuscany",
        "appellation": "Chianti Classico",
        "wine_type": "Red Wine",
        "varietal": "Sangiovese",
        "style": "Elegant",
        "abv": 14.5,
        "taste_notes": "Anise, Cherry",
        "body": "Full-bodied",
        "price": 22.99,
        "compare_at_price": 26.99,  # Real "Previously" pricing!
        "mix_6_price": 20.69,
        "customer_rating": 4.2,
        "customer_reviews": 165,
        "expert_rating": "93 • James Suckling",
        "sku": "113708750-1",
        "size": "750ml",
        "url": "https://www.totalwine.com/.../p/113708750",
        "image_url": "https://www.totalwine.com/media/...wine.jpg",
        "highlights": "James Suckling-Tuscany, Italy - A poised and focused Chianti..."
    }
    
    print("\n📊 Extracted Fields:")
    for key, value in extracted_data.items():
        print(f"   {key:20} = {value}")
    
    # Show CSV output format
    print("\n📄 CSV Output Format:")
    field_names = [field['name'] for field in product_config['fields']]
    
    print("CSV Headers:", ", ".join(field_names[:8]) + "...")
    
    return extracted_data

if __name__ == "__main__":
    demo_crawler_output()
