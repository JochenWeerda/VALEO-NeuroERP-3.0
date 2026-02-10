"""
Prospecting API Endpoints
Lead-Candidates basierend auf GAP-Daten und Customer-Potential-Snapshots
"""

from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/prospecting", tags=["prospecting", "leads"])


@router.get("/lead-candidates")
async def get_lead_candidates(
    ref_year: int = Query(..., description="Referenzjahr"),
    min_potential: Optional[float] = Query(None, description="Mindestpotenzial in EUR"),
    # region parameter removed in favor of zip_code range
    zip_code_start: Optional[str] = Query(None, description="PLZ-Bereich Start (z.B. 26000)"),
    zip_code_end: Optional[str] = Query(None, description="PLZ-Bereich Ende (z.B. 26999)"),
    source: Optional[str] = Query(None, description="Quelle (gap_de, cap_eu, etc.)"),
    segment: Optional[str] = Query(None, description="Segment (A, B, C)"),
    only_new_prospects: Optional[bool] = Query(False, description="Nur neue Prospekte (keine bestehenden Kunden)"),
    only_high_priority: Optional[bool] = Query(False, description="Nur hohe Priorität"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximale Anzahl Ergebnisse")
):
    """
    Gibt Lead-Candidates basierend auf GAP-Daten und Customer-Potential-Snapshots zurück.
    
    Die Daten kommen aus:
    - customer_potential_snapshot (für Potenzial-Daten)
    - gap_customer_match (für Matching-Info)
    - customers (um zu prüfen, ob bereits Kunde)
    """
    db = next(get_db())
    
    try:
        # Prüfe zuerst, ob Snapshot-Daten vorhanden sind
        snapshot_count = db.execute(
            text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :ref_year"),
            {"ref_year": ref_year}
        ).scalar() or 0
        
        if snapshot_count > 0:
            # Verwende Snapshot-Daten (ursprüngliche Logik)
            query = """
                SELECT DISTINCT
                    s.ref_year,
                    'gap_de'::text AS source_system,
                    
                    COALESCE(c.name, m.beneficiary_name_norm, 'Unbekannt') AS prospect_name,
                    COALESCE(c.postal_code, m.postal_code, '') AS postal_code,
                    COALESCE(c.city, m.city, '') AS city,
                    
                    s.gap_estimated_area_ha AS estimated_area_ha,
                    s.potential_total_eur AS estimated_potential_eur,
                    s.segment,
                    COALESCE(m.postal_code, '') AS region_cluster,
                    
                    CASE
                        WHEN s.segment = 'A' THEN 'high'::text
                        WHEN s.segment = 'B' THEN 'medium'::text
                        ELSE 'low'::text
                    END AS lead_priority,
                    
                    (c.id IS NOT NULL) AS is_existing_customer,
                    c.id::text AS matched_customer_id,
                    
                    COALESCE(c.analytics_is_core_customer, FALSE) AS is_core_customer,
                    COALESCE(c.analytics_block_auto_potential_update, FALSE) AS is_locked_by_sales,
                    
                    FALSE AS has_bio,
                    FALSE AS has_qs,
                    FALSE AS has_qm_milk,
                    
                    NULL::text AS suggested_owner_id
                    
                FROM customer_potential_snapshot s
                LEFT JOIN gap_customer_match m ON m.customer_id = s.customer_id AND m.ref_year = s.ref_year
                LEFT JOIN customers c ON c.id = s.customer_id
                WHERE s.ref_year = :ref_year
            """
        else:
            # 🔍 KRUMMHÖRN-TEST: Spezielle Analyse für Spaltenverschiebungs-Diagnose
            print(f"[DEBUG KRUMMHÖRN] Suche nach PLZ 26736 und Krummhörn...")
            
            # Test-Query für Krummhörn
            krummhoern_check = db.execute(text("""
                SELECT 
                    beneficiary_name_norm, postal_code, city, direct_total_eur
                FROM gap_payments_direct_agg 
                WHERE postal_code = '26736' OR UPPER(city) LIKE '%KRUMM%'
                LIMIT 5
            """))
            
            krummhoern_results = krummhoern_check.fetchall()
            print(f"[DEBUG KRUMMHÖRN] Gefunden {len(krummhoern_results)} Ergebnisse für PLZ 26736/Krummhörn")
            for i, row in enumerate(krummhoern_results):
                print(f"[DEBUG KRUMMHÖRN {i+1}] Name: {row[0]}, PLZ: {row[1]}, Ort: {row[2]}, Betrag: {row[3]}")
            
            # PLZ-Verteilung in 267xx Bereich prüfen
            plz_267_check = db.execute(text("""
                SELECT postal_code, COUNT(*) as count
                FROM gap_payments_direct_agg 
                WHERE postal_code LIKE '267%'
                GROUP BY postal_code
                ORDER BY postal_code
                LIMIT 10
            """))
            
            plz_267_results = plz_267_check.fetchall()
            print(f"[DEBUG PLZ 267xx] Gefunden {len(plz_267_results)} verschiedene PLZ im 267xx Bereich:")
            for row in plz_267_results:
                print(f"[DEBUG PLZ 267xx] PLZ {row[0]}: {row[1]} Einträge")
                
            # ECHTE GAP-DATEN mit korrekter Spalten-Reihenfolge
            query = """
                SELECT 
                    g.ref_year,                                                    -- row[0]
                    'gap_de' AS source_system,                                     -- row[1] 
                    COALESCE(g.beneficiary_name_norm, 'Unbekannt') AS prospect_name, -- row[2]
                    COALESCE(g.postal_code, '') AS postal_code,                    -- row[3]
                    COALESCE(g.city, 'Unbekannt') AS city,                         -- row[4]
                    COALESCE(g.direct_total_eur / 270.0, 0) AS estimated_area_ha, -- row[5]
                    COALESCE(g.direct_total_eur * 1.037, 0) AS estimated_potential_eur, -- row[6]
                    'B' AS segment,                                                -- row[7]
                    COALESCE(g.postal_code, '') AS region_cluster,                 -- row[8]
                    'medium' AS lead_priority,                                     -- row[9]
                    false AS is_existing_customer,                                 -- row[10]
                    '' AS matched_customer_id,                                     -- row[11]
                    false AS is_core_customer,                                     -- row[12]
                    false AS is_locked_by_sales,                                   -- row[13]
                    false AS has_bio,                                              -- row[14]
                    false AS has_qs,                                               -- row[15]
                    false AS has_qm_milk,                                          -- row[16]
                    '' AS suggested_owner_id                                       -- row[17]
                FROM gap_payments_direct_agg g
                WHERE g.ref_year = :ref_year
            """
        
        params = {"ref_year": ref_year}
        
        # Filter für GAP-direkt-basierte Query mit korrigierter Spalten-Reihenfolge
        if only_new_prospects:
            # Alle GAP-Daten sind per Definition neue Prospekte (da keine Matches)
            pass
        
        if min_potential is not None:
            # Berechnung: (direct_total_eur * 1.037) >= min_potential
            estimated_potential_threshold = min_potential / 1.037  # Rückrechnung
            query += " AND g.direct_total_eur >= :min_potential_threshold"
            params["min_potential_threshold"] = estimated_potential_threshold
        
        if segment:
            # Vereinfachte Segment-Filter
            if segment == 'A':
                query += " AND g.direct_total_eur >= 10000"
            elif segment == 'C':
                query += " AND g.direct_total_eur < 5000"
            # Segment 'B' wird nicht gefiltert (Standard)
        
        if zip_code_start and zip_code_end:
            query += " AND g.postal_code >= :zip_start AND g.postal_code <= :zip_end"
            params["zip_start"] = zip_code_start
            params["zip_end"] = zip_code_end
        elif zip_code_start:
            query += " AND g.postal_code >= :zip_start"
            params["zip_start"] = zip_code_start
        
        if only_high_priority:
            query += " AND g.direct_total_eur >= 10000"
        
        # Sortierung nach Potenzial
        query += """
            ORDER BY 
                g.direct_total_eur DESC
        """
        
        # Limit
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        # Führe Query aus
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        # Konvertiere zu Dict-Liste
        candidates = []
        for row in rows:
            candidate = {
                "ref_year": row[0],
                "source_system": row[1],
                "prospect_name": row[2] or "Unbekannt",
                "postal_code": row[3] or "",
                "city": row[4] or "",
                "estimated_area_ha": float(row[5]) if row[5] else None,
                "estimated_potential_eur": float(row[6]) if row[6] else None,
                "segment": row[7],
                "region_cluster": row[8] or None,
                "lead_priority": row[9] or "low",
                "is_existing_customer": bool(row[10]),
                "matched_customer_id": row[11],
                "is_core_customer": bool(row[12]),
                "is_locked_by_sales": bool(row[13]),
                "has_bio": bool(row[14]),
                "has_qs": bool(row[15]),
                "has_qm_milk": bool(row[16]),
                "suggested_owner_id": row[17],
                # Debug-Information
                "_debug_data_source": "snapshots" if snapshot_count > 0 else "gap_direct",
                "_debug_snapshot_count": snapshot_count
            }
            candidates.append(candidate)
        
        return candidates
    
    except Exception as e:
        import traceback
        error_detail = f"Fehler beim Abrufen der Lead-Candidates: {str(e)}\n{traceback.format_exc()}"
        print(f"[PROSPECTING ERROR] {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen der Lead-Candidates: {str(e)}"
        )
    finally:
        db.close()

