# Stealth Market Intelligence Engine

## 🎯 Overview

A **production-grade, enterprise-level** market intelligence system for e-commerce competitor analysis. Built with advanced stealth techniques to bypass anti-bot protection, AI-powered categorization, and professional client-ready visualizations.

### Key Features

✅ **Stealth Browser Automation** - Playwright with anti-detection mechanisms  
✅ **Human Behavior Simulation** - Realistic scrolling, delays, and mouse movements  
✅ **AI-Powered Enrichment** - OpenAI/Anthropic integration for smart categorization  
✅ **Professional Dashboard** - Interactive Streamlit + Plotly visualizations  
✅ **Modular Architecture** - Clean separation of concerns, easily extensible  
✅ **Configurable Targets** - Switch between sites without code changes  

---

## 🏗️ Architecture

```
scraping/
├── config/
│   └── scraping_config.py      # Centralized configuration
├── src/
│   ├── browser_manager.py      # Stealth browser with anti-detection
│   ├── human_behavior.py       # Realistic user behavior simulation
│   ├── stealth_scraper.py      # Main scraping orchestrator
│   └── ai_enrichment.py        # LLM-powered data categorization
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── output/
│   ├── products_raw.json       # Raw scraped data
│   └── products_enriched.json  # AI-enriched data
├── main.py                     # CLI entry point
├── requirements.txt            # Dependencies
└── .env.example                # Configuration template
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
copy .env.example .env
# Edit .env and add your API keys
```

### 2. Configuration

Edit `.env` file:

```env
# Choose your AI provider
AI_PROVIDER=openai  # or anthropic

# Add your API key
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Scraping settings
HEADLESS_MODE=False
REQUEST_DELAY_MIN=2
REQUEST_DELAY_MAX=5
```

### 3. Run the Pipeline

```bash
# Run complete pipeline (scrape + enrich)
python main.py

# Scrape specific target
python main.py --target books_toscrape --max-products 100

# Skip scraping (use existing data)
python main.py --skip-scraping

# List available targets
python main.py --list-targets
```

### 4. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard will open at `http://localhost:8501`

---

## 🎯 Available Targets

### 1. Books to Scrape (Default)
- **URL**: `https://books.toscrape.com/catalogue/category/books_1/index.html`
- **Type**: Static site (no bot protection)
- **Best for**: Testing and development

### 2. Amazon Wireless Headphones
- **URL**: `https://www.amazon.com/s?k=wireless+headphones`
- **Type**: Dynamic (JavaScript + lazy loading)
- **Features**: Anti-bot detection, lazy loading

### 3. eBay Laptops
- **URL**: `https://www.ebay.com/b/Laptops-Netbooks/175672/bn_1648276`
- **Type**: Dynamic (JavaScript)
- **Features**: Lazy loading, real-time updates

### Adding Custom Targets

Edit `config/scraping_config.py`:

```python
TARGET_URLS = {
    'my_custom_site': {
        'url': 'https://example.com/products',
        'type': 'dynamic',  # or 'static'
        'selectors': {
            'product_container': 'div.product',
            'name': 'h2.product-title',
            'price': 'span.price',
            'rating': 'div.rating',
            'availability': 'span.stock'
        }
    }
}
```

---

## 🧱 Core Components

### 1. Browser Manager (`src/browser_manager.py`)

Manages Playwright with stealth configurations:

- **Anti-detection scripts** (webdriver masking, plugin spoofing)
- **Realistic headers** (Accept-Language, DNT, Sec-Fetch-*)
- **User-agent rotation**
- **Fingerprint randomization**

```python
from src.browser_manager import BrowserManager

with BrowserManager() as browser:
    page = browser.get_page()
    browser.navigate_to("https://example.com")
```

### 2. Human Behavior Simulator (`src/human_behavior.py`)

Mimics real user interactions:

- **Random scrolling** with variable speeds
- **Mouse movements** across viewport
- **Reading delays** with micro-activities
- **Lazy-load triggering** for dynamic content

```python
from src.human_behavior import HumanBehaviorSimulator

simulator = HumanBehaviorSimulator(page)
simulator.simulate_product_browsing(num_interactions=3)
simulator.scroll_to_bottom()
```

### 3. Stealth Scraper (`src/stealth_scraper.py`)

Orchestrates scraping with resilient extraction:

- **Graceful error handling** for missing elements
- **Price/rating normalization**
- **Stock scarcity detection**
- **Structured JSON output**

```python
from src.stealth_scraper import StealthScraper

scraper = StealthScraper(target_name='books_toscrape')
products = scraper.scrape(max_products=50)
scraper.save_to_json(products)
```

### 4. AI Enrichment (`src/ai_enrichment.py`)

LLM-powered data enhancement:

- **Automatic categorization** (Budget/Mid Range/High End)
- **Price tier detection**
- **Provider abstraction** (OpenAI/Anthropic)
- **Batch processing** for efficiency

```python
from src.ai_enrichment import enrich_from_file

enriched_products = enrich_from_file(
    input_path='output/products_raw.json',
    provider='openai'
)
```

### 5. Visualization Dashboard (`dashboard/app.py`)

Professional Streamlit interface:

- **Interactive filters** (price, category, rating)
- **Plotly charts** (distributions, correlations)
- **Key metrics** (total products, averages)
- **Data export** (CSV download)

---

## 📊 Output Format

