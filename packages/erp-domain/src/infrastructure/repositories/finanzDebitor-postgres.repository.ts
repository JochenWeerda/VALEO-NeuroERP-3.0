import { Pool } from 'pg';
import { FinanzDebitor, FinanzDebitorProps } from '../../core/entities/finanzDebitor.entity';

type DbRow = Record<string, unknown>;

const TABLE = 'finanz.debitoren';
const COLUMNS = [
  'id',
  'tenant_id',
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
] as const;

function toNumber(value: unknown): number | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function toBoolean(value: unknown): boolean | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }
  if (typeof value === 'boolean') {
    return value;
  }
  return value === 1 || value === '1' || value === 'true';
}

function toDate(value: unknown): Date | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  return value instanceof Date ? value : new Date(String(value));
}

export class FinanzDebitorPostgresRepository {
  public constructor(private readonly pool: Pool) {}

  private mapRow(row: DbRow): FinanzDebitor {
    const props: FinanzDebitorProps = {
      id: row.id as string,
      tenant_id: String(row.tenant_id),
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

    return FinanzDebitor.create(props);
  }

  public async findById(id: string, tenantId: string): Promise<FinanzDebitor | null> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 AND tenant_id = $2 LIMIT 1`,
      [id, tenantId],
    );
    if (result.rowCount === 0) {
      return null;
    }
    return this.mapRow(result.rows[0]);
  }

  public async findByDebitorNr(tenantId: string, debitorNr: string): Promise<FinanzDebitor | null> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 AND debitor_nr = $2 LIMIT 1`,
      [tenantId, debitorNr],
    );
    if (result.rowCount === 0) {
      return null;
    }
    return this.mapRow(result.rows[0]);
  }

  public async count(tenantId: string): Promise<number> {
    const result = await this.pool.query<{ c: unknown }>(
      `SELECT COUNT(*)::int AS c FROM ${TABLE} WHERE tenant_id = $1`,
      [tenantId],
    );
    const c = result.rows[0]?.c;
    return typeof c === 'number' ? c : parseInt(String(c), 10);
  }

  public async listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzDebitor[]> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY debitor_nr ASC LIMIT $2 OFFSET $3`,
      [tenantId, limit, offset],
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  public async list(tenantId: string): Promise<FinanzDebitor[]> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY debitor_nr ASC`,
      [tenantId],
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  public async save(entity: FinanzDebitor): Promise<FinanzDebitor> {
    const primitives = entity.toPrimitives();
    const result = await this.pool.query(
      `INSERT INTO ${TABLE} (
        id,
        tenant_id,
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
        $10,
        COALESCE($11, true),
        $12,
        $13
      ) RETURNING ${COLUMNS.join(', ')}`,
      [
        primitives.id ?? null,
        primitives.tenant_id,
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
      ]
    );

    return this.mapRow(result.rows[0]);
  }

  public async update(entity: FinanzDebitor): Promise<FinanzDebitor> {
    const primitives = entity.toPrimitives();
    if (primitives.id === undefined || primitives.id === null) {
      throw new Error('Cannot update FinanzDebitor without primary key');
    }

    const result = await this.pool.query(
      `UPDATE ${TABLE}
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
        WHERE id = $1 AND tenant_id = $12
        RETURNING ${COLUMNS.join(', ')}
      `,
      [
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
        primitives.tenant_id,
      ]
    );

    if (result.rowCount === 0) {
      throw new Error(`FinanzDebitor with id ${primitives.id} not found`);
    }

    return this.mapRow(result.rows[0]);
  }

  public async delete(id: string, tenantId: string): Promise<void> {
    await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1 AND tenant_id = $2`, [id, tenantId]);
  }
}
