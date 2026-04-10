"""
RAG Indexer
Indexes domain entities into vector store.

Indexed collections:
  - articles: Artikel-Stammdaten
  - customers: Kunden-Stammdaten
  - contracts: Einkaufs- und Verkaufskontrakte
  - feed: Futtermittel (Einzelfutter + Rezepte)
  - knowledge: Wissensbasis-Einträge
  - documents: DMS-Dokument-Metadaten
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.models import Article, Customer
from app.domains.shared.domain_events import ArticleCreated, CustomerCreated
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

    async def index_contracts(self, db: Session, tenant_id: str) -> int:
        """Index Einkaufs-Kontrakte for semantic search."""
        try:
            from app.infrastructure.models.einkauf_models import EinkaufKontrakt
        except ImportError:
            logger.debug("EinkaufKontrakt model not available — skipping contract indexing")
            return 0

        contracts = db.query(EinkaufKontrakt).filter(
            EinkaufKontrakt.tenant_id == tenant_id,
        ).all()

        if not contracts:
            return 0

        documents, metadatas, ids = [], [], []
        for c in contracts:
            text = f"Kontrakt {getattr(c, 'kontraktnummer', c.id)}"
            if hasattr(c, 'artikel_bezeichnung') and c.artikel_bezeichnung:
                text += f" — {c.artikel_bezeichnung}"
            if hasattr(c, 'lieferant_name') and c.lieferant_name:
                text += f" Lieferant: {c.lieferant_name}"
            if hasattr(c, 'menge') and c.menge:
                text += f" Menge: {c.menge}"

            documents.append(text)
            metadatas.append({
                "kontraktnummer": getattr(c, "kontraktnummer", ""),
                "status": getattr(c, "status", ""),
                "tenant_id": tenant_id,
                "type": "einkauf_kontrakt",
            })
            ids.append(c.id)

        await self.vector_store.add_documents(
            collection_name="contracts",
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info("Indexed %d contracts", len(contracts))
        return len(contracts)

    async def index_feed(self, db: Session, tenant_id: str) -> int:
        """Index Futtermittel (Einzelfutter + Rezepte) for semantic search."""
        try:
            from app.infrastructure.models.futtermittel_models import (
                Einzelfuttermittel, FuttermittelRezept,
            )
        except ImportError:
            logger.debug("Futtermittel models not available — skipping feed indexing")
            return 0

        total = 0

        # Einzelfuttermittel
        items = db.query(Einzelfuttermittel).filter(
            Einzelfuttermittel.tenant_id == tenant_id,
            Einzelfuttermittel.aktiv.is_(True),
        ).all()
        if items:
            documents, metadatas, ids = [], [], []
            for ef in items:
                text = f"{ef.name} ({ef.art})"
                if ef.herkunft:
                    text += f" Herkunft: {ef.herkunft}"
                if ef.protein:
                    text += f" Protein: {ef.protein}%"
                if ef.gvo_status:
                    text += f" GVO: {ef.gvo_status}"
                documents.append(text)
                metadatas.append({
                    "artikel_nummer": ef.artikel_nummer,
                    "art": ef.art,
                    "tenant_id": tenant_id,
                    "type": "einzelfutter",
                })
                ids.append(ef.id)
            await self.vector_store.add_documents(
                collection_name="feed",
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            total += len(items)

        # Rezepte
        rezepte = db.query(FuttermittelRezept).filter(
            FuttermittelRezept.tenant_id == tenant_id,
            FuttermittelRezept.aktiv.is_(True),
        ).all()
        if rezepte:
            documents, metadatas, ids = [], [], []
            for r in rezepte:
                text = f"Rezept: {r.name} für {r.tierart}"
                if r.protein_ziel:
                    text += f" Protein-Ziel: {r.protein_ziel}%"
                if r.bemerkung:
                    text += f" — {r.bemerkung}"
                documents.append(text)
                metadatas.append({
                    "rezept_code": r.rezept_code,
                    "tierart": r.tierart,
                    "tenant_id": tenant_id,
                    "type": "rezept",
                })
                ids.append(r.id)
            await self.vector_store.add_documents(
                collection_name="feed",
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            total += len(rezepte)

        if total:
            logger.info("Indexed %d feed items", total)
        return total

    async def index_knowledge(self, db: Session, tenant_id: str) -> int:
        """Index Knowledge Store entries for RAG retrieval."""
        from sqlalchemy import text as sql_text

        try:
            rows = db.execute(sql_text(
                "SELECT id, title, body, category, tags "
                "FROM domain_shared.knowledge_entries "
                "WHERE tenant_id = :tid AND status = 'published'"
            ), {"tid": tenant_id}).fetchall()
        except Exception:
            logger.debug("knowledge_entries table not available — skipping")
            return 0

        if not rows:
            return 0

        documents, metadatas, ids = [], [], []
        for row in rows:
            text = f"{row.title}"
            if row.body:
                # Truncate body for embedding (first 500 chars)
                text += f" — {row.body[:500]}"
            documents.append(text)
            metadatas.append({
                "category": row.category or "",
                "tags": row.tags or "",
                "tenant_id": tenant_id,
                "type": "knowledge",
            })
            ids.append(row.id)

        await self.vector_store.add_documents(
            collection_name="knowledge",
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info("Indexed %d knowledge entries", len(rows))
        return len(rows)

    async def index_all(self, db: Session, tenant_id: str) -> dict[str, int]:
        """Index all entity types for a tenant. Returns counts per collection."""
        counts = {}
        counts["articles"] = await self.index_articles(db, tenant_id)
        counts["customers"] = await self.index_customers(db, tenant_id)
        counts["contracts"] = await self.index_contracts(db, tenant_id)
        counts["feed"] = await self.index_feed(db, tenant_id)
        counts["knowledge"] = await self.index_knowledge(db, tenant_id)
        logger.info("Full RAG index for tenant %s: %s", tenant_id, counts)
        return counts


# Global instance
_indexer: Optional[RAGIndexer] = None


def get_indexer() -> RAGIndexer:
    """Get the global RAG indexer instance."""
    global _indexer
    if _indexer is None:
        _indexer = RAGIndexer()
    return _indexer

