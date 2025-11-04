#!/usr/bin/env python3
"""Simple config loader for YAML files"""
import yaml
import os
import re
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path(__file__).parent
    
    def load_site_config(self, site_name: str) -> dict:
        with open(self.config_dir / "sites" / f"{site_name}.yaml") as f:
            return yaml.safe_load(f)
    
    def load_product_config(self, product_type: str) -> dict:
        with open(self.config_dir / "products" / f"{product_type}.yaml") as f:
            return yaml.safe_load(f)
    
    def load_shopify_config(self) -> dict:
        config = yaml.safe_load(open(self.config_dir / "shopify_config.yaml"))
        # Substitute env vars
        for key in ['shop_url', 'access_token']:
            val = config['shopify'][key]
            if val.startswith('${'):
                var = val[2:-1]
                config['shopify'][key] = os.getenv(var, '')
        return config
