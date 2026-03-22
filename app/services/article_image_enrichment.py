"""
Article Image Enrichment Service
---------------------------------
Fetches product images for articles from free public APIs:
1. Open Food Facts (EAN-based, best for consumer goods)
2. Wikipedia API (name-based, good for agrar commodities)
3. Static category mapping (agrar-specific fallback)

No API keys required. Respects rate limits with configurable delays.
"""

import asyncio
import logging
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ── Category mapping for common Agrar / Landhandel terms ─────────────────────
# Wikimedia Commons thumbnail URLs (stable, permissive license)
CATEGORY_IMAGE_MAP: dict[str, str] = {
    # Getreide
    "weizen":      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Wheat_close-up.JPG/320px-Wheat_close-up.JPG",
    "winterweizen":"https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Wheat_close-up.JPG/320px-Wheat_close-up.JPG",
    "sommerweizen":"https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Wheat_close-up.JPG/320px-Wheat_close-up.JPG",
    "gerste":      "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Barley_grains.jpg/320px-Barley_grains.jpg",
    "wintergerste":"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Barley_grains.jpg/320px-Barley_grains.jpg",
    "sommergerste":"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Barley_grains.jpg/320px-Barley_grains.jpg",
    "braugerste":  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Barley_grains.jpg/320px-Barley_grains.jpg",
    "roggen":      "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Secale_cereale_-_Köhler–s_Medizinal-Pflanzen-132.jpg/320px-Secale_cereale_-_Köhler–s_Medizinal-Pflanzen-132.jpg",
    "winterroggen":"https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Secale_cereale_-_Köhler–s_Medizinal-Pflanzen-132.jpg/320px-Secale_cereale_-_Köhler–s_Medizinal-Pflanzen-132.jpg",
    "hafer":       "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Avena_sativa_L..jpg/320px-Avena_sativa_L..jpg",
    "triticale":   "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Triticale_ährchen.jpg/320px-Triticale_ährchen.jpg",
    "mais":        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Corn_-_Zea_mays_-_geograph.org.uk_-_823981.jpg/320px-Corn_-_Zea_mays_-_geograph.org.uk_-_823981.jpg",
    "körnermais":  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Corn_-_Zea_mays_-_geograph.org.uk_-_823981.jpg/320px-Corn_-_Zea_mays_-_geograph.org.uk_-_823981.jpg",
    "silomais":    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Corn_-_Zea_mays_-_geograph.org.uk_-_823981.jpg/320px-Corn_-_Zea_mays_-_geograph.org.uk_-_823981.jpg",
    # Ölsaaten
    "raps":        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Brassica_napus_2.jpg/320px-Brassica_napus_2.jpg",
    "winterraps":  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Brassica_napus_2.jpg/320px-Brassica_napus_2.jpg",
    "sonnenblumen":"https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Sunflower_sky_backdrop.jpg/320px-Sunflower_sky_backdrop.jpg",
    "soja":        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Glycine_max_15.jpg/320px-Glycine_max_15.jpg",
    "sojabohnen":  "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Glycine_max_15.jpg/320px-Glycine_max_15.jpg",
    # Hülsenfrüchte
    "erbsen":      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Snowpeas.jpg/320px-Snowpeas.jpg",
    "bohnen":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Broad_beans_-_ripe.jpg/320px-Broad_beans_-_ripe.jpg",
    "ackerbohnen": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Broad_beans_-_ripe.jpg/320px-Broad_beans_-_ripe.jpg",
    # Futtermittel
    "kraftfutter":    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Pellet_mill_feed_pellets.jpg/320px-Pellet_mill_feed_pellets.jpg",
    "futtermittel":   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Pellet_mill_feed_pellets.jpg/320px-Pellet_mill_feed_pellets.jpg",
    "rinderfutter":   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Pellet_mill_feed_pellets.jpg/320px-Pellet_mill_feed_pellets.jpg",
    "schweinefutter": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Pellet_mill_feed_pellets.jpg/320px-Pellet_mill_feed_pellets.jpg",
    "geflügelfutter": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Pellet_mill_feed_pellets.jpg/320px-Pellet_mill_feed_pellets.jpg",
    "stroh":       "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Straw_bales_in_a_field.jpg/320px-Straw_bales_in_a_field.jpg",
    "heu":         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Straw_bales_in_a_field.jpg/320px-Straw_bales_in_a_field.jpg",
    # Düngemittel
    "düngemittel":  "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Fertilizer_urea.jpg/320px-Fertilizer_urea.jpg",
    "kalkammon":    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Fertilizer_urea.jpg/320px-Fertilizer_urea.jpg",
    "harnstoff":    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Fertilizer_urea.jpg/320px-Fertilizer_urea.jpg",
    "kalk":         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Limestone_quarry.jpg/320px-Limestone_quarry.jpg",
    "kalkung":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Limestone_quarry.jpg/320px-Limestone_quarry.jpg",
    # Saatgut
    "saatgut":     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Grains_of_wheat.jpg/320px-Grains_of_wheat.jpg",
    "saat":        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Grains_of_wheat.jpg/320px-Grains_of_wheat.jpg",
    # Pflanzenschutz
    "pflanzenschutzmittel": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Spraying_crops.jpg/320px-Spraying_crops.jpg",
    "herbizid":    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Spraying_crops.jpg/320px-Spraying_crops.jpg",
    "fungizid":    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Spraying_crops.jpg/320px-Spraying_crops.jpg",
    "insektizid":  "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Spraying_crops.jpg/320px-Spraying_crops.jpg",
    # Garten / Haus
    "erde":        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Topsoil_mound.jpg/320px-Topsoil_mound.jpg",
    "blumenerde":  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Topsoil_mound.jpg/320px-Topsoil_mound.jpg",
    "substrate":   "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Topsoil_mound.jpg/320px-Topsoil_mound.jpg",
}


