"""Realer BeautifulSoup-Selektorpfad des Wettbewerbsmonitors ohne Netzwerk."""
from app.services.competitor_monitor import CompetitorMonitor


def test_product_selectors_preserve_name_price_and_images(monkeypatch):
    monitor = CompetitorMonitor()
    monkeypatch.setattr(monitor, '_calculate_image_hash', lambda _url: 'fixture')
    html = '<section><h1 class="product-title">Weizen</h1><span class="price">29,99 €</span><div class="product-image"><img src="/item.png" width="80"></div></section>'
    result = monitor._parse_html_product(html, 'https://shop.invalid/p/1', {
        'name': 'Testshop', 'selectors': {'name': '.product-name, .product-title',
                                          'price': '.price, .product-price',
                                          'image': '.product-image img, .product-img'},
    })
    assert result is not None
    assert (result.product_name, result.price, result.currency) == ('Weizen', 29.99, 'EUR')
    assert [(image.url, image.width, image.hash) for image in result.images] == [('https://shop.invalid/item.png', 80, 'fixture')]
