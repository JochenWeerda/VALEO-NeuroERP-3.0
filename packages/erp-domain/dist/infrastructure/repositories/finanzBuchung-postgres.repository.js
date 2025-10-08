"use strict";
/**
 * FinanzBuchungPostgresRepository generated for FinanzBuchung using CRM migration toolkit.
 * Handles persistence with PostgreSQL using pg.Pool.
 * Start simple: find -> save -> update -> delete -> list. Extend for joins later.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBuchungPostgresRepository = void 0;
const finanzBuchung_entity_1 = require("../../core/entities/finanzBuchung.entity");
const toStringOrUndefined = (value) => {
    if (value === null || value === undefined) {
        return undefined;
    }
    return typeof value === 'string' ? value : String(value);
};
const toStringOrEmpty = (value, fallback = '') => {
    return toStringOrUndefined(value) ?? fallback;
};
const toNumberOrUndefined = (value) => {
    if (value === null || value === undefined) {
        return undefined;
    }
    return typeof value === 'number' ? value : Number(value);
};
const toBooleanOrUndefined = (value) => {
    if (value === null || value === undefined) {
        return undefined;
    }
    if (typeof value === 'boolean') {
        return value;
    }
    if (typeof value === 'number') {
        return value !== 0;
    }
    if (typeof value === 'string') {
        return ['true', '1', 't', 'y'].includes(value.toLowerCase());
    }
    return undefined;
};
const toDateOrUndefined = (value) => {
    if (value === null || value === undefined) {
        return undefined;
    }
    if (value instanceof Date) {
        return value;
    }
    const parsed = new Date(String(value));
    return Number.isNaN(parsed.getTime()) ? undefined : parsed;
};
class FinanzBuchungPostgresRepository {
    constructor(pool) {
        this.pool = pool;
    }
    mapRow(row) {
        const record = row;
        return finanzBuchung_entity_1.FinanzBuchung.create({
            id: toStringOrUndefined(record.id) ?? undefined,
            buchungsnummer: toStringOrEmpty(record.buchungsnummer),
            buchungsdatum: toDateOrUndefined(record.buchungsdatum) ?? new Date(),
            belegdatum: toDateOrUndefined(record.belegdatum) ?? new Date(),
            belegnummer: toStringOrUndefined(record.belegnummer),
            buchungstext: toStringOrEmpty(record.buchungstext),
            sollkonto: toStringOrUndefined(record.sollkonto),
            habenkonto: toStringOrUndefined(record.habenkonto),
            betrag: toNumberOrUndefined(record.betrag) ?? 0,
            waehrung: toStringOrUndefined(record.waehrung),
            steuerbetrag: toNumberOrUndefined(record.steuerbetrag),
            steuersatz: toNumberOrUndefined(record.steuersatz),
            buchungsart: toStringOrUndefined(record.buchungsart),
            referenz_typ: toStringOrUndefined(record.referenz_typ),
            referenz_id: toStringOrUndefined(record.referenz_id),
            ist_storniert: toBooleanOrUndefined(record.ist_storniert),
            storno_buchung_id: toStringOrUndefined(record.storno_buchung_id),
            erstellt_von: toStringOrUndefined(record.erstellt_von),
            erstellt_am: toDateOrUndefined(record.erstellt_am),
            aktualisiert_am: toDateOrUndefined(record.aktualisiert_am),
        });
    }
    async findById(id) {
        const result = await this.pool.query('SELECT id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am FROM finanz.buchungen WHERE id = $1 LIMIT 1', [id]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async list() {
        const result = await this.pool.query('SELECT id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am FROM finanz.buchungen ORDER BY id ASC');
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        await this.pool.query('INSERT INTO finanz.buchungen (id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20) ON CONFLICT (id) DO NOTHING', [primitives.id, primitives.buchungsnummer, primitives.buchungsdatum, primitives.belegdatum, primitives.belegnummer, primitives.buchungstext, primitives.sollkonto, primitives.habenkonto, primitives.betrag, primitives.waehrung, primitives.steuerbetrag, primitives.steuersatz, primitives.buchungsart, primitives.referenz_typ, primitives.referenz_id, primitives.ist_storniert, primitives.storno_buchung_id, primitives.erstellt_von, primitives.erstellt_am, primitives.aktualisiert_am]);
    }
    async update(entity) {
        const primitives = entity.toPrimitives();
        await this.pool.query('UPDATE finanz.buchungen SET buchungsnummer = $2, buchungsdatum = $3, belegdatum = $4, belegnummer = $5, buchungstext = $6, sollkonto = $7, habenkonto = $8, betrag = $9, waehrung = $10, steuerbetrag = $11, steuersatz = $12, buchungsart = $13, referenz_typ = $14, referenz_id = $15, ist_storniert = $16, storno_buchung_id = $17, erstellt_von = $18, erstellt_am = $19, aktualisiert_am = $20 WHERE id = $1', [primitives.id, primitives.buchungsnummer, primitives.buchungsdatum, primitives.belegdatum, primitives.belegnummer, primitives.buchungstext, primitives.sollkonto, primitives.habenkonto, primitives.betrag, primitives.waehrung, primitives.steuerbetrag, primitives.steuersatz, primitives.buchungsart, primitives.referenz_typ, primitives.referenz_id, primitives.ist_storniert, primitives.storno_buchung_id, primitives.erstellt_von, primitives.erstellt_am, primitives.aktualisiert_am]);
    }
    async delete(id) {
        await this.pool.query('DELETE FROM finanz.buchungen WHERE id = $1', [id]);
    }
}
exports.FinanzBuchungPostgresRepository = FinanzBuchungPostgresRepository;
//# sourceMappingURL=finanzBuchung-postgres.repository.js.map