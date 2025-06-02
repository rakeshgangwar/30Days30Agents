"""
Puppeteer-based web scraper using pyppeteer for JavaScript-heavy e-commerce sites
"""

import uuid
import json
import re
import logging
import asyncio
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus
from .models import Product

logger = logging.getLogger(__name__)

# Try to import pyppeteer, fall back gracefully if not available
try:
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False
    logger.warning("pyppeteer not available. Install with: pip install pyppeteer")


class PuppeteerProductScraper:
    """Puppeteer-based scraper for e-commerce sites that require JavaScript"""
    
    def __init__(self):
        logger.info(f"PuppeteerProductScraper initialized (pyppeteer available: {PYPPETEER_AVAILABLE})")
        self.browser = None
        self.page = None
    
    async def __aenter__(self):
        if PYPPETEER_AVAILABLE:
            try:
                self.browser = await launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--window-size=1920,1080'
                    ]
                )
                self.page = await self.browser.newPage()
                await self.page.setUserAgent(
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                logger.info("Browser launched successfully")
            except Exception as e:
                logger.warning(f"Failed to launch browser: {e}")
                self.browser = None
                self.page = None
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            try:
                await self.browser.close()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
    
    async def search_products(self, query: str, max_results: int = 10) -> List[Product]:
        """Search for products using Puppeteer"""
        logger.info(f"Puppeteer search for: '{query}' (max_results: {max_results})")
        
        if not PYPPETEER_AVAILABLE:
            logger.warning("pyppeteer not available - returning empty results")
            return []
        
        products = []
        
        async with self:
            if not self.browser or not self.page:
                logger.warning("Browser not available - returning empty results")
                return []
            
            # Search different e-commerce sites
            amazon_products = await self._search_amazon_puppeteer(query, max_results // 3)
            products.extend(amazon_products)
            
            # Add small delay between searches to be respectful
            await asyncio.sleep(1)
            
            walmart_products = await self._search_walmart_puppeteer(query, max_results // 3)
            products.extend(walmart_products)
            
            await asyncio.sleep(1)
            
            target_products = await self._search_target_puppeteer(query, max_results // 3)
            products.extend(target_products)
        
        logger.info(f"Puppeteer found {len(products)} products")
        return products[:max_results]
    
    async def _search_amazon_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Search Amazon using real Puppeteer"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.amazon.com/s?k={encoded_query}"
            
            logger.info(f"Navigating to Amazon: {url}")
            
            # Navigate to the page
            await self.page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})
            
            # Wait for products to load
            await self.page.waitForSelector('[data-component-type="s-search-result"]', {'timeout': 10000})
            
            # Extract product data
            products_data = await self.page.evaluate('''() => {
                const products = [];
                const productElements = document.querySelectorAll('[data-component-type="s-search-result"]');
                
                for (let i = 0; i < Math.min(productElements.length, 5); i++) {
                    const element = productElements[i];
                    
                    try {
                        const titleElement = element.querySelector('h2 a span') || element.querySelector('[data-cy="title-recipe-title"]');
                        const priceElement = element.querySelector('.a-price-whole') || element.querySelector('.a-price-range');
                        const ratingElement = element.querySelector('.a-icon-alt');
                        const linkElement = element.querySelector('h2 a');
                        const imageElement = element.querySelector('.s-image');
                        
                        if (titleElement && priceElement) {
                            const title = titleElement.textContent.trim();
                            const priceText = priceElement.textContent.replace(/[^0-9.]/g, '');
                            const price = parseFloat(priceText);
                            
                            if (title && price && price > 0) {
                                products.push({
                                    title: title,
                                    price: price,
                                    rating: ratingElement ? parseFloat(ratingElement.textContent.match(/\\d+\\.\\d+/)?.[0]) : null,
                                    url: linkElement ? 'https://www.amazon.com' + linkElement.getAttribute('href') : '',
                                    image: imageElement ? imageElement.getAttribute('src') : ''
                                });
                            }
                        }
                    } catch (err) {
                        console.log('Error parsing product:', err);
                    }
                }
                
                return products;
            }''')
            
            # Convert to Product objects
            for item in products_data:
                product = Product(
                    id=str(uuid.uuid4()),
                    title=item['title'],
                    price=float(item['price']),
                    url=item.get('url', ''),
                    image_url=item.get('image', ''),
                    rating=item.get('rating'),
                    review_count=0,
                    description=f"Amazon product: {item['title']}",
                    features=["Amazon Prime Eligible"],
                    brand="",
                    category="",
                    availability="Available on Amazon",
                    source="Amazon"
                )
                products.append(product)
            
            logger.info(f"Successfully scraped {len(products)} products from Amazon")
                
        except Exception as e:
            logger.warning(f"Amazon Puppeteer search failed: {e}")
        
        return products
    
    async def _search_walmart_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Search Walmart using real Puppeteer"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.walmart.com/search?q={encoded_query}"
            
            logger.info(f"Navigating to Walmart: {url}")
            
            # Navigate to the page
            await self.page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})
            
            # Wait for products to load
            await asyncio.sleep(3)  # Walmart takes time to load
            
            # Extract product data
            products_data = await self.page.evaluate('''() => {
                const products = [];
                const productElements = document.querySelectorAll('[data-automation-id="product-tile"], [data-testid="item-tile"]');
                
                for (let i = 0; i < Math.min(productElements.length, 3); i++) {
                    const element = productElements[i];
                    
                    try {
                        const titleElement = element.querySelector('[data-automation-id="product-title"]') || 
                                           element.querySelector('h2') || 
                                           element.querySelector('[aria-label*="title"]');
                        const priceElement = element.querySelector('[itemprop="price"]') || 
                                           element.querySelector('[data-automation-id="product-price"]') ||
                                           element.querySelector('.price');
                        const linkElement = element.querySelector('a[href*="/ip/"]');
                        
                        if (titleElement && priceElement) {
                            const title = titleElement.textContent.trim();
                            const priceText = priceElement.textContent.replace(/[^0-9.]/g, '');
                            const price = parseFloat(priceText);
                            
                            if (title && price && price > 0) {
                                products.push({
                                    title: title,
                                    price: price,
                                    url: linkElement ? 'https://www.walmart.com' + linkElement.getAttribute('href') : '',
                                    image: ''
                                });
                            }
                        }
                    } catch (err) {
                        console.log('Error parsing Walmart product:', err);
                    }
                }
                
                return products;
            }''')
            
            # Convert to Product objects
            for item in products_data:
                product = Product(
                    id=str(uuid.uuid4()),
                    title=item['title'],
                    price=float(item['price']),
                    url=item.get('url', ''),
                    image_url=item.get('image', ''),
                    rating=None,
                    review_count=0,
                    description=f"Walmart product: {item['title']}",
                    features=["Walmart+ Eligible", "Free Shipping Available"],
                    brand="",
                    category="",
                    availability="Available at Walmart",
                    source="Walmart"
                )
                products.append(product)
            
            logger.info(f"Successfully scraped {len(products)} products from Walmart")
                
        except Exception as e:
            logger.warning(f"Walmart Puppeteer search failed: {e}")
        
        return products
    
    async def _search_target_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Search Target using real Puppeteer"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.target.com/s?searchTerm={encoded_query}"
            
            logger.info(f"Navigating to Target: {url}")
            
            # Navigate to the page
            await self.page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})
            
            # Wait for products to load
            await asyncio.sleep(3)
            
            # Extract product data
            products_data = await self.page.evaluate('''() => {
                const products = [];
                const productElements = document.querySelectorAll('[data-test="product-details"], [data-test*="product"]');
                
                for (let i = 0; i < Math.min(productElements.length, 3); i++) {
                    const element = productElements[i];
                    
                    try {
                        const titleElement = element.querySelector('[data-test="product-title"]') || 
                                           element.querySelector('h2') ||
                                           element.querySelector('a[data-test="product-title"]');
                        const priceElement = element.querySelector('[data-test="product-price"]') || 
                                           element.querySelector('.price');
                        const linkElement = element.querySelector('a[href*="/p/"]');
                        
                        if (titleElement && priceElement) {
                            const title = titleElement.textContent.trim();
                            const priceText = priceElement.textContent.replace(/[^0-9.]/g, '');
                            const price = parseFloat(priceText);
                            
                            if (title && price && price > 0) {
                                products.push({
                                    title: title,
                                    price: price,
                                    url: linkElement ? 'https://www.target.com' + linkElement.getAttribute('href') : '',
                                    image: ''
                                });
                            }
                        }
                    } catch (err) {
                        console.log('Error parsing Target product:', err);
                    }
                }
                
                return products;
            }''')
            
            # Convert to Product objects
            for item in products_data:
                product = Product(
                    id=str(uuid.uuid4()),
                    title=item['title'],
                    price=float(item['price']),
                    url=item.get('url', ''),
                    image_url=item.get('image', ''),
                    rating=None,
                    review_count=0,
                    description=f"Target product: {item['title']}",
                    features=["Target Circle Eligible", "Same Day Delivery"],
                    brand="",
                    category="",
                    availability="Available at Target",
                    source="Target"
                )
                products.append(product)
            
            logger.info(f"Successfully scraped {len(products)} products from Target")
                
        except Exception as e:
            logger.warning(f"Target Puppeteer search failed: {e}")
        
        return products


