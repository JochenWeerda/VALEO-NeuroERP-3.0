/**

 * Application service for FinanzKonto generated via CRM toolkit.

 * Encapsulates use-cases and translates primitives to domain entities.

 */

import { FinanzKonto, FinanzKontoProps } from '../../core/entities/finanzKonto.entity';

import { FinanzKontoPostgresRepository } from '../../infrastructure/repositories/finanzKonto-postgres.repository';

import { ListResult, clampLimit, clampOffset } from '../../presentation/types/api-pagination';



const TAX_RATE_MIN = 0;

const TAX_RATE_MAX = 100;



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



function tenantFrom(existing?: FinanzKontoProps, tenantForCreate?: string): string {

  const t = existing?.tenant_id ?? tenantForCreate?.trim();

  if (!t) {

    throw new Error('tenant_id is required');

  }

  return t;

}



function normalizeProps(dto: CreateFinanzKontoDto, existing?: FinanzKontoProps, tenantForCreate?: string): FinanzKontoProps {

  const kontonummer = dto.kontonummer?.trim();

  const kontobezeichnung = dto.kontobezeichnung?.trim();

  const kontotyp = dto.kontotyp?.trim();



  if (kontonummer === undefined || kontonummer === null) {

    throw new Error('kontonummer is required');

  }

  if (kontobezeichnung === undefined || kontobezeichnung === null) {

    throw new Error('kontobezeichnung is required');

  }

  if (kontotyp === undefined || kontotyp === null) {

    throw new Error('kontotyp is required');

  }



  const payload: FinanzKontoProps = {

    ...existing,

    tenant_id: tenantFrom(existing, tenantForCreate),

    kontonummer,

    kontobezeichnung,

    kontotyp: assertKontotyp(kontotyp),

    kontenklasse: dto.kontenklasse?.trim() ?? existing?.kontenklasse,

    kontengruppe: dto.kontengruppe?.trim() ?? existing?.kontengruppe,

    ist_aktiv: dto.ist_aktiv ?? existing?.ist_aktiv ?? true,

    ist_steuerpflichtig: dto.ist_steuerpflichtig ?? existing?.ist_steuerpflichtig ?? false,

    steuersatz: dto.steuersatz ?? existing?.steuersatz,

    beschreibung: dto.beschreibung?.trim() ?? existing?.beschreibung,

    erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,

    id: existing?.id,

    erstellt_am: existing?.erstellt_am,

    aktualisiert_am: existing?.aktualisiert_am,

  };



  if (payload.steuersatz !== undefined && (payload.steuersatz < TAX_RATE_MIN || payload.steuersatz > TAX_RATE_MAX)) {

    throw new Error('steuersatz must be between 0 and 100');

  }



  return payload;

}



export class FinanzKontoService {

  public constructor(private readonly repository: FinanzKontoPostgresRepository) {}



  public async list(tenantId: string): Promise<FinanzKonto[]> {

    return this.repository.list(tenantId);

  }



  public async listPaged(

    tenantId: string,

    options?: { limit?: number; offset?: number },

  ): Promise<ListResult<FinanzKonto>> {

    const limit = clampLimit(options?.limit);

    const offset = clampOffset(options?.offset);

    const items = await this.repository.listPaged(tenantId, limit, offset);

    const total = await this.repository.count(tenantId);

    return { items, total };

  }



  public async findById(id: string, tenantId: string): Promise<FinanzKonto | null> {

    return this.repository.findById(id, tenantId);

  }



  public async create(tenantId: string, payload: CreateFinanzKontoDto): Promise<FinanzKonto> {

    const normalized = normalizeProps(payload, undefined, tenantId);



    const existingNr = await this.repository.findByKontonummer(tenantId, normalized.kontonummer);

    if (existingNr !== undefined && existingNr !== null) {

      throw new Error(`FinanzKonto with kontonummer ${normalized.kontonummer} already exists`);

    }



    const entity = FinanzKonto.create(normalized);

    return this.repository.save(entity);

  }



  public async update(id: string, tenantId: string, payload: UpdateFinanzKontoDto): Promise<FinanzKonto> {

    const existingRow = await this.repository.findById(id, tenantId);

    if (existingRow === undefined || existingRow === null) {

      throw new Error('FinanzKonto not found');

    }



    const currentProps = existingRow.toPrimitives();

    const normalized = normalizeProps(

      {

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

      },

      currentProps,

    );



    const duplicate = await this.repository.findByKontonummer(tenantId, normalized.kontonummer);

    if ((duplicate !== undefined && duplicate !== null) && duplicate.toPrimitives().id !== id) {

      throw new Error(`Another FinanzKonto already uses kontonummer ${normalized.kontonummer}`);

    }



    const entity = FinanzKonto.create({ ...normalized, id });

    return this.repository.update(entity);

  }



  public async remove(id: string, tenantId: string): Promise<void> {

    await this.repository.delete(id, tenantId);

  }

}


