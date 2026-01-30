"""
Stealth Browser Manager - Production-grade Playwright wrapper with anti-bot evasion
"""
import random
import time
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from fake_useragent import UserAgent
from config.scraping_config import ScrapingConfig


class BrowserManager:
    """
    Manages Playwright browser instances with stealth configurations
    to avoid detection by anti-bot systems.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ScrapingConfig.BROWSER_CONFIG
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.user_agent_generator = UserAgent()
        
    def initialize(self) -> 'BrowserManager':
        """Initialize Playwright and browser instance"""
        self.playwright = sync_playwright().start()
        
        # Launch browser with stealth settings
        self.browser = self.playwright.chromium.launch(
            headless=self.config['headless'],
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-setuid-sandbox'
            ]
        )
        
        # Create context with realistic fingerprint
        self._create_stealth_context()
        
        return self
    
    def _create_stealth_context(self):
        """Create browser context with human-like fingerprint"""
        
        # Generate or use configured user agent
        user_agent = self._get_realistic_user_agent()
        
        self.context = self.browser.new_context(
            viewport=self.config['viewport'],
            user_agent=user_agent,
            locale=self.config['locale'],
            timezone_id=self.config['timezone_id'],
            device_scale_factor=self.config['device_scale_factor'],
            is_mobile=self.config['is_mobile'],
            has_touch=self.config['has_touch'],
            
            # Additional stealth headers
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        )
        
        # Create page
        self.page = self.context.new_page()
        
        # Inject anti-detection scripts
        self._inject_stealth_scripts()
    
    def _get_realistic_user_agent(self) -> str:
        """Generate realistic user agent string"""
        if self.config.get('user_agent_rotation', True):
            return self.user_agent_generator.random
        else:
            # Default modern Chrome UA
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def _inject_stealth_scripts(self):
        """Inject JavaScript to mask automation detection"""
        stealth_js = """
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override plugins to appear more real
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Mock Chrome runtime
        window.chrome = {
            runtime: {}
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        self.page.add_init_script(stealth_js)
    
    def navigate_to(self, url: str, wait_until: str = 'networkidle') -> Page:
        """
        Navigate to URL with realistic timing and behavior
        
        Args:
            url: Target URL
            wait_until: Playwright wait condition ('load', 'domcontentloaded', 'networkidle')
        """
        # Random delay before navigation (simulating user thinking)
        time.sleep(random.uniform(1, 2.5))
        
        try:
            self.page.goto(url, wait_until=wait_until, timeout=60000)
            
            # Random delay after page load
            time.sleep(random.uniform(1.5, 3))
            
            return self.page
            
        except Exception as e:
            print(f"Navigation error: {e}")
            raise
    
    def get_page(self) -> Page:
        """Get current page instance"""
        return self.page
    
    def close(self):
        """Clean up resources"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def __enter__(self):
        """Context manager entry"""
        return self.initialize()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
