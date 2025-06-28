"""Configuration management module"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define configuration models using Pydantic
class DatabaseConfig(BaseModel):
    type: str = "sqlite"
    name: str = os.getenv("DB_NAME", "flipkart_products.db")
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 3306)) 
    username: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")


class ScraperConfig(BaseModel):
    base_url: str = "https://www.flipkart.com"
    search_endpoint: str = "/search"
    max_pages: int = 3
    delay_between_requests: float = 2.0
    timeout: int = 30
    headless: bool = True


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"


class Config(BaseModel):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self, config_path: str = "../../config.yaml"):
        self.config_path = Path(config_path)
        self._config = None
    
    def load_config(self) -> Config:
        """Load configuration from YAML file"""
        if self._config is not None:
            return self._config
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as file:
                    config_data = yaml.safe_load(file)
                self._config = Config(**config_data)
            else:
                self._config = Config()  # Use defaults
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = Config()  # Fallback to defaults
        
        return self._config
    
    @property
    def config(self) -> Config:
        """Get the current configuration"""
        if self._config is None:
            self._config = self.load_config()
        return self._config

# Global config instance
config_manager = ConfigManager()