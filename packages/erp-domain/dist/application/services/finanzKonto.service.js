"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzKontoService = void 0;
/**
 * Application service for FinanzKonto generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
const finanzKonto_entity_1 = require("../../core/entities/finanzKonto.entity");
const TAX_RATE_MIN = 0;
const TAX_RATE_MAX = 100;
const ALLOWED_ACCOUNT_TYPES = ['Aktiv', 'Passiv', 'Ertrag', 'Aufwand'];
function assertKontotyp(value) {
    if (!ALLOWED_ACCOUNT_TYPES.includes(value)) {
        throw new Error(`Unsupported kontotyp "${value}". Allowed: ${ALLOWED_ACCOUNT_TYPES.join(', ')}`);
    }
    return value;
}
function normalizeProps(dto, existing) {
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
    const payload = {
        ...existing,
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
class FinanzKontoService {
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
        const normalized = normalizeProps(payload);
        const existing = await this.repository.findByKontonummer(normalized.kontonummer);
        if (existing !== undefined && existing !== null) {
            throw new Error(`FinanzKonto with kontonummer ${normalized.kontonummer} already exists`);
        }
        const entity = finanzKonto_entity_1.FinanzKonto.create(normalized);
        return this.repository.save(entity);
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (existing === undefined || existing === null) {
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
        if ((duplicate !== undefined && duplicate !== null) && duplicate.toPrimitives().id !== id) {
            throw new Error(`Another FinanzKonto already uses kontonummer ${normalized.kontonummer}`);
        }
        const entity = finanzKonto_entity_1.FinanzKonto.create({ ...normalized, id });
        return this.repository.update(entity);
    }
    async remove(id) {
        await this.repository.delete(id);
    }
}
exports.FinanzKontoService = FinanzKontoService;
//# sourceMappingURL=finanzKonto.service.js.map