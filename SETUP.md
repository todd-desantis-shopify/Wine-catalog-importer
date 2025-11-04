# ⚙️ Basic Configuration Guide

## 1. Shopify Credentials

**Copy and edit:**
```bash
cp config_template.py config.py
```

**Fill in `config.py`:**
```python
SHOPIFY_CONFIG = {
    'SHOP_URL': 'https://your-store.myshopify.com',
    'ACCESS_TOKEN': 'shpat_xxxxx...',  # From Shopify Admin
}
```

## 2. Create Collection URL List

**Copy and edit:**
```bash
cp collections_template.txt collections.txt
```

**Add collection page URLs** (one per line):
```
https://www.totalwine.com/wine/red-wine/c/000009
https://www.totalwine.com/wine/white-wine/c/000002
```

The crawler will:
1. Visit each collection page
2. Extract all product detail URLs
3. Crawl each product page
4. Output Shopify CSV

## 3. Create Product Config

**Copy the template:**
```bash
cp config/products/product_template.yaml config/products/wine.yaml
```

**Edit to add extra fields:**
```yaml
product_type: "wine"

extra_fields:
  - varietal
  - region
  - abv
  - taste_notes
```

**Standard fields are automatic:**
- title, price, collection, description, msrp, brand, sku, image_url

**Examples for different products:**
```yaml
# Wine
extra_fields: [varietal, region, country, abv, wine_type]

# Electronics
extra_fields: [model, specs, warranty, dimensions]

# Clothing
extra_fields: [size, color, material, fit]
```

**For different sites:**
- Copy `config/sites/totalwine.yaml` → `config/sites/amazon.yaml`  
- Update `collection_page` selectors for how Amazon structures links
- Update `selectors` for Amazon's product page HTML

## That's it!

Two simple YAML files control everything.
