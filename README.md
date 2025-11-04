# 🕷️ Smart E-commerce Crawler for Shopify

Intelligent crawler that automatically figures out any e-commerce site and extracts product data.

## 🚀 Quick Start

**Just give it a collection page URL:**
```bash
python3 smart_crawl.py \
  --url "https://www.totalwine.com/wine/red-wine/c/000009" \
  --output wines.csv
```

That's it. It automatically:
1. Finds all product links on the collection page
2. Crawls each product detail page
3. Auto-extracts: title, price, msrp, brand, sku, image, description
4. Outputs Shopify-ready CSV

## ⚙️ Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Optional: Add product-specific fields
cp config/products/product_template.yaml config/products/wine.yaml
```

Edit `wine.yaml` to add extra fields:
```yaml
extra_fields:
  - varietal
  - region
  - abv
```

Then run with `--product wine` to extract those too.

## 📊 What Gets Extracted

**Standard fields (automatic):**
- title
- price
- msrp (compare at price)
- brand
- sku
- image_url
- description
- collection

**Extra fields (optional):**
- Whatever you add in `config/products/YOURTYPE.yaml`

## 🎯 Examples

```bash
# Basic - just standard fields
python3 smart_crawl.py --url "https://site.com/collection" --output products.csv

# With product-specific fields
python3 smart_crawl.py --url "https://site.com/wines" --product wine --output wines.csv

# Limit to first 10 products
python3 smart_crawl.py --url "https://site.com/collection" --output test.csv --limit 10
```

## 🎉 Import to Shopify

```bash
# Use your existing importer
python3 import_wines.py
```