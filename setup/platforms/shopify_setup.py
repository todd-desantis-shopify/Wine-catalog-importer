#!/usr/bin/env python3
"""
Shopify Platform Setup
Handles Shopify-specific setup for metafields and collections using GraphQL and REST APIs.
"""

import requests
import json
import time
from typing import Dict, Any, List, Set, Optional
import logging

class ShopifySetup:
    """Shopify-specific setup handler"""
    
    def __init__(self, platform_config: Dict[str, Any]):
        """Initialize Shopify setup with configuration"""
        self.config = platform_config
        
        # API configuration
        auth_config = platform_config.get('auth', {})
        self.shop_url = auth_config.get('shop_url', '').rstrip('/')
        self.access_token = auth_config.get('access_token', '')
        
        if not self.shop_url or not self.access_token:
            raise ValueError("Shopify shop_url and access_token are required")
        
        # API settings
        api_config = platform_config.get('api', {})
        self.api_version = platform_config.get('api_version', '2025-07')
        self.rate_limit = api_config.get('rate_limit', 0.5)
        self.max_retries = api_config.get('max_retries', 3)
        
        # Setup headers
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        self.graphql_headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/graphql'
        }
        
        self.logger = logging.getLogger(__name__)
        self.last_request = 0
    
    def _rate_limit_wait(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        
        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            time.sleep(wait_time)
        
        self.last_request = time.time()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, use_graphql: bool = False) -> requests.Response:
        """Make API request with rate limiting and retry logic"""
        self._rate_limit_wait()
        
        url = f"{self.shop_url}/admin/api/{self.api_version}/{endpoint}"
        headers = self.graphql_headers if use_graphql else self.headers
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, params=data)
                elif method.upper() == 'POST':
                    if use_graphql:
                        response = requests.post(url, headers=headers, data=data)
                    else:
                        response = requests.post(url, headers=headers, json=data)
                elif method.upper() == 'PUT':
                    response = requests.put(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                return response
                
            except Exception as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def create_metafield_definition(self, metafield_config: Dict[str, Any]) -> bool:
        """Create a metafield definition using GraphQL"""
        namespace = metafield_config['namespace']
        key = metafield_config['key']
        name = metafield_config['name']
        description = metafield_config.get('description', '')
        field_type = metafield_config['type']
        
        # Check if metafield definition already exists
        if self._metafield_definition_exists(namespace, key):
            return False
        
        # GraphQL mutation to create metafield definition
        mutation = f"""
        mutation metafieldDefinitionCreate($definition: MetafieldDefinitionInput!) {{
            metafieldDefinitionCreate(definition: $definition) {{
                createdDefinition {{
                    id
                    name
                    namespace
                    key
                    type {{
                        name
                    }}
                }}
                userErrors {{
                    field
                    message
                }}
            }}
        }}
        """
        
        variables = {
            "definition": {
                "name": name,
                "namespace": namespace,
                "key": key,
                "description": description,
                "type": field_type,
                "ownerType": "PRODUCT"
            }
        }
        
        payload = {
            "query": mutation,
            "variables": variables
        }
        
        try:
            response = self._make_request('POST', 'graphql.json', json.dumps(payload), use_graphql=False)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'errors' in result:
                    self.logger.error(f"GraphQL errors: {result['errors']}")
                    return False
                
                data = result.get('data', {}).get('metafieldDefinitionCreate', {})
                
                if data.get('userErrors'):
                    self.logger.error(f"Metafield creation errors: {data['userErrors']}")
                    return False
                
                if data.get('createdDefinition'):
                    return True
                
            else:
                self.logger.error(f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating metafield definition: {e}")
            return False
        
        return False
    
    def _metafield_definition_exists(self, namespace: str, key: str) -> bool:
        """Check if metafield definition already exists"""
        query = """
        query {
            metafieldDefinitions(first: 250, ownerType: PRODUCT) {
                edges {
                    node {
                        namespace
                        key
                    }
                }
            }
        }
        """
        
        try:
            response = self._make_request('POST', 'graphql.json', json.dumps({"query": query}), use_graphql=False)
            
            if response.status_code == 200:
                result = response.json()
                definitions = result.get('data', {}).get('metafieldDefinitions', {}).get('edges', [])
                
                for edge in definitions:
                    node = edge.get('node', {})
                    if node.get('namespace') == namespace and node.get('key') == key:
                        return True
            
        except Exception as e:
            self.logger.debug(f"Error checking metafield definition: {e}")
        
        return False
    
    def create_collection(self, collection_name: str, rule_type: str, templates: Dict[str, Any], values: Set[str]) -> bool:
        """Create a collection using REST API"""
        # Check if collection already exists
        if self._collection_exists(collection_name):
            return False
        
        # Determine collection type and rules
        if rule_type == 'smart':
            return self._create_smart_collection(collection_name, templates, values)
        else:
            return self._create_automated_collection(collection_name, templates, values)
    
    def _create_smart_collection(self, collection_name: str, templates: Dict[str, Any], values: Set[str]) -> bool:
        """Create a smart collection with rules"""
        smart_templates = templates.get('smart', [])
        
        # Find matching template
        collection_rules = []
        for template in smart_templates:
            if template['name'] == collection_name:
                collection_rules = template.get('rules', [])
                break
        
        if not collection_rules:
            self.logger.warning(f"No rules found for smart collection: {collection_name}")
            return False
        
        collection_data = {
            "smart_collection": {
                "title": collection_name,
                "rules": collection_rules,
                "disjunctive": False,  # AND logic
                "published": True
            }
        }
        
        try:
            response = self._make_request('POST', 'smart_collections.json', collection_data)
            
            if response.status_code == 201:
                return True
            else:
                self.logger.error(f"Failed to create smart collection {collection_name}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating smart collection {collection_name}: {e}")
            return False
    
    def _create_automated_collection(self, collection_name: str, templates: Dict[str, Any], values: Set[str]) -> bool:
        """Create an automated (custom) collection"""
        # For now, create as a regular collection
        # In a full implementation, you would add products programmatically
        
        collection_data = {
            "custom_collection": {
                "title": collection_name,
                "published": True
            }
        }
        
        try:
            response = self._make_request('POST', 'custom_collections.json', collection_data)
            
            if response.status_code == 201:
                return True
            else:
                self.logger.error(f"Failed to create collection {collection_name}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating collection {collection_name}: {e}")
            return False
    
    def _collection_exists(self, collection_name: str) -> bool:
        """Check if collection already exists"""
        try:
            # Check smart collections
            response = self._make_request('GET', 'smart_collections.json', {'title': collection_name})
            if response.status_code == 200:
                smart_collections = response.json().get('smart_collections', [])
                if any(col['title'] == collection_name for col in smart_collections):
                    return True
            
            # Check custom collections
            response = self._make_request('GET', 'custom_collections.json', {'title': collection_name})
            if response.status_code == 200:
                custom_collections = response.json().get('custom_collections', [])
                if any(col['title'] == collection_name for col in custom_collections):
                    return True
                    
        except Exception as e:
            self.logger.debug(f"Error checking collection existence: {e}")
        
        return False
    
    def get_existing_collections(self) -> List[Dict[str, Any]]:
        """Get all existing collections"""
        collections = []
        
        try:
            # Get smart collections
            response = self._make_request('GET', 'smart_collections.json')
            if response.status_code == 200:
                smart_collections = response.json().get('smart_collections', [])
                collections.extend([{'type': 'smart', **col} for col in smart_collections])
            
            # Get custom collections
            response = self._make_request('GET', 'custom_collections.json')
            if response.status_code == 200:
                custom_collections = response.json().get('custom_collections', [])
                collections.extend([{'type': 'custom', **col} for col in custom_collections])
                
        except Exception as e:
            self.logger.error(f"Error getting existing collections: {e}")
        
        return collections
    
    def get_existing_metafield_definitions(self) -> List[Dict[str, Any]]:
        """Get all existing metafield definitions"""
        query = """
        query {
            metafieldDefinitions(first: 250, ownerType: PRODUCT) {
                edges {
                    node {
                        id
                        name
                        namespace
                        key
                        type {
                            name
                        }
                        description
                    }
                }
            }
        }
        """
        
        try:
            response = self._make_request('POST', 'graphql.json', json.dumps({"query": query}), use_graphql=False)
            
            if response.status_code == 200:
                result = response.json()
                definitions = result.get('data', {}).get('metafieldDefinitions', {}).get('edges', [])
                return [edge['node'] for edge in definitions]
                
        except Exception as e:
            self.logger.error(f"Error getting metafield definitions: {e}")
        
        return []