def _normalize(name: str) -> str:
    """Lowercase, strip special chars for keyword matching."""
    return re.sub(r"[^a-zäöüß\s]", "", name.lower()).strip()


def _lookup_category(name: str) -> Optional[str]:
    """Match article name against known category keywords."""
    normalized = _normalize(name)
    for keyword, url in CATEGORY_IMAGE_MAP.items():
        if keyword in normalized:
            return url
    return None


async def fetch_open_food_facts(ean: str) -> Optional[str]:
    """Query Open Food Facts API for product image by EAN."""
    if not ean or len(ean) < 8:
        return None
    url = f"https://world.openfoodfacts.org/api/v2/product/{ean}?fields=image_front_small_url,image_url"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers={"User-Agent": "VALEO-NeuroERP/3.0 image-enrichment"})
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("status") != 1:
                return None
            product = data.get("product", {})
            return product.get("image_front_small_url") or product.get("image_url")
    except Exception as exc:
        logger.debug("Open Food Facts lookup failed for EAN %s: %s", ean, exc)
        return None


async def fetch_wikipedia_image(name: str) -> Optional[str]:
    """Search German Wikipedia for the article name and return first thumbnail."""
    search_term = name.split()[0] if name else ""  # first word usually best
    if len(search_term) < 3:
        return None
    url = (
        "https://de.wikipedia.org/w/api.php"
        "?action=query&generator=search&gsrsearch={q}"
        "&prop=pageimages&piprop=thumbnail&pithumbsize=300"
        "&format=json&origin=*&gsrlimit=1"
    ).format(q=httpx.QueryParams({"q": search_term})["q"])
    # Build properly
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_term,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": "300",
        "format": "json",
        "gsrlimit": "1",
    }
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                "https://de.wikipedia.org/w/api.php",
                params=params,
                headers={"User-Agent": "VALEO-NeuroERP/3.0 image-enrichment"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                thumb = page.get("thumbnail", {}).get("source")
                if thumb:
                    return thumb
        return None
    except Exception as exc:
        logger.debug("Wikipedia lookup failed for '%s': %s", search_term, exc)
        return None


async def resolve_image_for_article(
    name: str,
    ean: Optional[str] = None,
    *,
    use_wikipedia: bool = True,
) -> Optional[str]:
    """
    Try to find an image URL for an article.
    Priority: category mapping → Open Food Facts (EAN) → Wikipedia (name)
    Returns None if nothing found.
    """
    # 1. Category keyword mapping (instant, no network)
    cat_url = _lookup_category(name)
    if cat_url:
        return cat_url

    # 2. Open Food Facts by EAN
    if ean:
        off_url = await fetch_open_food_facts(ean)
        if off_url:
            return off_url

    # 3. Wikipedia by name
    if use_wikipedia:
        wiki_url = await fetch_wikipedia_image(name)
        if wiki_url:
            return wiki_url

    return None


async def enrich_articles_batch(
    articles: list[dict],
    *,
    delay_s: float = 0.3,
    use_wikipedia: bool = True,
) -> dict[str, Optional[str]]:
    """
    Enrich a batch of articles with image URLs.
    articles: list of dicts with at least {"id", "name"} and optionally {"ean", "barcode"}
    Returns: dict mapping article_id → image_url (or None if not found)
    """
    results: dict[str, Optional[str]] = {}
    for art in articles:
        art_id = art["id"]
        name = art.get("name") or art.get("bezeichnung") or ""
        ean = art.get("ean_code") or art.get("barcode") or art.get("ean")
        url = await resolve_image_for_article(name, ean, use_wikipedia=use_wikipedia)
        results[art_id] = url
        if delay_s > 0:
            await asyncio.sleep(delay_s)
    return results
