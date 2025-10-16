"""
Competitor Price & Image Monitoring Service
Hybrid approach: Search API discovery + structured scraping with JSON-LD/schema.org
"""

import asyncio
import logging
import json
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


@dataclass
class ProductImage:
    """Product image with metadata"""
    url: str
    hash: str
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: Optional[datetime] = None


@dataclass
class CompetitorPrice:
    """Competitor price data"""
    shop_name: str
    product_url: str
    product_name: str
    price: float
    currency: str
    unit: Optional[str] = None
    quantity: Optional[float] = None
    gtin: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    images: List[ProductImage] = None
    scraped_at: Optional[datetime] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []


class CompetitorMonitor:
    """Monitor competitor prices and product images from agricultural B2B shops"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Agricultural B2B shop configurations
        self.shops = {
            'baywa': {
                'name': 'BayWa',
                'base_url': 'https://www.baywa.de',
                'search_url': 'https://www.baywa.de/suche',
                'categories': ['psm', 'duenger', 'saatgut'],
                'selectors': {
                    'product_link': '.product-item a, .product-link',
                    'price': '.price, .product-price, [data-price]',
                    'image': '.product-image img, .product-img',
                    'name': '.product-name, .product-title'
                }
            },
            'raiffeisen': {
                'name': 'Raiffeisen',
                'base_url': 'https://www.raiffeisenmarkt.de',
                'search_url': 'https://www.raiffeisenmarkt.de/suche',
                'categories': ['duenger', 'saatgut', 'garten'],
                'selectors': {
                    'product_link': '.product-item a, .product-link',
                    'price': '.price, .product-price',
                    'image': '.product-image img',
                    'name': '.product-name'
                }
            },
            'agrar24': {
                'name': 'Agrar24',
                'base_url': 'https://www.agrar24.com',
                'search_url': 'https://www.agrar24.com/search',
                'categories': ['psm', 'duenger', 'saatgut'],
                'selectors': {
                    'product_link': '.product-link, .product-item a',
                    'price': '.price, .product-price',
                    'image': '.product-image img',
                    'name': '.product-name, .product-title'
                }
            },
            'farmitoo': {
                'name': 'Farmitoo',
                'base_url': 'https://www.farmitoo.com',
                'search_url': 'https://www.farmitoo.com/search',
                'categories': ['psm', 'duenger', 'saatgut'],
                'selectors': {
                    'product_link': '.product-link',
                    'price': '.price',
                    'image': '.product-image img',
                    'name': '.product-name'
                }
            }
        }

        # Price history storage
        self.price_history_file = Path("data/price_history.json")
        self.price_history_file.parent.mkdir(parents=True, exist_ok=True)

    async def search_products(self, query: str, category: str = 'psm',
                            max_results: int = 50) -> List[str]:
        """Search for product URLs using shop search APIs"""
        product_urls = []

        for shop_key, shop_config in self.shops.items():
            if category not in shop_config['categories']:
                continue

            try:
                # Use Google Custom Search API or similar for discovery
                search_urls = await self._google_custom_search(
                    f"site:{shop_config['base_url']} {query} {category}",
                    max_results=max_results // len(self.shops)
                )

                # Filter and validate URLs
                for url in search_urls:
                    if self._is_product_url(url, shop_config):
                        product_urls.append(url)

                logger.info(f"Found {len(search_urls)} potential products from {shop_key}")

            except Exception as e:
                logger.warning(f"Failed to search {shop_key}: {e}")
                continue

        return list(set(product_urls))  # Remove duplicates

    async def scrape_product_data(self, product_url: str) -> Optional[CompetitorPrice]:
        """Scrape product data using structured approach (JSON-LD first, then HTML)"""
        try:
            # Determine shop from URL
            shop_config = self._get_shop_config(product_url)
            if not shop_config:
                return None

            # Fetch page
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()

            # Try JSON-LD/schema.org first
            product_data = self._extract_json_ld(response.text)
            if product_data:
                return self._parse_json_ld_product(product_data, product_url, shop_config)

            # Fallback to HTML parsing
            return self._parse_html_product(response.text, product_url, shop_config)

        except Exception as e:
            logger.warning(f"Failed to scrape {product_url}: {e}")
            return None

    def _extract_json_ld(self, html: str) -> Optional[Dict[str, Any]]:
        """Extract JSON-LD structured data from HTML"""
        import json

        # Find JSON-LD scripts
        json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(json_ld_pattern, html, re.DOTALL | re.IGNORECASE)

        for match in matches:
            try:
                data = json.loads(match.strip())
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    return data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            return item
            except json.JSONDecodeError:
                continue

        return None

    def _parse_json_ld_product(self, data: Dict[str, Any], url: str,
                             shop_config: Dict) -> CompetitorPrice:
        """Parse product data from JSON-LD"""
        # Extract price
        price = None
        currency = 'EUR'

        offers = data.get('offers', [])
        if isinstance(offers, dict):
            offers = [offers]

        for offer in offers:
            if isinstance(offer, dict):
                price_val = offer.get('price')
                if price_val:
                    try:
                        price = float(price_val)
                        currency = offer.get('priceCurrency', 'EUR')
                        break
                    except (ValueError, TypeError):
                        continue

        # Extract images
        images = []
        image_urls = data.get('image', [])
        if isinstance(image_urls, str):
            image_urls = [image_urls]

        for img_url in image_urls:
            if isinstance(img_url, str):
                images.append(ProductImage(
                    url=img_url,
                    hash=self._calculate_image_hash(img_url),
                    source_url=url,
                    scraped_at=datetime.now()
                ))

        return CompetitorPrice(
            shop_name=shop_config['name'],
            product_url=url,
            product_name=data.get('name', ''),
            price=price or 0.0,
            currency=currency,
            gtin=data.get('gtin13') or data.get('gtin'),
            brand=data.get('brand', {}).get('name') if isinstance(data.get('brand'), dict) else data.get('brand'),
            images=images,
            scraped_at=datetime.now()
        )

    def _parse_html_product(self, html: str, url: str,
                          shop_config: Dict) -> Optional[CompetitorPrice]:
        """Parse product data from HTML as fallback"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        # Extract product name
        name_selectors = shop_config['selectors']['name'].split(', ')
        product_name = None
        for selector in name_selectors:
            element = soup.select_one(selector.strip())
            if element:
                product_name = element.get_text().strip()
                break

        # Extract price
        price_selectors = shop_config['selectors']['price'].split(', ')
        price = None
        currency = 'EUR'

        for selector in price_selectors:
            element = soup.select_one(selector.strip())
            if element:
                price_text = element.get_text().strip()
                # Parse price (e.g., "29,99 €" or "29.99 EUR")
                price_match = re.search(r'(\d+[.,]\d+)', price_text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '.')
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        continue

        # Extract images
        images = []
        image_selectors = shop_config['selectors']['image'].split(', ')

        for selector in image_selectors:
            img_elements = soup.select(selector.strip())
            for img in img_elements:
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    # Make URL absolute
                    img_url = urljoin(url, img_url)
                    images.append(ProductImage(
                        url=img_url,
                        hash=self._calculate_image_hash(img_url),
                        width=int(img.get('width', 0)) if img.get('width') else None,
                        height=int(img.get('height', 0)) if img.get('height') else None,
                        source_url=url,
                        scraped_at=datetime.now()
                    ))

        if not product_name or not price:
            return None

        return CompetitorPrice(
            shop_name=shop_config['name'],
            product_url=url,
            product_name=product_name,
            price=price,
            currency=currency,
            images=images,
            scraped_at=datetime.now()
        )

    def _calculate_image_hash(self, image_url: str) -> str:
        """Calculate perceptual hash for image deduplication"""
        try:
            # Try to download and hash the actual image
            response = self.session.get(image_url, timeout=5, stream=True)
            if response.status_code == 200:
                # Use imagehash for perceptual hashing if available
                try:
                    import imagehash
                    from PIL import Image
                    import io

                    image_data = io.BytesIO(response.content)
                    img = Image.open(image_data)
                    # Calculate perceptual hash
                    phash = imagehash.phash(img)
                    return str(phash)
                except ImportError:
                    # Fallback to content hash
                    return hashlib.md5(response.content).hexdigest()[:16]
                except Exception:
                    # Fallback to URL hash
                    return hashlib.md5(image_url.encode()).hexdigest()[:16]
            else:
                return hashlib.md5(image_url.encode()).hexdigest()[:16]
        except Exception:
            # Fallback to URL hash
            return hashlib.md5(image_url.encode()).hexdigest()[:16]

    async def _google_custom_search(self, query: str, max_results: int = 10) -> List[str]:
        """Use Google Custom Search API for product discovery"""
        # Placeholder - would need actual Google Custom Search API key
        # For now, return mock results
        return [
            f"https://example-shop.com/product/{i}"
            for i in range(min(max_results, 5))
        ]

    def _get_shop_config(self, url: str) -> Optional[Dict]:
        """Get shop configuration based on URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for shop_key, config in self.shops.items():
            shop_domain = urlparse(config['base_url']).netloc.lower()
            if shop_domain in domain:
                return config

        return None

    def _parse_scraped_data(self, data: Dict) -> Optional[CompetitorPrice]:
        """Parse scraped data back into CompetitorPrice object"""
        try:
            return CompetitorPrice(
                shop_name=data.get('shop_name', ''),
                product_url=data.get('product_url', ''),
                product_name=data.get('product_name', ''),
                price=data.get('price', 0.0),
                currency=data.get('currency', 'EUR'),
                brand=data.get('brand'),
                gtin=data.get('gtin'),
                images=[
                    ProductImage(
                        url=img['url'],
                        hash=img['hash'],
                        width=img.get('width'),
                        height=img.get('height'),
                        source_url=data.get('product_url'),
                        scraped_at=datetime.now()
                    ) for img in data.get('images', [])
                ],
                scraped_at=datetime.now()
            )
        except Exception:
            return None

    def _is_product_url(self, url: str, shop_config: Dict) -> bool:
        """Check if URL is likely a product page"""
        # Basic heuristics for product URLs
        product_indicators = [
            '/product/', '/artikel/', '/item/',
            '/p/', '/produkt/', '/mittel/'
        ]

        url_lower = url.lower()
        return any(indicator in url_lower for indicator in product_indicators)

    def save_price_history(self, prices: List[CompetitorPrice]):
        """Save price data to history file"""
        try:
            history = []
            if self.price_history_file.exists():
                with open(self.price_history_file, 'r') as f:
                    history = json.load(f)

            # Add new entries
            for price in prices:
                history.append({
                    'shop_name': price.shop_name,
                    'product_url': price.product_url,
                    'product_name': price.product_name,
                    'price': price.price,
                    'currency': price.currency,
                    'scraped_at': price.scraped_at.isoformat() if price.scraped_at else None,
                    'images': [
                        {
                            'url': img.url,
                            'hash': img.hash,
                            'width': img.width,
                            'height': img.height
                        } for img in price.images
                    ]
                })

            # Keep only last 24 months of data
            cutoff_date = datetime.now() - timedelta(days=730)
            history = [
                entry for entry in history
                if not entry.get('scraped_at') or
                   datetime.fromisoformat(entry['scraped_at']) > cutoff_date
            ]

            with open(self.price_history_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)

            logger.info(f"Saved {len(prices)} price entries to history")

        except Exception as e:
            logger.error(f"Failed to save price history: {e}")

    def get_price_alerts(self, threshold_percent: float = 15.0) -> List[Dict]:
        """Check for significant price changes and generate alerts"""
        try:
            if not self.price_history_file.exists():
                return []

            with open(self.price_history_file, 'r') as f:
                history = json.load(f)

            alerts = []
            # Group by product URL
            product_groups = {}
            for entry in history:
                url = entry['product_url']
                if url not in product_groups:
                    product_groups[url] = []
                product_groups[url].append(entry)

            for url, entries in product_groups.items():
                if len(entries) < 2:
                    continue

                # Sort by date
                entries.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
                latest = entries[0]
                previous = entries[1]

                if latest['price'] and previous['price']:
                    change_percent = ((latest['price'] - previous['price']) / previous['price']) * 100

                    if abs(change_percent) >= threshold_percent:
                        alerts.append({
                            'product_url': url,
                            'product_name': latest['product_name'],
                            'shop_name': latest['shop_name'],
                            'old_price': previous['price'],
                            'new_price': latest['price'],
                            'change_percent': round(change_percent, 2),
                            'currency': latest['currency'],
                            'alert_time': datetime.now().isoformat()
                        })

            return alerts

        except Exception as e:
            logger.error(f"Failed to generate price alerts: {e}")
            return []


# Global competitor monitor instance
competitor_monitor = CompetitorMonitor()