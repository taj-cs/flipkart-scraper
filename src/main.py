"""Main application entry point"""
import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager
from scraper.flipkart_scraper import FlipkartScraper
from utils.logger import app_logger
from utils.config import config_manager


class FlipkartScraperApp:
    """Main application class"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scraper = FlipkartScraper(self.db_manager)
    
    async def run_scraper(self, keyword: str, pages: int = 3):
        """Run the scraper for a given keyword"""
        try:
            app_logger.info(f"Starting Flipkart scraper for keyword: '{keyword}'")
            
            # Show current database status
            current_count = self.db_manager.get_product_count()
            app_logger.info(f"Current products in database: {current_count}")
            
            # Run scraper
            saved_count = await self.scraper.scrape_and_save(keyword, pages)
            
            # Show final status
            final_count = self.db_manager.get_product_count()
            app_logger.info(f"Scraping completed. Total products in database: {final_count}")
            app_logger.info(f"New products added: {saved_count}")
            
            return saved_count
            
        except Exception as e:
            app_logger.error(f"Application error: {e}")
            return 0
    
    def show_products(self, limit: int = 10):
        """Display products from database"""
        products = self.db_manager.get_products(limit=limit)
        
        if not products:
            print("No products found in database.")
            return
        
        print(f"\n--- Showing {len(products)} products ---")
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product['title']}")
            print(f"   Price: {product['price']}")
            print(f"   Image: {product['image_url'][:80]}..." if len(product['image_url']) > 80 else f"   Image: {product['image_url']}")
            print(f"   Added: {product['created_at']}")
    
    def clear_database(self):
        """Clear all products from database"""
        if self.db_manager.clear_products():
            print("Database cleared successfully.")
        else:
            print("Failed to clear database.")


def main():
    """Entry point for the application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Flipkart Product Scraper')
    parser.add_argument('keyword', nargs='?', help='Search keyword (e.g., "smartphone")')
    parser.add_argument('--pages', '-p', type=int, default=3, help='Number of pages to scrape (default: 3)')
    parser.add_argument('--show', '-s', type=int, metavar='N', help='Show N products from database')
    parser.add_argument('--clear', action='store_true', help='Clear all products from database')
    
    args = parser.parse_args()
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    app = FlipkartScraperApp()
    
    try:
        if args.clear:
            app.clear_database()
        elif args.show is not None:
            app.show_products(limit=args.show)
        elif args.keyword:
            # Run scraper
            asyncio.run(app.run_scraper(args.keyword, args.pages))
        else:
            # Interactive mode
            print("Flipkart Product Scraper")
            print("=" * 30)
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                asyncio.run(app.run_scraper(keyword, args.pages))
            else:
                print("No keyword provided.")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        app_logger.error(f"Application error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
