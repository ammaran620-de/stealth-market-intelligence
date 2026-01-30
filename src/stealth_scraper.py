"""
Data Extraction Layer - Robust product data scraping with graceful error handling
"""
import json
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from playwright.sync_api import Page, ElementHandle
from src.browser_manager import BrowserManager
from src.human_behavior import HumanBehaviorSimulator
from config.scraping_config import ScrapingConfig


class DataExtractor:
    """
    Handles extraction of product data with resilient selectors
    and graceful failure handling
    """
    
    @staticmethod
    def extract_text(element: ElementHandle, selector: str, default: str = "N/A") -> str:
        """
        Safely extract text from an element
        
        Args:
            element: Parent element
            selector: CSS selector
            default: Default value if extraction fails
        """
        try:
            target = element.query_selector(selector)
            if target:
                text = target.inner_text().strip()
                return text if text else default
            return default
        except Exception as e:
            return default
    
    @staticmethod
    def extract_price(price_text: str) -> Optional[float]:
        """
        Extract numerical price from text
        
        Args:
            price_text: Raw price string (e.g., "$29.99", "£45.00")
        
        Returns:
            Float price or None
        """
        if not price_text or price_text == "N/A":
            return None
        
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        
        if price_match:
            try:
                return float(price_match.group(0))
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def extract_rating(rating_text: str) -> Optional[float]:
        """
        Extract numerical rating from text
        
        Args:
            rating_text: Raw rating string (e.g., "4.5 out of 5 stars", "Three")
        
        Returns:
            Float rating or None
        """
        if not rating_text or rating_text == "N/A":
            return None
        
        # Try to find decimal rating
        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
        
        if rating_match:
            try:
                rating = float(rating_match.group(1))
                return min(rating, 5.0)  # Cap at 5.0
            except ValueError:
                pass
        
        # Handle word-based ratings (e.g., "Three" -> 3)
        word_ratings = {
            'one': 1.0, 'two': 2.0, 'three': 3.0, 
            'four': 4.0, 'five': 5.0
        }
        
        for word, value in word_ratings.items():
            if word in rating_text.lower():
                return value
        
        return None
    
    @staticmethod
    def extract_stock_info(availability_text: str) -> Dict[str, Any]:
        """
        Extract stock availability and scarcity signals
        
        Args:
            availability_text: Raw availability text
        
        Returns:
            Dict with in_stock (bool) and scarcity_signal (str)
        """
        if not availability_text or availability_text == "N/A":
            return {"in_stock": None, "scarcity_signal": None}
        
        availability_lower = availability_text.lower()
        
        # Check if in stock
        in_stock = any(phrase in availability_lower for phrase in [
            'in stock', 'available', 'ready to ship'
        ])
        
        # Extract scarcity signals
        scarcity_match = re.search(r'only (\d+) left', availability_lower)
        scarcity_signal = scarcity_match.group(0) if scarcity_match else None
        
        return {
            "in_stock": in_stock,
            "scarcity_signal": scarcity_signal,
            "raw_text": availability_text
        }


class StealthScraper:
    """
    Main scraping orchestrator that coordinates browser, behavior simulation,
    and data extraction
    """
    
    def __init__(self, target_name: str = 'books_toscrape'):
        self.target_name = target_name
        self.target_config = ScrapingConfig.get_target_config(target_name)
        
        if not self.target_config:
            raise ValueError(f"Unknown target: {target_name}")
        
        self.browser_manager = None
        self.behavior_simulator = None
        self.extractor = DataExtractor()
    
    def scrape(self, max_products: int = 50) -> List[Dict]:
        """
        Execute the scraping process
        
        Args:
            max_products: Maximum number of products to scrape
        
        Returns:
            List of product dictionaries
        """
        print(f"🚀 Starting scrape for target: {self.target_name}")
        print(f"📍 URL: {self.target_config['url']}")
        
        products = []
        
        with BrowserManager() as browser_manager:
            self.browser_manager = browser_manager
            page = browser_manager.get_page()
            
            # Initialize behavior simulator
            self.behavior_simulator = HumanBehaviorSimulator(page)
            
            # Navigate to target
            print("🌐 Navigating to target URL...")
            browser_manager.navigate_to(self.target_config['url'])
            
            # Simulate browsing behavior
            print("👤 Simulating human browsing behavior...")
            self.behavior_simulator.simulate_product_browsing(num_interactions=2)
            
            # Handle lazy loading for dynamic sites
            if self.target_config['type'] == 'dynamic':
                print("📜 Triggering lazy-loaded content...")
                self.behavior_simulator.scroll_to_bottom(scroll_pause_time=2.0)
            
            # Extract products
            print("🔍 Extracting product data...")
            products = self._extract_products(page, max_products)
            
            print(f"✅ Successfully extracted {len(products)} products")
        
        return products
    
    def _extract_products(self, page: Page, max_products: int) -> List[Dict]:
        """
        Extract product data from page
        
        Args:
            page: Playwright page instance
            max_products: Maximum products to extract
        
        Returns:
            List of product dictionaries
        """
        products = []
        selectors = self.target_config['selectors']
        
        # Find all product containers
        product_elements = page.query_selector_all(selectors['product_container'])
        
        print(f"   Found {len(product_elements)} product elements")
        
        for idx, element in enumerate(product_elements[:max_products]):
            try:
                # Extract individual fields
                name = self.extractor.extract_text(element, selectors['name'])
                price_text = self.extractor.extract_text(element, selectors['price'])
                rating_text = self.extractor.extract_text(element, selectors['rating'])
                availability_text = self.extractor.extract_text(element, selectors['availability'])
                
                # Process extracted data
                price = self.extractor.extract_price(price_text)
                rating = self.extractor.extract_rating(rating_text)
                stock_info = self.extractor.extract_stock_info(availability_text)
                
                product = {
                    'id': f"{self.target_name}_{idx + 1}",
                    'name': name,
                    'price': price,
                    'price_raw': price_text,
                    'rating': rating,
                    'rating_raw': rating_text,
                    'stock_info': stock_info,
                    'source': self.target_name,
                    'source_url': self.target_config['url'],
                    'scraped_at': datetime.now().isoformat()
                }
                
                products.append(product)
                
                # Progress indicator
                if (idx + 1) % 10 == 0:
                    print(f"   Processed {idx + 1} products...")
                
            except Exception as e:
                print(f"   ⚠️  Error extracting product {idx + 1}: {e}")
                continue
        
        return products
    
    def save_to_json(self, products: List[Dict], output_path: str = None):
        """
        Save products to JSON file
        
        Args:
            products: List of product dictionaries
            output_path: Output file path
        """
        output_path = output_path or ScrapingConfig.OUTPUT_PATHS['raw_data']
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'target': self.target_name,
                    'total_products': len(products),
                    'scraped_at': datetime.now().isoformat()
                },
                'products': products
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to: {output_path}")
