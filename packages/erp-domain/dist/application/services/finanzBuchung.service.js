"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBuchungService = void 0;
/**
 * Application service for FinanzBuchung generated via CRM toolkit.
 * Encapsulates use-cases and translates primitives to domain entities.
 */
const crypto_1 = require("crypto");
const finanzBuchung_entity_1 = require("../../core/entities/finanzBuchung.entity");
const api_pagination_1 = require("../../presentation/types/api-pagination");
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
function tenantFrom(existing, tenantForCreate) {
    const t = existing?.tenant_id ?? tenantForCreate?.trim();
    if (!t) {
        throw new Error('tenant_id is required');
    }
    return t;
}
function normalizeBuchung(dto, existing, tenantForCreate) {
    const rawText = dto.buchungstext ?? existing?.buchungstext;
    const textTrim = rawText?.trim();
    if (textTrim === undefined || textTrim.length === 0) {
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
        tenant_id: tenantFrom(existing, tenantForCreate),
        buchungsnummer: dto.buchungsnummer?.trim() ?? existing?.buchungsnummer ?? '',
        buchungsdatum: toDate(dto.buchungsdatum ?? existing?.buchungsdatum ?? new Date()),
        belegdatum: toDate(dto.belegdatum ?? existing?.belegdatum ?? new Date()),
        belegnummer: dto.belegnummer?.trim() ?? existing?.belegnummer,
        buchungstext: textTrim,
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
    if (payload.buchungsnummer === undefined || payload.buchungsnummer === null || payload.buchungsnummer.length === 0) {
        payload.buchungsnummer = `BCH-${Date.now()}-${(0, crypto_1.randomUUID)().slice(0, RANDOM_SUFFIX_LENGTH)}`;
    }
    return payload;
}
class FinanzBuchungService {
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
        const normalized = normalizeBuchung(payload, undefined, tenantId);
        const dup = await this.repository.findByBuchungsnummer(tenantId, normalized.buchungsnummer);
        if (dup !== undefined && dup !== null) {
            throw new Error(`Buchung mit Nummer ${normalized.buchungsnummer} existiert bereits`);
        }
        const id = normalized.id ?? (0, crypto_1.randomUUID)();
        const entity = finanzBuchung_entity_1.FinanzBuchung.create({ ...normalized, id });
        await this.repository.save(entity);
        return entity;
    }
    async update(id, tenantId, payload) {
        const existingRow = await this.repository.findById(id, tenantId);
        if (existingRow === undefined || existingRow === null) {
            throw new Error('FinanzBuchung not found');
        }
        const existingProps = existingRow.toPrimitives();
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
        const dup = await this.repository.findByBuchungsnummer(tenantId, normalized.buchungsnummer);
        if ((dup !== undefined && dup !== null) && dup.toPrimitives().id !== id) {
            throw new Error(`Another Buchung already uses buchungsnummer ${normalized.buchungsnummer}`);
        }
        const entity = finanzBuchung_entity_1.FinanzBuchung.create({ ...normalized, id });
        await this.repository.update(entity);
        return entity;
    }
    async remove(id, tenantId) {
        await this.repository.delete(id, tenantId);
    }
}
exports.FinanzBuchungService = FinanzBuchungService;
//# sourceMappingURL=finanzBuchung.service.js.map