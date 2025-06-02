"""
Enhanced web scraper using requests-html for reliable e-commerce product scraping
"""

import uuid
import re
import logging
import time
import random
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urljoin

from .models import Product

logger = logging.getLogger(__name__)

# Try to import requests-html, fall back gracefully if not available
try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    logger.warning("requests-html not available. Install with: pip install requests-html")


class EnhancedProductScraper:
    """Enhanced scraper using requests-html for better e-commerce site support"""
    
    def __init__(self):
        logger.info(f"EnhancedProductScraper initialized (requests-html available: {REQUESTS_HTML_AVAILABLE})")
        if REQUESTS_HTML_AVAILABLE:
            self.session = HTMLSession()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
        else:
            self.session = None
    
    def search_products(self, query: str, max_results: int = 10) -> List[Product]:
        """Search for products across multiple e-commerce sites"""
        if not REQUESTS_HTML_AVAILABLE:
            logger.warning("requests-html not available - returning empty results")
            return []
        
        logger.info(f"Enhanced search for: '{query}' (max_results: {max_results})")
        
        products = []
        
        # Search Amazon
        try:
            amazon_products = self._search_amazon_enhanced(query, max_results // 4)
            products.extend(amazon_products)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            logger.warning(f"Amazon enhanced search failed: {e}")
        
        # Search eBay
        try:
            ebay_products = self._search_ebay_enhanced(query, max_results // 4)
            products.extend(ebay_products)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            logger.warning(f"eBay enhanced search failed: {e}")
        
        # Search Walmart
        try:
            walmart_products = self._search_walmart_enhanced(query, max_results // 4)
            products.extend(walmart_products)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            logger.warning(f"Walmart enhanced search failed: {e}")
        
        # Search Target
        try:
            target_products = self._search_target_enhanced(query, max_results // 4)
            products.extend(target_products)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            logger.warning(f"Target enhanced search failed: {e}")
        
        logger.info(f"Enhanced scraper found {len(products)} products")
        return products[:max_results]
    
    def _search_amazon_enhanced(self, query: str, max_results: int) -> List[Product]:
        """Enhanced Amazon search using requests-html"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.amazon.com/s?k={encoded_query}"
            
            logger.info(f"Enhanced Amazon search: {url}")
            
            # Get the page
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
            
            # Find product containers
            product_containers = r.html.find('[data-component-type="s-search-result"]')
            
            for container in product_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = container.find('h2 a span', first=True) or container.find('[data-cy="title-recipe-title"]', first=True)
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Extract URL
                    link_elem = container.find('h2 a', first=True)
                    product_url = ""
                    if link_elem and 'href' in link_elem.attrs:
                        product_url = urljoin("https://www.amazon.com", link_elem.attrs['href'])
                    
                    # Extract price
                    price = None
                    price_elem = (container.find('.a-price-whole', first=True) or 
                                 container.find('.a-price', first=True))
                    
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract rating
                    rating = None
                    rating_elem = container.find('.a-icon-alt', first=True)
                    if rating_elem:
                        rating_text = rating_elem.text
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    # Extract image
                    image_url = None
                    img_elem = container.find('.s-image', first=True)
                    if img_elem and 'src' in img_elem.attrs:
                        image_url = img_elem.attrs['src']
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url=image_url,
                            rating=rating,
                            review_count=0,
                            description=f"Amazon product: {title}",
                            features=["Amazon Prime Eligible", "Fast Shipping"],
                            brand="",
                            category="",
                            availability="Available on Amazon",
                            source="Amazon"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Amazon product: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Amazon enhanced search failed: {e}")
        
        return products
    
    def _search_ebay_enhanced(self, query: str, max_results: int) -> List[Product]:
        """Enhanced eBay search using requests-html"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}&_sacat=0"
            
            logger.info(f"Enhanced eBay search: {url}")
            
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
            
            # Find product containers
            product_containers = r.html.find('.s-item__wrapper')
            
            for container in product_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = container.find('.s-item__title', first=True)
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Skip ads
                    if 'sponsored' in title.lower() or not title:
                        continue
                    
                    # Extract URL
                    link_elem = container.find('.s-item__link', first=True)
                    product_url = ""
                    if link_elem and 'href' in link_elem.attrs:
                        product_url = link_elem.attrs['href']
                    
                    # Extract price
                    price = None
                    price_elem = container.find('.s-item__price', first=True)
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract condition
                    condition = "Used"
                    condition_elem = container.find('.SECONDARY_INFO', first=True)
                    if condition_elem and 'new' in condition_elem.text.lower():
                        condition = "New"
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url="",
                            rating=4.0,
                            review_count=0,
                            description=f"eBay listing: {title} ({condition})",
                            features=[condition, "eBay Buyer Protection"],
                            brand="",
                            category="",
                            availability=condition,
                            source="eBay"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing eBay product: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"eBay enhanced search failed: {e}")
        
        return products
    
    def _search_walmart_enhanced(self, query: str, max_results: int) -> List[Product]:
        """Enhanced Walmart search using requests-html with JavaScript rendering"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.walmart.com/search?q={encoded_query}"
            
            logger.info(f"Enhanced Walmart search: {url}")
            
            # Get the page (skip JavaScript rendering to avoid event loop issues)
            r = self.session.get(url, timeout=20)
            r.raise_for_status()
            
            # Skip JavaScript rendering for now to avoid event loop conflicts
            # The static HTML parsing still works well for many products
            logger.info("Using static HTML for Walmart (JavaScript rendering disabled in web environments)")
            
            # Look for product containers (try multiple selectors)
            selectors = [
                '[data-automation-id="product-tile"]',
                '[data-testid="item-tile"]',
                '[data-testid="list-view"]',
                '.search-result-listview-item'
            ]
            
            product_containers = []
            for selector in selectors:
                containers = r.html.find(selector)
                if containers:
                    product_containers = containers
                    logger.info(f"Found {len(containers)} Walmart products using selector: {selector}")
                    break
            
            for container in product_containers[:max_results]:
                try:
                    # Extract title (try multiple selectors)
                    title_elem = (container.find('[data-automation-id="product-title"]', first=True) or
                                 container.find('h3', first=True) or
                                 container.find('[aria-label*="title"]', first=True))
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Extract price
                    price = None
                    price_elem = (container.find('[itemprop="price"]', first=True) or
                                 container.find('[data-automation-id="product-price"]', first=True) or
                                 container.find('.price', first=True))
                    
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract URL
                    link_elem = container.find('a[href*="/ip/"]', first=True)
                    product_url = ""
                    if link_elem and 'href' in link_elem.attrs:
                        product_url = urljoin("https://www.walmart.com", link_elem.attrs['href'])
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url="",
                            rating=None,
                            review_count=0,
                            description=f"Walmart product: {title}",
                            features=["Walmart+ Eligible", "Free Shipping Available"],
                            brand="",
                            category="",
                            availability="Available at Walmart",
                            source="Walmart"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Walmart product: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Walmart enhanced search failed: {e}")
        
        return products
    
    def _search_target_enhanced(self, query: str, max_results: int) -> List[Product]:
        """Enhanced Target search using requests-html"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.target.com/s?searchTerm={encoded_query}"
            
            logger.info(f"Enhanced Target search: {url}")
            
            r = self.session.get(url, timeout=20)
            r.raise_for_status()
            
            # Skip JavaScript rendering for now to avoid event loop conflicts
            logger.info("Using static HTML for Target (JavaScript rendering disabled in web environments)")
            
            # Look for product containers
            selectors = [
                '[data-test="product-details"]',
                '[data-test*="product"]',
                '.ProductCardVariantDefault'
            ]
            
            product_containers = []
            for selector in selectors:
                containers = r.html.find(selector)
                if containers:
                    product_containers = containers
                    logger.info(f"Found {len(containers)} Target products using selector: {selector}")
                    break
            
            for container in product_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = (container.find('[data-test="product-title"]', first=True) or
                                 container.find('h3', first=True) or
                                 container.find('a[data-test="product-title"]', first=True))
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Extract price
                    price = None
                    price_elem = (container.find('[data-test="product-price"]', first=True) or
                                 container.find('.price', first=True))
                    
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract URL
                    link_elem = container.find('a[href*="/p/"]', first=True)
                    product_url = ""
                    if link_elem and 'href' in link_elem.attrs:
                        product_url = urljoin("https://www.target.com", link_elem.attrs['href'])
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url="",
                            rating=None,
                            review_count=0,
                            description=f"Target product: {title}",
                            features=["Target Circle Eligible", "Same Day Delivery"],
                            brand="",
                            category="",
                            availability="Available at Target",
                            source="Target"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Target product: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Target enhanced search failed: {e}")
        
        return products 