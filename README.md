# 🍷 E-commerce Catalog System for Shopify

Simple, modular system for crawling product data and importing to Shopify.

## ⚙️ Setup

1. **Copy config template:**
   ```bash
   cp config_template.py config.py
   # Edit config.py with your Shopify credentials
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create product config** for what you're crawling:
   ```bash
   cp config/products/product_template.yaml config/products/YOURPRODUCT.yaml
   # Edit to add your product-specific fields
   # e.g., wine.yaml, electronics.yaml, clothing.yaml
   ```

## 🚀 Quick Start

### 1. Crawl Products
```bash
# Create collections.txt with collection page URLs (see collections_template.txt)
python3 crawler/simple_crawl.py --site totalwine --product wine --collections collections.txt --output wines.csv
```

### 2. Setup Shopify
```bash
python3 setup/setup_shopify.py --product wine
```

### 3. Import to Shopify  
```bash
python3 import_wines.py  # Uses existing importer with CSV
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