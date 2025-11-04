#!/usr/bin/env python3
"""
Configuration Manager for Generic E-commerce Catalog System
Handles loading and managing YAML configurations for sites, products, and platforms.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import re
from string import Template

class ConfigManager:
    """Manages configuration loading and environment variable substitution"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize config manager with config directory"""
        if config_dir is None:
            config_dir = Path(__file__).parent
        
        self.config_dir = Path(config_dir)
        self.sites_dir = self.config_dir / "sites"
        self.products_dir = self.config_dir / "products"  
        self.platforms_dir = self.config_dir / "platforms"
        self._loaded_configs = {}
    
    def load_site_config(self, site_name: str) -> Dict[str, Any]:
        """Load site-specific configuration"""
        cache_key = f"site_{site_name}"
        if cache_key in self._loaded_configs:
            return self._loaded_configs[cache_key]
            
        config_path = self.sites_dir / f"{site_name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Site config not found: {config_path}")
            
        config = self._load_yaml(config_path)
        self._loaded_configs[cache_key] = config
        return config
    
    def load_product_config(self, product_type: str) -> Dict[str, Any]:
        """Load product-type configuration"""
        cache_key = f"product_{product_type}"
        if cache_key in self._loaded_configs:
            return self._loaded_configs[cache_key]
            
        config_path = self.products_dir / f"{product_type}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Product config not found: {config_path}")
            
        config = self._load_yaml(config_path)
        self._loaded_configs[cache_key] = config
        return config
    
    def load_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """Load platform-specific configuration"""
        cache_key = f"platform_{platform_name}"
        if cache_key in self._loaded_configs:
            return self._loaded_configs[cache_key]
            
        config_path = self.platforms_dir / f"{platform_name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Platform config not found: {config_path}")
            
        config = self._load_yaml(config_path)
        
        # Substitute environment variables
        config = self._substitute_env_vars(config)
        
        self._loaded_configs[cache_key] = config
        return config
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load {file_path}: {e}")
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in config"""
        if isinstance(config, dict):
            return {key: self._substitute_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Handle ${VAR} or $VAR patterns
            pattern = r'\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)'
            
            def replace_var(match):
                var_name = match.group(1) or match.group(2)
                return os.getenv(var_name, match.group(0))  # Keep original if not found
                
            return re.sub(pattern, replace_var, config)
        else:
            return config
    
    def get_available_sites(self) -> list[str]:
        """Get list of available site configurations"""
        if not self.sites_dir.exists():
            return []
        return [f.stem for f in self.sites_dir.glob("*.yaml")]
    
    def get_available_products(self) -> list[str]:
        """Get list of available product configurations"""
        if not self.products_dir.exists():
            return []
        return [f.stem for f in self.products_dir.glob("*.yaml")]
    
    def get_available_platforms(self) -> list[str]:
        """Get list of available platform configurations"""
        if not self.platforms_dir.exists():
            return []
        return [f.stem for f in self.platforms_dir.glob("*.yaml")]
    
    def validate_config(self, config_type: str, config_name: str) -> bool:
        """Validate that a configuration exists and is loadable"""
        try:
            if config_type == "site":
                self.load_site_config(config_name)
            elif config_type == "product":
                self.load_product_config(config_name)
            elif config_type == "platform":
                self.load_platform_config(config_name)
            else:
                return False
            return True
        except Exception:
            return False
    
    def get_field_mapping(self, product_type: str, platform: str) -> Dict[str, str]:
        """Get field mapping between product config and platform"""
        product_config = self.load_product_config(product_type)
        platform_config = self.load_platform_config(platform)
        
        field_mapping = {}
        
        for field in product_config.get('fields', []):
            field_name = field['name']
            
            # Check for platform-specific field mapping
            platform_field_key = f"{platform}_field"
            if platform_field_key in field:
                field_mapping[field_name] = field[platform_field_key]
            elif f"{platform}_metafield" in field:
                field_mapping[field_name] = field[f"{platform}_metafield"]
            
        return field_mapping
    
    def get_collection_rules(self, product_type: str) -> Dict[str, Any]:
        """Get collection creation rules for product type"""
        product_config = self.load_product_config(product_type)
        return product_config.get('collections', [])
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._loaded_configs.clear()

# Convenience functions for backward compatibility
def load_site_config(site_name: str) -> Dict[str, Any]:
    """Load site configuration"""
    manager = ConfigManager()
    return manager.load_site_config(site_name)

def load_product_config(product_type: str) -> Dict[str, Any]:
    """Load product configuration"""
    manager = ConfigManager()
    return manager.load_product_config(product_type)

def load_platform_config(platform_name: str) -> Dict[str, Any]:
    """Load platform configuration"""
    manager = ConfigManager()
    return manager.load_platform_config(platform_name)

if __name__ == "__main__":
    # Test configuration loading
    manager = ConfigManager()
    
    print("📁 Available configurations:")
    print(f"Sites: {manager.get_available_sites()}")
    print(f"Products: {manager.get_available_products()}")  
    print(f"Platforms: {manager.get_available_platforms()}")
    
    # Test loading
    try:
        site_config = manager.load_site_config("totalwine")
        print(f"\n✅ Total Wine config loaded: {site_config['site']['name']}")
    except Exception as e:
        print(f"\n❌ Failed to load Total Wine config: {e}")
    
    try:
        product_config = manager.load_product_config("wine")
        field_count = len(product_config.get('fields', []))
        print(f"✅ Wine product config loaded: {field_count} fields")
    except Exception as e:
        print(f"❌ Failed to load wine product config: {e}")
    
    try:
        platform_config = manager.load_platform_config("shopify")
        metafield_count = len(platform_config.get('metafields', []))
        print(f"✅ Shopify platform config loaded: {metafield_count} metafields")
    except Exception as e:
        print(f"❌ Failed to load Shopify platform config: {e}")
