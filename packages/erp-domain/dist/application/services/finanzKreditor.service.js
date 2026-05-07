"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKreditorService = void 0;
const finanzKreditor_entity_1 = require("../../core/entities/finanzKreditor.entity");
const DEFAULT_PAYMENT_TARGET_DAYS = 30;
function normalize(dto, existing) {
    const kreditorNr = dto.kreditor_nr?.trim();
    if (kreditorNr === undefined || kreditorNr === null) {
        throw new Error('kreditor_nr is required');
    }
    // kreditlimit validation removed as it's not in DTO
    if (dto.zahlungsziel !== undefined && dto.zahlungsziel < 0) {
        throw new Error('zahlungsziel must be positive');
    }
    return {
        ...existing,
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
class FinanzKreditorService {
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
        const existing = await this.repository.findByKreditorNr(normalized.kreditor_nr);
        if (existing !== undefined && existing !== null) {
            throw new Error(`Kreditor ${normalized.kreditor_nr} already exists`);
        }
        const entity = finanzKreditor_entity_1.FinanzKreditor.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (existing === undefined || existing === null) {
            throw new Error('FinanzKreditor not found');
        }
        const current = existing.toPrimitives();
        const normalized = normalize({
            lieferanten_id: payload.lieferanten_id ?? current.lieferanten_id,
            kreditor_nr: payload.kreditor_nr ?? current.kreditor_nr,
            zahlungsziel: payload.zahlungsziel ?? current.zahlungsziel,
            zahlungsart: payload.zahlungsart ?? current.zahlungsart,
            bankverbindung: payload.bankverbindung ?? current.bankverbindung,
            steuernummer: payload.steuer_id ?? current.steuernummer,
            ist_aktiv: payload.ist_aktiv ?? current.ist_aktiv,
            notizen: payload.notizen ?? current.notizen,
            erstellt_von: current.erstellt_von,
        }, current);
        const duplicate = await this.repository.findByKreditorNr(normalized.kreditor_nr);
        if ((duplicate !== undefined && duplicate !== null) && duplicate.toPrimitives().id !== id) {
            throw new Error(`Another Kreditor already uses kreditor_nr ${normalized.kreditor_nr}`);
        }
        const entity = finanzKreditor_entity_1.FinanzKreditor.create({ ...normalized, id });
        return this.repository.update(entity);
    }
    async remove(id) {
        await this.repository.delete(id);
    }
}
exports.FinanzKreditorService = FinanzKreditorService;
//# sourceMappingURL=finanzKreditor.service.js.map