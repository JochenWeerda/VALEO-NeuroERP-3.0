"""
Seed script for Price Adjustment Rules.
Creates example rules for HL-weight, impurities, and mycotoxin adjustments.
"""

import os
import sys
from pathlib import Path
from datetime import date, datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.uuid7 import uuid7
from app.core.config import settings
from app.infrastructure.models import PriceAdjustmentRule


def seed_price_adjustment_rules():
    """
    Seed example price adjustment rules.
    
    Erstellt Beispiel-Regeln für:
    - HL-Gewicht Anpassungen
    - Besatz (Impurities) Anpassungen
    - Mykotoxin Anpassungen
    """
    db: Session = SessionLocal()
    tenant_id = os.environ.get("TENANT_ID") or getattr(settings, "DEFAULT_TENANT_ID", "default")

    try:
        # Beispiel: HL-Gewicht Anpassung für Hafer
        # Regel: Zuschlag/Abschlag je 0,10 kg/hl über/unter Basis
        hl_weight_rule = PriceAdjustmentRule(
            id=uuid7(),
            tenant_id=tenant_id,
            article_id=None,  # Allgemein für Warengruppe
            warengruppe="HAFER",
            adjustment_type="hl_weight",
            parameter_name="hl_weight_kg_per_hl",
            method="factor",
            steps={
                "base_value": 50.0,  # Basis-HL-Gewicht (kg/hl)
                "base_factor": 1.0,
                "factor_per_unit": 2.5,  # EUR/t je 0.1 kg/hl über Basis
            },
            effective_from=date(2024, 1, 1),
            effective_to=None,
            created_at=datetime.utcnow(),
            created_by="system",
        )
        db.add(hl_weight_rule)
        
        # Beispiel: Besatz (Impurities) Anpassung für Raps
        # Regel: "2% frei", darüber gestaffelte Preisabzüge
        impurity_rule_raps = PriceAdjustmentRule(
            id=uuid7(),
            tenant_id=tenant_id,
            article_id=None,
            warengruppe="RAPS",
            adjustment_type="impurity",
            parameter_name="impurity_pct",
            method="table",
            steps=[
                {
                    "from": 0.0,
                    "to": 2.0,
                    "adjustment_eur_per_ton": 0.0,
                    "adjustment_pct": 0.0,
                },
                {
                    "from": 2.0,
                    "to": 3.0,
                    "adjustment_eur_per_ton": -5.0,  # 5 EUR/t Abzug
                    "adjustment_pct": None,
                },
                {
                    "from": 3.0,
                    "to": 4.0,
                    "adjustment_eur_per_ton": -10.0,  # 10 EUR/t Abzug
                    "adjustment_pct": None,
                },
                {
                    "from": 4.0,
                    "to": 100.0,
                    "adjustment_eur_per_ton": -20.0,  # 20 EUR/t Abzug
                    "adjustment_pct": None,
                },
            ],
            effective_from=date(2024, 1, 1),
            effective_to=None,
            created_at=datetime.utcnow(),
            created_by="system",
        )
        db.add(impurity_rule_raps)
        
        # Beispiel: Besatz (Impurities) Anpassung für Getreide (allgemein)
        # Regel: Mengenabzug 1:1 (Besatz wirkt direkt als Mengenabzug)
        impurity_rule_getreide = PriceAdjustmentRule(
            id=uuid7(),
            tenant_id=tenant_id,
            article_id=None,
            warengruppe=None,  # Allgemein für alle Getreide
            adjustment_type="impurity",
            parameter_name="impurity_pct",
            method="percentage",
            steps={
                "base_pct": 0.0,
                "pct_per_unit": -1.0,  # -1% Preis je 1% Besatz
            },
            effective_from=date(2024, 1, 1),
            effective_to=None,
            created_at=datetime.utcnow(),
            created_by="system",
        )
        db.add(impurity_rule_getreide)
        
        # Beispiel: Mykotoxin Anpassung
        # Regel: Abzug ab bestimmten Grenzwerten
        mycotoxin_rule = PriceAdjustmentRule(
            id=uuid7(),
            tenant_id=tenant_id,
            article_id=None,
            warengruppe=None,  # Allgemein
            adjustment_type="mycotoxin",
            parameter_name="mycotoxin_ppb",
            method="table",
            steps=[
                {
                    "from": 0.0,
                    "to": 1250.0,  # Grenzwert (ppb)
                    "adjustment_eur_per_ton": 0.0,
                    "adjustment_pct": 0.0,
                },
                {
                    "from": 1250.0,
                    "to": 2000.0,
                    "adjustment_eur_per_ton": -10.0,  # 10 EUR/t Abzug
                    "adjustment_pct": None,
                },
                {
                    "from": 2000.0,
                    "to": 10000.0,
                    "adjustment_eur_per_ton": -50.0,  # 50 EUR/t Abzug
                    "adjustment_pct": None,
                },
            ],
            effective_from=date(2024, 1, 1),
            effective_to=None,
            created_at=datetime.utcnow(),
            created_by="system",
        )
        db.add(mycotoxin_rule)
        
        db.commit()
        print("✅ Price adjustment rules seeded successfully")
        
    except Exception as e:
        print(f"❌ Error seeding price adjustment rules: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_price_adjustment_rules()

