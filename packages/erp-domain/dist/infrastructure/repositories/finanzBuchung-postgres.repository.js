"use strict";
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
            tenant_id: String(record.tenant_id ?? ''),
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
    async findById(id, tenantId) {
        const result = await this.pool.query(`${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE id = $1 AND tenant_id = $2 LIMIT 1`, [id, tenantId]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async findByBuchungsnummer(tenantId, buchungsnummer) {
        const result = await this.pool.query(`${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE tenant_id = $1 AND buchungsnummer = $2 LIMIT 1`, [tenantId, buchungsnummer]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async count(tenantId) {
        const result = await this.pool.query('SELECT COUNT(*)::int AS c FROM finanz.buchungen WHERE tenant_id = $1', [tenantId]);
        const c = result.rows[0]?.c;
        return typeof c === 'number' ? c : parseInt(String(c), 10);
    }
    async listPaged(tenantId, limit, offset) {
        const result = await this.pool.query(`${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE tenant_id = $1 ORDER BY id ASC LIMIT $2 OFFSET $3`, [tenantId, limit, offset]);
        return result.rows.map((row) => this.mapRow(row));
    }
    async list(tenantId) {
        const result = await this.pool.query(`${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE tenant_id = $1 ORDER BY id ASC`, [tenantId]);
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        await this.pool.query(`INSERT INTO finanz.buchungen (id, tenant_id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21) ON CONFLICT (id) DO NOTHING`, [
            primitives.id,
            primitives.tenant_id,
            primitives.buchungsnummer,
            primitives.buchungsdatum,
            primitives.belegdatum,
            primitives.belegnummer,
            primitives.buchungstext,
            primitives.sollkonto,
            primitives.habenkonto,
            primitives.betrag,
            primitives.waehrung,
            primitives.steuerbetrag,
            primitives.steuersatz,
            primitives.buchungsart,
            primitives.referenz_typ,
            primitives.referenz_id,
            primitives.ist_storniert,
            primitives.storno_buchung_id,
            primitives.erstellt_von,
            primitives.erstellt_am,
            primitives.aktualisiert_am,
        ]);
    }
    async update(entity) {
        const primitives = entity.toPrimitives();
        await this.pool.query('UPDATE finanz.buchungen SET buchungsnummer = $2, buchungsdatum = $3, belegdatum = $4, belegnummer = $5, buchungstext = $6, sollkonto = $7, habenkonto = $8, betrag = $9, waehrung = $10, steuerbetrag = $11, steuersatz = $12, buchungsart = $13, referenz_typ = $14, referenz_id = $15, ist_storniert = $16, storno_buchung_id = $17, erstellt_von = $18, erstellt_am = $19, aktualisiert_am = $20 WHERE id = $1 AND tenant_id = $21', [
            primitives.id,
            primitives.buchungsnummer,
            primitives.buchungsdatum,
            primitives.belegdatum,
            primitives.belegnummer,
            primitives.buchungstext,
            primitives.sollkonto,
            primitives.habenkonto,
            primitives.betrag,
            primitives.waehrung,
            primitives.steuerbetrag,
            primitives.steuersatz,
            primitives.buchungsart,
            primitives.referenz_typ,
            primitives.referenz_id,
            primitives.ist_storniert,
            primitives.storno_buchung_id,
            primitives.erstellt_von,
            primitives.erstellt_am,
            primitives.aktualisiert_am,
            primitives.tenant_id,
        ]);
    }
    async delete(id, tenantId) {
        await this.pool.query('DELETE FROM finanz.buchungen WHERE id = $1 AND tenant_id = $2', [id, tenantId]);
    }
}
exports.FinanzBuchungPostgresRepository = FinanzBuchungPostgresRepository;
FinanzBuchungPostgresRepository.LIST_SELECT = 'SELECT id, tenant_id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am FROM finanz.buchungen';
//# sourceMappingURL=finanzBuchung-postgres.repository.js.map