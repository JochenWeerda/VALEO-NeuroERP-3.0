import { Pool } from 'pg';
import { FinanzBankkonto, FinanzBankkontoProps } from '../../core/entities/finanzBankkonto.entity';

type DbRow = Record<string, unknown>;

const TABLE = 'finanz.bankkonten';
const COLUMNS = [
  'id',
  'tenant_id',
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

export class FinanzBankkontoPostgresRepository {
  public constructor(private readonly pool: Pool) {}

  private mapRow(row: DbRow): FinanzBankkonto {
    const props: FinanzBankkontoProps = {
      id: row.id as string,
      tenant_id: String(row.tenant_id),
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

    return FinanzBankkonto.create(props);
  }

  public async findById(id: string, tenantId: string): Promise<FinanzBankkonto | null> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 AND tenant_id = $2 LIMIT 1`,
      [id, tenantId],
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

  public async listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzBankkonto[]> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY kontoname ASC LIMIT $2 OFFSET $3`,
      [tenantId, limit, offset],
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  public async list(tenantId: string): Promise<FinanzBankkonto[]> {
    const result = await this.pool.query(
      `SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE tenant_id = $1 ORDER BY kontoname ASC`,
      [tenantId],
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  public async save(entity: FinanzBankkonto): Promise<FinanzBankkonto> {
    const primitives = entity.toPrimitives();
    const result = await this.pool.query(
      `INSERT INTO ${TABLE} (
        id,
        tenant_id,
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
        $11,
        COALESCE($12, true),
        $13,
        $14
      ) RETURNING ${COLUMNS.join(', ')}`,
      [
        primitives.id ?? null,
        primitives.tenant_id,
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
      ]
    );

    return this.mapRow(result.rows[0]);
  }

  public async update(entity: FinanzBankkonto): Promise<FinanzBankkonto> {
    const primitives = entity.toPrimitives();
    if (primitives.id === undefined || primitives.id === null) {
      throw new Error('Cannot update FinanzBankkonto without primary key');
    }

    const result = await this.pool.query(
      `UPDATE ${TABLE}
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
        WHERE id = $1 AND tenant_id = $13
        RETURNING ${COLUMNS.join(', ')}
      `,
      [
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
        primitives.tenant_id,
      ]
    );

    if (result.rowCount === 0) {
      throw new Error(`FinanzBankkonto with id ${primitives.id} not found`);
    }

    return this.mapRow(result.rows[0]);
  }

  public async delete(id: string, tenantId: string): Promise<void> {
    await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1 AND tenant_id = $2`, [id, tenantId]);
  }
}
