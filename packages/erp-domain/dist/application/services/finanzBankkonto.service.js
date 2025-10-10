"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBankkontoService = void 0;
const finanzBankkonto_entity_1 = require("../../core/entities/finanzBankkonto.entity");
const IBAN_PATTERN = /^[A-Z]{2}[0-9A-Z]{13,30}$/i;
const BIC_PATTERN = /^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$/i;
function toDate(value) {
    if (value === undefined || value === null) {
        return undefined;
    }
    return value instanceof Date ? value : new Date(value);
}
function normalize(dto, existing) {
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
    async list() {
        return this.repository.list();
    }
    async findById(id) {
        return this.repository.findById(id);
    }
    async create(payload) {
        const normalized = normalize(payload);
        const entity = finanzBankkonto_entity_1.FinanzBankkonto.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (existing === undefined || existing === null) {
            throw new Error('FinanzBankkonto not found');
        }
        const current = existing.toPrimitives();
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
    async remove(id) {
        await this.repository.delete(id);
    }
}
exports.FinanzBankkontoService = FinanzBankkontoService;
//# sourceMappingURL=finanzBankkonto.service.js.map