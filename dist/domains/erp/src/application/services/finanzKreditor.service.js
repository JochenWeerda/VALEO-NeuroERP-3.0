"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKreditorService = void 0;
const finanzKreditor_entity_1 = require("../../core/entities/finanzKreditor.entity");
function normalize(dto, existing) {
    const kreditorNr = dto.kreditor_nr?.trim();
    if (!kreditorNr) {
        throw new Error('kreditor_nr is required');
    }
    if (dto.kreditlimit !== undefined && dto.kreditlimit < 0) {
        throw new Error('kreditlimit must be positive');
    }
    if (dto.zahlungsziel !== undefined && dto.zahlungsziel < 0) {
        throw new Error('zahlungsziel must be positive');
    }
    return {
        ...existing,
        lieferanten_id: dto.lieferanten_id ?? existing?.lieferanten_id,
        kreditor_nr: kreditorNr,
        kreditlimit: dto.kreditlimit ?? existing?.kreditlimit ?? 0,
        zahlungsziel: dto.zahlungsziel ?? existing?.zahlungsziel ?? 30,
        zahlungsbedingungen: dto.zahlungsbedingungen ?? existing?.zahlungsbedingungen,
        bankverbindung: dto.bankverbindung ?? existing?.bankverbindung,
        steuer_id: dto.steuer_id ?? existing?.steuer_id,
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
        if (existing) {
            throw new Error(`Kreditor ${normalized.kreditor_nr} already exists`);
        }
        const entity = finanzKreditor_entity_1.FinanzKreditor.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (!existing) {
            throw new Error('FinanzKreditor not found');
        }
        const current = existing.toPrimitives();
        const normalized = normalize({
            lieferanten_id: payload.lieferanten_id ?? current.lieferanten_id,
            kreditor_nr: payload.kreditor_nr ?? current.kreditor_nr,
            kreditlimit: payload.kreditlimit ?? current.kreditlimit,
            zahlungsziel: payload.zahlungsziel ?? current.zahlungsziel,
            zahlungsbedingungen: payload.zahlungsbedingungen ?? current.zahlungsbedingungen,
            bankverbindung: payload.bankverbindung ?? current.bankverbindung,
            steuer_id: payload.steuer_id ?? current.steuer_id,
            ist_aktiv: payload.ist_aktiv ?? current.ist_aktiv,
            notizen: payload.notizen ?? current.notizen,
            erstellt_von: current.erstellt_von,
        }, current);
        const duplicate = await this.repository.findByKreditorNr(normalized.kreditor_nr);
        if (duplicate && duplicate.toPrimitives().id !== id) {
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
