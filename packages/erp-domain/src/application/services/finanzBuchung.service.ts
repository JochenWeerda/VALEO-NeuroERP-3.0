/**
 * Application service for FinanzBuchung generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
import { randomUUID } from 'crypto';
import { FinanzBuchung, FinanzBuchungProps } from '../../core/entities/finanzBuchung.entity';
import { FinanzBuchungPostgresRepository } from '../../infrastructure/repositories/finanzBuchung-postgres.repository';
import { ListResult, clampLimit, clampOffset } from '../../presentation/types/api-pagination';

const RANDOM_SUFFIX_LENGTH = 6;

export interface CreateFinanzBuchungDto {
  buchungsnummer?: string;
  buchungsdatum: string | Date;
  belegdatum: string | Date;
  belegnummer?: string;
  buchungstext: string;
  sollkonto?: string;
  habenkonto?: string;
  betrag: number;
  waehrung?: string;
  steuerbetrag?: number;
  steuersatz?: number;
  buchungsart?: string;
  referenz_typ?: string;
  referenz_id?: string;
  ist_storniert?: boolean;
  storno_buchung_id?: string;
  erstellt_von?: string;
}

export type UpdateFinanzBuchungDto = Partial<CreateFinanzBuchungDto>;

function toDate(value: string | Date): Date {
  if (value instanceof Date) {
    return value;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    throw new Error(`Invalid date value: ${value}`);
  }
  return parsed;
}

function tenantFrom(existing?: FinanzBuchungProps, tenantForCreate?: string): string {
  const t = existing?.tenant_id ?? tenantForCreate?.trim();
  if (!t) {
    throw new Error('tenant_id is required');
  }
  return t;
}

function normalizeBuchung(dto: CreateFinanzBuchungDto, existing?: FinanzBuchungProps, tenantForCreate?: string): FinanzBuchungProps {
  const rawText = dto.buchungstext ?? existing?.buchungstext;
  const textTrim = rawText?.trim();
  if (textTrim === undefined || textTrim.length === 0) {
    throw new Error('buchungstext is required');
  }

  if (dto.betrag === undefined || dto.betrag === null) {
    throw new Error('betrag is required');
  }
  if (Number(dto.betrag) === 0) {
    throw new Error('betrag must not be zero');
  }
  if (dto.sollkonto != null && dto.habenkonto != null && dto.sollkonto === dto.habenkonto) {
    throw new Error('sollkonto and habenkonto must differ');
  }

  const payload: FinanzBuchungProps = {
    ...existing,
    tenant_id: tenantFrom(existing, tenantForCreate),
    buchungsnummer: dto.buchungsnummer?.trim() ?? existing?.buchungsnummer ?? '',
    buchungsdatum: toDate(dto.buchungsdatum ?? existing?.buchungsdatum ?? new Date()),
    belegdatum: toDate(dto.belegdatum ?? existing?.belegdatum ?? new Date()),
    belegnummer: dto.belegnummer?.trim() ?? existing?.belegnummer,
    buchungstext: textTrim,
    sollkonto: dto.sollkonto ?? existing?.sollkonto,
    habenkonto: dto.habenkonto ?? existing?.habenkonto,
    betrag: Number(dto.betrag),
    waehrung: dto.waehrung ?? existing?.waehrung ?? 'EUR',
    steuerbetrag: dto.steuerbetrag ?? existing?.steuerbetrag ?? 0,
    steuersatz: dto.steuersatz ?? existing?.steuersatz ?? 0,
    buchungsart: dto.buchungsart ?? existing?.buchungsart,
    referenz_typ: dto.referenz_typ ?? existing?.referenz_typ,
    referenz_id: dto.referenz_id ?? existing?.referenz_id,
    ist_storniert: dto.ist_storniert ?? existing?.ist_storniert ?? false,
    storno_buchung_id: dto.storno_buchung_id ?? existing?.storno_buchung_id,
    erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,
    id: existing?.id,
    erstellt_am: existing?.erstellt_am,
    aktualisiert_am: existing?.aktualisiert_am,
  };

  if (payload.buchungsnummer === undefined || payload.buchungsnummer === null || payload.buchungsnummer.length === 0) {
    payload.buchungsnummer = `BCH-${Date.now()}-${randomUUID().slice(0, RANDOM_SUFFIX_LENGTH)}`;
  }

  return payload;
}

export class FinanzBuchungService {
  public constructor(private readonly repository: FinanzBuchungPostgresRepository) {}

  public async list(tenantId: string): Promise<FinanzBuchung[]> {
    return this.repository.list(tenantId);
  }

  public async listPaged(
    tenantId: string,
    options?: { limit?: number; offset?: number },
  ): Promise<ListResult<FinanzBuchung>> {
    const limit = clampLimit(options?.limit);
    const offset = clampOffset(options?.offset);
    const items = await this.repository.listPaged(tenantId, limit, offset);
    const total = await this.repository.count(tenantId);
    return { items, total };
  }

  public async findById(id: string, tenantId: string): Promise<FinanzBuchung | null> {
    return this.repository.findById(id, tenantId);
  }

  public async create(tenantId: string, payload: CreateFinanzBuchungDto): Promise<FinanzBuchung> {
    const normalized = normalizeBuchung(payload, undefined, tenantId);
    const dup = await this.repository.findByBuchungsnummer(tenantId, normalized.buchungsnummer);
    if (dup !== undefined && dup !== null) {
      throw new Error(`Buchung mit Nummer ${normalized.buchungsnummer} existiert bereits`);
    }
    const id = normalized.id ?? randomUUID();
    const entity = FinanzBuchung.create({ ...normalized, id });
    await this.repository.save(entity);
    return entity;
  }

  public async update(id: string, tenantId: string, payload: UpdateFinanzBuchungDto): Promise<FinanzBuchung> {
    const existingRow = await this.repository.findById(id, tenantId);
    if (existingRow === undefined || existingRow === null) {
      throw new Error('FinanzBuchung not found');
    }

    const existingProps = existingRow.toPrimitives();
    const normalized = normalizeBuchung(
      {
        buchungsnummer: payload.buchungsnummer ?? existingProps.buchungsnummer,
        buchungsdatum: payload.buchungsdatum ?? existingProps.buchungsdatum,
        belegdatum: payload.belegdatum ?? existingProps.belegdatum,
        belegnummer: payload.belegnummer ?? existingProps.belegnummer,
        buchungstext: payload.buchungstext ?? existingProps.buchungstext,
        sollkonto: payload.sollkonto ?? existingProps.sollkonto,
        habenkonto: payload.habenkonto ?? existingProps.habenkonto,
        betrag: payload.betrag ?? existingProps.betrag,
        waehrung: payload.waehrung ?? existingProps.waehrung,
        steuerbetrag: payload.steuerbetrag ?? existingProps.steuerbetrag,
        steuersatz: payload.steuersatz ?? existingProps.steuersatz,
        buchungsart: payload.buchungsart ?? existingProps.buchungsart,
        referenz_typ: payload.referenz_typ ?? existingProps.referenz_typ,
        referenz_id: payload.referenz_id ?? existingProps.referenz_id,
        ist_storniert: payload.ist_storniert ?? existingProps.ist_storniert,
        storno_buchung_id: payload.storno_buchung_id ?? existingProps.storno_buchung_id,
        erstellt_von: existingProps.erstellt_von,
      },
      existingProps,
    );

    const dup = await this.repository.findByBuchungsnummer(tenantId, normalized.buchungsnummer);
    if ((dup !== undefined && dup !== null) && dup.toPrimitives().id !== id) {
      throw new Error(`Another Buchung already uses buchungsnummer ${normalized.buchungsnummer}`);
    }

    const entity = FinanzBuchung.create({ ...normalized, id });
    await this.repository.update(entity);
    return entity;
  }

  public async remove(id: string, tenantId: string): Promise<void> {
    await this.repository.delete(id, tenantId);
  }
}
