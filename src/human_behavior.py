"""
Human Behavior Simulator - Mimics realistic user interactions
"""
import random
import time
from typing import Tuple
from playwright.sync_api import Page
from config.scraping_config import ScrapingConfig


class HumanBehaviorSimulator:
    """
    Simulates human-like browsing patterns to avoid bot detection
    including scrolling, mouse movements, and randomized delays
    """
    
    def __init__(self, page: Page, config: dict = None):
        self.page = page
        self.config = config or ScrapingConfig.BEHAVIOR_CONFIG
    
    def random_delay(self, min_delay: float = None, max_delay: float = None):
        """Add random delay between actions"""
        min_val = min_delay or self.config['action_delay_min']
        max_val = max_delay or self.config['action_delay_max']
        time.sleep(random.uniform(min_val, max_val))
    
    def human_scroll(self, times: int = 3) -> None:
        """
        Simulate human-like scrolling behavior
        
        Args:
            times: Number of scroll iterations
        """
        for i in range(times):
            # Random scroll amount
            scroll_amount = random.randint(
                self.config['scroll_amount_min'],
                self.config['scroll_amount_max']
            )
            
            # Execute scroll
            self.page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            
            # Random delay between scrolls
            delay = random.uniform(
                self.config['scroll_delay_min'],
                self.config['scroll_delay_max']
            )
            time.sleep(delay)
    
    def scroll_to_bottom(self, scroll_pause_time: float = 2.0) -> None:
        """
        Gradually scroll to bottom of page to trigger lazy loading
        
        Args:
            scroll_pause_time: Time to wait between scroll increments
        """
        last_height = self.page.evaluate('document.body.scrollHeight')
        
        while True:
            # Scroll down incrementally (not instantly to bottom)
            scroll_increment = random.randint(300, 800)
            self.page.evaluate(f'window.scrollBy(0, {scroll_increment})')
            
            # Wait for potential lazy-loaded content
            time.sleep(random.uniform(scroll_pause_time * 0.7, scroll_pause_time * 1.3))
            
            # Calculate new scroll height
            new_height = self.page.evaluate('document.body.scrollHeight')
            
            # Check if we've reached the bottom
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def random_mouse_movement(self) -> None:
        """Simulate random mouse movements"""
        if not self.config.get('mouse_movement_enabled', True):
            return
        
        # Get viewport size
        viewport = self.page.viewport_size
        
        # Generate random coordinates
        x = random.randint(100, viewport['width'] - 100)
        y = random.randint(100, viewport['height'] - 100)
        
        # Move mouse
        self.page.mouse.move(x, y)
        
        # Small delay
        time.sleep(random.uniform(0.1, 0.3))
    
    def simulate_reading_behavior(self, duration: float = None) -> None:
        """
        Simulate user reading/viewing behavior
        
        Args:
            duration: Time to simulate reading (seconds)
        """
        read_time = duration or random.uniform(2, 5)
        
        # Perform micro-activities during "reading"
        start_time = time.time()
        
        while (time.time() - start_time) < read_time:
            if self.config.get('random_mouse_moves', True):
                self.random_mouse_movement()
            
            # Small scroll movements
            if random.random() > 0.7:
                small_scroll = random.randint(-50, 150)
                self.page.evaluate(f'window.scrollBy(0, {small_scroll})')
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def wait_for_lazy_load(self, selector: str = None, timeout: int = 5000) -> bool:
        """
        Wait for lazy-loaded elements to appear
        
        Args:
            selector: CSS selector to wait for
            timeout: Maximum wait time in milliseconds
        
        Returns:
            True if element appeared, False otherwise
        """
        if selector:
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                return True
            except:
                return False
        
        # Generic wait for network idle
        try:
            self.page.wait_for_load_state('networkidle', timeout=timeout)
            return True
        except:
            return False
    
    def simulate_product_browsing(self, num_interactions: int = 3) -> None:
        """
        Simulate browsing behavior typical for e-commerce sites
        
        Args:
            num_interactions: Number of browsing interactions to perform
        """
        for _ in range(num_interactions):
            # Scroll a bit
            self.human_scroll(times=random.randint(1, 2))
            
            # Pause as if reading
            self.simulate_reading_behavior(duration=random.uniform(1, 3))
            
            # Random mouse movement
            if random.random() > 0.5:
                self.random_mouse_movement()
            
            # Random delay
            self.random_delay(min_delay=0.5, max_delay=2)
