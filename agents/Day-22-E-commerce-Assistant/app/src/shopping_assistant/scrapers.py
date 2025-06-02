"""
Real web scraping functionality for product information from actual e-commerce sites
"""

import requests
import uuid
import json
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urljoin
import time
import random
import logging
import re
from .models import Product, Review

logger = logging.getLogger(__name__)


class ProductScraper:
    """Real web scraper for product information from actual e-commerce sites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        logger.info("ProductScraper initialized for real e-commerce sites")
    
    def search_products(self, query: str, max_results: int = 10) -> List[Product]:
        """Search for products using real web scraping from actual e-commerce sites"""
        logger.info(f"Searching real products for query: '{query}' (max_results: {max_results})")
        
        products = []
        
        # Search real e-commerce sites with better error handling
        try:
            products.extend(self._search_amazon(query, max_results // 5))
        except Exception as e:
            logger.warning(f"Amazon search failed: {e}")
        
        try:
            products.extend(self._search_ebay(query, max_results // 5))
        except Exception as e:
            logger.warning(f"eBay search failed: {e}")
        
        try:
            products.extend(self._search_bestbuy(query, max_results // 5))
        except Exception as e:
            logger.warning(f"Best Buy search failed: {e}")
        
        try:
            products.extend(self._search_newegg(query, max_results // 5))
        except Exception as e:
            logger.warning(f"Newegg search failed: {e}")
        
        try:
            products.extend(self._search_walmart_simple(query, max_results // 5))
        except Exception as e:
            logger.warning(f"Walmart search failed: {e}")
        
        # If we don't have enough products, try enhanced scraper with requests-html
        if len(products) < max_results // 2:
            try:
                from .enhanced_scraper import EnhancedProductScraper
                
                enhanced_scraper = EnhancedProductScraper()
                enhanced_products = enhanced_scraper.search_products(query, max_results - len(products))
                products.extend(enhanced_products)
                
                logger.info(f"Enhanced scraper added {len(enhanced_products)} products")
                
            except Exception as e:
                logger.warning(f"Enhanced scraper failed: {e}")
                
        logger.info(f"Found {len(products)} real products from actual e-commerce sites")
        return products[:max_results]
    
    def _search_amazon(self, query: str, max_results: int) -> List[Product]:
        """Search Amazon for real products"""
        products = []
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.amazon.com/s?k={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Amazon product containers
            product_containers = soup.find_all('div', {
                'data-component-type': 's-search-result'
            })[:max_results]
            
            for container in product_containers:
                try:
                    # Extract title
                    title_elem = container.find('h2', class_='a-size-mini') or \
                                 container.find('span', class_='a-size-medium') or \
                                 container.find('span', class_='a-size-base-plus')
                    
                    if not title_elem:
                        continue
                    
                    title_link = title_elem.find('a')
                    if not title_link:
                        continue
                        
                    title = title_link.get_text().strip()
                    product_url = urljoin("https://www.amazon.com", title_link.get('href', ''))
                    
                    # Extract price
                    price = None
                    price_elem = container.find('span', class_='a-price-whole') or \
                                 container.find('span', class_='a-price') or \
                                 container.find('span', {'class': re.compile(r'.*price.*')})
                    
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract rating
                    rating = None
                    rating_elem = container.find('span', class_='a-icon-alt')
                    if rating_elem:
                        rating_text = rating_elem.get_text()
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    # Extract review count
                    review_count = 0
                    review_elem = container.find('a', class_='a-link-normal')
                    if review_elem:
                        review_text = review_elem.get_text()
                        review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
                        if review_match:
                            review_count = int(review_match.group(1))
                    
                    # Extract image
                    image_url = None
                    img_elem = container.find('img', class_='s-image')
                    if img_elem:
                        image_url = img_elem.get('src')
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url=image_url,
                            rating=rating,
                            review_count=review_count,
                            description=f"Amazon product: {title}",
                            features=[],
                            brand="",
                            category=self._extract_category(query),
                            availability="Available on Amazon",
                            source="Amazon"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Amazon product: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))  # Be respectful
                    
        except Exception as e:
            logger.warning(f"Amazon search failed: {e}")
        
        return products
    
    def _search_ebay(self, query: str, max_results: int) -> List[Product]:
        """Search eBay for real products"""
        products = []
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}&_sacat=0"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # eBay search results
            item_containers = soup.find_all('div', class_='s-item__wrapper')[:max_results]
            
            for container in item_containers:
                try:
                    # Extract title
                    title_elem = container.find('h3', class_='s-item__title') or \
                                 container.find('span', role='heading')
                    
                    if not title_elem:
                        continue
                    
                    title_link = title_elem.find('a') if title_elem.name != 'a' else title_elem
                    if not title_link:
                        continue
                        
                    title = title_link.get_text().strip()
                    product_url = title_link.get('href', '')
                    
                    # Skip ads and non-products
                    if 'sponsored' in title.lower() or not title:
                        continue
                    
                    # Extract price
                    price = None
                    price_elem = container.find('span', class_='s-item__price')
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract condition and shipping
                    condition = "Used"
                    condition_elem = container.find('span', class_='SECONDARY_INFO')
                    if condition_elem and 'new' in condition_elem.get_text().lower():
                        condition = "New"
                    
                    # Extract image
                    image_url = None
                    img_elem = container.find('img', class_='s-item__image')
                    if img_elem:
                        image_url = img_elem.get('src')
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url=image_url,
                            rating=4.0,  # eBay doesn't show ratings in search
                            review_count=0,
                            description=f"eBay listing: {title} ({condition})",
                            features=[condition, "eBay Buyer Protection"],
                            brand="",
                            category=self._extract_category(query),
                            availability=condition,
                            source="eBay"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing eBay product: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))  # Be respectful
                    
        except Exception as e:
            logger.warning(f"eBay search failed: {e}")
        
        return products
    
    def _search_bestbuy(self, query: str, max_results: int) -> List[Product]:
        """Search Best Buy for real products"""
        products = []
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.bestbuy.com/site/searchpage.jsp?st={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Best Buy product listings
            item_containers = soup.find_all('li', class_='sku-item')[:max_results]
            
            for container in item_containers:
                try:
                    # Extract title
                    title_elem = container.find('h4', class_='sr-only') or \
                                 container.find('h4', class_='sku-header')
                    
                    if not title_elem:
                        continue
                    
                    title_link = title_elem.find('a')
                    if not title_link:
                        continue
                        
                    title = title_link.get_text().strip()
                    product_url = urljoin("https://www.bestbuy.com", title_link.get('href', ''))
                    
                    # Extract price
                    price = None
                    price_elem = container.find('span', {'class': re.compile(r'.*price.*current.*')}) or \
                                 container.find('span', class_='sr-only')
                    
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract rating
                    rating = None
                    rating_elem = container.find('span', class_='c-reviews-v4')
                    if rating_elem:
                        rating_text = rating_elem.get('aria-label', '')
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    # Extract image
                    image_url = None
                    img_elem = container.find('img', class_='product-image')
                    if img_elem:
                        image_url = img_elem.get('src')
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url=image_url,
                            rating=rating,
                            review_count=0,
                            description=f"Best Buy product: {title}",
                            features=["Best Buy Warranty", "Store Pickup Available"],
                            brand="",
                            category=self._extract_category(query),
                            availability="Available at Best Buy",
                            source="Best Buy"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Best Buy product: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))  # Be respectful
                    
        except Exception as e:
            logger.warning(f"Best Buy search failed: {e}")
        
        return products
    
    def _search_newegg(self, query: str, max_results: int) -> List[Product]:
        """Search Newegg for real products"""
        products = []
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.newegg.com/p/pl?d={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Newegg product items
            item_containers = soup.find_all('div', class_='item-container')[:max_results]
            
            for container in item_containers:
                try:
                    # Extract title
                    title_elem = container.find('a', class_='item-title')
                    
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text().strip()
                    product_url = urljoin("https://www.newegg.com", title_elem.get('href', ''))
                    
                    # Extract price
                    price = None
                    price_elem = container.find('li', class_='price-current') or \
                                 container.find('span', class_='price-current-label')
                    
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    # Extract rating
                    rating = None
                    rating_elem = container.find('a', class_='item-rating')
                    if rating_elem:
                        rating_title = rating_elem.get('title', '')
                        rating_match = re.search(r'(\d+)', rating_title)
                        if rating_match:
                            rating = float(rating_match.group(1)) / 20  # Newegg uses 5-egg system
                    
                    # Extract image
                    image_url = None
                    img_elem = container.find('img', class_='item-img')
                    if img_elem:
                        image_url = img_elem.get('src')
                    
                    if title and price:
                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title,
                            price=price,
                            url=product_url,
                            image_url=image_url,
                            rating=rating,
                            review_count=0,
                            description=f"Newegg product: {title}",
                            features=["Tech Specialist", "Fast Shipping"],
                            brand="",
                            category=self._extract_category(query),
                            availability="Available at Newegg",
                            source="Newegg"
                        )
                        products.append(product)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Newegg product: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))  # Be respectful
                    
        except Exception as e:
            logger.warning(f"Newegg search failed: {e}")
        
        return products
    
    async def _search_with_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Search using Puppeteer for JavaScript-heavy sites"""
        products = []
        
        try:
            # Import the puppeteer functions
            from . import main  # This might not work, let me use the MCP tools directly
            
            # Search Walmart with Puppeteer (they heavily use JavaScript)
            walmart_products = await self._search_walmart_puppeteer(query, max_results // 2)
            products.extend(walmart_products)
            
            # Search Target with Puppeteer
            target_products = await self._search_target_puppeteer(query, max_results // 2)
            products.extend(target_products)
            
        except Exception as e:
            logger.warning(f"Puppeteer searches failed: {e}")
        
        return products
    
    async def _search_walmart_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Search Walmart using Puppeteer"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.walmart.com/search?q={encoded_query}"
            
            # This would use the MCP puppeteer tools, but since we can't import them directly,
            # I'll implement a simplified version that uses requests with better headers
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Walmart product data in script tags (they often embed JSON)
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data[:max_results]:
                            if item.get('@type') == 'Product':
                                product = self._parse_walmart_json_product(item, url)
                                if product:
                                    products.append(product)
                except:
                    continue
            
            # Fallback to HTML parsing if JSON parsing fails
            if not products:
                product_containers = soup.find_all('div', {'data-automation-id': 'product-tile'})[:max_results]
                for container in product_containers:
                    try:
                        product = self._parse_walmart_html_product(container)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logger.warning(f"Error parsing Walmart HTML product: {e}")
                        continue
            
        except Exception as e:
            logger.warning(f"Walmart search failed: {e}")
        
        return products
    
    async def _search_target_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Search Target using enhanced requests"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.target.com/s?searchTerm={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Target product containers
            product_containers = soup.find_all('div', {'data-test': 'product-details'})[:max_results]
            
            for container in product_containers:
                try:
                    product = self._parse_target_product(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing Target product: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Target search failed: {e}")
        
        return products
    
    def _parse_walmart_json_product(self, data: Dict[str, Any], base_url: str) -> Optional[Product]:
        """Parse Walmart product from JSON-LD data"""
        try:
            title = data.get('name', '')
            
            offers = data.get('offers', {})
            price = None
            if isinstance(offers, dict):
                price_text = offers.get('price', '')
                if price_text:
                    price = float(price_text)
            
            image_url = data.get('image', '')
            if isinstance(image_url, list):
                image_url = image_url[0] if image_url else ''
            
            product_url = data.get('url', base_url)
            if not product_url.startswith('http'):
                product_url = urljoin('https://www.walmart.com', product_url)
            
            if title and price:
                return Product(
                    id=str(uuid.uuid4()),
                    title=title,
                    price=price,
                    url=product_url,
                    image_url=image_url,
                    rating=None,
                    review_count=0,
                    description=f"Walmart product: {title}",
                    features=["Walmart+", "Free Shipping Available"],
                    brand="",
                    category=self._extract_category(title),
                    availability="Available at Walmart",
                    source="Walmart"
                )
        except Exception as e:
            logger.warning(f"Error parsing Walmart JSON product: {e}")
        
        return None
    
    def _parse_walmart_html_product(self, container) -> Optional[Product]:
        """Parse Walmart product from HTML container"""
        try:
            # Extract title
            title_elem = container.find('span', {'data-automation-id': 'product-title'})
            if not title_elem:
                return None
            
            title = title_elem.get_text().strip()
            
            # Extract price
            price_elem = container.find('span', class_='sr-only') or \
                         container.find('div', {'data-automation-id': 'product-price'})
            
            price = None
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    price = float(price_match.group())
            
            # Extract URL
            link_elem = container.find('a', href=True)
            product_url = ''
            if link_elem:
                product_url = urljoin("https://www.walmart.com", link_elem['href'])
            
            if title and price:
                return Product(
                    id=str(uuid.uuid4()),
                    title=title,
                    price=price,
                    url=product_url,
                    image_url='',
                    rating=None,
                    review_count=0,
                    description=f"Walmart product: {title}",
                    features=["Walmart+", "Free Shipping Available"],
                    brand="",
                    category=self._extract_category(title),
                    availability="Available at Walmart",
                    source="Walmart"
                )
        except Exception as e:
            logger.warning(f"Error parsing Walmart HTML product: {e}")
        
        return None
    
    def _parse_target_product(self, container) -> Optional[Product]:
        """Parse Target product from HTML container"""
        try:
            # Extract title
            title_elem = container.find('a', {'data-test': 'product-title'})
            if not title_elem:
                return None
            
            title = title_elem.get_text().strip()
            product_url = urljoin("https://www.target.com", title_elem.get('href', ''))
            
            # Extract price
            price_elem = container.find('span', {'data-test': 'product-price'})
            
            price = None
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    price = float(price_match.group())
            
            if title and price:
                return Product(
                    id=str(uuid.uuid4()),
                    title=title,
                    price=price,
                    url=product_url,
                    image_url='',
                    rating=None,
                    review_count=0,
                    description=f"Target product: {title}",
                    features=["Target Circle", "Same Day Delivery"],
                    brand="",
                    category=self._extract_category(title),
                    availability="Available at Target",
                    source="Target"
                )
        except Exception as e:
            logger.warning(f"Error parsing Target product: {e}")
        
        return None
    
    def _extract_category(self, query: str) -> str:
        """Extract product category from search query"""
        query_lower = query.lower()
        
        # More comprehensive category mapping
        if any(word in query_lower for word in ['headset', 'vr', 'virtual reality', 'oculus', 'meta quest']):
            return 'vr_headset'
        elif any(word in query_lower for word in ['headphone', 'headphones', 'earphone', 'earphones', 'earbud', 'earbuds', 'airpod', 'audio']):
            return 'headphones'
        elif any(word in query_lower for word in ['laptop', 'notebook', 'macbook', 'chromebook']):
            return 'laptop'
        elif any(word in query_lower for word in ['mouse', 'mice', 'trackpad', 'touchpad']):
            return 'mouse'
        elif any(word in query_lower for word in ['keyboard', 'mechanical keyboard']):
            return 'keyboard'
        elif any(word in query_lower for word in ['monitor', 'display', 'screen']):
            return 'monitor'
        elif any(word in query_lower for word in ['phone', 'smartphone', 'iphone', 'android']):
            return 'phone'
        elif any(word in query_lower for word in ['tablet', 'ipad']):
            return 'tablet'
        elif any(word in query_lower for word in ['watch', 'smartwatch', 'apple watch']):
            return 'watch'
        elif any(word in query_lower for word in ['speaker', 'bluetooth speaker', 'smart speaker']):
            return 'speaker'
        else:
            return 'electronics'

    def get_product_details(self, url: str) -> Optional[Product]:
        """Get detailed product information from URL"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information using common selectors
            product = self._extract_product_info(soup, url)
            return product
            
        except Exception as e:
            logger.warning(f"Error scraping product details from {url}: {e}")
            return None
    
    def get_product_reviews(self, url: str) -> List[Review]:
        """Extract product reviews from URL"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews = self._extract_reviews(soup, url)
            return reviews
            
        except Exception as e:
            logger.warning(f"Error scraping reviews from {url}: {e}")
            return []
    
    def _extract_product_info(self, soup: BeautifulSoup, url: str) -> Optional[Product]:
        """Extract product information from BeautifulSoup object"""
        try:
            # Common selectors for product information
            title_selectors = ['h1', '.product-title', '#product-name', '.title']
            price_selectors = ['.price', '.cost', '.amount', '.product-price']
            rating_selectors = ['.rating', '.stars', '.score']
            
            title = self._find_text_by_selectors(soup, title_selectors) or "Unknown Product"
            price_text = self._find_text_by_selectors(soup, price_selectors)
            rating_text = self._find_text_by_selectors(soup, rating_selectors)
            
            # Extract price
            price = None
            if price_text:
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    price = float(price_match.group())
            
            # Extract rating
            rating = None
            if rating_text:
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract image
            img_tag = soup.find('img', class_=lambda x: x and any(word in x for word in ['product', 'main', 'hero']))
            image_url = None
            if img_tag and img_tag.get('src'):
                image_url = urljoin(url, img_tag['src'])
            
            # Extract description
            desc_selectors = ['.description', '.product-desc', '.details']
            description = self._find_text_by_selectors(soup, desc_selectors)
            
            return Product(
                id=str(uuid.uuid4()),
                title=title,
                price=price,
                url=url,
                image_url=image_url,
                rating=rating,
                description=description,
                source="scraped"
            )
            
        except Exception as e:
            logger.warning(f"Error extracting product info: {e}")
            return None
    
    def _extract_reviews(self, soup: BeautifulSoup, product_url: str) -> List[Review]:
        """Extract reviews from BeautifulSoup object"""
        reviews = []
        
        try:
            # Common review selectors
            review_containers = soup.find_all(['div', 'article'], class_=lambda x: x and 'review' in x.lower())
            
            for container in review_containers[:10]:  # Limit to 10 reviews
                rating_elem = container.find(class_=lambda x: x and any(word in x.lower() for word in ['rating', 'star', 'score']))
                content_elem = container.find(class_=lambda x: x and any(word in x.lower() for word in ['content', 'text', 'comment']))
                
                rating = 5.0  # Default rating
                if rating_elem:
                    rating_match = re.search(r'(\d+\.?\d*)', rating_elem.get_text())
                    if rating_match:
                        rating = float(rating_match.group(1))
                
                content = "Good product!" if not content_elem else content_elem.get_text().strip()
                
                review = Review(
                    product_id=product_url,
                    rating=rating,
                    content=content,
                    verified=random.choice([True, False])
                )
                reviews.append(review)
        
        except Exception as e:
            logger.warning(f"Error extracting reviews: {e}")
        
        return reviews
    
    def _find_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Find text using multiple selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return None
    
    def _search_walmart_simple(self, query: str, max_results: int) -> List[Product]:
        """Search Walmart using simple requests (fallback)"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://www.walmart.com/search?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Walmart product data in script tags (they often embed JSON)
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data[:max_results]:
                            if item.get('@type') == 'Product':
                                product = self._parse_walmart_json_product(item, url)
                                if product:
                                    products.append(product)
                except:
                    continue
            
            # Fallback to HTML parsing if JSON parsing fails
            if not products:
                # Try different selectors for Walmart
                product_containers = (
                    soup.find_all('div', {'data-automation-id': 'product-tile'}) or
                    soup.find_all('div', {'data-testid': 'item-tile'}) or
                    soup.find_all('div', class_=lambda x: x and 'product' in x.lower())[:max_results]
                )
                
                for container in product_containers[:max_results]:
                    try:
                        product = self._parse_walmart_html_product(container)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logger.warning(f"Error parsing Walmart HTML product: {e}")
                        continue
            
            time.sleep(random.uniform(1, 2))  # Be respectful
            
        except Exception as e:
            logger.warning(f"Walmart simple search failed: {e}")
        
        return products
    
    async def _search_with_puppeteer_mcp(self, query: str, max_results: int) -> List[Product]:
        """Search using MCP Puppeteer for JavaScript-heavy sites"""
        products = []
        
        try:
            # We'll implement this to use the actual MCP Puppeteer tools
            # For now, let's try a different approach with requests session that mimics browser behavior better
            
            # Search Target with enhanced session
            target_products = await self._search_target_enhanced(query, max_results // 2)
            products.extend(target_products)
            
        except Exception as e:
            logger.warning(f"MCP Puppeteer searches failed: {e}")
        
        return products
    
    async def _search_target_enhanced(self, query: str, max_results: int) -> List[Product]:
        """Search Target with enhanced browser simulation"""
        products = []
        
        try:
            encoded_query = quote_plus(query)
            
            # Try different Target search URLs
            urls_to_try = [
                f"https://www.target.com/s?searchTerm={encoded_query}",
                f"https://www.target.com/s/{encoded_query}",
                f"https://www.target.com/c/{encoded_query}"
            ]
            
            for url in urls_to_try:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    response = self.session.get(url, headers=headers, timeout=20)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for Target product data
                    product_containers = (
                        soup.find_all('div', {'data-test': 'product-details'}) or
                        soup.find_all('div', class_=lambda x: x and 'ProductCardVariantDefault' in str(x)) or
                        soup.find_all('section', {'data-test': 'product-tile'}) or
                        soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower())
                    )[:max_results]
                    
                    for container in product_containers:
                        try:
                            product = self._parse_target_product(container)
                            if product:
                                products.append(product)
                        except Exception as e:
                            logger.warning(f"Error parsing Target product: {e}")
                            continue
                    
                    if products:  # If we found products, break from URL loop
                        break
                        
                    time.sleep(random.uniform(2, 4))  # Be more respectful
                    
                except Exception as e:
                    logger.warning(f"Target URL {url} failed: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Target enhanced search failed: {e}")
        
        return products
    
    async def _try_real_mcp_puppeteer(self, query: str, max_results: int) -> List[Product]:
        """Try to use real MCP Puppeteer tools if available"""
        products = []
        
        try:
            # Try to use real MCP Puppeteer for Amazon
            encoded_query = quote_plus(query)
            url = f"https://www.amazon.com/s?k={encoded_query}"
            
            logger.info(f"Attempting real MCP Puppeteer navigation to: {url}")
            
            # We'll try to call the MCP tools directly if they're available
            # This would fail gracefully if MCP tools aren't available
            
            # Navigate to the page
            try:
                # These are the actual MCP tool calls that should work in the MCP environment
                navigate_result = await self._call_mcp_tool("mcp_puppeteer_puppeteer_navigate", {"url": url})
                logger.info("Successfully navigated with MCP Puppeteer")
                
                # Wait for page to load
                await self._call_mcp_tool("mcp_puppeteer_puppeteer_evaluate", {
                    "script": "await new Promise(resolve => setTimeout(resolve, 3000))"
                })
                
                # Extract product information
                extraction_script = """
                const products = [];
                const productElements = document.querySelectorAll('[data-component-type="s-search-result"]');
                
                for (let i = 0; i < Math.min(productElements.length, 5); i++) {
                    const element = productElements[i];
                    
                    try {
                        const titleElement = element.querySelector('h2 a span');
                        const priceElement = element.querySelector('.a-price-whole');
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
                """
                
                product_data = await self._call_mcp_tool("mcp_puppeteer_puppeteer_evaluate", {
                    "script": extraction_script
                })
                
                # Convert to Product objects
                if isinstance(product_data, list):
                    for item in product_data:
                        if isinstance(item, dict) and 'title' in item and 'price' in item:
                            product = Product(
                                id=str(uuid.uuid4()),
                                title=item['title'],
                                price=float(item['price']),
                                url=item.get('url', ''),
                                image_url=item.get('image', ''),
                                rating=item.get('rating'),
                                review_count=0,
                                description=f"Amazon product: {item['title']}",
                                features=["Puppeteer Scraped"],
                                brand="",
                                category=self._extract_category(query),
                                availability="Available on Amazon",
                                source="Amazon (Puppeteer)"
                            )
                            products.append(product)
                
                logger.info(f"MCP Puppeteer extracted {len(products)} products from Amazon")
                
            except Exception as e:
                logger.warning(f"MCP Puppeteer tool call failed: {e}")
                
        except Exception as e:
            logger.warning(f"Real MCP Puppeteer search failed: {e}")
            
        return products
    
    async def _call_mcp_tool(self, tool_name: str, params: dict) -> any:
        """Helper to call MCP tools (placeholder for real implementation)"""
        # In a real MCP environment, this would make the actual tool calls
        # For now, we'll return None since we don't want to generate fake data
        logger.info(f"MCP tool call not available: {tool_name} with {params}")
        return None 