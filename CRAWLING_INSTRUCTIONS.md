# 🕷️ Crawling Instructions for AI

## When User Provides a Collection URL:

**User will say something like:**
- "Crawl this: https://site.com/products"
- "Extract products from: https://site.com/category" 
- "Get all items from: [URL]"

## Your Response (AI):

1. **Navigate to collection page** using `browser_navigate`
2. **Take snapshot** using `browser_snapshot`
3. **Extract all product links** from snapshot (look for links to product detail pages)
4. **For each product** (limit to 10-20 for testing):
   - Navigate to product URL
   - Take snapshot
   - Extract: title, price, msrp, brand, sku, image_url, description, collection
5. **Save to CSV** in Shopify format with standard fields
6. **Inform user** CSV is ready

## Standard Shopify Fields (Always Extract):
- title
- price
- msrp (compare at price, if shown)
- brand  
- sku (from URL or page)
- image_url (main product image)
- description
- collection (from breadcrumbs or URL path)

## Auto-detect Extra Fields:
- If product has unique attributes (size, color, unit, etc.) include them as extra columns

## Output:
- Shopify-compatible CSV
- Filename: `{site}_{category}.csv` (e.g., `citarella_fish.csv`)
- Ready to import with existing import scripts
