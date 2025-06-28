"""Abstract base scraper class"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseScraper(ABC):
    """Abstract base class for web scrapers"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    @abstractmethod
    async def search_products(self, keyword: str, pages: int = 3) -> List[Dict]:
        """Search for products based on keyword"""
        pass
    
    @abstractmethod
    def parse_product_data(self, html: str) -> List[Dict]:
        """Parse product data from HTML"""
        pass
    
    @abstractmethod
    async def scrape_and_save(self, keyword: str, pages: int = 3) -> int:
        """Scrape products and save to database"""
        pass
