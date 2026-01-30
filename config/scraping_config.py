"""
Centralized Configuration for Stealth Market Intelligence Engine
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class ScrapingConfig:
    """Configuration manager for scraping targets and behavior"""
    
    # Target URLs - Easily configurable
    TARGET_URLS = {
        'books_toscrape': {
            'url': 'https://books.toscrape.com/catalogue/category/books_1/index.html',
            'type': 'static',
            'selectors': {
                'product_container': 'article.product_pod',
                'name': 'h3 a',
                'price': 'p.price_color',
                'rating': 'p.star-rating',
                'availability': 'p.availability'
            }
        },
        'amazon_headphones': {
            'url': 'https://www.amazon.com/s?k=wireless+headphones',
            'type': 'dynamic',
            'selectors': {
                'product_container': 'div[data-component-type="s-search-result"]',
                'name': 'h2 a span',
                'price': 'span.a-price span.a-offscreen',
                'rating': 'span[aria-label*="stars"]',
                'availability': 'span[aria-label*="stock"]'
            }
        },
        'ebay_laptops': {
            'url': 'https://www.ebay.com/b/Laptops-Netbooks/175672/bn_1648276',
            'type': 'dynamic',
            'selectors': {
                'product_container': 'div.s-item',
                'name': 'h3.s-item__title',
                'price': 'span.s-item__price',
                'rating': 'span.clipped',
                'availability': 'span.s-item__quantity'
            }
        }
    }
    
    # Browser stealth settings
    BROWSER_CONFIG = {
        'headless': os.getenv('HEADLESS_MODE', 'False').lower() == 'true',
        'viewport': {'width': 1920, 'height': 1080},
        'locale': 'en-US',
        'timezone_id': 'America/New_York',
        'device_scale_factor': 1,
        'is_mobile': False,
        'has_touch': False,
        'user_agent_rotation': True
    }
    
    # Human behavior simulation
    BEHAVIOR_CONFIG = {
        'scroll_delay_min': 0.8,
        'scroll_delay_max': 2.5,
        'scroll_amount_min': 200,
        'scroll_amount_max': 600,
        'action_delay_min': float(os.getenv('REQUEST_DELAY_MIN', '2')),
        'action_delay_max': float(os.getenv('REQUEST_DELAY_MAX', '5')),
        'mouse_movement_enabled': True,
        'random_mouse_moves': True
    }
    
    # AI Configuration
    AI_CONFIG = {
        'provider': os.getenv('AI_PROVIDER', 'openai'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model_openai': 'gpt-4-turbo-preview',
        'model_anthropic': 'claude-3-sonnet-20240229',
        'temperature': 0.3,
        'max_tokens': 2000
    }
    
    # Output paths
    OUTPUT_PATHS = {
        'raw_data': 'output/products_raw.json',
        'enriched_data': 'output/products_enriched.json',
        'logs': 'output/scraping_logs.txt'
    }
    
    @classmethod
    def get_target_config(cls, target_name: str) -> Dict:
        """Get configuration for a specific target"""
        return cls.TARGET_URLS.get(target_name, {})
    
    @classmethod
    def get_all_targets(cls) -> List[str]:
        """Get list of all available targets"""
        return list(cls.TARGET_URLS.keys())
