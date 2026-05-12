"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzDebitorService = void 0;
const finanzDebitor_entity_1 = require("../../core/entities/finanzDebitor.entity");
const api_pagination_1 = require("../../presentation/types/api-pagination");
const DEFAULT_PAYMENT_TARGET_DAYS = 30;
function tenantFrom(existing, tenantForCreate) {
    const t = existing?.tenant_id ?? tenantForCreate?.trim();
    if (!t) {
        throw new Error('tenant_id is required');
    }
    return t;
}
function normalize(dto, existing, tenantForCreate) {
    const debitorNr = dto.debitor_nr?.trim();
    if (debitorNr === undefined || debitorNr === null) {
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
        tenant_id: tenantFrom(existing, tenantForCreate),
        kunden_id: dto.kunden_id ?? existing?.kunden_id,
        debitor_nr: debitorNr,
        kreditlimit: dto.kreditlimit ?? existing?.kreditlimit ?? 0,
        zahlungsziel: dto.zahlungsziel ?? existing?.zahlungsziel ?? DEFAULT_PAYMENT_TARGET_DAYS,
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
class FinanzDebitorService {
    constructor(repository) {
        this.repository = repository;
    }
    async list(tenantId) {
        return this.repository.list(tenantId);
    }
    async listPaged(tenantId, options) {
        const limit = (0, api_pagination_1.clampLimit)(options?.limit);
        const offset = (0, api_pagination_1.clampOffset)(options?.offset);
        const items = await this.repository.listPaged(tenantId, limit, offset);
        const total = await this.repository.count(tenantId);
        return { items, total };
    }
    async findById(id, tenantId) {
        return this.repository.findById(id, tenantId);
    }
    async create(tenantId, payload) {
        const normalized = normalize(payload, undefined, tenantId);
        const existingNr = await this.repository.findByDebitorNr(tenantId, normalized.debitor_nr);
        if (existingNr !== undefined && existingNr !== null) {
            throw new Error(`Debitor ${normalized.debitor_nr} already exists`);
        }
        const entity = finanzDebitor_entity_1.FinanzDebitor.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, tenantId, payload) {
        const existingRow = await this.repository.findById(id, tenantId);
        if (existingRow === undefined || existingRow === null) {
            throw new Error('FinanzDebitor not found');
        }
        const current = existingRow.toPrimitives();
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
        const duplicate = await this.repository.findByDebitorNr(tenantId, normalized.debitor_nr);
        if ((duplicate !== undefined && duplicate !== null) && duplicate.toPrimitives().id !== id) {
            throw new Error(`Another Debitor already uses debitor_nr ${normalized.debitor_nr}`);
        }
        const entity = finanzDebitor_entity_1.FinanzDebitor.create({ ...normalized, id });
        return this.repository.update(entity);
    }
    async remove(id, tenantId) {
        await this.repository.delete(id, tenantId);
    }
}
exports.FinanzDebitorService = FinanzDebitorService;
//# sourceMappingURL=finanzDebitor.service.js.map