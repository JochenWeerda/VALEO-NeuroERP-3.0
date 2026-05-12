import { FinanzKreditor, FinanzKreditorProps } from '../../core/entities/finanzKreditor.entity';
import { FinanzKreditorPostgresRepository } from '../../infrastructure/repositories/finanzKreditor-postgres.repository';
import { clampLimit, clampOffset, ListResult } from '../../presentation/types/api-pagination';

const DEFAULT_PAYMENT_TARGET_DAYS = 30;

export interface CreateFinanzKreditorDto {
  lieferanten_id?: string;
  kreditor_nr: string;
  zahlungsziel?: number;
  zahlungsart?: string;
  bankverbindung?: string;
  steuer_id?: string;
  steuernummer?: string;
  ist_aktiv?: boolean;
  notizen?: string;
  erstellt_von?: string;
}

export type UpdateFinanzKreditorDto = Partial<CreateFinanzKreditorDto>;

function tenantFrom(existing?: FinanzKreditorProps, tenantForCreate?: string): string {
  const t = existing?.tenant_id ?? tenantForCreate?.trim();
  if (!t) {
    throw new Error('tenant_id is required');
  }
  return t;
}

function normalize(dto: CreateFinanzKreditorDto, existing?: FinanzKreditorProps, tenantForCreate?: string): FinanzKreditorProps {
  const kreditorNr = dto.kreditor_nr?.trim();
  if (kreditorNr === undefined || kreditorNr === null) {
    throw new Error('kreditor_nr is required');
  }

  if (dto.zahlungsziel !== undefined && dto.zahlungsziel < 0) {
    throw new Error('zahlungsziel must be positive');
  }

  return {
    ...existing,
    tenant_id: tenantFrom(existing, tenantForCreate),
    lieferanten_id: dto.lieferanten_id ?? existing?.lieferanten_id,
    kreditor_nr: kreditorNr,
    zahlungsziel: dto.zahlungsziel ?? existing?.zahlungsziel ?? DEFAULT_PAYMENT_TARGET_DAYS,
    zahlungsart: dto.zahlungsart ?? existing?.zahlungsart,
    bankverbindung: dto.bankverbindung ?? existing?.bankverbindung,
    steuernummer: dto.steuer_id ?? existing?.steuernummer,
    ist_aktiv: dto.ist_aktiv ?? existing?.ist_aktiv ?? true,
    notizen: dto.notizen ?? existing?.notizen,
    erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,
    id: existing?.id,
    erstellt_am: existing?.erstellt_am,
    aktualisiert_am: existing?.aktualisiert_am,
  };
}

export class FinanzKreditorService {
  public constructor(private readonly repository: FinanzKreditorPostgresRepository) {}

  public async list(tenantId: string): Promise<FinanzKreditor[]> {
    return this.repository.list(tenantId);
  }

  public async listPaged(
    tenantId: string,
    options?: { limit?: number; offset?: number },
  ): Promise<ListResult<FinanzKreditor>> {
    const limit = clampLimit(options?.limit);
    const offset = clampOffset(options?.offset);
    const items = await this.repository.listPaged(tenantId, limit, offset);
    const total = await this.repository.count(tenantId);
    return { items, total };
  }

  public async findById(id: string, tenantId: string): Promise<FinanzKreditor | null> {
    return this.repository.findById(id, tenantId);
  }

  public async create(tenantId: string, payload: CreateFinanzKreditorDto): Promise<FinanzKreditor> {
    const normalized = normalize(payload, undefined, tenantId);
    const existingNr = await this.repository.findByKreditorNr(tenantId, normalized.kreditor_nr);
    if (existingNr !== undefined && existingNr !== null) {
      throw new Error(`Kreditor ${normalized.kreditor_nr} already exists`);
    }

    const entity = FinanzKreditor.create(normalized);
    return this.repository.save(entity);
  }

  public async update(id: string, tenantId: string, payload: UpdateFinanzKreditorDto): Promise<FinanzKreditor> {
    const existingRow = await this.repository.findById(id, tenantId);
    if (existingRow === undefined || existingRow === null) {
      throw new Error('FinanzKreditor not found');
    }

    const current = existingRow.toPrimitives();
    const normalized = normalize(
      {
        lieferanten_id: payload.lieferanten_id ?? current.lieferanten_id,
        kreditor_nr: payload.kreditor_nr ?? current.kreditor_nr,
        zahlungsziel: payload.zahlungsziel ?? current.zahlungsziel,
        zahlungsart: payload.zahlungsart ?? current.zahlungsart,
        bankverbindung: payload.bankverbindung ?? current.bankverbindung,
        steuer_id: payload.steuer_id ?? current.steuernummer,
        ist_aktiv: payload.ist_aktiv ?? current.ist_aktiv,
        notizen: payload.notizen ?? current.notizen,
        erstellt_von: current.erstellt_von,
      },
      current,
    );

    const duplicate = await this.repository.findByKreditorNr(tenantId, normalized.kreditor_nr);
    if ((duplicate !== undefined && duplicate !== null) && duplicate.toPrimitives().id !== id) {
      throw new Error(`Another Kreditor already uses kreditor_nr ${normalized.kreditor_nr}`);
    }

    const entity = FinanzKreditor.create({ ...normalized, id });
    return this.repository.update(entity);
  }

  public async remove(id: string, tenantId: string): Promise<void> {
    await this.repository.delete(id, tenantId);
  }
}
