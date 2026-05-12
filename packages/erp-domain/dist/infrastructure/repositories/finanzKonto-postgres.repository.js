"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKontoPostgresRepository = void 0;
const finanzKonto_entity_1 = require("../../core/entities/finanzKonto.entity");
const TABLE = 'finanz.konten';
const BASE_COLUMNS = [
    'id',
    'tenant_id',
    'kontonummer',
    'kontobezeichnung',
    'kontotyp',
    'kontenklasse',
    'kontengruppe',
    'ist_aktiv',
    'ist_steuerpflichtig',
    'steuersatz',
    'beschreibung',
    'erstellt_von',
    'erstellt_am',
    'aktualisiert_am',
];
function toBoolean(value) {
    if (value === null || value === undefined) {
        return undefined;
    }
    if (typeof value === 'boolean') {
        return value;
    }
    return value === 1 || value === '1' || value === 'true';
}
function toNumber(value) {
    if (value === null || value === undefined) {
        return undefined;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
}
function toDate(value) {
    if (value === undefined || value === null) {
        return undefined;
    }
    return value instanceof Date ? value : new Date(String(value));
}
class FinanzKontoPostgresRepository {
    constructor(pool) {
        this.pool = pool;
    }
    mapRow(row) {
        const props = {
            id: row.id,
            tenant_id: String(row.tenant_id),
            kontonummer: String(row.kontonummer),
            kontobezeichnung: String(row.kontobezeichnung),
            kontotyp: String(row.kontotyp),
            kontenklasse: (row.kontenklasse !== undefined && row.kontenklasse !== null) ? String(row.kontenklasse) : undefined,
            kontengruppe: (row.kontengruppe !== undefined && row.kontengruppe !== null) ? String(row.kontengruppe) : undefined,
            ist_aktiv: toBoolean(row.ist_aktiv),
            ist_steuerpflichtig: toBoolean(row.ist_steuerpflichtig),
            steuersatz: toNumber(row.steuersatz),
            beschreibung: (row.beschreibung !== undefined && row.beschreibung !== null) ? String(row.beschreibung) : undefined,
            erstellt_von: (row.erstellt_von !== undefined && row.erstellt_von !== null) ? String(row.erstellt_von) : undefined,
            erstellt_am: toDate(row.erstellt_am),
            aktualisiert_am: toDate(row.aktualisiert_am),
        };
        return finanzKonto_entity_1.FinanzKonto.create(props);
    }
    async findById(id, tenantId) {
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 AND tenant_id = $2 LIMIT 1`, [id, tenantId]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async findByKontonummer(tenantId, kontonummer) {
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 AND kontonummer = $2 LIMIT 1`, [tenantId, kontonummer]);
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
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY kontonummer ASC LIMIT $2 OFFSET $3`, [tenantId, limit, offset]);
        return result.rows.map((row) => this.mapRow(row));
    }
    async list(tenantId) {
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY kontonummer ASC`, [tenantId]);
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        const result = await this.pool.query(`INSERT INTO ${TABLE} (
        id,
        tenant_id,
        kontonummer,
        kontobezeichnung,
        kontotyp,
        kontenklasse,
        kontengruppe,
        ist_aktiv,
        ist_steuerpflichtig,
        steuersatz,
        beschreibung,
        erstellt_von
      )
      VALUES (
        COALESCE($1, gen_random_uuid()),
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        COALESCE($8, true),
        COALESCE($9, false),
        $10,
        $11,
        $12
      )
      RETURNING ${BASE_COLUMNS.join(', ')}
      `, [
            primitives.id ?? null,
            primitives.tenant_id,
            primitives.kontonummer,
            primitives.kontobezeichnung,
            primitives.kontotyp,
            primitives.kontenklasse ?? null,
            primitives.kontengruppe ?? null,
            primitives.ist_aktiv ?? null,
            primitives.ist_steuerpflichtig ?? null,
            primitives.steuersatz ?? null,
            primitives.beschreibung ?? null,
            primitives.erstellt_von ?? null,
        ]);
        return this.mapRow(result.rows[0]);
    }
    async update(entity) {
        const primitives = entity.toPrimitives();
        if (primitives.id === undefined || primitives.id === null) {
            throw new Error('Cannot update FinanzKonto without primary key');
        }
        const result = await this.pool.query(`UPDATE ${TABLE}
          SET kontonummer = $2,
              kontobezeichnung = $3,
              kontotyp = $4,
              kontenklasse = $5,
              kontengruppe = $6,
              ist_aktiv = COALESCE($7, ist_aktiv),
              ist_steuerpflichtig = COALESCE($8, ist_steuerpflichtig),
              steuersatz = $9,
              beschreibung = $10,
              aktualisiert_am = CURRENT_TIMESTAMP
        WHERE id = $1 AND tenant_id = $11
        RETURNING ${BASE_COLUMNS.join(', ')}
      `, [
            primitives.id,
            primitives.kontonummer,
            primitives.kontobezeichnung,
            primitives.kontotyp,
            primitives.kontenklasse ?? null,
            primitives.kontengruppe ?? null,
            primitives.ist_aktiv ?? null,
            primitives.ist_steuerpflichtig ?? null,
            primitives.steuersatz ?? null,
            primitives.beschreibung ?? null,
            primitives.tenant_id,
        ]);
        if (result.rowCount === 0) {
            throw new Error(`FinanzKonto with id ${primitives.id} not found`);
        }
        return this.mapRow(result.rows[0]);
    }
    async delete(id, tenantId) {
        await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1 AND tenant_id = $2`, [id, tenantId]);
    }
}
exports.FinanzKontoPostgresRepository = FinanzKontoPostgresRepository;
//# sourceMappingURL=finanzKonto-postgres.repository.js.map