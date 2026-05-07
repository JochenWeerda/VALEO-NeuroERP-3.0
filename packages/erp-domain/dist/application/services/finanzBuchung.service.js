"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBuchungService = void 0;
/**
 * Application service for FinanzBuchung generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
const crypto_1 = require("crypto");
const finanzBuchung_entity_1 = require("../../core/entities/finanzBuchung.entity");
const RANDOM_SUFFIX_LENGTH = 6;
function toDate(value) {
    if (value instanceof Date) {
        return value;
    }
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
        throw new Error(`Invalid date value: ${value}`);
    }
    return parsed;
}
function normalizeBuchung(dto, existing) {
    if (!dto.buchungstext?.trim()) {
        throw new Error('buchungstext is required');
    }
    if (dto.betrag === undefined || dto.betrag === null) {
        throw new Error('betrag is required');
    }
    if (Number(dto.betrag) === 0) {
        throw new Error('betrag must not be zero');
    }
    if (dto.sollkonto != null && dto.habenkonto != null && dto.sollkonto === dto.habenkonto) {
        throw new Error('sollkonto and habenkonto must differ');
    }
    const payload = {
        ...existing,
        buchungsnummer: dto.buchungsnummer?.trim() ?? existing?.buchungsnummer ?? '',
        buchungsdatum: toDate(dto.buchungsdatum ?? existing?.buchungsdatum ?? new Date()),
        belegdatum: toDate(dto.belegdatum ?? existing?.belegdatum ?? new Date()),
        belegnummer: dto.belegnummer?.trim() ?? existing?.belegnummer,
        buchungstext: dto.buchungstext.trim(),
        sollkonto: dto.sollkonto ?? existing?.sollkonto,
        habenkonto: dto.habenkonto ?? existing?.habenkonto,
        betrag: Number(dto.betrag),
        waehrung: dto.waehrung ?? existing?.waehrung ?? 'EUR',
        steuerbetrag: dto.steuerbetrag ?? existing?.steuerbetrag ?? 0,
        steuersatz: dto.steuersatz ?? existing?.steuersatz ?? 0,
        buchungsart: dto.buchungsart ?? existing?.buchungsart,
        referenz_typ: dto.referenz_typ ?? existing?.referenz_typ,
        referenz_id: dto.referenz_id ?? existing?.referenz_id,
        ist_storniert: dto.ist_storniert ?? existing?.ist_storniert ?? false,
        storno_buchung_id: dto.storno_buchung_id ?? existing?.storno_buchung_id,
        erstellt_von: dto.erstellt_von ?? existing?.erstellt_von,
        id: existing?.id,
        erstellt_am: existing?.erstellt_am,
        aktualisiert_am: existing?.aktualisiert_am,
    };
    if (payload.buchungsnummer === undefined || payload.buchungsnummer === null) {
        payload.buchungsnummer = `BCH-${Date.now()}-${(0, crypto_1.randomUUID)().slice(0, RANDOM_SUFFIX_LENGTH)}`;
    }
    return payload;
}
class FinanzBuchungService {
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
        const normalized = normalizeBuchung(payload);
        const entity = finanzBuchung_entity_1.FinanzBuchung.create(normalized);
        await this.repository.save(entity);
        return entity;
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (existing === undefined || existing === null) {
            throw new Error('FinanzBuchung not found');
        }
        const existingProps = existing.toPrimitives();
        const normalized = normalizeBuchung({
            buchungsnummer: payload.buchungsnummer ?? existingProps.buchungsnummer,
            buchungsdatum: payload.buchungsdatum ?? existingProps.buchungsdatum,
            belegdatum: payload.belegdatum ?? existingProps.belegdatum,
            belegnummer: payload.belegnummer ?? existingProps.belegnummer,
            buchungstext: payload.buchungstext ?? existingProps.buchungstext,
            sollkonto: payload.sollkonto ?? existingProps.sollkonto,
            habenkonto: payload.habenkonto ?? existingProps.habenkonto,
            betrag: payload.betrag ?? existingProps.betrag,
            waehrung: payload.waehrung ?? existingProps.waehrung,
            steuerbetrag: payload.steuerbetrag ?? existingProps.steuerbetrag,
            steuersatz: payload.steuersatz ?? existingProps.steuersatz,
            buchungsart: payload.buchungsart ?? existingProps.buchungsart,
            referenz_typ: payload.referenz_typ ?? existingProps.referenz_typ,
            referenz_id: payload.referenz_id ?? existingProps.referenz_id,
            ist_storniert: payload.ist_storniert ?? existingProps.ist_storniert,
            storno_buchung_id: payload.storno_buchung_id ?? existingProps.storno_buchung_id,
            erstellt_von: existingProps.erstellt_von,
        }, existingProps);
        const entity = finanzBuchung_entity_1.FinanzBuchung.create({ ...normalized, id });
        await this.repository.update(entity);
        return entity;
    }
    async remove(id) {
        await this.repository.delete(id);
    }
}
exports.FinanzBuchungService = FinanzBuchungService;
//# sourceMappingURL=finanzBuchung.service.js.map