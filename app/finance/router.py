"""
Finance Router
Finance-Endpunkte: Nebenbuch-Abstimmung und GoBD (Verfahrensdokumentation, Aufbewahrung, Loeschsperren)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from app.core.uuid7 import uuid7

from app.auth.deps import get_current_user, get_tenant_id
from app.core.database import get_db
from app.finance.schemas import NebenbuchAbstimmungCreate, NebenbuchAbstimmungResponse
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router = APIRouter(prefix="/finance", tags=["Finance Advanced"])


# Wechselkurse, Buchungsschemata, Kostenstellen, Abschlusschecklisten und Intercompany standen bis 23.11.2026 hier
# auf Tabellen, die keine Migration anlegt (nur in der gewachsenen Datenbank). Fuehrend sind /api/v1/exchange-rates,
# /api/v1/booking-templates, /api/v1/kostenrechnung und /api/v1/closing-checklists; Intercompany hatte keinen Nutzer.

# ============================================================================
# NEBENBUCH-ABSTIMMUNG
# ============================================================================

@router.get("/abstimmung/nebenbuch", response_model=List[NebenbuchAbstimmungResponse])
async def list_abstimmungen(
    tenant_id: str = Depends(get_tenant_id),
    periode: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Nebenbuch-Abstimmungen"""
    from app.finance.models import NebenbuchAbstimmung
    from sqlalchemy import select
    
    query = select(NebenbuchAbstimmung).where(NebenbuchAbstimmung.tenant_id == tenant_id)
    
    if periode:
        query = query.where(NebenbuchAbstimmung.periode == periode)
    if status:
        query = query.where(NebenbuchAbstimmung.status == status)
    
    query = query.order_by(NebenbuchAbstimmung.periode.desc())
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/abstimmung/nebenbuch/{id}", response_model=NebenbuchAbstimmungResponse)
async def get_abstimmung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Abstimmung"""
    from app.finance.models import NebenbuchAbstimmung
    from sqlalchemy import select
    
    result = db.execute(
        select(NebenbuchAbstimmung).where(
            NebenbuchAbstimmung.id == id,
            NebenbuchAbstimmung.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")
    return result


@router.post("/abstimmung/nebenbuch", response_model=NebenbuchAbstimmungResponse, dependencies=SCHREIBEN["FINANZ"])
async def create_abstimmung(
    data: NebenbuchAbstimmungCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Abstimmung"""
    from app.finance.models import NebenbuchAbstimmung
    
    abstimmung = NebenbuchAbstimmung(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        periode=data.abstimmungs_datum.strftime("%Y-%m"),
        status="OFFEN",
        nebenbuch_saldo=0,
        hauptbuch_saldo=0,
        differenz=0,
        nicht_abgestimmte=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(abstimmung)
    db.commit()
    db.refresh(abstimmung)
    return abstimmung


@router.post("/abstimmung/nebenbuch/{id}/ausfuehren", dependencies=SCHREIBEN["FINANZ"])
async def execute_abstimmung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Stimmt beide Nebenbuecher der offenen Posten mit ihrem Sammelkonto im Hauptbuch ab.

    Je Nebenbuch (Debitoren, Kreditoren): offener Betrag aller nicht stornierten Posten in
    ``domain_erp.offene_posten`` gegen den Saldo des Sammelkontos aus dem Kontenrahmen des Mandanten (SKR03
    1400/1600, SKR04 1200/3300) ueber alle gebuchten Journalzeilen (``posted`` und ``reversed``: ein Storno zaehlt
    mit seinem Original), beides zum Ausfuehrungszeitpunkt. ``nebenbuch_saldo``/``hauptbuch_saldo`` sind die
    Nettoposition (Forderungen minus Verbindlichkeiten); ``differenz`` ist die Summe der Betragsabweichungen beider
    Nebenbuecher, damit sich Abweichungen nicht gegenseitig aufheben. Abweichende Nebenbuecher stehen in
    ``nicht_abgestimmte``.

    Bis 23.11.2026 las das Nebenbuch den leeren Altspeicher ``public.offene_posten`` und das Hauptbuch die Summe
    aller Buchungen der Periode (Haben minus Soll - fuer ausgeglichene Buchungen immer null); ein Lesefehler wurde
    still zu 0. So meldete jede Abstimmung "ABGESTIMMT".
    """
    from app.finance.models import NebenbuchAbstimmung as NbModel
    from app.finance.steuerschluessel import DEBITORENKONTO, KREDITORENKONTO, kontenrahmen
    from sqlalchemy import select, text as sqlt

    ab = db.execute(
        select(NbModel).where(NbModel.id == id, NbModel.tenant_id == tenant_id)
    ).scalar_one_or_none()
    if not ab:
        raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")
    rahmen = kontenrahmen(db, tenant_id)
    if rahmen not in DEBITORENKONTO or rahmen not in KREDITORENKONTO:
        raise HTTPException(status_code=409, detail="Kontenrahmen des Mandanten nicht eingerichtet")

    nebenbuecher = []
    # Vorzeichen: Forderungen stehen im Soll, Verbindlichkeiten im Haben.
    for art, konto, vorzeichen in (("debitoren", DEBITORENKONTO[rahmen], 1), ("kreditoren", KREDITORENKONTO[rahmen], -1)):
        nb = round(float(db.execute(sqlt("""
            SELECT COALESCE(SUM(offen), 0) FROM domain_erp.offene_posten
            WHERE tenant_id = :tid AND konto_typ = :typ AND COALESCE(op_status, 'offen') <> 'storniert'
        """), {"tid": tenant_id, "typ": art}).scalar() or 0), 2)
        hb = round(vorzeichen * float(db.execute(sqlt("""
            SELECT COALESCE(SUM(jel.debit_amount - jel.credit_amount), 0)
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON je.id = jel.journal_entry_id AND je.tenant_id = jel.tenant_id
            JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id AND coa.tenant_id = je.tenant_id
            WHERE je.tenant_id = :tid AND je.status IN ('posted', 'reversed') AND coa.account_number = :konto
        """), {"tid": tenant_id, "konto": konto}).scalar() or 0), 2)
        nebenbuecher.append({"nebenbuch": art, "sammelkonto": konto, "nebenbuch_saldo": nb,
                             "hauptbuch_saldo": hb, "differenz": round(nb - hb, 2)})

    debitoren, kreditoren = nebenbuecher
    ab.nebenbuch_saldo = round(debitoren["nebenbuch_saldo"] - kreditoren["nebenbuch_saldo"], 2)
    ab.hauptbuch_saldo = round(debitoren["hauptbuch_saldo"] - kreditoren["hauptbuch_saldo"], 2)
    ab.differenz = round(sum(abs(n["differenz"]) for n in nebenbuecher), 2)
    ab.nicht_abgestimmte = [n for n in nebenbuecher if abs(n["differenz"]) >= 0.01]
    ab.status = "ABWEICHEND" if ab.nicht_abgestimmte else "ABGESTIMMT"
    ab.abgestimmt_durch = str(current_user.get("sub", "system"))
    ab.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Abstimmung ausgeführt",
        "id": id,
        "nebenbuch_saldo": ab.nebenbuch_saldo,
        "hauptbuch_saldo": ab.hauptbuch_saldo,
        "differenz": ab.differenz,
        "status": ab.status,
        "nebenbuecher": nebenbuecher,
    }


# ============================================================================
# GOBD COMPLIANCE - VERFAHRENSDOKUMENTATION
# ============================================================================

@router.get("/gobd/verfahrensdokumentation", response_model=List)
async def list_verfahrensdokumentation(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Verfahrensdokumentation (GoBD §147 AO)"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    query = select(ProcedureDoc).where(ProcedureDoc.tenant_id == tenant_id)
    
    if status:
        query = query.where(ProcedureDoc.status == status)
    
    query = query.order_by(ProcedureDoc.created_at.desc())
    
    result = db.execute(query).scalars().all()
    return [dict(
        id=r.id,
        title=r.title,
        version=r.version,
        status=r.status,
        scope=r.scope,
        software_name=r.software_name,
        software_version=r.software_version,
        released_by=r.released_by,
        released_at=r.released_at.isoformat() if r.released_at else None,
        created_at=r.created_at.isoformat() if r.created_at else None,
    ) for r in result]


@router.get("/gobd/verfahrensdokumentation/{id}")
async def get_verfahrensdokumentation(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole einzelne Verfahrensdokumentation"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    result = db.execute(
        select(ProcedureDoc).where(
            ProcedureDoc.id == id,
            ProcedureDoc.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Verfahrensdokumentation nicht gefunden")
    
    return {
        "id": result.id,
        "title": result.title,
        "version": result.version,
        "status": result.status,
        "scope": result.scope,
        "anwenderbeschreibung": result.anwenderbeschreibung,
        "technische_beschreibung": result.technische_beschreibung,
        "betriebsanleitung": result.betriebsanleitung,
        "pruefwege": result.pruefwege,
        "software_name": result.software_name,
        "software_version": result.software_version,
        "datenbank": result.datenbank,
        "betriebssystem": result.betriebssystem,
        "released_by": result.released_by,
        "released_at": result.released_at.isoformat() if result.released_at else None,
        "created_at": result.created_at.isoformat() if result.created_at else None,
        "updated_at": result.updated_at.isoformat() if result.updated_at else None,
    }


@router.post("/gobd/verfahrensdokumentation", dependencies=SCHREIBEN["FINANZ"])
async def create_verfahrensdokumentation(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Verfahrensdokumentation (GoBD-konform)"""
    from app.finance.models import ProcedureDoc
    
    doc = ProcedureDoc(
        id=uuid7(),
        tenant_id=tenant_id,
        title=data.get("title", "Neue Verfahrensdokumentation"),
        version=data.get("version", "1.0"),
        status="DRAFT",
        scope=data.get("scope"),
        anwenderbeschreibung=data.get("anwenderbeschreibung"),
        technische_beschreibung=data.get("technische_beschreibung"),
        betriebsanleitung=data.get("betriebsanleitung"),
        pruefwege=data.get("pruefwege"),
        software_name=data.get("software_name", "VALEO NeuroERP"),
        software_version=data.get("software_version", "3.0"),
        datenbank=data.get("datenbank"),
        betriebssystem=data.get("betriebssystem"),
        created_at=datetime.utcnow()
    )
    db.add(doc)
    db.commit()
    
    return {"id": doc.id, "message": "Verfahrensdokumentation erstellt"}


@router.put("/gobd/verfahrensdokumentation/{id}/freigabe", dependencies=SCHREIBEN["FINANZ"])
async def release_verfahrensdokumentation(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Verfahrensdokumentation freigeben (GoBD-konform)"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    result = db.execute(
        select(ProcedureDoc).where(
            ProcedureDoc.id == id,
            ProcedureDoc.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Verfahrensdokumentation nicht gefunden")
    
    result.status = "RELEASED"
    result.released_by = current_user.get("username", current_user.get("sub", "system"))
    result.released_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Freigegeben", "released_at": result.released_at.isoformat()}


@router.get("/gobd/verfahrensdokumentation/{id}/export")
async def export_verfahrensdokumentation_pdf(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Exportiere Verfahrensdokumentation als PDF (GoBD-konform)"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    result = db.execute(
        select(ProcedureDoc).where(
            ProcedureDoc.id == id,
            ProcedureDoc.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Verfahrensdokumentation nicht gefunden")
    
    # GoBD-konforme PDF-Struktur
    pdf_content = f"""
VERFAHRENSDOKUMENTATION (GoBD §147 AO)
{'=' * 50}

Titel: {result.title}
Version: {result.version}
Status: {result.status}
Freigegeben von: {result.released_by or 'N/A'}
Freigegeben am: {result.released_at.isoformat() if result.released_at else 'N/A'}

{'=' * 50}

1. ANWENDUNGSBEREICH
--------------------
{result.scope or 'Keine Angabe'}

2. TECHNISCHE BESCHREIBUNG
--------------------------
Software: {result.software_name} {result.software_version}
Datenbank: {result.datenbank or 'N/A'}
Betriebssystem: {result.betriebssystem or 'N/A'}

3. ANWENDERBESCHREIBUNG
-----------------------
{result.anwenderbeschreibung or 'Siehe separates Benutzerhandbuch'}

4. PRÜFWEGE (GoBD-konform)
--------------------------
{result.pruefwege or 'Alle Buchungen sind durchgehend nummeriert und revisionssicher protokolliert.'}

Erstellt am: {result.created_at.isoformat() if result.created_at else 'N/A'}
Letzte Änderung: {result.updated_at.isoformat() if result.updated_at else 'N/A'}
    """
    
    # In production, use reportlab or weasyprint for real PDF
    return {
        "content": pdf_content,
        "filename": f"verfahrensdokumentation_{result.title}_{result.version}.txt",
        "content_type": "text/plain"
    }


# ============================================================================
# GOBD COMPLIANCE - AUBBEWAHRUNGSFRISTEN
# ============================================================================

@router.get("/gobd/richtlinien", response_model=List)
async def list_retention_policies(
    aktiv: Optional[bool] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Aufbewahrungsrichtlinien (GoBD §147 AO)"""
    from app.finance.models import RetentionPolicy
    from sqlalchemy import select
    
    query = select(RetentionPolicy).where(RetentionPolicy.tenant_id.in_([tenant_id, 'default']))
    
    if aktiv is not None:
        query = query.where(RetentionPolicy.aktiv == aktiv)
    
    query = query.order_by(RetentionPolicy.aufbewahrungs_jahre.desc())
    
    result = db.execute(query).scalars().all()
    return [dict(
        id=r.id,
        dokument_typ=r.dokument_typ,
        beschreibung=r.beschreibung,
        aufbewahrungs_jahre=r.aufbewahrungs_jahre,
        frist_trigger=r.frist_trigger,
        gesetzliche_grundlage=r.gesetzliche_grundlage,
        aktiv=r.aktiv,
    ) for r in result]


@router.get("/gobd/richtlinien/{dokument_typ}/frist")
async def calculate_retention_date(
    dokument_typ: str,
    dokument_datum: date,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Berechne Aufbewahrungsfrist für Dokument (GoBD-konform)"""
    from app.finance.models import RetentionPolicy, DocumentHold
    from sqlalchemy import select
    
    # Finde passende Policy
    policy = db.execute(
        select(RetentionPolicy).where(
            RetentionPolicy.dokument_typ == dokument_typ.upper(),
            RetentionPolicy.tenant_id.in_([tenant_id, 'default']),
            RetentionPolicy.aktiv == True
        )
    ).scalar_one_or_none()
    
    if not policy:
        # Default: 10 Jahre (GoBD Standard)
        jahre = 10
        trigger = "FISCAL_YEAR_END"
        legal = "§147 AO (Standard)"
    else:
        jahre = policy.aufbewahrungs_jahre
        trigger = policy.frist_trigger
        legal = policy.gesetzliche_grundlage
    
    # Berechne Fristende basierend auf Trigger
    if trigger == "FISCAL_YEAR_END":
        # Geschäftsjahresende
        frist_datum = date(dokument_datum.year + jahre, 12, 31)
    elif trigger == "CALENDAR_YEAR_END":
        # Kalenderjahresende
        frist_datum = date(dokument_datum.year + jahre, 12, 31)
    elif trigger == "CONTRACT_END":
        # Vertragsende (hier vereinfacht)
        frist_datum = date(dokument_datum.year + jahre, dokument_datum.month, dokument_datum.day)
    else:
        # Default: creation date + jahre
        frist_datum = date(dokument_datum.year + jahre, dokument_datum.month, dokument_datum.day)
    
    # Prüfe auf aktive Löschsperren
    holds = db.execute(
        select(DocumentHold).where(
            DocumentHold.dokument_typ == dokument_typ.upper(),
            DocumentHold.tenant_id == tenant_id,
            DocumentHold.status == "ACTIVE"
        )
    ).scalars().all()
    
    active_holds = []
    for hold in holds:
        if hold.hold_end_date is None or hold.hold_end_date >= date.today():
            active_holds.append({
                "sperrgrund": hold.sperrgrund,
                "hold_start_date": hold.hold_start_date.isoformat(),
                "hold_end_date": hold.hold_end_date.isoformat() if hold.hold_end_date else "unbefristet"
            })
    
    return {
        "dokument_typ": dokument_typ.upper(),
        "dokument_datum": dokument_datum.isoformat(),
        "aufbewahrungs_jahre": jahre,
        "frist_datum": frist_datum.isoformat(),
        "gesetzliche_grundlage": legal,
        "loeschsperren": active_holds,
        "loeschbar": len(active_holds) == 0 and frist_datum < date.today()
    }


@router.get("/gobd/loeschsperren", response_model=List)
async def list_document_holds(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste aktive Löschsperren"""
    from app.finance.models import DocumentHold
    from sqlalchemy import select
    
    query = select(DocumentHold).where(DocumentHold.tenant_id == tenant_id)
    
    if status:
        query = query.where(DocumentHold.status == status)
    else:
        query = query.where(DocumentHold.status == "ACTIVE")
    
    query = query.order_by(DocumentHold.hold_start_date.desc())
    
    result = db.execute(query).scalars().all()
    return [dict(
        id=r.id,
        dokument_id=r.dokument_id,
        dokument_typ=r.dokument_typ,
        belegnr=r.belegnr,
        sperrgrund=r.sperrgrund,
        hold_start_date=r.hold_start_date.isoformat(),
        hold_end_date=r.hold_end_date.isoformat() if r.hold_end_date else None,
        status=r.status,
        released_by=r.released_by,
    ) for r in result]


@router.post("/gobd/loeschsperren", dependencies=SCHREIBEN["FINANZ"])
async def create_document_hold(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Löschsperre (GoBD §147 Abs. 3 AO)"""
    from app.finance.models import DocumentHold
    
    hold = DocumentHold(
        id=uuid7(),
        tenant_id=tenant_id,
        dokument_id=data.get("dokument_id"),
        dokument_typ=data.get("dokument_typ", "ALLGEMEIN").upper(),
        belegnr=data.get("belegnr"),
        sperrgrund=data.get("sperrgrund", "MANUELL"),
        beschreibung=data.get("beschreibung"),
        hold_start_date=datetime.strptime(data.get("hold_start_date", str(date.today())), "%Y-%m-%d").date(),
        hold_end_date=datetime.strptime(data["hold_end_date"], "%Y-%m-%d").date() if data.get("hold_end_date") else None,
        status="ACTIVE",
        created_at=datetime.utcnow()
    )
    db.add(hold)
    db.commit()
    
    return {"id": hold.id, "message": "Löschsperre erstellt"}


@router.put("/gobd/loeschsperren/{id}/freigabe", dependencies=SCHREIBEN["FINANZ"])
async def release_document_hold(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Löschsperre aufheben"""
    from app.finance.models import DocumentHold
    from sqlalchemy import select
    
    result = db.execute(
        select(DocumentHold).where(
            DocumentHold.id == id,
            DocumentHold.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Löschsperre nicht gefunden")
    
    result.status = "RELEASED"
    result.released_by = current_user.get("username", current_user.get("sub", "system"))
    result.released_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Löschsperre aufgehoben", "released_at": result.released_at.isoformat()}


@router.get("/gobd/audit/loeschprotokoll")
async def get_deletion_audit_log(
    von_datum: Optional[date] = Query(None),
    bis_datum: Optional[date] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Audit-Log für Löschungen (GoBD §147 Abs. 3 AO)"""
    # In production, this would query a real audit log table
    # For now, return placeholder
    return {
        "message": "Audit-Log für Löschungen",
        "von_datum": von_datum.isoformat() if von_datum else None,
        "bis_datum": bis_datum.isoformat() if bis_datum else None,
        "eintraege": []
    }
