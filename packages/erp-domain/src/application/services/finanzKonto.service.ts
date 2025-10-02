/**
 * Application service for FinanzKonto generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
import { FinanzKonto, FinanzKontoProps } from '../../core/entities/finanzKonto.entity';
import { FinanzKontoPostgresRepository } from '../../infrastructure/repositories/finanzKonto-postgres.repository';

const ALLOWED_ACCOUNT_TYPES = ['Aktiv', 'Passiv', 'Ertrag', 'Aufwand'];

export interface CreateFinanzKontoDto {
  kontonummer: string;
  kontobezeichnung: string;
  kontotyp: string;
  kontenklasse?: string;
  kontengruppe?: string;
  ist_aktiv?: boolean;
  ist_steuerpflichtig?: boolean;
  steuersatz?: number;
  beschreibung?: string;
  erstellt_von?: string;
}

export type UpdateFinanzKontoDto = Partial<CreateFinanzKontoDto>;

function assertKontotyp(value: string): string {
  if (!ALLOWED_ACCOUNT_TYPES.includes(value)) {
    throw new Error(`Unsupported kontotyp "${value}". Allowed: ${ALLOWED_ACCOUNT_TYPES.join(', ')}`);
  }
  return value;
}

function normalizeProps(dto: CreateFinanzKontoDto, existing?: FinanzKontoProps): FinanzKontoProps {
  const kontonummer = dto.kontonummer?.trim();
  const kontobezeichnung = dto.kontobezeichnung?.trim();
  const kontotyp = dto.kontotyp?.trim();

  if (!kontonummer) {
    throw new Error('kontonummer is required');
  }
  if (!kontobezeichnung) {
    throw new Error('kontobezeichnung is required');
  }
  if (!kontotyp) {
    throw new Error('kontotyp is required');
  }

  const payload: FinanzKontoProps = {
    ...existing,
    kontonummer,
    kontobezeichnung,
    kontotyp: assertKontotyp(kontotyp),
    kontenklasse: dto.kontenklasse?.trim() || existing?.kontenklasse,
    kontengruppe: dto.kontengruppe?.trim() || existing?.kontengruppe,
    ist_aktiv: dto.ist_aktiv ?? existing?.ist_aktiv ?? true,
    ist_steuerpflichtig: dto.ist_steuerpflichtig ?? existing?.ist_steuerpflichtig ?? false,
    steuersatz: dto.steuersatz ?? existing?.steuersatz,
    beschreibung: dto.beschreibung?.trim() || existing?.beschreibung,
    erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,
    id: existing?.id,
    erstellt_am: existing?.erstellt_am,
    aktualisiert_am: existing?.aktualisiert_am,
  };

  if (payload.steuersatz !== undefined && (payload.steuersatz < 0 || payload.steuersatz > 100)) {
    throw new Error('steuersatz must be between 0 and 100');
  }

  return payload;
}

export class FinanzKontoService {
  public constructor(private readonly repository: FinanzKontoPostgresRepository) {}

  public async list(): Promise<FinanzKonto[]> {
    return this.repository.list();
  }

  public async findById(id: string): Promise<FinanzKonto | null> {
    return this.repository.findById(id);
  }

  public async create(payload: CreateFinanzKontoDto): Promise<FinanzKonto> {
    const normalized = normalizeProps(payload);

    const existing = await this.repository.findByKontonummer(normalized.kontonummer);
    if (existing) {
      throw new Error(`FinanzKonto with kontonummer ${normalized.kontonummer} already exists`);
    }

    const entity = FinanzKonto.create(normalized);
    return this.repository.save(entity);
  }

  public async update(id: string, payload: UpdateFinanzKontoDto): Promise<FinanzKonto> {
    const existing = await this.repository.findById(id);
    if (!existing) {
      throw new Error('FinanzKonto not found');
    }

    const currentProps = existing.toPrimitives();
    const normalized = normalizeProps({
      kontonummer: payload.kontonummer ?? currentProps.kontonummer,
      kontobezeichnung: payload.kontobezeichnung ?? currentProps.kontobezeichnung,
      kontotyp: payload.kontotyp ?? currentProps.kontotyp,
      kontenklasse: payload.kontenklasse ?? currentProps.kontenklasse,
      kontengruppe: payload.kontengruppe ?? currentProps.kontengruppe,
      ist_aktiv: payload.ist_aktiv ?? currentProps.ist_aktiv,
      ist_steuerpflichtig: payload.ist_steuerpflichtig ?? currentProps.ist_steuerpflichtig,
      steuersatz: payload.steuersatz ?? currentProps.steuersatz,
      beschreibung: payload.beschreibung ?? currentProps.beschreibung,
      erstellt_von: currentProps.erstellt_von,
    }, currentProps);

    const duplicate = await this.repository.findByKontonummer(normalized.kontonummer);
    if (duplicate && duplicate.toPrimitives().id !== id) {
      throw new Error(`Another FinanzKonto already uses kontonummer ${normalized.kontonummer}`);
    }

    const entity = FinanzKonto.create({ ...normalized, id });
    return this.repository.update(entity);
  }

  public async remove(id: string): Promise<void> {
    await this.repository.delete(id);
  }
}