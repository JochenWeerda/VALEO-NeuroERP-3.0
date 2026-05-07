"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBankkontoPostgresRepository = void 0;
const finanzBankkonto_entity_1 = require("../../core/entities/finanzBankkonto.entity");
const TABLE = 'finanz.bankkonten';
const COLUMNS = [
    'id',
    'kontoname',
    'bankname',
    'iban',
    'bic',
    'kontonummer',
    'blz',
    'waehrung',
    'kontostand',
    'letzter_abgleich',
    'ist_aktiv',
    'notizen',
    'erstellt_von',
    'erstellt_am',
    'aktualisiert_am',
];
function toNumber(value) {
    if (value === null || value === undefined) {
        return undefined;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
}
function toBoolean(value) {
    if (value === null || value === undefined) {
        return undefined;
    }
    if (typeof value === 'boolean') {
        return value;
    }
    return value === 1 || value === '1' || value === 'true';
}
function toDate(value) {
    if (value === undefined || value === null) {
        return undefined;
    }
    return value instanceof Date ? value : new Date(String(value));
}
class FinanzBankkontoPostgresRepository {
    constructor(pool) {
        this.pool = pool;
    }
    mapRow(row) {
        const props = {
            id: row.id,
            kontoname: String(row.kontoname),
            bankname: String(row.bankname),
            iban: (row.iban !== undefined && row.iban !== null) ? String(row.iban) : undefined,
            bic: (row.bic !== undefined && row.bic !== null) ? String(row.bic) : undefined,
            kontonummer: (row.kontonummer !== undefined && row.kontonummer !== null) ? String(row.kontonummer) : undefined,
            blz: (row.blz !== undefined && row.blz !== null) ? String(row.blz) : undefined,
            waehrung: (row.waehrung !== undefined && row.waehrung !== null) ? String(row.waehrung) : undefined,
            kontostand: toNumber(row.kontostand),
            letzter_abgleich: toDate(row.letzter_abgleich),
            ist_aktiv: toBoolean(row.ist_aktiv),
            notizen: (row.notizen !== undefined && row.notizen !== null) ? String(row.notizen) : undefined,
            erstellt_von: (row.erstellt_von !== undefined && row.erstellt_von !== null) ? String(row.erstellt_von) : undefined,
            erstellt_am: toDate(row.erstellt_am),
            aktualisiert_am: toDate(row.aktualisiert_am),
        };
        return finanzBankkonto_entity_1.FinanzBankkonto.create(props);
    }
    async findById(id) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 LIMIT 1`, [id]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async list() {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} ORDER BY kontoname ASC`);
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        const result = await this.pool.query(`INSERT INTO ${TABLE} (
        id,
        kontoname,
        bankname,
        iban,
        bic,
        kontonummer,
        blz,
        waehrung,
        kontostand,
        letzter_abgleich,
        ist_aktiv,
        notizen,
        erstellt_von
      ) VALUES (
        COALESCE($1, gen_random_uuid()),
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        $10,
        COALESCE($11, true),
        $12,
        $13
      ) RETURNING ${COLUMNS.join(', ')}`, [
            primitives.id ?? null,
            primitives.kontoname,
            primitives.bankname,
            primitives.iban ?? null,
            primitives.bic ?? null,
            primitives.kontonummer ?? null,
            primitives.blz ?? null,
            primitives.waehrung ?? 'EUR',
            primitives.kontostand ?? 0,
            primitives.letzter_abgleich ?? null,
            primitives.ist_aktiv ?? null,
            primitives.notizen ?? null,
            primitives.erstellt_von ?? null,
        ]);
        return this.mapRow(result.rows[0]);
    }
    async update(entity) {
        const primitives = entity.toPrimitives();
        if (primitives.id === undefined || primitives.id === null) {
            throw new Error('Cannot update FinanzBankkonto without primary key');
        }
        const result = await this.pool.query(`UPDATE ${TABLE}
          SET kontoname = $2,
              bankname = $3,
              iban = $4,
              bic = $5,
              kontonummer = $6,
              blz = $7,
              waehrung = $8,
              kontostand = $9,
              letzter_abgleich = $10,
              ist_aktiv = COALESCE($11, ist_aktiv),
              notizen = $12,
              aktualisiert_am = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING ${COLUMNS.join(', ')}
      `, [
            primitives.id,
            primitives.kontoname,
            primitives.bankname,
            primitives.iban ?? null,
            primitives.bic ?? null,
            primitives.kontonummer ?? null,
            primitives.blz ?? null,
            primitives.waehrung ?? 'EUR',
            primitives.kontostand ?? 0,
            primitives.letzter_abgleich ?? null,
            primitives.ist_aktiv ?? null,
            primitives.notizen ?? null,
        ]);
        if (result.rowCount === 0) {
            throw new Error(`FinanzBankkonto with id ${primitives.id} not found`);
        }
        return this.mapRow(result.rows[0]);
    }
    async delete(id) {
        await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1`, [id]);
    }
}
exports.FinanzBankkontoPostgresRepository = FinanzBankkontoPostgresRepository;
//# sourceMappingURL=finanzBankkonto-postgres.repository.js.map