"""
Numbering Service (PostgreSQL)
Automatische Belegnummern-Generierung mit PostgreSQL-Persistenz
Multi-Tenant & Jahreswechsel-Support
"""

from __future__ import annotations
import os
import logging
from datetime import datetime
from typing import Annotated
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database_pg import get_db

logger = logging.getLogger(__name__)


class NumberingServicePG:
    """PostgreSQL-basierter Nummernkreis-Service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def next_number(
        self,
        domain: str,
        tenant_id: str = "default",
        year: int | None = None,
    ) -> str:
        """
        Generiert nächste Belegnummer (thread-safe via PostgreSQL-Lock)
        
        Args:
            domain: Belegtyp (z.B. "sales_order", "invoice")
            tenant_id: Mandanten-ID (für Multi-Tenant)
            year: Jahr (für Jahreswechsel, None = kein Jahreswechsel)
        
        Returns:
            Formatierte Belegnummer (z.B. "SO-2025-00001")
        """
        # Hole Konfiguration aus ENV
        prefix = self._get_prefix(domain, tenant_id, year)
        width = int(os.environ.get(f"NUMBER_WIDTH_{domain.upper()}", "5"))
        
        # Hole oder erstelle Nummernkreis (mit Row-Level-Lock)
        result = await self.db.execute(
            text("""
                SELECT counter FROM number_series
                WHERE domain = :domain
                  AND tenant_id = :tenant_id
                  AND (year = :year OR (:year IS NULL AND year IS NULL))
                FOR UPDATE
            """),
            {"domain": domain, "tenant_id": tenant_id, "year": year}
        )
        
        row = result.fetchone()
        
        if row is None:
            # Erstelle neuen Nummernkreis
            counter = 1
            await self.db.execute(
                text("""
                    INSERT INTO number_series (domain, tenant_id, year, prefix, counter, width)
                    VALUES (:domain, :tenant_id, :year, :prefix, :counter, :width)
                """),
                {
                    "domain": domain,
                    "tenant_id": tenant_id,
                    "year": year,
                    "prefix": prefix,
                    "counter": counter,
                    "width": width,
                }
            )
        else:
            # Incrementiere Counter
            counter = row[0] + 1
            await self.db.execute(
                text("""
                    UPDATE number_series
                    SET counter = :counter
                    WHERE domain = :domain
                      AND tenant_id = :tenant_id
                      AND (year = :year OR (:year IS NULL AND year IS NULL))
                """),
                {"domain": domain, "tenant_id": tenant_id, "year": year, "counter": counter}
            )
        
        await self.db.commit()
        
        # Formatiere Nummer
        number = f"{prefix}{counter:0{width}d}"
        logger.info(f"Generated number: {number} for {domain}/{tenant_id}/{year}")
        
        return number

    async def peek(
        self,
        domain: str,
        tenant_id: str = "default",
        year: int | None = None,
    ) -> str:
        """
        Gibt nächste Nummer zurück ohne zu incrementieren
        """
        prefix = self._get_prefix(domain, tenant_id, year)
        width = int(os.environ.get(f"NUMBER_WIDTH_{domain.upper()}", "5"))
        
        result = await self.db.execute(
            text("""
                SELECT counter FROM number_series
                WHERE domain = :domain
                  AND tenant_id = :tenant_id
                  AND (year = :year OR (:year IS NULL AND year IS NULL))
            """),
            {"domain": domain, "tenant_id": tenant_id, "year": year}
        )
        
        row = result.fetchone()
        counter = row[0] + 1 if row else 1
        
        return f"{prefix}{counter:0{width}d}"

    async def reset(
        self,
        domain: str,
        tenant_id: str = "default",
        year: int | None = None,
    ) -> None:
        """
        Setzt Nummernkreis zurück (nur für Admin/Testing)
        """
        await self.db.execute(
            text("""
                UPDATE number_series
                SET counter = 0
                WHERE domain = :domain
                  AND tenant_id = :tenant_id
                  AND (year = :year OR (:year IS NULL AND year IS NULL))
            """),
            {"domain": domain, "tenant_id": tenant_id, "year": year}
        )
        await self.db.commit()
        logger.warning(f"Reset number series: {domain}/{tenant_id}/{year}")

    def _get_prefix(self, domain: str, tenant_id: str, year: int | None) -> str:
        """
        Generiert Präfix basierend auf Konfiguration
        
        Beispiele:
        - Ohne Tenant/Jahr: "SO-"
        - Mit Tenant: "SO-A-"
        - Mit Jahr: "SO-2025-"
        - Mit Tenant+Jahr: "SO-A-2025-"
        """
        # Base-Prefix aus ENV
        base = os.environ.get(f"NUMBER_PREFIX_{domain.upper()}", f"{domain.upper()}-")
        
        # Multi-Tenant aktiviert?
        multi_tenant = os.environ.get("NUMBERING_MULTI_TENANT", "false").lower() == "true"
        
        # Jahreswechsel aktiviert?
        yearly_reset = os.environ.get("NUMBERING_YEARLY_RESET", "false").lower() == "true"
        
        # Baue Präfix zusammen
        parts = [base.rstrip("-")]
        
        if multi_tenant and tenant_id != "default":
            parts.append(tenant_id)
        
        if yearly_reset and year:
            parts.append(str(year))
        
        return "-".join(parts) + "-"


# Dependency für FastAPI
async def get_numbering_pg(db: Annotated[AsyncSession, Depends(get_db)]) -> NumberingServicePG:
    """FastAPI Dependency für NumberingServicePG"""
    return NumberingServicePG(db)

