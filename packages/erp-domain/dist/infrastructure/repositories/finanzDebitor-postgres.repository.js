"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzDebitorPostgresRepository = void 0;
const finanzDebitor_entity_1 = require("../../core/entities/finanzDebitor.entity");
const TABLE = 'finanz.debitoren';
const COLUMNS = [
    'id',
    'kunden_id',
    'debitor_nr',
    'kreditlimit',
    'zahlungsziel',
    'zahlungsart',
    'bankverbindung',
    'steuernummer',
    'ust_id',
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
class FinanzDebitorPostgresRepository {
    constructor(pool) {
        this.pool = pool;
    }
    mapRow(row) {
        const props = {
            id: row.id,
            kunden_id: (row.kunden_id !== undefined && row.kunden_id !== null) ? String(row.kunden_id) : undefined,
            debitor_nr: String(row.debitor_nr),
            kreditlimit: toNumber(row.kreditlimit),
            zahlungsziel: toNumber(row.zahlungsziel),
            zahlungsart: (row.zahlungsart !== undefined && row.zahlungsart !== null) ? String(row.zahlungsart) : undefined,
            bankverbindung: (row.bankverbindung !== undefined && row.bankverbindung !== null) ? String(row.bankverbindung) : undefined,
            steuernummer: (row.steuernummer !== undefined && row.steuernummer !== null) ? String(row.steuernummer) : undefined,
            ust_id: (row.ust_id !== undefined && row.ust_id !== null) ? String(row.ust_id) : undefined,
            ist_aktiv: toBoolean(row.ist_aktiv),
            notizen: (row.notizen !== undefined && row.notizen !== null) ? String(row.notizen) : undefined,
            erstellt_von: (row.erstellt_von !== undefined && row.erstellt_von !== null) ? String(row.erstellt_von) : undefined,
            erstellt_am: toDate(row.erstellt_am),
            aktualisiert_am: toDate(row.aktualisiert_am),
        };
        return finanzDebitor_entity_1.FinanzDebitor.create(props);
    }
    async findById(id) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 LIMIT 1`, [id]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async findByDebitorNr(debitorNr) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE debitor_nr = $1 LIMIT 1`, [debitorNr]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async list() {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} ORDER BY debitor_nr ASC`);
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        const result = await this.pool.query(`INSERT INTO ${TABLE} (
        id,
        kunden_id,
        debitor_nr,
        kreditlimit,
        zahlungsziel,
        zahlungsart,
        bankverbindung,
        steuernummer,
        ust_id,
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
        COALESCE($10, true),
        $11,
        $12
      ) RETURNING ${COLUMNS.join(', ')}`, [
            primitives.id ?? null,
            primitives.kunden_id ?? null,
            primitives.debitor_nr,
            primitives.kreditlimit ?? null,
            primitives.zahlungsziel ?? null,
            primitives.zahlungsart ?? null,
            primitives.bankverbindung ?? null,
            primitives.steuernummer ?? null,
            primitives.ust_id ?? null,
            primitives.ist_aktiv ?? null,
            primitives.notizen ?? null,
            primitives.erstellt_von ?? null,
        ]);
        return this.mapRow(result.rows[0]);
    }
    async update(entity) {
        const primitives = entity.toPrimitives();
        if (primitives.id === undefined || primitives.id === null) {
            throw new Error('Cannot update FinanzDebitor without primary key');
        }
        const result = await this.pool.query(`UPDATE ${TABLE}
          SET kunden_id = $2,
              debitor_nr = $3,
              kreditlimit = $4,
              zahlungsziel = $5,
              zahlungsart = $6,
              bankverbindung = $7,
              steuernummer = $8,
              ust_id = $9,
              ist_aktiv = COALESCE($10, ist_aktiv),
              notizen = $11,
              aktualisiert_am = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING ${COLUMNS.join(', ')}
      `, [
            primitives.id,
            primitives.kunden_id ?? null,
            primitives.debitor_nr,
            primitives.kreditlimit ?? null,
            primitives.zahlungsziel ?? null,
            primitives.zahlungsart ?? null,
            primitives.bankverbindung ?? null,
            primitives.steuernummer ?? null,
            primitives.ust_id ?? null,
            primitives.ist_aktiv ?? null,
            primitives.notizen ?? null,
        ]);
        if (result.rowCount === 0) {
            throw new Error(`FinanzDebitor with id ${primitives.id} not found`);
        }
        return this.mapRow(result.rows[0]);
    }
    async delete(id) {
        await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1`, [id]);
    }
}
exports.FinanzDebitorPostgresRepository = FinanzDebitorPostgresRepository;
//# sourceMappingURL=finanzDebitor-postgres.repository.js.map