# 🕷️ Smart E-commerce Crawler for Shopify

Automatically extracts product data from any e-commerce site using AI + browser automation.

## 🚀 Quick Start (For Teammates)

### Setup (One Time):
```bash
git clone <repo>
cd "Wine Catalog"
pip install -r requirements.txt
```

In Cursor:
1. Click browser extension icon → Connect
2. Open this folder in Cursor

### Usage:
**In Cursor chat, just say:**
```
Crawl this collection page: https://site.com/products
```

The AI will:
- Navigate to the page with the browser
- Extract all product links
- Visit each product page
- Extract: title, price, msrp, brand, sku, image, description
- Save to `{site}_{category}.csv`

That's it! CSV is ready to import to Shopify.

## 📋 For AI Context

Include `CRAWLING_INSTRUCTIONS.md` in your Cursor context so the AI knows how to crawl when you provide a URL.

## 🎯 What It Does

- **Auto-detects** product links on collection pages
- **Auto-extracts** standard Shopify fields from any site
- **Bypasses bot protection** using real browser
- **Outputs Shopify CSV** ready to import
- **No config files needed** - just works!