### Raw Data (`products_raw.json`)

```json
{
  "metadata": {
    "target": "books_toscrape",
    "total_products": 50,
    "scraped_at": "2026-01-30T10:00:00"
  },
  "products": [
    {
      "id": "books_toscrape_1",
      "name": "A Light in the Attic",
      "price": 51.77,
      "price_raw": "£51.77",
      "rating": 3.0,
      "rating_raw": "Three",
      "stock_info": {
        "in_stock": true,
        "scarcity_signal": null
      },
      "source": "books_toscrape",
      "scraped_at": "2026-01-30T10:00:00"
    }
  ]
}
```

### Enriched Data (`products_enriched.json`)

```json
{
  "metadata": {
    "total_products": 50,
    "enriched_at": "2026-01-30T10:05:00",
    "ai_provider": "openai",
    "category_distribution": {
      "Budget": 15,
      "Mid Range": 25,
      "High End": 10
    }
  },
  "products": [
    {
      "id": "books_toscrape_1",
      "name": "A Light in the Attic",
      "price": 51.77,
      "rating": 3.0,
      "ai_category": "High End",
      "ai_reasoning": "Priced above average with moderate rating",
      "enriched_at": "2026-01-30T10:05:00"
    }
  ]
}
```

---

## 🛡️ Anti-Bot Evasion Techniques

1. **JavaScript Injection**
   - Masks `navigator.webdriver`
   - Spoofs plugins and languages
   - Adds Chrome runtime objects

2. **HTTP Headers**
   - Realistic Accept-Language, Accept-Encoding
   - Proper Sec-Fetch-* headers
   - DNT (Do Not Track) flag

3. **Behavioral Mimicry**
   - Random delays (2-5 seconds)
   - Gradual scrolling (200-600px increments)
   - Mouse movements before actions
   - Reading pauses (2-5 seconds)

4. **Fingerprint Randomization**
   - Rotating user agents
   - Consistent viewport sizes
   - Timezone and locale spoofing

---

## 💡 Advanced Usage

### Custom AI Prompting

Modify the prompt in `src/ai_enrichment.py` → `_enrich_batch()` to customize categorization logic.

### Multiple Targets in One Run

```python
from src.stealth_scraper import StealthScraper

targets = ['books_toscrape', 'amazon_headphones', 'ebay_laptops']
all_products = []

for target in targets:
    scraper = StealthScraper(target_name=target)
    products = scraper.scrape(max_products=30)
    all_products.extend(products)
```

### Scheduled Execution

Use Windows Task Scheduler or cron:

```bash
# Windows Task Scheduler (daily at 9 AM)
schtasks /create /tn "MarketIntel" /tr "python C:\path\to\main.py" /sc daily /st 09:00

# Linux cron (daily at 9 AM)
0 9 * * * cd /path/to/scraping && python main.py
```

---

## 🔧 Troubleshooting

### Issue: "No enriched data found"
- **Solution**: Run `python main.py` first to collect and enrich data

### Issue: "API key not configured"
- **Solution**: Create `.env` file and add your API key (see `.env.example`)

### Issue: "Playwright browser not found"
- **Solution**: Run `playwright install chromium`

### Issue: "Rate limited by website"
- **Solution**: Increase delays in `.env`:
  ```env
  REQUEST_DELAY_MIN=5
  REQUEST_DELAY_MAX=10
  ```

### Issue: "Selectors not finding elements"
- **Solution**: Inspect target site and update selectors in `config/scraping_config.py`

---

## 📝 Best Practices

### For Clients

1. **Always test on practice sites first** (books.toscrape.com)
2. **Respect rate limits** - adjust delays appropriately
3. **Review robots.txt** before scraping production sites
4. **Use residential proxies** for high-volume scraping (not included)
5. **Schedule during off-peak hours** to reduce detection risk

### For Development

1. **Test with `headless=False`** to debug visually
2. **Start with small batches** (10-20 products)
3. **Log all errors** for selector refinement
4. **Version control your selectors** when sites update
5. **Mock AI responses** during development to save costs

---

## 🚀 Deployment Considerations

### Production Checklist

- [ ] Set `HEADLESS_MODE=True` in `.env`
- [ ] Add error alerting (email/Slack webhooks)
- [ ] Implement proxy rotation (not included)
- [ ] Set up database storage (PostgreSQL/MongoDB)
- [ ] Add retry logic with exponential backoff
- [ ] Schedule regular runs (daily/weekly)
- [ ] Monitor API costs (OpenAI/Anthropic)

### Scalability

For high-volume production:

1. **Use async Playwright** (replace `sync_api` with `async_api`)
2. **Implement queue system** (Celery + Redis)
3. **Distribute across multiple machines**
4. **Cache results** with TTL
5. **Add database layer** instead of JSON files

---

## 📄 License & Legal

This is a **demonstration project** for educational and freelance purposes.

**Legal Disclaimer:**
- Always respect website Terms of Service
- Comply with robots.txt directives
- Implement rate limiting and respectful scraping practices
- Do not use for unauthorized data collection
- Consult legal counsel for commercial deployments

---

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review configuration in `config/scraping_config.py`
3. Test with default target (books.toscrape.com)
4. Verify API keys are correctly set in `.env`

---

## 📚 Further Reading

- [Playwright Documentation](https://playwright.dev/python/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)

---

**Built with ❤️ for professional market intelligence gathering**
