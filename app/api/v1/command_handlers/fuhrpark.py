"""Fuhrpark command implementations; routes remain in the public endpoint module."""
from datetime import datetime
from typing import Any
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body
from app.api.v1.endpoints.fuhrpark import (
    FahrzeugRepository, FuhrparkTerminartRepository, FuhrparkRechnungRepository,
    FuhrparkAusgehendesDokumentRepository, FuhrparkFahrzeugPayload,
    FuhrparkTerminartPayload, FuhrparkRechnungPayload, FuhrparkAusgehendesDokumentPayload,
    _to_dict, ValidationError,
)

def _strip_tenant(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if k not in {"tenant_id", "mandanten_id"}}


def upsert_fahrzeug(db: Session, tenant_id: str, data: dict[str, Any], *, commit: bool = False, validate_only: bool = False) -> dict[str, Any]:
    """Create or update Fahrzeug in Token-Mandant; strips client tenant_id."""
    repo = FahrzeugRepository(db)
    clean = _strip_tenant(data)
    raw_id = clean.pop("id", None)
    alias_id = clean.pop("fahrzeug_id", None)
    if raw_id and alias_id and str(raw_id) != str(alias_id):
        raise HTTPException(422, "Widerspruechliche Datensatz-IDs")
    entity_id = str(raw_id or alias_id or "").strip() or None
    try:
        clean = FuhrparkFahrzeugPayload.model_validate(clean).model_dump(exclude_unset=True)
    except ValidationError as exc:
        raise HTTPException(422, "Ungueltige Fuhrpark-Eingabedaten") from exc
    kennzeichen = str(clean.get("kennzeichen") or "").strip()
    typ = str(clean.get("typ") or "").strip()
    if not kennzeichen or not typ:
        raise HTTPException(status_code=422, detail="kennzeichen und typ sind Pflichtfelder")
    if entity_id:
        existing = repo.get_by_id(tenant_id, entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Fahrzeug not found")
        if kennzeichen != existing.kennzeichen:
            dup = repo.get_by_kennzeichen(tenant_id, kennzeichen)
            if dup:
                raise HTTPException(status_code=409, detail="Kennzeichen already exists")
        if validate_only:
            return clean
        row = repo.update(tenant_id, entity_id, clean, commit=commit)
        assert row is not None
        return _to_dict(row)
    dup = repo.get_by_kennzeichen(tenant_id, kennzeichen)
    if dup:
        raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    if validate_only:
        return clean
    row = repo.create(tenant_id, clean, commit=commit)
    return _to_dict(row)


def delete_fahrzeug_tenant(
    db: Session, tenant_id: str, fahrzeug_id: str, *, commit: bool = False
) -> str:
    repo = FahrzeugRepository(db)
    if not repo.delete(tenant_id, fahrzeug_id, commit=commit):
        raise HTTPException(status_code=404, detail="Fahrzeug not found")
    return fahrzeug_id


def upsert_terminart(db: Session, tenant_id: str, data: dict[str, Any], *, commit: bool = False, validate_only: bool = False) -> dict[str, Any]:
    repo = FuhrparkTerminartRepository(db)
    clean = _strip_tenant(data)
    raw_id = clean.pop("id", None)
    alias_id = clean.pop("terminart_id", None)
    if raw_id and alias_id and str(raw_id) != str(alias_id):
        raise HTTPException(422, "Widerspruechliche Datensatz-IDs")
    entity_id = str(raw_id or alias_id or "").strip() or None
    try:
        clean = FuhrparkTerminartPayload.model_validate(clean).model_dump(exclude_unset=True)
    except ValidationError as exc:
        raise HTTPException(422, "Ungueltige Fuhrpark-Eingabedaten") from exc
    name = str(clean.get("terminart") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="terminart ist Pflichtfeld")
    payload = {
        "terminart": name,
        "intervall_monate": int(clean.get("intervall_monate") or 0),
        "intervall_km": int(clean.get("intervall_km") or 0),
    }
    if entity_id:
        existing = repo.get_by_id(tenant_id, entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Terminart not found")
        if name != existing.terminart:
            dup = repo.get_by_name(tenant_id, name)
            if dup:
                raise HTTPException(status_code=409, detail="Terminart already exists")
        if validate_only:
            return clean
        row = repo.update(tenant_id, entity_id, payload, commit=commit)
        assert row is not None
        return _to_dict(row)
    dup = repo.get_by_name(tenant_id, name)
    if dup:
        raise HTTPException(status_code=409, detail="Terminart already exists")
    if validate_only:
        return clean
    row = repo.create(tenant_id, payload, commit=commit)
    return _to_dict(row)


def upsert_rechnung(db: Session, tenant_id: str, data: dict[str, Any], *, commit: bool = False, validate_only: bool = False) -> dict[str, Any]:
    repo = FuhrparkRechnungRepository(db)
    clean = _strip_tenant(data)
    raw_id = clean.pop("id", None)
    alias_id = clean.pop("rechnung_id", None)
    if raw_id and alias_id and str(raw_id) != str(alias_id):
        raise HTTPException(422, "Widerspruechliche Datensatz-IDs")
    entity_id = str(raw_id or alias_id or "").strip() or None
    try:
        clean = FuhrparkRechnungPayload.model_validate(clean).model_dump(exclude_unset=True)
    except ValidationError as exc:
        raise HTTPException(422, "Ungueltige Fuhrpark-Eingabedaten") from exc
    nr = str(clean.get("rechnungs_nr") or "").strip()
    if not nr:
        raise HTTPException(status_code=422, detail="rechnungs_nr ist Pflichtfeld")
    if "datum" not in clean or clean.get("datum") in (None, ""):
        raise HTTPException(status_code=422, detail="datum ist Pflichtfeld")
    if isinstance(clean.get("datum"), str):
        raw = str(clean["datum"]).strip().replace("Z", "+00:00")
        try:
            clean["datum"] = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="datum ungueltig") from exc
    vehicle_id = clean.get("fahrzeug_id")
    if vehicle_id and not FahrzeugRepository(db).get_by_id(tenant_id, vehicle_id):
        raise HTTPException(404, "Fahrzeug not found")
    if entity_id:
        existing = repo.get_by_id(tenant_id, entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Rechnung not found")
        if nr != existing.rechnungs_nr:
            dup = repo.get_by_rechnungs_nr(tenant_id, nr)
            if dup:
                raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
        if validate_only:
            return clean
        row = repo.update(tenant_id, entity_id, clean, commit=commit)
        assert row is not None
        return _to_dict(row)
    dup = repo.get_by_rechnungs_nr(tenant_id, nr)
    if dup:
        raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
    if validate_only:
        return clean
    row = repo.create(tenant_id, clean, commit=commit)
    return _to_dict(row)


def upsert_ausgehendes_dokument(
    db: Session, tenant_id: str, data: dict[str, Any], *, commit: bool = False, validate_only: bool = False
) -> dict[str, Any]:
    repo = FuhrparkAusgehendesDokumentRepository(db)
    clean = _strip_tenant(data)
    raw_id = clean.pop("id", None)
    alias_id = clean.pop("dokument_id", None)
    if raw_id and alias_id and str(raw_id) != str(alias_id):
        raise HTTPException(422, "Widerspruechliche Datensatz-IDs")
    entity_id = str(raw_id or alias_id or "").strip() or None
    try:
        clean = FuhrparkAusgehendesDokumentPayload.model_validate(clean).model_dump(exclude_unset=True)
    except ValidationError as exc:
        raise HTTPException(422, "Ungueltige Fuhrpark-Eingabedaten") from exc
    beleg = str(clean.get("beleg_typ") or "").strip()
    if not beleg:
        raise HTTPException(status_code=422, detail="beleg_typ ist Pflichtfeld")
    if entity_id:
        existing = repo.get_by_id(tenant_id, entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Ausgehendes Dokument not found")
        if validate_only:
            return clean
        row = repo.update(tenant_id, entity_id, clean, commit=commit)
        assert row is not None
        return _to_dict(row)
    if validate_only:
        return clean
    row = repo.create(tenant_id, clean, commit=commit)
    return _to_dict(row)


def _ce_invalid_mode(action_key: str) -> MaskActionResult:
    return MaskActionResult(
        actionKey=action_key,
        mode="invalid",
        success=False,
        error="Unbekannter Aktionsmodus.",
        validationErrors=[
            {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
        ],
    )


def action_fahrzeug_speichern(
    request: Request,
    body: dict[str, Any],
    db: Session,
    tenant_id: str,
) -> MaskActionResult:
    from app.api.v1.endpoints.fuhrpark import upsert_fahrzeug
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return _ce_invalid_mode("speichern")
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    data = _strip_tenant(dict(data))
    preview = {
        "kennzeichen": data.get("kennzeichen"),
        "typ": data.get("typ"),
        "id": data.get("id") or data.get("fahrzeug_id"),
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        try:
            upsert_fahrzeug(db, tenant_id, data, validate_only=True)
        except HTTPException as exc:
            db.rollback()
            return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=str(exc.detail))
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Fahrzeug wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = upsert_fahrzeug(db, tenant_id, data, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="fuhrpark_fahrzeug",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Fahrzeug {created.get('kennzeichen')} gespeichert",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="fuhrpark.fahrzeug.saved",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Fahrzeug konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Fahrzeug {created.get('kennzeichen')} gespeichert.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


def action_fahrzeug_loeschen(
    entity_id: str,
    request: Request,
    body: dict[str, Any],
    db: Session,
    tenant_id: str,
) -> MaskActionResult:
    from app.api.v1.endpoints.fuhrpark import delete_fahrzeug_tenant
    del request
    try:
        mode, audit_reason, idempotency_key, _payload = parse_action_body(body)
    except ValueError:
        return _ce_invalid_mode("loeschen")
    preview = {"fahrzeug_id": entity_id, "tenant_id": tenant_id}
    if mode != "execute":
        repo = FahrzeugRepository(db)
        if not repo.get_by_id(tenant_id, entity_id):
            db.rollback()
            return MaskActionResult(
                actionKey="loeschen",
                mode=mode,
                success=False,
                error="Fahrzeug nicht im Authentifizierungs-Mandanten.",
                validationErrors=[
                    {"field": "entity_id", "message": "Nicht im Authentifizierungs-Mandanten", "severity": "blocking"}
                ],
            )
        db.rollback()
        return MaskActionResult(
            actionKey="loeschen",
            mode=mode,
            success=True,
            summary="Fahrzeug wuerde geloescht — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        deleted_id = delete_fahrzeug_tenant(db, tenant_id, entity_id, commit=False)
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="loeschen",
            entity_type="fuhrpark_fahrzeug",
            entity_id=deleted_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Fahrzeug {deleted_id} geloescht",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="fuhrpark.fahrzeug.deleted",
            aggregate_id=deleted_id,
            payload={"id": deleted_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="loeschen", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="loeschen", mode=mode, success=False, error="Fahrzeug konnte nicht geloescht werden."
        )
    return MaskActionResult(
        actionKey="loeschen",
        mode=mode,
        success=True,
        summary=f"Fahrzeug {deleted_id} geloescht.",
        affectedIds=[deleted_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


def action_terminart_speichern(
    request: Request,
    body: dict[str, Any],
    db: Session,
    tenant_id: str,
) -> MaskActionResult:
    from app.api.v1.endpoints.fuhrpark import upsert_terminart
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return _ce_invalid_mode("speichern")
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    data = _strip_tenant(dict(data))
    preview = {"terminart": data.get("terminart"), "tenant_id": tenant_id, "id": data.get("id")}
    if mode != "execute":
        try:
            upsert_terminart(db, tenant_id, data, validate_only=True)
        except HTTPException as exc:
            db.rollback()
            return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=str(exc.detail))
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Terminart wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = upsert_terminart(db, tenant_id, data, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="fuhrpark_terminart",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Terminart {created.get('terminart')} gespeichert",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="fuhrpark.terminart.saved",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Terminart konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Terminart {created.get('terminart')} gespeichert.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


def action_rechnung_speichern(
    request: Request,
    body: dict[str, Any],
    db: Session,
    tenant_id: str,
) -> MaskActionResult:
    from app.api.v1.endpoints.fuhrpark import upsert_rechnung
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return _ce_invalid_mode("speichern")
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    data = _strip_tenant(dict(data))
    preview = {
        "rechnungs_nr": data.get("rechnungs_nr"),
        "betrag_eur": data.get("betrag_eur"),
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        try:
            upsert_rechnung(db, tenant_id, data, validate_only=True)
        except HTTPException as exc:
            db.rollback()
            return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=str(exc.detail))
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Rechnung wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = upsert_rechnung(db, tenant_id, data, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="fuhrpark_rechnung",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Rechnung {created.get('rechnungs_nr')} gespeichert",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="fuhrpark.rechnung.saved",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Rechnung konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Rechnung {created.get('rechnungs_nr')} gespeichert.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


def action_dokument_speichern(
    request: Request,
    body: dict[str, Any],
    db: Session,
    tenant_id: str,
) -> MaskActionResult:
    from app.api.v1.endpoints.fuhrpark import upsert_ausgehendes_dokument
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return _ce_invalid_mode("speichern")
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    data = _strip_tenant(dict(data))
    preview = {"beleg_typ": data.get("beleg_typ"), "tenant_id": tenant_id}
    if mode != "execute":
        try:
            upsert_ausgehendes_dokument(db, tenant_id, data, validate_only=True)
        except HTTPException as exc:
            db.rollback()
            return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=str(exc.detail))
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Dokument wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = upsert_ausgehendes_dokument(db, tenant_id, data, commit=False)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="fuhrpark_ausgehendes_dokument",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Dokument {created.get('beleg_typ')} gespeichert",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="fuhrpark.dokument.saved",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Dokument konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Dokument {created.get('beleg_typ')} gespeichert.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


