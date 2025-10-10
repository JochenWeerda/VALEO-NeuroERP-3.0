"""
Translation Models für Database-Driven i18n
Ermöglicht Verwaltung von Übersetzungen zur Laufzeit
"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Translation(Base):
    """
    Haupttabelle für Übersetzungs-Keys
    Jeder Key repräsentiert einen zu übersetzenden Text
    """
    __tablename__ = 'translations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    translation_key = Column(String(255), unique=True, nullable=False, index=True)
    context = Column(String(100), index=True, comment='Module/Feature-Kontext (z.B. agrar, futter, common)')
    description = Column(Text, comment='Beschreibung für Übersetzer')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    values = relationship(
        "TranslationValue",
        back_populates="translation",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    
    def __repr__(self):
        return f"<Translation {self.translation_key}>"


class TranslationValue(Base):
    """
    Übersetzungs-Werte pro Sprache
    Ein Translation-Key kann mehrere Values haben (eine pro Sprache)
    """
    __tablename__ = 'translation_values'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    translation_id = Column(UUID(as_uuid=True), ForeignKey('translations.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(5), nullable=False, index=True, comment='ISO 639-1 Code (de, en, fr, etc.)')
    value = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False, comment='Review-Status für Quality-Control')
    translated_by = Column(String(100), comment='Name des Übersetzers')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    translation = relationship("Translation", back_populates="values")
    
    # Unique Constraint: Ein Translation-Key kann nur eine Übersetzung pro Sprache haben
    __table_args__ = (
        Index('idx_translation_lang', 'translation_id', 'language_code', unique=True),
    )
    
    def __repr__(self):
        return f"<TranslationValue {self.language_code}: {self.value[:30]}...>"


# Helper-Functions für Seeds
def create_translation(db, key: str, context: str, values: dict, description: str = None):
    """
    Helper zum Erstellen einer Übersetzung mit Werten
    
    Example:
        create_translation(
            db,
            'common.save',
            'common',
            {'de': 'Speichern', 'en': 'Save', 'fr': 'Enregistrer'},
            'Save button label'
        )
    """
    translation = Translation(
        translation_key=key,
        context=context,
        description=description
    )
    db.add(translation)
    db.flush()
    
    for lang_code, value in values.items():
        trans_value = TranslationValue(
            translation_id=translation.id,
            language_code=lang_code,
            value=value,
            is_approved=True  # Seeds sind pre-approved
        )
        db.add(trans_value)
    
    return translation

