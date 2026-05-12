"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKreditorPostgresRepository = void 0;
const finanzKreditor_entity_1 = require("../../core/entities/finanzKreditor.entity");
const TABLE = 'finanz.kreditoren';
const COLUMNS = [
    'id',
    'tenant_id',
    'lieferanten_id',
    'kreditor_nr',
    'kreditlimit',
    'zahlungsziel',
    'zahlungsbedingungen',
    'bankverbindung',
    'steuer_id',
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
class FinanzKreditorPostgresRepository {
    constructor(pool) {
        this.pool = pool;
    }
    mapRow(row) {
        const props = {
            id: row.id,
            tenant_id: String(row.tenant_id),
            lieferanten_id: (row.lieferanten_id !== undefined && row.lieferanten_id !== null) ? String(row.lieferanten_id) : undefined,
            kreditor_nr: String(row.kreditor_nr),
            zahlungsziel: toNumber(row.zahlungsziel),
            zahlungsart: (row.zahlungsart !== undefined && row.zahlungsart !== null) ? String(row.zahlungsart) : undefined,
            bankverbindung: (row.bankverbindung !== undefined && row.bankverbindung !== null) ? String(row.bankverbindung) : undefined,
            steuernummer: (row.steuer_id !== undefined && row.steuer_id !== null) ? String(row.steuer_id) : undefined,
            ist_aktiv: toBoolean(row.ist_aktiv),
            notizen: (row.notizen !== undefined && row.notizen !== null) ? String(row.notizen) : undefined,
            erstellt_von: (row.erstellt_von !== undefined && row.erstellt_von !== null) ? String(row.erstellt_von) : undefined,
            erstellt_am: toDate(row.erstellt_am),
            aktualisiert_am: toDate(row.aktualisiert_am),
        };
        return finanzKreditor_entity_1.FinanzKreditor.create(props);
    }
    async findById(id, tenantId) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 AND tenant_id = $2 LIMIT 1`, [id, tenantId]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async findByKreditorNr(tenantId, kreditorNr) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 AND kreditor_nr = $2 LIMIT 1`, [tenantId, kreditorNr]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async count(tenantId) {
        const result = await this.pool.query(`SELECT COUNT(*)::int AS c FROM ${TABLE} WHERE tenant_id = $1`, [tenantId]);
        const c = result.rows[0]?.c;
        return typeof c === 'number' ? c : parseInt(String(c), 10);
    }
    async listPaged(tenantId, limit, offset) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY kreditor_nr ASC LIMIT $2 OFFSET $3`, [tenantId, limit, offset]);
        return result.rows.map((row) => this.mapRow(row));
    }
    async list(tenantId) {
        const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY kreditor_nr ASC`, [tenantId]);
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        const result = await this.pool.query(`INSERT INTO ${TABLE} (
        id,
        tenant_id,
        lieferanten_id,
        kreditor_nr,
        kreditlimit,
        zahlungsziel,
        zahlungsbedingungen,
        bankverbindung,
        steuer_id,
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
            primitives.tenant_id,
            primitives.lieferanten_id ?? null,
            primitives.kreditor_nr,
            null,
            primitives.zahlungsziel ?? null,
            primitives.zahlungsart ?? null,
            primitives.bankverbindung ?? null,
            primitives.steuernummer ?? null,
            primitives.ist_aktiv ?? null,
            primitives.notizen ?? null,
            primitives.erstellt_von ?? null,
        ]);
        return this.mapRow(result.rows[0]);
    }
    async update(entity) {
        const primitives = entity.toPrimitives();
        if (primitives.id === undefined || primitives.id === null) {
            throw new Error('Cannot update FinanzKreditor without primary key');
        }
        const result = await this.pool.query(`UPDATE ${TABLE}
          SET lieferanten_id = $2,
              kreditor_nr = $3,
              kreditlimit = $4,
              zahlungsziel = $5,
              zahlungsbedingungen = $6,
              bankverbindung = $7,
              steuer_id = $8,
              ist_aktiv = COALESCE($9, ist_aktiv),
              notizen = $10,
              aktualisiert_am = CURRENT_TIMESTAMP
        WHERE id = $1 AND tenant_id = $11
        RETURNING ${COLUMNS.join(', ')}
      `, [
            primitives.id,
            primitives.lieferanten_id ?? null,
            primitives.kreditor_nr,
            null,
            primitives.zahlungsziel ?? null,
            primitives.zahlungsart ?? null,
            primitives.bankverbindung ?? null,
            primitives.steuernummer ?? null,
            primitives.ist_aktiv ?? null,
            primitives.notizen ?? null,
            primitives.tenant_id,
        ]);
        if (result.rowCount === 0) {
            throw new Error(`FinanzKreditor with id ${primitives.id} not found`);
        }
        return this.mapRow(result.rows[0]);
    }
    async delete(id, tenantId) {
        await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1 AND tenant_id = $2`, [id, tenantId]);
    }
}
exports.FinanzKreditorPostgresRepository = FinanzKreditorPostgresRepository;
//# sourceMappingURL=finanzKreditor-postgres.repository.js.map