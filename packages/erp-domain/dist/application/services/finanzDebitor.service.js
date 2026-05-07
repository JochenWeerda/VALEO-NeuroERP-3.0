"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzDebitorService = void 0;
const finanzDebitor_entity_1 = require("../../core/entities/finanzDebitor.entity");
const DEFAULT_PAYMENT_TARGET_DAYS = 30;
function normalize(dto, existing) {
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
    async list() {
        return this.repository.list();
    }
    async findById(id) {
        return this.repository.findById(id);
    }
    async create(payload) {
        const normalized = normalize(payload);
        const existing = await this.repository.findByDebitorNr(normalized.debitor_nr);
        if (existing !== undefined && existing !== null) {
            throw new Error(`Debitor ${normalized.debitor_nr} already exists`);
        }
        const entity = finanzDebitor_entity_1.FinanzDebitor.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (existing === undefined || existing === null) {
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
        if ((duplicate !== undefined && duplicate !== null) && duplicate.toPrimitives().id !== id) {
            throw new Error(`Another Debitor already uses debitor_nr ${normalized.debitor_nr}`);
        }
        const entity = finanzDebitor_entity_1.FinanzDebitor.create({ ...normalized, id });
        return this.repository.update(entity);
    }
    async remove(id) {
        await this.repository.delete(id);
    }
}
exports.FinanzDebitorService = FinanzDebitorService;
//# sourceMappingURL=finanzDebitor.service.js.map