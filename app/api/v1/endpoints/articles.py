"""
Inventory Articles management endpoints
"""

from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()


@router.get("/")
async def get_articles():
    """Get all articles"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, article_number, name, unit, category, sales_price, current_stock, is_active FROM inventory_articles")
        articles = cursor.fetchall()

        result = []
        for article in articles:
            result.append({
                "id": article[0],
                "article_number": article[1],
                "name": article[2],
                "unit": article[3],
                "category": article[4],
                "sales_price": article[5],
                "current_stock": article[6],
                "is_active": bool(article[7])
            })

        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{article_id}")
async def get_article(article_id: str):
    """Get article by ID"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, article_number, name, unit, category, sales_price, current_stock, is_active FROM inventory_articles WHERE id = ?", (article_id,))
        article = cursor.fetchone()

        conn.close()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "id": article[0],
            "article_number": article[1],
            "name": article[2],
            "unit": article[3],
            "category": article[4],
            "sales_price": article[5],
            "current_stock": article[6],
            "is_active": bool(article[7])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")