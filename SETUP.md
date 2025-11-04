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
    'ACCESS_TOKEN': 'shpat_xxxxx...',
    'API_VERSION': '2024-10',
}
```

## 2. Create URL List

**Copy and edit:**
```bash
cp urls_template.txt urls.txt
```

**Add your product URLs** (one per line):
```
https://www.totalwine.com/wine/red-wine/cabernet/.../p/214578750
https://www.totalwine.com/wine/white-wine/chardonnay/.../p/117938750
```

## 3. Customize Fields to Extract

**Edit `config/sites/totalwine.yaml`:**

Turn fields on/off as needed:
```yaml
fields_to_extract:
  - field: "name"
    enabled: true       # Always extract
    required: true
  
  - field: "expert_rating"
    enabled: false      # Skip this field
    required: false
```

For a **different site** (like Amazon):
1. Copy `config/sites/totalwine.yaml` to `config/sites/amazon.yaml`
2. Update `fields_to_extract` for what Amazon has
3. Update CSS selectors for Amazon's page structure

## That's it!

Three simple config files determine everything the crawler does.
