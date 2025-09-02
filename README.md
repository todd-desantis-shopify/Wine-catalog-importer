# 🍷 Wine Catalog to Shopify Importer

Automated system to crawl wine data from retailers and import to Shopify with rich metafields.

## 🚀 Quick Start

### Test with Sample Data
```bash
# Run the transformation
python3 shopify_wine_importer.py

# This generates:
# - shopify_wine_import.csv (for manual import)
# - Displays preview of transformed product
```

### Manual Import to Shopify
1. Open the generated `shopify_wine_import.csv`  
2. Go to Shopify Admin → Products → Import
3. Upload the CSV file
4. All wine metafields will be automatically created!

### API Import (Automatic)
1. Copy `config_template.py` to `config.py`
2. Fill in your Shopify store URL and access token
3. Run: `python3 test_api_import.py`

## 📊 What Gets Imported

### Standard Shopify Fields
- **Title**: Full wine name
- **Handle**: URL-friendly slug  
- **Vendor**: Wine brand/producer
- **Price**: Retail price
- **SKU**: Product identifier
- **Tags**: Varietal, region, appellation
- **Description**: Tasting notes and highlights

### Wine Metafields (Custom Fields)
- **wine.varietal**: Grape variety (e.g., "Cabernet Sauvignon")
- **wine.vintage**: Year (e.g., 2022)
- **wine.appellation**: Specific region (e.g., "Paso Robles")
- **wine.region**: Broader region (e.g., "Central Coast") 
- **wine.country_state**: Location (e.g., "California")
- **wine.abv**: Alcohol percentage (e.g., 13.8)
- **wine.body**: Wine body (Light/Medium/Full-bodied)
- **wine.style**: Style descriptor (Elegant/Intense)
- **wine.tasting_notes**: Flavor profile
- **wine.expert_rating**: Professional ratings
- **wine.customer_rating**: Customer reviews (e.g., "4.4/5")
- **wine.customer_reviews_count**: Number of reviews
- **wine.mix_6_price**: Bulk pricing
- **wine.source_url**: Original retailer URL
- **wine.size**: Bottle size (e.g., "750ml")
- **wine.wine_type**: Category (e.g., "Red Wine")

## 🔧 Setup Shopify API

1. **Create Private App**:
   - Shopify Admin → Settings → Apps and sales channels
   - "Develop apps for your store" → "Create an app"
   
2. **Configure API Scopes**:
   - Enable `write_products`
   - Enable `read_products`
   - Enable `write_product_listings`
   - Enable `read_product_listings`

3. **Get Credentials**:
   - Install the app
   - Copy Admin API access token
   - Add to `config.py`

## 📁 Files

- `shopify_wine_importer.py` - Main transformation script
- `sample_wine_catalog.csv` - Crawled wine data (input)  
- `shopify_wine_import.csv` - Shopify-ready CSV (output)
- `test_api_import.py` - API import demo
- `config_template.py` - Configuration template
- `requirements.txt` - Python dependencies

## ✅ Test Results

Successfully transformed **1858 by Caymus Vineyards Cabernet Sauvignon Paso Robles**:

- ✅ All wine metadata extracted and structured
- ✅ 15+ metafields automatically created
- ✅ Ready for Shopify import
- ✅ Proper handle and tags generated
- ✅ Price and inventory configured

## 🔮 Next Steps

1. **Scale Up**: Crawl entire wine catalog (hundreds/thousands of products)
2. **Image Import**: Add wine bottle image URLs  
3. **Inventory Sync**: Real-time stock updates
4. **Review Sync**: Update ratings automatically
5. **Multi-Store**: Support multiple wine retailers

Ready to import your first wine! 🍷
