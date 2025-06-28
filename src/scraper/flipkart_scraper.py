"""Flipkart web scraper implementation"""
import asyncio
from typing import List, Dict, Optional
from urllib.parse import urlencode
from playwright.async_api import async_playwright, Browser, Page
from .base_scraper import BaseScraper
from .parser import FlipkartParser
from utils.config import config_manager
from utils.logger import app_logger


class FlipkartScraper(BaseScraper):
    """Flipkart product scraper implementation"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.config = config_manager.config.scraper
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def _setup_browser(self):
        """Setup Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # Create page with mobile user agent to avoid some anti-bot measures
            # self.page = await self.browser.new_page(
            #     user_agent='Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
            # )
            
            # Set timeout
            self.page.set_default_timeout(self.config.timeout * 1000)
            
            app_logger.info("Browser setup completed")
            
        except Exception as e:
            app_logger.error(f"Failed to setup browser: {e}")
            raise
    
    async def _cleanup_browser(self):
        """Cleanup browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            app_logger.info("Browser cleanup completed")
        except Exception as e:
            app_logger.warning(f"Error during browser cleanup: {e}")
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """Build search URL for Flipkart"""
        params = {
            'q': keyword,
            'page': page
        }
        return f"{self.config.base_url}/search?{urlencode(params)}"
    
    
    async def _get_page_content(self, url: str) -> Optional[str]:
        """Get page content with error handling"""
        try:
            app_logger.info(f"Fetching: {url}")
            
            # Navigate to URL with timeout
            await self.page.goto(
                url, 
                wait_until='domcontentloaded',
                timeout=30000  
            )
            
            # Wait for products to load with multiple fallback selectors
            selectors_to_try = [
                '[data-id]',
                '[data-tkid]', 
                '.DOjaWF.gdgoEp',
                '.tUxRFH',
                '._75nlfW',
                '.cPHDOP.col-12-12'
            ]
            
            product_found = False
            for selector in selectors_to_try:
                try:
                    await self.page.wait_for_selector(selector, timeout=20000)
                    product_found = True
                    app_logger.info(f"Found products using selector: {selector}")
                    break
                except Exception:
                    continue
            
            if not product_found:
                app_logger.warning("No product selectors found, continuing anyway")
            
            # Get page content
            content = await self.page.content()
            
            # Validate content isn't empty
            if not content or len(content.strip()) < 100:
                app_logger.warning(f"Suspiciously short content from {url}")
            
            # Add delay between requests
            await asyncio.sleep(self.config.delay_between_requests)
            
            return content
            
        except Exception as e:
            app_logger.error(f"Failed to get page content from {url}: {e}")
            return None
    
    async def search_products(self, keyword: str, pages: int = 3) -> List[Dict]:
        """Search for products on Flipkart"""
        all_products = []
        
        try:
            await self._setup_browser()
            
            for page_num in range(1, min(pages + 1, self.config.max_pages + 1)):
                try:
                    url = self._build_search_url(keyword, page_num)
                    html_content = await self._get_page_content(url)
                    
                    if html_content:
                        products = self.parse_product_data(html_content)
                        all_products.extend(products)
                        app_logger.info(f"Page {page_num}: Found {len(products)} products")
                    else:
                        app_logger.warning(f"No content retrieved for page {page_num}")
                        
                except Exception as e:
                    app_logger.error(f"Error processing page {page_num}: {e}")
                    continue
            
            app_logger.info(f"Total products found: {len(all_products)}")
            
        except Exception as e:
            app_logger.error(f"Error during product search: {e}")
        finally:
            await self._cleanup_browser()
        
        return all_products
    
    def parse_product_data(self, html: str) -> List[Dict]:
        """Parse product data from HTML using FlipkartParser"""
        return FlipkartParser.parse_product_listings(html)
    
    async def scrape_and_save(self, keyword: str, pages: int = 3) -> int:
        """Scrape products and save to database"""
        try:
            app_logger.info(f"Starting scrape for keyword: '{keyword}' ({pages} pages)")
            
            # Scrape products
            products = await self.search_products(keyword, pages)
            
            if not products:
                app_logger.warning("No products found to save")
                return 0
            
            # Save to database
            saved_count = self.db_manager.insert_products_batch(products)
            app_logger.info(f"Successfully saved {saved_count} products to database")
            
            return saved_count
            
        except Exception as e:
            app_logger.error(f"Error during scrape and save: {e}")
            return 0