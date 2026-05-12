"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBankkontoService = void 0;
const finanzBankkonto_entity_1 = require("../../core/entities/finanzBankkonto.entity");
const api_pagination_1 = require("../../presentation/types/api-pagination");
const IBAN_PATTERN = /^[A-Z]{2}[0-9A-Z]{13,30}$/i;
const BIC_PATTERN = /^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$/i;
function toDate(value) {
    if (value === undefined || value === null) {
        return undefined;
    }
    return value instanceof Date ? value : new Date(value);
}
function tenantFrom(existing, tenantForCreate) {
    const t = existing?.tenant_id ?? tenantForCreate?.trim();
    if (!t) {
        throw new Error('tenant_id is required');
    }
    return t;
}
function normalize(dto, existing, tenantForCreate) {
    const kontoname = dto.kontoname?.trim();
    const bankname = dto.bankname?.trim();
    if (kontoname === undefined || kontoname === null) {
        throw new Error('kontoname is required');
    }
    if (bankname === undefined || bankname === null) {
        throw new Error('bankname is required');
    }
    if (dto.iban != null && !IBAN_PATTERN.test(dto.iban.replace(/\s+/g, ''))) {
        throw new Error('iban format is invalid');
    }
    if (dto.bic != null && !BIC_PATTERN.test(dto.bic)) {
        throw new Error('bic format is invalid');
    }
    return {
        ...existing,
        tenant_id: tenantFrom(existing, tenantForCreate),
        kontoname,
        bankname,
        iban: dto.iban != null ? dto.iban.replace(/\s+/g, '').toUpperCase() : existing?.iban,
        bic: dto.bic != null ? dto.bic.toUpperCase() : existing?.bic,
        kontonummer: dto.kontonummer ?? existing?.kontonummer,
        blz: dto.blz ?? existing?.blz,
        waehrung: dto.waehrung ?? existing?.waehrung ?? 'EUR',
        kontostand: dto.kontostand ?? existing?.kontostand ?? 0,
        letzter_abgleich: toDate(dto.letzter_abgleich) ?? existing?.letzter_abgleich,
        ist_aktiv: dto.ist_aktiv ?? existing?.ist_aktiv ?? true,
        notizen: dto.notizen ?? existing?.notizen,
        erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,
        id: existing?.id,
        erstellt_am: existing?.erstellt_am,
        aktualisiert_am: existing?.aktualisiert_am,
    };
}
class FinanzBankkontoService {
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
        const entity = finanzBankkonto_entity_1.FinanzBankkonto.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, tenantId, payload) {
        const existingRow = await this.repository.findById(id, tenantId);
        if (existingRow === undefined || existingRow === null) {
            throw new Error('FinanzBankkonto not found');
        }
        const current = existingRow.toPrimitives();
        const normalized = normalize({
            kontoname: payload.kontoname ?? current.kontoname,
            bankname: payload.bankname ?? current.bankname,
            iban: payload.iban ?? current.iban,
            bic: payload.bic ?? current.bic,
            kontonummer: payload.kontonummer ?? current.kontonummer,
            blz: payload.blz ?? current.blz,
            waehrung: payload.waehrung ?? current.waehrung,
            kontostand: payload.kontostand ?? current.kontostand,
            letzter_abgleich: payload.letzter_abgleich ?? current.letzter_abgleich,
            ist_aktiv: payload.ist_aktiv ?? current.ist_aktiv,
            notizen: payload.notizen ?? current.notizen,
            erstellt_von: current.erstellt_von,
        }, current);
        const entity = finanzBankkonto_entity_1.FinanzBankkonto.create({ ...normalized, id });
        return this.repository.update(entity);
    }
    async remove(id, tenantId) {
        await this.repository.delete(id, tenantId);
    }
}
exports.FinanzBankkontoService = FinanzBankkontoService;
//# sourceMappingURL=finanzBankkonto.service.js.map