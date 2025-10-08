import { Pool } from 'pg';
import { FinanzKreditor, FinanzKreditorProps } from '../../core/entities/finanzKreditor.entity';

type DbRow = Record<string, unknown>;

const TABLE = 'finanz.kreditoren';
const COLUMNS = [
  'id',
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

export class FinanzKreditorPostgresRepository {
  public constructor(private readonly pool: Pool) {}

  private mapRow(row: DbRow): FinanzKreditor {
    const props: FinanzKreditorProps = {
      id: row.id as string,
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

    return FinanzKreditor.create(props);
  }

  public async findById(id: string): Promise<FinanzKreditor | null> {
    const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE id = $1 LIMIT 1`, [id]);
    if (result.rowCount === 0) {
      return null;
    }
    return this.mapRow(result.rows[0]);
  }

  public async findByKreditorNr(kreditorNr: string): Promise<FinanzKreditor | null> {
    const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} WHERE kreditor_nr = $1 LIMIT 1`, [kreditorNr]);
    if (result.rowCount === 0) {
      return null;
    }
    return this.mapRow(result.rows[0]);
  }

  public async list(): Promise<FinanzKreditor[]> {
    const result = await this.pool.query(`SELECT ${COLUMNS.join(', ')} FROM ${TABLE} ORDER BY kreditor_nr ASC`);
    return result.rows.map((row) => this.mapRow(row));
  }

  public async save(entity: FinanzKreditor): Promise<FinanzKreditor> {
    const primitives = entity.toPrimitives();
    const result = await this.pool.query(
      `INSERT INTO ${TABLE} (
        id,
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
        COALESCE($9, true),
        $10,
        $11
      ) RETURNING ${COLUMNS.join(', ')}`,
      [
        primitives.id ?? null,
        primitives.lieferanten_id ?? null,
        primitives.kreditor_nr,
        primitives.zahlungsziel ?? null,
        primitives.zahlungsart ?? null,
        primitives.bankverbindung ?? null,
        primitives.steuernummer ?? null,
        primitives.ist_aktiv ?? null,
        primitives.notizen ?? null,
        primitives.erstellt_von ?? null,
      ]
    );

    return this.mapRow(result.rows[0]);
  }

  public async update(entity: FinanzKreditor): Promise<FinanzKreditor> {
    const primitives = entity.toPrimitives();
    if (primitives.id === undefined || primitives.id === null) {
      throw new Error('Cannot update FinanzKreditor without primary key');
    }

    const result = await this.pool.query(
      `UPDATE ${TABLE}
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
        WHERE id = $1
        RETURNING ${COLUMNS.join(', ')}
      `,
      [
        primitives.id,
        primitives.lieferanten_id ?? null,
        primitives.kreditor_nr,
        primitives.zahlungsziel ?? null,
        primitives.zahlungsart ?? null,
        primitives.bankverbindung ?? null,
        primitives.steuernummer ?? null,
        primitives.ist_aktiv ?? null,
        primitives.notizen ?? null,
      ]
    );

    if (result.rowCount === 0) {
      throw new Error(`FinanzKreditor with id ${primitives.id} not found`);
    }

    return this.mapRow(result.rows[0]);
  }

  public async delete(id: string): Promise<void> {
    await this.pool.query(`DELETE FROM ${TABLE} WHERE id = $1`, [id]);
  }
}

