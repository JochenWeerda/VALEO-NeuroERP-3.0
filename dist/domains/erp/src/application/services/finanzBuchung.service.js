"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBuchungService = void 0;
/**
 * Application service for FinanzBuchung generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
const crypto_1 = require("crypto");
const finanzBuchung_entity_1 = require("../../core/entities/finanzBuchung.entity");
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
    if (dto.sollkonto && dto.habenkonto && dto.sollkonto === dto.habenkonto) {
        throw new Error('sollkonto and habenkonto must differ');
    }
    const payload = {
        ...existing,
        buchungsnummer: dto.buchungsnummer?.trim() || existing?.buchungsnummer || '',
        buchungsdatum: toDate(dto.buchungsdatum ?? existing?.buchungsdatum ?? new Date()),
        belegdatum: toDate(dto.belegdatum ?? existing?.belegdatum ?? new Date()),
        belegnummer: dto.belegnummer?.trim() || existing?.belegnummer,
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
    if (!payload.buchungsnummer) {
        payload.buchungsnummer = `BCH-${Date.now()}-${(0, crypto_1.randomUUID)().slice(0, 6)}`;
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
        return this.repository.save(entity);
    }
    async update(id, payload) {
        const existing = await this.repository.findById(id);
        if (!existing) {
            throw new Error('FinanzBuchung not found');
        }
        const normalized = normalizeBuchung({
            buchungsnummer: payload.buchungsnummer ?? existing.buchungsnummer,
            buchungsdatum: payload.buchungsdatum ?? existing.buchungsdatum,
            belegdatum: payload.belegdatum ?? existing.belegdatum,
            belegnummer: payload.belegnummer ?? existing.belegnummer,
            buchungstext: payload.buchungstext ?? existing.buchungstext,
            sollkonto: payload.sollkonto ?? existing.sollkonto,
            habenkonto: payload.habenkonto ?? existing.habenkonto,
            betrag: payload.betrag ?? existing.betrag,
            waehrung: payload.waehrung ?? existing.waehrung,
            steuerbetrag: payload.steuerbetrag ?? existing.steuerbetrag,
            steuersatz: payload.steuersatz ?? existing.steuersatz,
            buchungsart: payload.buchungsart ?? existing.buchungsart,
            referenz_typ: payload.referenz_typ ?? existing.referenz_typ,
            referenz_id: payload.referenz_id ?? existing.referenz_id,
            ist_storniert: payload.ist_storniert ?? existing.ist_storniert,
            storno_buchung_id: payload.storno_buchung_id ?? existing.storno_buchung_id,
            erstellt_von: existing.erstellt_von,
        }, existing.toPrimitives());
        const entity = finanzBuchung_entity_1.FinanzBuchung.create({ ...normalized, id });
        return this.repository.update(entity);
    }
    async remove(id) {
        await this.repository.delete(id);
    }
}
exports.FinanzBuchungService = FinanzBuchungService;
