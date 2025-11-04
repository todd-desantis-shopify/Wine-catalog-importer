# 🍷 E-commerce Catalog System for Shopify

Simple, modular system for crawling product data and importing to Shopify.

## 🚀 Quick Start

### 1. Crawl Products
```bash
python3 crawler/crawl.py --site totalwine --product wine --urls urls.txt --output wines.csv
```

### 2. Setup Shopify
```bash
python3 setup/setup_shopify.py --product wine
```

### 3. Import to Shopify  
```bash
python3 import_wines.py  # Uses your existing importer
```

## 📁 Structure

```
crawler/          # Crawls any e-commerce site → CSV
setup/            # Creates Shopify metafields/collections  
config/           # Site & product configurations (YAML)
*.csv             # Your wine catalog data
shopify_wine_importer.py  # Shopify import (your existing code)
```

## ⚙️ Configuration

All site-specific selectors in `config/sites/*.yaml`  
All product fields in `config/products/*.yaml`

Change selectors without touching code.

## 🎯 Current Setup

- **70 wines** imported to Shopify
- **100% image coverage**
- **2 wines** with real compare-at pricing
- **All authentic data** from Total Wine