# Real MCP Puppeteer implementation (to be used when MCP tools are available)
class MCPPuppeteerScraper:
    """Real Puppeteer scraper using MCP tools"""
    
    def __init__(self):
        self.browser_launched = False
        logger.info("MCPPuppeteerScraper initialized")
    
    async def search_amazon_real(self, query: str, max_results: int = 5) -> List[Product]:
        """Actually search Amazon using MCP Puppeteer tools"""
        products = []
        
        try:
            # Navigate to Amazon
            encoded_query = quote_plus(query)
            url = f"https://www.amazon.com/s?k={encoded_query}"
            
            # These would be the actual MCP tool calls when MCP environment is available:
            # await mcp_puppeteer_puppeteer_navigate({"url": url})
            # 
            # # Wait for results to load
            # await mcp_puppeteer_puppeteer_evaluate({
            #     "script": "await new Promise(resolve => setTimeout(resolve, 3000))"
            # })
            # 
            # # Extract product data
            # product_data = await mcp_puppeteer_puppeteer_evaluate({
            #     "script": """
            #     const products = [];
            #     const productElements = document.querySelectorAll('[data-component-type="s-search-result"]');
            #     
            #     for (let i = 0; i < Math.min(productElements.length, 5); i++) {
            #         const element = productElements[i];
            #         
            #         const titleElement = element.querySelector('h2 a span');
            #         const priceElement = element.querySelector('.a-price-whole');
            #         const ratingElement = element.querySelector('.a-icon-alt');
            #         const linkElement = element.querySelector('h2 a');
            #         const imageElement = element.querySelector('.s-image');
            #         
            #         if (titleElement && priceElement) {
            #             products.push({
            #                 title: titleElement.textContent.trim(),
            #                 price: parseFloat(priceElement.textContent.replace(',', '')),
            #                 rating: ratingElement ? parseFloat(ratingElement.textContent.match(/\\d+\\.\\d+/)?.[0]) : null,
            #                 url: linkElement ? 'https://www.amazon.com' + linkElement.getAttribute('href') : '',
            #                 image: imageElement ? imageElement.getAttribute('src') : ''
            #             });
            #         }
            #     }
            #     
            #     return products;
            #     """
            # })
            # 
            # # Convert to Product objects
            # for item in product_data:
            #     product = Product(
            #         id=str(uuid.uuid4()),
            #         title=item['title'],
            #         price=item['price'],
            #         url=item['url'],
            #         image_url=item['image'],
            #         rating=item['rating'],
            #         review_count=0,
            #         description=f"Amazon product: {item['title']}",
            #         source="Amazon"
            #     )
            #     products.append(product)
            
            # For now, return empty since we don't want to generate fake data
            logger.info("MCP Puppeteer tools not available - returning empty results")
            
        except Exception as e:
            logger.error(f"MCP Puppeteer Amazon search failed: {e}")
        
        return products 