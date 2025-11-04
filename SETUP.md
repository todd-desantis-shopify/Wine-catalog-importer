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

## 3. Customize Fields to Extract

**Edit `config/products/wine.yaml`** (or create new product configs):

Turn fields on/off:
```yaml
fields:
  - name: "name"
    enabled: true       # Include this field
    required: true
  
  - name: "expert_rating"
    enabled: false      # Skip this field
    required: false
```

**For different product types:**
- Copy `config/products/wine.yaml` → `config/products/electronics.yaml`
- Update fields list for electronics (model, specs, warranty, etc.)
- Set `enabled: true` for fields that product type has

**For different sites:**
- Copy `config/sites/totalwine.yaml` → `config/sites/amazon.yaml`  
- Update `collection_page` selectors for how Amazon structures links
- Update `selectors` for Amazon's product page HTML

## That's it!

Two simple YAML files control everything.
