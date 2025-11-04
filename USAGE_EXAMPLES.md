# 🛍️ Generic E-commerce Catalog System - Usage Examples

## 🎯 Quick Start

The system is now completely modular and can work with any e-commerce site and product type!

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables for Shopify
export SHOPIFY_SHOP_URL="https://your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="your_access_token"
```

## 🍷 Example 1: Wine Catalog (Using Existing Data)

### Option A: Use Existing Wine Data
```bash
# Full process with existing CSV
python run_catalog_system.py \
    --site totalwine \
    --product wine \
    --platform shopify \
    --csv master_wine_catalog.csv
```

### Option B: Import Only (Skip Crawling)
```bash
# Just setup platform and import
python run_catalog_system.py \
    --import-only \
    --platform shopify \
    --product wine \
    --csv master_wine_catalog.csv
```

### Option C: Setup Only
```bash
# Setup metafields and collections only
python run_catalog_system.py \
    --setup-only \
    --platform shopify \
    --product wine \
    --csv master_wine_catalog.csv
```

## 📱 Example 2: Electronics from Amazon (New Configuration)

### Step 1: Create Configurations
```bash
# Create Amazon site configuration
python configure.py --create-site
# Enter: amazon, Amazon, https://www.amazon.com, etc.

# Create electronics product configuration  
python configure.py --create-product
# Enter: electronics, with fields like brand, model, price, etc.
```

### Step 2: Run Full Process
```bash
# Crawl Amazon electronics and import to Shopify
python run_catalog_system.py \
    --site amazon \
    --product electronics \
    --platform shopify \
    --urls "https://amazon.com/product1,https://amazon.com/product2"
```

## 👕 Example 3: Clothing from Any Site

### Step 1: Create Clothing Product Config
```bash
python configure.py --create-product
# Configure fields: name, brand, size, color, material, price, etc.
```

### Step 2: Run with URL File
```bash
# Create urls.txt with clothing product URLs
echo "https://site.com/shirt1" > clothing_urls.txt
echo "https://site.com/dress1" >> clothing_urls.txt

# Run full process
python run_catalog_system.py \
    --site mysite \
    --product clothing \
    --platform shopify \
    --url-file clothing_urls.txt
```

## 🔧 Individual Steps

### Crawling Only
```bash
python run_catalog_system.py \
    --crawl-only \
    --site totalwine \
    --product wine \
    --urls "https://totalwine.com/wine1,https://totalwine.com/wine2" \
    --output-csv new_wines.csv
```

### Platform Setup Only
```bash
python run_catalog_system.py \
    --setup-only \
    --platform shopify \
    --product wine \
    --csv products.csv
```

### Import with Dry Run
```bash
python run_catalog_system.py \
    --import-only \
    --platform shopify \
    --product wine \
    --csv products.csv \
    --dry-run
```

## 🎨 Advanced Usage

### Custom Batch Size
```bash
python run_catalog_system.py \
    --platform shopify \
    --product wine \
    --csv products.csv \
    --batch-size 10
```

### Skip Platform Setup
```bash
python run_catalog_system.py \
    --site totalwine \
    --product wine \
    --platform shopify \
    --csv products.csv \
    --skip-setup
```

### Continue on Errors
```bash
python run_catalog_system.py \
    --site totalwine \
    --product wine \
    --platform shopify \
    --csv products.csv \
    --continue-on-error
```

## 📋 Configuration Management

### List All Configurations
```bash
python configure.py --list
```

### Test Configurations
```bash
python configure.py --test
```

### Create New Site Config
```bash
python configure.py --create-site
```

### Create New Product Config
```bash
python configure.py --create-product
```

### Create New Platform Config
```bash
python configure.py --create-platform
```

## 🌐 Multi-Platform Support

The system is designed to support multiple platforms. Currently implemented:
- ✅ **Shopify** (GraphQL + REST API)
- 🚧 **WooCommerce** (coming soon)
- 🚧 **Magento** (coming soon)

## 🎯 Benefits of Modular System

1. **🔄 Reusable**: Works with any site and product type
2. **⚙️ Configurable**: No code changes needed for new sites
3. **🏢 Multi-platform**: Import to different e-commerce platforms  
4. **📈 Scalable**: Handle catalogs of any size
5. **🛡️ Robust**: Error handling, retry logic, rate limiting
6. **🧩 Modular**: Run individual steps independently
7. **📊 Trackable**: Detailed logging and progress reporting

## 🎉 Migration from Original System

Your existing wine catalog data works seamlessly:
```bash
# Use your existing master_wine_catalog.csv
python run_catalog_system.py \
    --platform shopify \
    --product wine \
    --csv master_wine_catalog.csv \
    --skip-setup  # Metafields already exist
```

The system maintains 100% compatibility with your existing 70-wine catalog while adding powerful new capabilities for any future products or sites!
