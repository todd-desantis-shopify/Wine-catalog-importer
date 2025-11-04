#!/usr/bin/env python3
"""
Main Orchestration Script for Generic E-commerce Catalog System
Runs the complete process: crawl → setup → import
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
import subprocess
import tempfile

def run_command(command: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"🔄 {description}")
    print(f"   Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print("Output:", result.stdout.strip())
            return True
        else:
            print(f"❌ {description} failed")
            print("Error:", result.stderr.strip())
            return False
            
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def create_url_file(urls: list, temp_dir: Path) -> Path:
    """Create temporary file with URLs"""
    url_file = temp_dir / "urls.txt"
    with open(url_file, 'w') as f:
        for url in urls:
            f.write(f"{url}\n")
    return url_file

def run_full_process(args):
    """Run the complete catalog process"""
    print("🚀 Starting Generic E-commerce Catalog System")
    print("=" * 60)
    
    # Validate configurations exist
    config_dir = Path(__file__).parent / "config"
    
    site_config = config_dir / "sites" / f"{args.site}.yaml"
    product_config = config_dir / "products" / f"{args.product}.yaml"  
    platform_config = config_dir / "platforms" / f"{args.platform}.yaml"
    
    for config_file, config_type in [
        (site_config, "site"),
        (product_config, "product"),
        (platform_config, "platform")
    ]:
        if not config_file.exists():
            print(f"❌ {config_type.title()} configuration not found: {config_file}")
            print(f"   Create it with: python configure.py --create-{config_type}")
            return False
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        csv_file = temp_path / "products.csv"
        
        success = True
        
        # Step 1: Crawling (if URLs provided)
        if args.urls or args.url_file:
            print("\n" + "="*60)
            print("📡 STEP 1: CRAWLING PRODUCTS")
            print("="*60)
            
            # Prepare URL file
            if args.urls:
                urls = args.urls.split(',')
                url_file = create_url_file(urls, temp_path)
            else:
                url_file = Path(args.url_file)
                if not url_file.exists():
                    print(f"❌ URL file not found: {url_file}")
                    return False
            
            # Run crawler
            crawl_command = [
                "python3", "crawler/crawl.py",
                "--site", args.site,
                "--product", args.product,
                "--urls", str(url_file),
                "--output", str(csv_file)
            ]
            
            success = run_command(crawl_command, "Product crawling")
            
        elif args.csv:
            print("\n" + "="*60)
            print("📂 STEP 1: USING PROVIDED CSV")
            print("="*60)
            
            # Copy provided CSV
            import shutil
            shutil.copy(args.csv, csv_file)
            print(f"✅ Using CSV file: {args.csv}")
        else:
            print("❌ No data source provided. Use --urls, --url-file, or --csv")
            return False
        
        if not success or not csv_file.exists():
            print("❌ No product data available for setup and import")
            return False
        
        # Step 2: Platform Setup
        if not args.skip_setup:
            print("\n" + "="*60)
            print("🏗️  STEP 2: PLATFORM SETUP")
            print("="*60)
            
            setup_command = [
                "python3", "setup/setup_platform.py",
                "--platform", args.platform,
                "--product", args.product,
                "--csv", str(csv_file)
            ]
            
            success = run_command(setup_command, "Platform setup (metafields & collections)")
            
            if not success and not args.continue_on_error:
                print("❌ Platform setup failed. Use --continue-on-error to proceed anyway.")
                return False
        else:
            print("\n🏗️  STEP 2: PLATFORM SETUP (SKIPPED)")
        
        # Step 3: Product Import
        if not args.skip_import:
            print("\n" + "="*60)
            print("📦 STEP 3: PRODUCT IMPORT")
            print("="*60)
            
            import_command = [
                "python3", "importer/import_products.py",
                "--platform", args.platform,
                "--product", args.product,
                "--csv", str(csv_file)
            ]
            
            if args.dry_run:
                import_command.append("--dry-run")
            
            if args.batch_size:
                import_command.extend(["--batch-size", str(args.batch_size)])
            
            success = run_command(import_command, "Product import")
        else:
            print("\n📦 STEP 3: PRODUCT IMPORT (SKIPPED)")
        
        # Copy final CSV to output directory if specified
        if success and args.output_csv:
            import shutil
            shutil.copy(csv_file, args.output_csv)
            print(f"📁 Final CSV saved to: {args.output_csv}")
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("🎉 CATALOG SYSTEM COMPLETE!")
        print("✅ All steps completed successfully")
    else:
        print("⚠️  CATALOG SYSTEM COMPLETED WITH ISSUES")
        print("❌ Some steps failed - check logs above")
    print("="*60)
    
    return success

def run_individual_step(args):
    """Run individual step based on arguments"""
    if args.crawl_only:
        print("📡 Running crawler only...")
        if not args.urls and not args.url_file:
            print("❌ URLs required for crawling. Use --urls or --url-file")
            return False
        
        # Prepare URL file
        if args.urls:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for url in args.urls.split(','):
                    f.write(f"{url}\n")
                url_file = f.name
        else:
            url_file = args.url_file
        
        command = [
            "python3", "crawler/crawl.py",
            "--site", args.site,
            "--product", args.product,
            "--urls", url_file,
            "--output", args.output_csv or "products.csv"
        ]
        
        return run_command(command, "Product crawling")
    
    elif args.setup_only:
        print("🏗️  Running platform setup only...")
        if not args.csv:
            print("❌ CSV file required for setup. Use --csv")
            return False
        
        command = [
            "python3", "setup/setup_platform.py",
            "--platform", args.platform,
            "--product", args.product,
            "--csv", args.csv
        ]
        
        return run_command(command, "Platform setup")
    
    elif args.import_only:
        print("📦 Running product import only...")
        if not args.csv:
            print("❌ CSV file required for import. Use --csv")
            return False
        
        command = [
            "python3", "importer/import_products.py",
            "--platform", args.platform,
            "--product", args.product,
            "--csv", args.csv
        ]
        
        if args.dry_run:
            command.append("--dry-run")
        
        if args.batch_size:
            command.extend(["--batch-size", str(args.batch_size)])
        
        return run_command(command, "Product import")
    
    return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generic E-commerce Catalog System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full process with URLs
  python run_catalog_system.py --site totalwine --product wine --platform shopify --urls "https://example.com/wine1,https://example.com/wine2"
  
  # Full process with URL file
  python run_catalog_system.py --site totalwine --product wine --platform shopify --url-file urls.txt
  
  # Full process with existing CSV
  python run_catalog_system.py --site totalwine --product wine --platform shopify --csv products.csv
  
  # Crawling only
  python run_catalog_system.py --crawl-only --site totalwine --product wine --urls "url1,url2" --output-csv products.csv
  
  # Setup only
  python run_catalog_system.py --setup-only --platform shopify --product wine --csv products.csv
  
  # Import only (dry run)
  python run_catalog_system.py --import-only --platform shopify --product wine --csv products.csv --dry-run
        """
    )
    
    # Required configurations
    parser.add_argument("--site", help="Site configuration name")
    parser.add_argument("--product", required=True, help="Product configuration name")
    parser.add_argument("--platform", help="Platform configuration name")
    
    # Data sources (mutually exclusive)
    data_group = parser.add_mutually_exclusive_group()
    data_group.add_argument("--urls", help="Comma-separated URLs to crawl")
    data_group.add_argument("--url-file", help="File containing URLs to crawl")
    data_group.add_argument("--csv", help="Existing CSV file to use")
    
    # Step control
    parser.add_argument("--crawl-only", action="store_true", help="Run crawling step only")
    parser.add_argument("--setup-only", action="store_true", help="Run platform setup only")
    parser.add_argument("--import-only", action="store_true", help="Run product import only")
    parser.add_argument("--skip-setup", action="store_true", help="Skip platform setup step")
    parser.add_argument("--skip-import", action="store_true", help="Skip product import step")
    
    # Options
    parser.add_argument("--output-csv", help="Output CSV file path")
    parser.add_argument("--batch-size", type=int, help="Import batch size")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't import")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue on non-critical errors")
    
    args = parser.parse_args()
    
    # Validate individual step arguments
    individual_steps = [args.crawl_only, args.setup_only, args.import_only]
    if sum(individual_steps) > 1:
        print("❌ Can only run one individual step at a time")
        return 1
    
    # Check if running individual step
    if any(individual_steps):
        # Individual step validation
        if args.crawl_only and not args.site:
            print("❌ --site required for crawling")
            return 1
        if (args.setup_only or args.import_only) and not args.platform:
            print("❌ --platform required for setup and import")
            return 1
        
        success = run_individual_step(args)
    else:
        # Full process validation
        if not args.site or not args.platform:
            print("❌ --site and --platform required for full process")
            return 1
        if not (args.urls or args.url_file or args.csv):
            print("❌ Data source required: --urls, --url-file, or --csv")
            return 1
        
        success = run_full_process(args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
