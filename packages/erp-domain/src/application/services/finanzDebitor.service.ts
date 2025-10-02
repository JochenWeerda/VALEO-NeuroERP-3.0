import { FinanzDebitor, FinanzDebitorProps } from '../../core/entities/finanzDebitor.entity';
import { FinanzDebitorPostgresRepository } from '../../infrastructure/repositories/finanzDebitor-postgres.repository';

export interface CreateFinanzDebitorDto {
  kunden_id?: string;
  debitor_nr: string;
  kreditlimit?: number;
  zahlungsziel?: number;
  zahlungsart?: string;
  bankverbindung?: string;
  steuernummer?: string;
  ust_id?: string;
  ist_aktiv?: boolean;
  notizen?: string;
  erstellt_von?: string;
}

export type UpdateFinanzDebitorDto = Partial<CreateFinanzDebitorDto>;

function normalize(dto: CreateFinanzDebitorDto, existing?: FinanzDebitorProps): FinanzDebitorProps {
  const debitorNr = dto.debitor_nr?.trim();
  if (!debitorNr) {
    throw new Error('debitor_nr is required');
  }

  if (dto.kreditlimit !== undefined && dto.kreditlimit < 0) {
    throw new Error('kreditlimit must be positive');
  }
  if (dto.zahlungsziel !== undefined && dto.zahlungsziel < 0) {
    throw new Error('zahlungsziel must be positive');
  }

  return {
    ...existing,
    kunden_id: dto.kunden_id ?? existing?.kunden_id,
    debitor_nr: debitorNr,
    kreditlimit: dto.kreditlimit ?? existing?.kreditlimit ?? 0,
    zahlungsziel: dto.zahlungsziel ?? existing?.zahlungsziel ?? 30,
    zahlungsart: dto.zahlungsart ?? existing?.zahlungsart,
    bankverbindung: dto.bankverbindung ?? existing?.bankverbindung,
    steuernummer: dto.steuernummer ?? existing?.steuernummer,
    ust_id: dto.ust_id ?? existing?.ust_id,
    ist_aktiv: dto.ist_aktiv ?? existing?.ist_aktiv ?? true,
    notizen: dto.notizen ?? existing?.notizen,
    erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,
    id: existing?.id,
    erstellt_am: existing?.erstellt_am,
    aktualisiert_am: existing?.aktualisiert_am,
  };
}

export class FinanzDebitorService {
  public constructor(private readonly repository: FinanzDebitorPostgresRepository) {}

  public async list(): Promise<FinanzDebitor[]> {
    return this.repository.list();
  }

  public async findById(id: string): Promise<FinanzDebitor | null> {
    return this.repository.findById(id);
  }

  public async create(payload: CreateFinanzDebitorDto): Promise<FinanzDebitor> {
    const normalized = normalize(payload);
    const existing = await this.repository.findByDebitorNr(normalized.debitor_nr);
    if (existing) {
      throw new Error(`Debitor ${normalized.debitor_nr} already exists`);
    }
    const entity = FinanzDebitor.create(normalized);
    return this.repository.save(entity);
  }

  public async update(id: string, payload: UpdateFinanzDebitorDto): Promise<FinanzDebitor> {
    const existing = await this.repository.findById(id);
    if (!existing) {
      throw new Error('FinanzDebitor not found');
    }

    const current = existing.toPrimitives();
    const normalized = normalize({
      kunden_id: payload.kunden_id ?? current.kunden_id,
      debitor_nr: payload.debitor_nr ?? current.debitor_nr,
      kreditlimit: payload.kreditlimit ?? current.kreditlimit,
      zahlungsziel: payload.zahlungsziel ?? current.zahlungsziel,
      zahlungsart: payload.zahlungsart ?? current.zahlungsart,
      bankverbindung: payload.bankverbindung ?? current.bankverbindung,
      steuernummer: payload.steuernummer ?? current.steuernummer,
      ust_id: payload.ust_id ?? current.ust_id,
      ist_aktiv: payload.ist_aktiv ?? current.ist_aktiv,
      notizen: payload.notizen ?? current.notizen,
      erstellt_von: current.erstellt_von,
    }, current);

    const duplicate = await this.repository.findByDebitorNr(normalized.debitor_nr);
    if (duplicate && duplicate.toPrimitives().id !== id) {
      throw new Error(`Another Debitor already uses debitor_nr ${normalized.debitor_nr}`);
    }

    const entity = FinanzDebitor.create({ ...normalized, id });
    return this.repository.update(entity);
  }

  public async remove(id: string): Promise<void> {
    await this.repository.delete(id);
  }
}