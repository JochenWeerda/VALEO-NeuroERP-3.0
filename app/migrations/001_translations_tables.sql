-- Migration: Translation Tables für Database-Driven i18n
-- Version: 001
-- Date: 2024-10-10

-- Translations-Haupttabelle
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_key VARCHAR(255) NOT NULL UNIQUE,
    context VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Translation-Values (pro Sprache)
CREATE TABLE IF NOT EXISTS translation_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_id UUID NOT NULL REFERENCES translations(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL,
    value TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    translated_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_translation_lang UNIQUE(translation_id, language_code)
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_trans_key ON translations(translation_key);
CREATE INDEX IF NOT EXISTS idx_trans_context ON translations(context);
CREATE INDEX IF NOT EXISTS idx_trans_lang ON translation_values(language_code);
CREATE INDEX IF NOT EXISTS idx_trans_approved ON translation_values(is_approved);

-- Comments für bessere Dokumentation
COMMENT ON TABLE translations IS 'Haupttabelle für Übersetzungs-Keys';
COMMENT ON TABLE translation_values IS 'Übersetzungs-Werte pro Sprache';
COMMENT ON COLUMN translations.translation_key IS 'Eindeutiger Key (z.B. agrar.saatgut.title)';
COMMENT ON COLUMN translations.context IS 'Module/Feature-Kontext (agrar, futter, common, etc.)';
COMMENT ON COLUMN translation_values.language_code IS 'ISO 639-1 Code (de, en, fr, es, pt, zh)';
COMMENT ON COLUMN translation_values.is_approved IS 'Review-Status für Quality-Control';

-- Trigger für auto-update von updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_translations_updated_at
    BEFORE UPDATE ON translations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translation_values_updated_at
    BEFORE UPDATE ON translation_values
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

