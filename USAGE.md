# 🍷 Wine Import Workflow Guide

This guide shows you the **correct order** to set up and use the wine importer.

## 🎯 **Three-Step Process**

### **Step 1: Setup Metafields (Run Once)** 
Create all wine metafield definitions in your Shopify store:

```bash
# Option A: Enhanced metafields with categories (Recommended)
python3 setup_enhanced_metafields.py

# Option B: Basic metafields 
python3 setup_metafields.py
```

**Enhanced setup creates 16 categorized metafields:**
- 🍷 **Wine Details** (7): varietal, vintage, ABV, body, style, size, type
- 🌍 **Location** (3): appellation, region, country/state  
- 👃 **Tasting** (1): tasting notes
- ⭐ **Ratings** (3): expert ratings, customer ratings, review count
- 💰 **Pricing** (1): mix-6 pricing
- 🔗 **Reference** (1): source URL

**✅ Run this ONCE per Shopify store**
**✅ Uses latest API version (2024-10)**
**✅ Metafields appear organized by category in Shopify Admin**

### **Step 2: Setup Collections (Run Once)**
Create organized collections for better wine browsing:

```bash
python3 setup_collections.py
```

**This creates automated collections:**
- 🍷 **Wine Types**: Red, White, Rosé, Sparkling  
- 💰 **Price Ranges**: Under $20, $20-50, $50+ 
- 🍇 **Varietals**: Cabernet Sauvignon, Chardonnay, Pinot Noir
- 🌍 **Regions**: California, Napa Valley

**✅ Run this ONCE per Shopify store**

### **Step 3: Import Products (Run Many Times)**
Import wine products using the existing metafields and collections:

```bash
# Import single file
python3 import_wines.py sample_wine_catalog.csv

# Import different batches
python3 import_wines.py red_wines_batch_1.csv
python3 import_wines.py white_wines_batch_2.csv  
python3 import_wines.py total_wine_cabernets.csv
```

**✅ Run this for every new wine catalog**

## 🔧 **Initial Configuration**

Before running either script, configure your Shopify credentials:

1. **Get API Access Token**:
   - Shopify Admin → Settings → Apps and sales channels
   - "Develop apps for your store" → "Create an app"
   - Name: "Wine Importer"
   - Configure Admin API scopes: Enable `write_products`, `read_products`
   - Install app → Copy access token

2. **Configure credentials**:
   ```bash
   # Edit config.py with your real values:
   SHOPIFY_CONFIG = {
       'SHOP_URL': 'https://your-store-name.myshopify.com',
       'ACCESS_TOKEN': 'shpat_abc123...',  # Your actual token
   }
   ```

## 📊 **Example Workflow**

```bash
# 1. First time setup (once per store)
python3 setup_metafields.py
# ✅ Created wine.varietal, wine.vintage, wine.appellation...

# 2. Import your first batch
python3 import_wines.py sample_wine_catalog.csv
# ✅ Imported 1858 Caymus Cabernet

# 3. Later: Import more wines
python3 import_wines.py red_wines_january.csv
# ✅ Imported 50 red wines

# 4. Even later: Import another batch  
python3 import_wines.py white_wines_february.csv
# ✅ Imported 75 white wines
```

## 🚨 **What Happens If You Run Setup Multiple Times?**

**It's safe!** The setup script detects existing metafields:

```
⚠️ Metafield definition already exists: wine.varietal
⚠️ Metafield definition already exists: wine.vintage  
...
```

No duplicates are created.

## 📁 **File Formats**

Your CSV files need these headers (minimum):
```csv
Name,Brand,Country_State,Region,Appellation,Wine_Type,Varietal,Style,ABV,Taste_Notes,Body,SKU,Size,Price,Mix_6_Price,Customer_Rating,Customer_Reviews,Expert_Rating,URL,Image_URL,Product_Highlights
```

## 🔄 **Alternative: Manual Import**

If API import fails, you can always fall back to manual CSV import:

1. Generate Shopify-ready CSV:
   ```bash
   python3 shopify_wine_importer.py  # Creates shopify_wine_import.csv
   ```

2. Import manually:
   - Shopify Admin → Products → Import
   - Upload `shopify_wine_import.csv`
   - Metafields created automatically!
