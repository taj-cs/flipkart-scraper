# flipkart-scraper
A scalable, modular, maintainable, scraping solution for extracting product information from Flipkart (e-commerce platform) using Python, Playwright, BeautifulSoup, Stuctured DB (SQLite is used by default), and ORM.


## 🚀 Features

- **Scalable Architecture**: Object-oriented design with clean separation of concerns
- **Robust Scraping**: 
    - Uses Playwright for reliable web scraping with anti-bot measures.
    - Multiple CSS selectors for reliability and Handles different Flipkart page layouts
    - Proper error handling for missing elements
    - Rate limiting to avoid blocking
- **Database Integration**: SQLAlchemy ORM with SQLite/MySQL support. Batch insertions for performance

- **Error Handling**: Comprehensive error handling and logging
- **Configurable**: YAML-based configuration management
- **Clean Code**: Follows PEP 8 and best practices

## 📋 Requirements

- Python 3.8+
- Internet connection
- 2GB+ RAM (for browser automation)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/taj-cs/flipkart-scraper.git
cd flipkart-scraper
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**
```bash
playwright install chromium
```

5. **Create logs directory**
```bash
mkdir logs
```

## 🔧 Configuration

The application uses `config.yaml` for configuration. Default settings work out of the box, but you can customize for DB, Scraping, and Logging:


## 🚀 Usage

### Command Line Interface

**Basic usage:**
```bash
python src/main.py "smartphone"
```

**Scrape specific number of pages:**
```bash
python src/main.py "laptop" --pages 5
```

**Show products from database:**
```bash
python src/main.py --show 10
```

**Clear database:**
```bash
python src/main.py --clear
```

**Get help using:**
```bash
python src/main.py --help
```

### Interactive Mode

Run without arguments for interactive mode:
```bash
python src/main.py
```

## 📊 Database Schema

The application creates a `product_info` table with the following structure:

```sql
CREATE TABLE product_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    image_url TEXT,
    price VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🏗️ Project Structure

```
src/
├── database/
│   ├── models.py          # Data models for 'product_info'
│   └── db_manager.py      # Database operations
├── scraper/
│   ├── base_scraper.py    # Abstract base class
│   ├── flipkart_scraper.py # Main orchestrator/scraper
│   └── parser.py          # HTML parsing
├── utils/
│   ├── config.py          # Configuration management
│   └── logger.py          # Logging setup
└── main.py                # Application entry point
|__ requirements.txt       # Dependencies
|__ README.md              # Comprehensive documentation
|__ config.yaml            # Config setting for customization 
```

## 📊 Expected Output:
The scraper will:

- Navigate through 3 pages of Flipkart search results
- Extract product title, price, and image URL
- Save to SQLite database with timestamps
- Provide detailed logging and progress updates
- Handle errors gracefully and continue scraping

## 🔧 Customization:
The solution is highly configurable and scalable through config.yaml:

- Change number of pages
- Adjust delays between requests
- Switch between SQLite/MySQL
- Configure logging levels
- Enable/disable headless mode


**Happy Scraping! 🎉**
