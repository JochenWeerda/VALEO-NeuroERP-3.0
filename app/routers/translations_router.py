"""
Translation API Router
Ermöglicht Frontend den Zugriff auf Übersetzungen aus der Datenbank
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.translation import Translation, TranslationValue, create_translation


router = APIRouter(prefix="/api/translations", tags=["translations"])


# Pydantic-Models
class TranslationCreate(BaseModel):
    translation_key: str
    context: str
    description: Optional[str] = None
    values: Dict[str, str]  # {'de': 'Speichern', 'en': 'Save'}


class TranslationUpdate(BaseModel):
    language_code: str
    value: str
    is_approved: Optional[bool] = None


class MissingTranslationsResponse(BaseModel):
    language: str
    total_keys: int
    translated_keys: int
    missing_count: int
    missing_keys: List[str]


# --- GET-Endpoints ---

@router.get("/{language_code}")
async def get_translations(
    language_code: str,
    context: Optional[str] = Query(None, description="Filter by context (e.g. 'agrar')"),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Liefert alle Übersetzungen für eine Sprache als Flat-Object.
    
    Response: { "agrar.saatgut.title": "Saatgutverwaltung", ... }
    """
    query = db.query(Translation, TranslationValue).join(
        TranslationValue,
        Translation.id == TranslationValue.translation_id
    ).filter(TranslationValue.language_code == language_code)
    
    if context:
        query = query.filter(Translation.context == context)
    
    results = query.all()
    
    translations = {
        trans.translation_key: value.value
        for trans, value in results
    }
    
    return translations


@router.get("/missing/{language_code}", response_model=MissingTranslationsResponse)
async def get_missing_translations(
    language_code: str,
    db: Session = Depends(get_db)
):
    """
    Findet fehlende Übersetzungen für eine Sprache.
    Wichtig beim Hinzufügen neuer Sprachen!
    """
    # Alle Translation-Keys
    all_keys_query = db.query(Translation.translation_key).all()
    all_keys = {key[0] for key in all_keys_query}
    
    # Existierende Übersetzungen für diese Sprache
    existing_query = db.query(Translation.translation_key).join(
        TranslationValue
    ).filter(TranslationValue.language_code == language_code).all()
    existing_keys = {key[0] for key in existing_query}
    
    # Fehlende Keys
    missing = sorted(all_keys - existing_keys)
    
    return MissingTranslationsResponse(
        language=language_code,
        total_keys=len(all_keys),
        translated_keys=len(existing_keys),
        missing_count=len(missing),
        missing_keys=missing
    )


@router.get("/contexts/list")
async def get_contexts(
    db: Session = Depends(get_db)
) -> List[Dict[str, any]]:
    """
    Liefert alle verfügbaren Kontexte mit Statistiken
    """
    results = db.query(
        Translation.context,
        func.count(Translation.id).label('count')
    ).group_by(Translation.context).all()
    
    return [
        {"context": context, "translation_count": count}
        for context, count in results
    ]


# --- POST-Endpoints ---

@router.post("/")
async def create_new_translation(
    translation: TranslationCreate,
    db: Session = Depends(get_db)
):
    """
    Neue Übersetzung anlegen mit Werten für mehrere Sprachen
    """
    # Prüfe ob Key bereits existiert
    existing = db.query(Translation).filter(
        Translation.translation_key == translation.translation_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Translation key '{translation.translation_key}' already exists"
        )
    
    # Erstelle Translation
    new_translation = create_translation(
        db,
        key=translation.translation_key,
        context=translation.context,
        values=translation.values,
        description=translation.description
    )
    
    db.commit()
    
    return {
        "id": str(new_translation.id),
        "translation_key": new_translation.translation_key,
        "languages": list(translation.values.keys())
    }


@router.put("/{translation_key}")
async def update_translation(
    translation_key: str,
    update: TranslationUpdate,
    db: Session = Depends(get_db)
):
    """
    Übersetzung für eine Sprache aktualisieren
    """
    # Finde Translation
    translation = db.query(Translation).filter(
        Translation.translation_key == translation_key
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=404,
            detail=f"Translation key '{translation_key}' not found"
        )
    
    # Finde oder erstelle TranslationValue
    trans_value = db.query(TranslationValue).filter(
        and_(
            TranslationValue.translation_id == translation.id,
            TranslationValue.language_code == update.language_code
        )
    ).first()
    
    if trans_value:
        # Update existing
        trans_value.value = update.value
        if update.is_approved is not None:
            trans_value.is_approved = update.is_approved
    else:
        # Create new
        trans_value = TranslationValue(
            translation_id=translation.id,
            language_code=update.language_code,
            value=update.value,
            is_approved=update.is_approved or False
        )
        db.add(trans_value)
    
    db.commit()
    
    return {
        "translation_key": translation_key,
        "language_code": update.language_code,
        "value": update.value
    }


# --- Bulk-Operations ---

@router.post("/bulk/seed")
async def bulk_seed_translations(
    translations: List[TranslationCreate],
    db: Session = Depends(get_db)
):
    """
    Bulk-Import von Übersetzungen (für Initial-Seeds)
    """
    created = []
    errors = []
    
    for trans in translations:
        try:
            # Prüfe ob bereits existiert
            existing = db.query(Translation).filter(
                Translation.translation_key == trans.translation_key
            ).first()
            
            if not existing:
                new_trans = create_translation(
                    db,
                    key=trans.translation_key,
                    context=trans.context,
                    values=trans.values,
                    description=trans.description
                )
                created.append(trans.translation_key)
            
        except Exception as e:
            errors.append({
                "key": trans.translation_key,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "created_count": len(created),
        "error_count": len(errors),
        "created_keys": created,
        "errors": errors
    }


@router.get("/export/{language_code}")
async def export_translations(
    language_code: str,
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """
    Exportiert Übersetzungen für eine Sprache.
    Format: json oder csv
    """
    translations = await get_translations(language_code, None, db)
    
    if format == "json":
        return translations
    
    elif format == "csv":
        # CSV-Export (für Übersetzer)
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Key', 'Value', 'Context'])
        
        for key, value in translations.items():
            context = key.split('.')[0] if '.' in key else ''
            writer.writerow([key, value, context])
        
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=translations_{language_code}.csv"
            }
        )

