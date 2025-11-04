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

## 3. Create Product Config for What You're Crawling

**Copy the template:**
```bash
cp config/products/product_template.yaml config/products/YOURTYPE.yaml
```

**Examples:**
```bash
# For wine products
cp config/products/product_template.yaml config/products/wine.yaml

# For electronics  
cp config/products/product_template.yaml config/products/electronics.yaml

# For clothing
cp config/products/product_template.yaml config/products/clothing.yaml
```

**Edit the file** to add your product-specific fields:
```yaml
product_type: "wine"  # or electronics, clothing, etc.

fields:
  # Common fields (all products have these)
  - name: "name"
    enabled: true
  - name: "price"
    enabled: true
  
  # Wine-specific fields
  - name: "varietal"
    enabled: true
    shopify_metafield: "wine.varietal"
  - name: "region"
    enabled: true
    shopify_metafield: "wine.region"
```

**For different sites:**
- Copy `config/sites/totalwine.yaml` → `config/sites/amazon.yaml`  
- Update `collection_page` selectors for how Amazon structures links
- Update `selectors` for Amazon's product page HTML

## That's it!

Two simple YAML files control everything.
