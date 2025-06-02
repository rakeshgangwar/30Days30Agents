# 🛍️ AI Shopping Assistant

An intelligent e-commerce assistant that helps users search, compare, and get recommendations for products using AI-powered analysis.

## 🌟 Features

- **🔍 Smart Product Search**: Natural language product search across multiple sources
- **⚖️ Product Comparison**: Compare multiple products with AI analysis
- **💡 Personalized Recommendations**: Get AI-powered product recommendations based on preferences
- **📈 Price Tracking**: Track product prices and get notified when they drop
- **📝 Review Analysis**: AI-powered review summarization and sentiment analysis
- **🌐 Web Interface**: Beautiful, responsive web UI
- **⌨️ Command Line Interface**: Full CLI for power users
- **📊 RESTful API**: Complete API for integration with other applications

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (for AI features)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ShoppingAssistant
   ```

2. **Install dependencies**:
   ```bash
   uv sync  # or pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   cp config.env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application**:
   ```bash
   # Web interface (default)
   python main.py

   # Command line interface
   python main.py --mode cli search "wireless headphones under $200"
   ```

## 🌐 Web Interface

Access the web interface at `http://localhost:8000` after starting the server.

### Features:
- **Search Tab**: Search for products with natural language queries
- **Compare Tab**: Compare multiple products by entering their URLs
- **Recommend Tab**: Get personalized recommendations based on your requirements
- **Price Track Tab**: Set up price alerts for products

### Example Queries:
- "Find me red running shoes under $100 with good cushioning"
- "Recommend a good laptop for programming under $1500"
- "Show me 4-star rated bluetooth headphones sorted by price"

## ⌨️ Command Line Interface

The CLI provides full functionality through command-line commands:

### Search Products
```bash
python main.py --mode cli search "wireless headphones" --max-results 5 --sort-by price
```

### Compare Products
```bash
python main.py --mode cli compare \
  "https://example.com/product1" \
  "https://example.com/product2"
```

### Get Recommendations
```bash
python main.py --mode cli recommend "laptop for gaming" --budget 1200 --brands Dell HP
```

### Track Price
```bash
python main.py --mode cli track "user@example.com" "https://example.com/product" 99.99
```

### Analyze Reviews
```bash
python main.py --mode cli reviews "https://example.com/product"
```

## 📖 API Documentation

Start the web server and visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints:

- `POST /search` - Search for products
- `POST /compare` - Compare multiple products
- `POST /recommend` - Get product recommendations
- `POST /track` - Set up price tracking
- `GET /track/{user_id}` - Get user's price trackers
- `GET /reviews/{product_url}` - Get review summary

### Example API Usage:

```python
import requests

# Search for products
response = requests.post("http://localhost:8000/search", json={
    "query": "wireless headphones under $200",
    "query_type": "search",
    "max_results": 10
})

products = response.json()["products"]
```

## 🏗️ Architecture

The Shopping Assistant is built with a modular architecture:

```
src/shopping_assistant/
├── models.py           # Data models and schemas
├── agent.py            # Main shopping assistant logic
├── scrapers.py         # Web scraping functionality
├── llm_service.py      # AI/LLM integration
├── database.py         # Database models and setup
├── api.py              # FastAPI web interface
└── cli.py              # Command line interface
```

### Key Components:

- **ShoppingAssistant**: Main agent that coordinates all functionality
- **ProductScraper**: Handles web scraping and data extraction
- **LLMService**: Manages AI-powered features like query parsing and review analysis
- **Database**: SQLite/PostgreSQL storage for user preferences and price tracking
- **FastAPI**: Modern web framework for the API and web interface

## 🔧 Configuration

Configure the application using environment variables in `.env`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
DATABASE_URL=sqlite:///./shopping_assistant.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

## 🛠️ Development

### Adding New Data Sources

To add new e-commerce data sources:

1. Extend the `ProductScraper` class in `scrapers.py`
2. Add new search methods for your data source
3. Update the `search_products` method to include your source

### Extending AI Features

To add new AI-powered features:

1. Add new methods to the `LLMService` class
2. Update the `ShoppingAssistant` agent to use new features
3. Add corresponding API endpoints and CLI commands

### Custom Product Categories

Product templates in `scrapers.py` can be extended with new categories:

```python
product_templates = {
    'your_category': {
        'features': ['Feature1', 'Feature2'],
        'price_range': (min_price, max_price),
        'brands': ['Brand1', 'Brand2']
    }
}
```

## 📊 Database Schema

The application uses the following main tables:

- `user_preferences` - User shopping preferences and history
- `price_trackers` - Active price tracking requests
- `product_cache` - Cached product information
- `search_history` - User search history for analytics

## 🔒 Privacy & Ethics

- **Data Privacy**: User data is stored locally by default
- **Respectful Scraping**: Implements delays and respects robots.txt
- **Transparent AI**: All AI recommendations include explanations
- **No Tracking**: No user tracking without explicit consent

## 🚨 Limitations

- **Demo Data**: Currently uses simulated data for demonstration
- **Rate Limits**: Respects API rate limits and scraping guidelines
- **Regional Availability**: Product availability may vary by region
- **AI Accuracy**: AI recommendations are suggestions, not guarantees

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the [GitHub issues](issues)
3. Join our community discussions

## 🗺️ Roadmap

- [ ] Integration with real e-commerce APIs
- [ ] Machine learning recommendation engine
- [ ] Mobile app companion
- [ ] Advanced price prediction
- [ ] Social sharing features
- [ ] Multi-language support

---

Built with ❤️ using Python, FastAPI, and OpenAI
