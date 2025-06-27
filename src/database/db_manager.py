"""Database operations manager"""
from typing import List, Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, ProductInfo
from ..utils.config import config_manager
from ..utils.logger import app_logger


class DatabaseManager:
    """Database management operations"""
    
    def __init__(self):
        self.config = config_manager.config.database
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create database URL based on config
            if self.config.type.lower() == 'sqlite':
                database_url = f"sqlite:///{self.config.name}"
            elif self.config.type.lower() == 'mysql':
                database_url = (
                    f"mysql+pymysql://{self.config.username}:{self.config.password}@"
                    f"{self.config.host}:{self.config.port}/{self.config.name}"
                )
            else:
                raise ValueError(f"Unsupported database type: {self.config.type}")
            
            self.engine = create_engine(database_url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            self.create_tables()
            app_logger.info(f"Database initialized successfully: {database_url}")
            
        except Exception as e:
            app_logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            app_logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            app_logger.error(f"Failed to create tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def insert_product(self, product_data: Dict) -> bool:
        """Insert a single product into database"""
        session = self.get_session()
        try:
            product = ProductInfo(
                title=product_data.get('title', ''),
                image_url=product_data.get('image_url', ''),
                price=product_data.get('price', '')
            )
            session.add(product)
            session.commit()
            app_logger.debug(f"Product inserted: {product_data.get('title', '')[:50]}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            app_logger.error(f"Failed to insert product: {e}")
            return False
        finally:
            session.close()
    
    def insert_products_batch(self, products_data: List[Dict]) -> int:
        """Insert multiple products in batch"""
        session = self.get_session()
        inserted_count = 0
        
        try:
            products = [
                ProductInfo(
                    title=product.get('title', ''),
                    image_url=product.get('image_url', ''),
                    price=product.get('price', '')
                )
                for product in products_data
            ]
            
            session.add_all(products)
            session.commit()
            inserted_count = len(products)
            app_logger.info(f"Batch inserted {inserted_count} products")
            
        except SQLAlchemyError as e:
            session.rollback()
            app_logger.error(f"Failed to insert batch: {e}")
        finally:
            session.close()
        
        return inserted_count
    
    def get_products(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve products from database"""
        session = self.get_session()
        try:
            query = session.query(ProductInfo)
            if limit:
                query = query.limit(limit)
            
            products = query.all()
            return [product.to_dict() for product in products]
        except SQLAlchemyError as e:
            app_logger.error(f"Failed to retrieve products: {e}")
            return []
        finally:
            session.close()
    
    def get_product_count(self) -> int:
        """Get total number of products in database"""
        session = self.get_session()
        try:
            count = session.query(ProductInfo).count()
            return count
        except SQLAlchemyError as e:
            app_logger.error(f"Failed to get product count: {e}")
            return 0
        finally:
            session.close()
    
    def clear_products(self) -> bool:
        """Clear all products from database"""
        session = self.get_session()
        try:
            session.query(ProductInfo).delete()
            session.commit()
            app_logger.info("All products cleared from database")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            app_logger.error(f"Failed to clear products: {e}")
            return False
        finally:
            session.close()
