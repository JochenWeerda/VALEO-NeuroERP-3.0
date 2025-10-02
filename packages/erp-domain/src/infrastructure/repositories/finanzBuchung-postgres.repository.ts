/**
 * FinanzBuchungPostgresRepository generated for FinanzBuchung using CRM migration toolkit.
 * Handles persistence with PostgreSQL using pg.Pool.
 * Start simple: find -> save -> update -> delete -> list. Extend for joins later.
 */

import { Pool } from 'pg';
import { FinanzBuchung } from '../../core/entities/finanzBuchung.entity';

type DbRow = Record<string, unknown>;

export class FinanzBuchungPostgresRepository {
  public constructor(private readonly pool: Pool) {}

  private mapRow(row: DbRow): FinanzBuchung {
    return FinanzBuchung.create({
      id: row['id'] as any,
      buchungsnummer: row['buchungsnummer'] as any,
      buchungsdatum: row['buchungsdatum'] as any,
      belegdatum: row['belegdatum'] as any,
      belegnummer: row['belegnummer'] as any,
      buchungstext: row['buchungstext'] as any,
      sollkonto: row['sollkonto'] as any,
      habenkonto: row['habenkonto'] as any,
      betrag: row['betrag'] as any,
      waehrung: row['waehrung'] as any,
      steuerbetrag: row['steuerbetrag'] as any,
      steuersatz: row['steuersatz'] as any,
      buchungsart: row['buchungsart'] as any,
      referenz_typ: row['referenz_typ'] as any,
      referenz_id: row['referenz_id'] as any,
      ist_storniert: row['ist_storniert'] as any,
      storno_buchung_id: row['storno_buchung_id'] as any,
      erstellt_von: row['erstellt_von'] as any,
      erstellt_am: row['erstellt_am'] as any,
      aktualisiert_am: row['aktualisiert_am'] as any,
    });
  }

  public async findById(id: string): Promise<FinanzBuchung | null> {
    const result = await this.pool.query(
      'SELECT id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am FROM finanz.buchungen WHERE id = $1 LIMIT 1',
      [id]
    );

    if (result.rowCount === 0) {
      return null;
    }

    return this.mapRow(result.rows[0]);
  }

  public async list(): Promise<FinanzBuchung[]> {
    const result = await this.pool.query('SELECT id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am FROM finanz.buchungen ORDER BY id ASC');
    return result.rows.map((row) => this.mapRow(row));
  }

  public async save(entity: FinanzBuchung): Promise<void> {
    const primitives = entity.toPrimitives();
    await this.pool.query(
      'INSERT INTO finanz.buchungen (id, buchungsnummer, buchungsdatum, belegdatum, belegnummer, buchungstext, sollkonto, habenkonto, betrag, waehrung, steuerbetrag, steuersatz, buchungsart, referenz_typ, referenz_id, ist_storniert, storno_buchung_id, erstellt_von, erstellt_am, aktualisiert_am) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20) ON CONFLICT (id) DO NOTHING',
      [primitives.id, primitives.buchungsnummer, primitives.buchungsdatum, primitives.belegdatum, primitives.belegnummer, primitives.buchungstext, primitives.sollkonto, primitives.habenkonto, primitives.betrag, primitives.waehrung, primitives.steuerbetrag, primitives.steuersatz, primitives.buchungsart, primitives.referenz_typ, primitives.referenz_id, primitives.ist_storniert, primitives.storno_buchung_id, primitives.erstellt_von, primitives.erstellt_am, primitives.aktualisiert_am]
    );
  }

  public async update(entity: FinanzBuchung): Promise<void> {
    const primitives = entity.toPrimitives();
    await this.pool.query(
      'UPDATE finanz.buchungen SET buchungsnummer = $2, buchungsdatum = $3, belegdatum = $4, belegnummer = $5, buchungstext = $6, sollkonto = $7, habenkonto = $8, betrag = $9, waehrung = $10, steuerbetrag = $11, steuersatz = $12, buchungsart = $13, referenz_typ = $14, referenz_id = $15, ist_storniert = $16, storno_buchung_id = $17, erstellt_von = $18, erstellt_am = $19, aktualisiert_am = $20 WHERE id = $1',
      [primitives.id, primitives.buchungsnummer, primitives.buchungsdatum, primitives.belegdatum, primitives.belegnummer, primitives.buchungstext, primitives.sollkonto, primitives.habenkonto, primitives.betrag, primitives.waehrung, primitives.steuerbetrag, primitives.steuersatz, primitives.buchungsart, primitives.referenz_typ, primitives.referenz_id, primitives.ist_storniert, primitives.storno_buchung_id, primitives.erstellt_von, primitives.erstellt_am, primitives.aktualisiert_am]
    );
  }

  public async delete(id: string): Promise<void> {
    await this.pool.query('DELETE FROM finanz.buchungen WHERE id = $1', [id]);
  }
}
