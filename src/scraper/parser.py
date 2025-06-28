"""Handles HTML parsing, multiple page layouts, and data extraction using BeautifulSoup"""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup, Tag
from utils.logger import app_logger


class FlipkartParser:
    """HTML parsing utilities for Flipkart product listings"""
    
    @staticmethod
    def parse_product_listings(html: str) -> List[Dict]:
        """Parse product listings from search results page"""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Multiple selectors to handle different page layouts
            product_selectors = [
                '[data-id]',  # Main product containers
                '[data-tkid]',  # Alternative product containers
                '._75nlfW',   # Alternative product container
                '.CGtC98',   # Another layout variation
                '.cPHDOP.col-12-12',    # Grid layout products
                '.DOjaWF.gdgoEp',    # List layout products
                '.DOjaWF.gdgoEp'
            ]
            
            product_elements = []
            for selector in product_selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements
                    app_logger.debug(f"Found {len(elements)} products with selector: {selector}")
                    break
            
            if not product_elements:
                app_logger.warning("No product elements found with any selector")
                return products
            
            for element in product_elements:
                try:
                    product_data = FlipkartParser._extract_product_info(element)
                    if product_data and product_data.get('title'):
                        products.append(product_data)
                except Exception as e:
                    app_logger.debug(f"Error parsing individual product: {e}")
                    continue
            
            app_logger.info(f"Successfully parsed {len(products)} products")
            
        except Exception as e:
            app_logger.error(f"Error parsing product listings: {e}")
        
        return products
    
    @staticmethod
    def _extract_product_info(element: Tag) -> Optional[Dict]:
        """Extract product information from a product element"""
        try:
            # Title extraction with multiple selectors
            title_selectors = [
                '.KzDlHZ',      # Common title class
                '._4rR01T',     # Alternative title class
                '.IRpwTa',      # Another title variation
                '._2WkVRV',     # Grid layout title
                'a[title]',     # Link with title attribute
                'KzDlHZ',      # Product name class
                '._2mylT6'      # Another title class
            ]
            
            title = FlipkartParser._get_text_by_selectors(element, title_selectors)
            if not title:
                return None
            
            # Price extraction
            price_selectors = [
                '.Nx9bqj._4b5DiR',     # Common price class
                '.yRaY8j.ZYYwLA',     # Alternative price class
                '._3tbFF2',     # Another price variation
                '.Ce9jPB',      # Price in grid layout
                '._2_R_DZ',     # Discounted price
                '._3auQ3N'      # Regular price
            ]
            
            price = FlipkartParser._get_text_by_selectors(element, price_selectors)
            
            # Image extraction
            image_selectors = [
                'img[src]',     # Any image with src
                '.DByuf4', # Image in container
                '._2r_T1I img', # Alternative image container
                '.CXW8mj img',   # Grid layout image
                '.yPq5Io',
                'img.DByuf4'
            ]
            
            image_url = FlipkartParser._get_image_by_selectors(element, image_selectors)
            
            product_data = {
                'title': title.strip() if title else '',
                'price': price.strip() if price else 'N/A',
                'image_url': image_url or ''
            }
            
            return product_data
            
        except Exception as e:
            app_logger.debug(f"Error extracting product info: {e}")
            return None
    
    @staticmethod
    def _get_text_by_selectors(element: Tag, selectors: List[str]) -> Optional[str]:
        """Get text content using multiple selectors"""
        for selector in selectors:
            try:
                found_element = element.select_one(selector)
                if found_element:
                    text = found_element.get_text(strip=True)
                    if text:
                        return text
                    # Try title attribute if no text
                    if found_element.get('title'):
                        return found_element.get('title')
            except Exception:
                continue
        return None
    
    @staticmethod
    def _get_image_by_selectors(element: Tag, selectors: List[str]) -> Optional[str]:
        """Get image URL using multiple selectors"""
        for selector in selectors:
            try:
                img_element = element.select_one(selector)
                if img_element:
                    # Try different image URL attributes
                    for attr in ['src', 'data-src', 'data-original']:
                        img_url = img_element.get(attr)
                        if img_url and img_url.startswith(('http', '//')):
                            return img_url
            except Exception:
                continue
        return None
