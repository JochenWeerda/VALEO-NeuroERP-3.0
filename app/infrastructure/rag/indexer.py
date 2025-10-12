"""
RAG Indexer
Indexes domain entities into vector store
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from ...infrastructure.models import Article, Customer
from ...domains.shared.domain_events import ArticleCreated, CustomerCreated
from .vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RAGIndexer:
    """Indexes domain entities for semantic search."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
    
    async def index_articles(self, db: Session, tenant_id: str) -> int:
        """
        Index all articles from database.
        
        Returns:
            Number of articles indexed
        """
        articles = db.query(Article).filter(
            Article.tenant_id == tenant_id,
            Article.is_active == True  # noqa: E712
        ).all()
        
        if not articles:
            logger.info("No articles to index")
            return 0
        
        documents = []
        metadatas = []
        ids = []
        
        for article in articles:
            # Combine name and description for better search
            text = f"{article.name}"
            if article.description:
                text += f" - {article.description}"
            
            documents.append(text)
            metadatas.append({
                "article_number": article.article_number,
                "name": article.name,
                "category": article.category or "",
                "price": float(article.price),
                "stock_quantity": article.stock_quantity,
                "tenant_id": tenant_id
            })
            ids.append(article.id)
        
        await self.vector_store.add_documents(
            collection_name="articles",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Indexed {len(articles)} articles")
        return len(articles)
    
    async def index_single_article(self, article: Article) -> None:
        """Index a single article (triggered by ArticleCreated event)."""
        text = f"{article.name}"
        if article.description:
            text += f" - {article.description}"
        
        await self.vector_store.add_documents(
            collection_name="articles",
            documents=[text],
            metadatas=[{
                "article_number": article.article_number,
                "name": article.name,
                "category": article.category or "",
                "price": float(article.price),
                "stock_quantity": article.stock_quantity,
                "tenant_id": article.tenant_id
            }],
            ids=[article.id]
        )
        
        logger.info(f"Indexed article: {article.article_number}")
    
    async def index_customers(self, db: Session, tenant_id: str) -> int:
        """
        Index all customers from database.
        
        Returns:
            Number of customers indexed
        """
        customers = db.query(Customer).filter(
            Customer.tenant_id == tenant_id,
            Customer.is_active == True  # noqa: E712
        ).all()
        
        if not customers:
            logger.info("No customers to index")
            return 0
        
        documents = []
        metadatas = []
        ids = []
        
        for customer in customers:
            # Combine relevant fields
            text = f"{customer.name}"
            if customer.address:
                text += f" - {customer.address}"
            
            documents.append(text)
            metadatas.append({
                "customer_number": customer.customer_number,
                "name": customer.name,
                "email": customer.email or "",
                "phone": customer.phone or "",
                "tenant_id": tenant_id
            })
            ids.append(customer.id)
        
        await self.vector_store.add_documents(
            collection_name="customers",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Indexed {len(customers)} customers")
        return len(customers)
    
    async def on_article_created(self, event: ArticleCreated, db: Session) -> None:
        """Event handler: Re-index when article is created."""
        logger.info(f"Auto-indexing article: {event.article_number}")
        
        article = db.query(Article).filter(Article.id == event.aggregate_id).first()
        if article:
            await self.index_single_article(article)
    
    async def on_customer_created(self, event: CustomerCreated, db: Session) -> None:
        """Event handler: Re-index when customer is created."""
        logger.info(f"Auto-indexing customer: {event.customer_number}")
        
        customer = db.query(Customer).filter(Customer.id == event.aggregate_id).first()
        if customer:
            text = f"{customer.name}"
            if customer.address:
                text += f" - {customer.address}"
            
            await self.vector_store.add_documents(
                collection_name="customers",
                documents=[text],
                metadatas=[{
                    "customer_number": customer.customer_number,
                    "name": customer.name,
                    "email": customer.email or "",
                    "phone": customer.phone or "",
                    "tenant_id": customer.tenant_id
                }],
                ids=[customer.id]
            )


# Global instance
_indexer: Optional[RAGIndexer] = None


def get_indexer() -> RAGIndexer:
    """Get the global RAG indexer instance."""
    global _indexer
    if _indexer is None:
        _indexer = RAGIndexer()
    return _indexer

