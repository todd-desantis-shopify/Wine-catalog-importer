# 🛍️ Generic E-commerce Catalog System

A modular, configurable system for crawling product data from any e-commerce site and importing to any platform.

## 🏗️ Architecture

### 1. **Universal Web Crawler** (`crawler/`)
- **Site-agnostic**: Works with any e-commerce website
- **Product-agnostic**: Wines, electronics, clothing, etc.
- **Configuration-driven**: CSS selectors and patterns in config files
- **Output**: Standardized CSV format

### 2. **Platform Setup** (`setup/`)
- **Collections Manager**: Auto-creates collections from product data
- **Metafields Manager**: Auto-creates custom fields from attributes
- **Multi-platform**: Shopify, WooCommerce, Magento support
- **Rule-based**: Configurable collection and field creation rules

### 3. **Product Importer** (`importer/`)
- **Multi-platform**: Import to Shopify, WooCommerce, etc.
- **Batch processing**: Efficient handling of large catalogs
- **Media management**: Images, videos, documents
- **Advanced features**: Variants, inventory, SEO, collections

### 4. **Configuration System** (`config/`)
- **Site Configs**: Different e-commerce sites (Total Wine, Amazon, etc.)
- **Product Configs**: Different product types with specific fields
- **Platform Configs**: Target platform settings (Shopify, WooCommerce, etc.)

## 🚀 Usage Workflow

```bash
# 1. Configure site and product type
python configure.py --site totalwine --product wine

# 2. Crawl products from any site  
python crawler/crawl.py --config config/sites/totalwine.yaml --output data/wines.csv

# 3. Setup collections and metafields
python setup/setup_platform.py --config config/platforms/shopify.yaml --data data/wines.csv

# 4. Import products to platform
python importer/import_products.py --config config/platforms/shopify.yaml --data data/wines.csv
```

## 📁 Directory Structure

```
├── crawler/                 # Universal web crawler
│   ├── crawl.py            # Main crawler engine
│   ├── extractors/         # Site-specific extractors
│   └── utils/              # Helper functions
├── setup/                   # Platform setup tools
│   ├── collections.py      # Collections manager
│   ├── metafields.py       # Metafields manager
│   └── platforms/          # Platform-specific setup
├── importer/               # Product import tools
│   ├── import_products.py  # Main importer
│   ├── platforms/          # Platform-specific importers
│   └── media/              # Media processing
├── config/                 # Configuration files
│   ├── sites/              # Site-specific configs
│   ├── products/           # Product-type configs
│   └── platforms/          # Platform configs
├── data/                   # Generated data files
└── templates/              # Template configs
```

## 🎯 Benefits

- **🔄 Reusable**: Works with any site and product type
- **⚙️ Configurable**: No code changes needed for new sites
- **🏢 Multi-platform**: Import to different e-commerce platforms
- **📈 Scalable**: Handle catalogs of any size
- **🛡️ Robust**: Error handling, retry logic, rate limiting
