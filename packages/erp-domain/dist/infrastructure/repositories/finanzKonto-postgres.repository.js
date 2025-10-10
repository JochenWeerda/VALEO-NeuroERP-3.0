"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKontoPostgresRepository = void 0;
const finanzKonto_entity_1 = require("../../core/entities/finanzKonto.entity");
const TABLE = 'finanz.konten';
const BASE_COLUMNS = [
    'id',
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
    async findById(id) {
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 LIMIT 1`, [id]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async findByKontonummer(kontonummer) {
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} WHERE kontonummer = $1 LIMIT 1`, [kontonummer]);
        if (result.rowCount === 0) {
            return null;
        }
        return this.mapRow(result.rows[0]);
    }
    async list() {
        const result = await this.pool.query(`SELECT ${BASE_COLUMNS.join(', ')} FROM ${TABLE} ORDER BY kontonummer ASC`);
        return result.rows.map((row) => this.mapRow(row));
    }
    async save(entity) {
        const primitives = entity.toPrimitives();
        const result = await this.pool.query(`INSERT INTO ${TABLE} (
        id,
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
        COALESCE($7, true),
        COALESCE($8, false),
        $9,
        $10,
        $11
      )
      RETURNING ${BASE_COLUMNS.join(', ')}
      `, [
            primitives.id ?? null,
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
        WHERE id = $1
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
        ]);
        if (result.rowCount === 0) {
            throw new Error(`FinanzKonto with id ${primitives.id} not found`);
        }
        return this.mapRow(result.rows[0]);
    }
    async delete(id) {
        await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1`, [id]);
    }
}
exports.FinanzKontoPostgresRepository = FinanzKontoPostgresRepository;
//# sourceMappingURL=finanzKonto-postgres.repository.js.map