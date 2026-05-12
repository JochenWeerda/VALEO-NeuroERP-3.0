/**
 * FinanzBuchungPostgresRepository generated for FinanzBuchung using CRM migration toolkit.
 * Handles persistence with PostgreSQL using pg.Pool.
 */
import { Pool } from 'pg';
import { FinanzBuchung } from '../../core/entities/finanzBuchung.entity';

type DbRow = Record<string, unknown>;

interface FinanzBuchungRow {
  id: string;
  tenant_id: string | null;
  buchungsnummer: string | null;
  buchungsdatum: Date | string;
  belegdatum: Date | string;
  belegnummer: string | null;
  buchungstext: string;
  sollkonto: string | null;
  habenkonto: string | null;
  betrag: number | string;
  waehrung: string | null;
  steuerbetrag: number | string | null;
  steuersatz: number | string | null;
  buchungsart: string | null;
  referenz_typ: string | null;
  referenz_id: string | null;
  ist_storniert: boolean | null;
  storno_buchung_id: string | null;
  erstellt_von: string | null;
  erstellt_am: Date | string | null;
  aktualisiert_am: Date | string | null;
}

const toStringOrUndefined = (value: unknown | null): string | undefined => {
  if (value === null || value === undefined) {
    return undefined;
  }
  return typeof value === 'string' ? value : String(value);
};

const toStringOrEmpty = (value: unknown | null, fallback = ''): string => {
  return toStringOrUndefined(value) ?? fallback;
};

const toNumberOrUndefined = (value: unknown | null): number | undefined => {
  if (value === null || value === undefined) {
    return undefined;
  }
  return typeof value === 'number' ? value : Number(value);
};

const toBooleanOrUndefined = (value: unknown | null): boolean | undefined => {
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

const toDateOrUndefined = (value: unknown | null): Date | undefined => {
  if (value === null || value === undefined) {
    return undefined;
  }
  if (value instanceof Date) {
    return value;
  }
  const parsed = new Date(String(value));
  return Number.isNaN(parsed.getTime()) ? undefined : parsed;
};

export class FinanzBuchungPostgresRepository {
  public constructor(private readonly pool: Pool) {}

  private mapRow(row: DbRow): FinanzBuchung {
    const record = row as unknown as FinanzBuchungRow;

    return FinanzBuchung.create({
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

  private static readonly LIST_SELECT =
    'SELECT id, tenant_id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am FROM finanz.buchungen';

  public async findById(id: string, tenantId: string): Promise<FinanzBuchung | null> {
    const result = await this.pool.query(
      `${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE id = $1 AND tenant_id = $2 LIMIT 1`,
      [id, tenantId],
    );

    if (result.rowCount === 0) {
      return null;
    }

    return this.mapRow(result.rows[0]);
  }

  public async findByBuchungsnummer(tenantId: string, buchungsnummer: string): Promise<FinanzBuchung | null> {
    const result = await this.pool.query(
      `${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE tenant_id = $1 AND buchungsnummer = $2 LIMIT 1`,
      [tenantId, buchungsnummer],
    );
    if (result.rowCount === 0) {
      return null;
    }
    return this.mapRow(result.rows[0]);
  }

  public async count(tenantId: string): Promise<number> {
    const result = await this.pool.query<{ c: unknown }>(
      'SELECT COUNT(*)::int AS c FROM finanz.buchungen WHERE tenant_id = $1',
      [tenantId],
    );
    const c = result.rows[0]?.c;
    return typeof c === 'number' ? c : parseInt(String(c), 10);
  }

  public async listPaged(tenantId: string, limit: number, offset: number): Promise<FinanzBuchung[]> {
    const result = await this.pool.query(
      `${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE tenant_id = $1 ORDER BY id ASC LIMIT $2 OFFSET $3`,
      [tenantId, limit, offset],
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  public async list(tenantId: string): Promise<FinanzBuchung[]> {
    const result = await this.pool.query(
      `${FinanzBuchungPostgresRepository.LIST_SELECT} WHERE tenant_id = $1 ORDER BY id ASC`,
      [tenantId],
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  public async save(entity: FinanzBuchung): Promise<void> {
    const primitives = entity.toPrimitives();
    await this.pool.query(
      `INSERT INTO finanz.buchungen (id, tenant_id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21) ON CONFLICT (id) DO NOTHING`,
      [
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
      ]
    );
  }

  public async update(entity: FinanzBuchung): Promise<void> {
    const primitives = entity.toPrimitives();
    await this.pool.query(
      'UPDATE finanz.buchungen SET buchungsnummer = $2, buchungsdatum = $3, belegdatum = $4, belegnummer = $5, buchungstext = $6, sollkonto = $7, habenkonto = $8, betrag = $9, waehrung = $10, steuerbetrag = $11, steuersatz = $12, buchungsart = $13, referenz_typ = $14, referenz_id = $15, ist_storniert = $16, storno_buchung_id = $17, erstellt_von = $18, erstellt_am = $19, aktualisiert_am = $20 WHERE id = $1 AND tenant_id = $21',
      [
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
      ]
    );
  }

  public async delete(id: string, tenantId: string): Promise<void> {
    await this.pool.query('DELETE FROM finanz.buchungen WHERE id = $1 AND tenant_id = $2', [id, tenantId]);
  }
}
