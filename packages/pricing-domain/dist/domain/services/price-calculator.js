"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.calculateQuote = calculateQuote;
exports.getQuoteById = getQuoteById;
const connection_1 = require("../../infra/db/connection");
const schema_1 = require("../../infra/db/schema");
const formula_engine_1 = require("../calc/formula-engine");
const publisher_1 = require("../../infra/messaging/publisher");
const drizzle_orm_1 = require("drizzle-orm");
const crypto_1 = require("crypto");
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'price-calculator' });
async function calculateQuote(tenantId, input, userId) {
    logger.info({ tenantId, sku: input.sku, customerId: input.customerId }, 'Calculating price quote');
    const components = [];
    let runningTotal = 0;
    const baseResult = await resolveBasePrice(tenantId, input.sku, input.qty);
    components.push(...baseResult.components);
    runningTotal = baseResult.price;
    const conditionResult = await applyConditions(tenantId, input, runningTotal);
    components.push(...conditionResult.components);
    runningTotal += conditionResult.adjustment;
    const dynamicResult = await applyDynamicFormula(tenantId, input, runningTotal);
    if (dynamicResult) {
        components.push(...dynamicResult.components);
        runningTotal = dynamicResult.price;
    }
    const chargeResult = await applyCharges(tenantId, input, runningTotal);
    components.push(...chargeResult.components);
    runningTotal += chargeResult.total;
    const taxResult = await applyTaxes(tenantId, input, runningTotal);
    components.push(...taxResult.components);
    const totalGross = runningTotal + taxResult.total;
    const quoteId = (0, crypto_1.randomUUID)();
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
    const quote = {
        id: quoteId,
        tenantId,
        inputs: input,
        components,
        totalNet: Math.round(runningTotal * 100) / 100,
        totalGross: Math.round(totalGross * 100) / 100,
        currency: 'EUR',
        calculatedAt: new Date().toISOString(),
        expiresAt: expiresAt.toISOString(),
        createdBy: userId,
    };
    await connection_1.db.insert(schema_1.priceQuotes).values({
        tenantId,
        inputs: input,
        components: components,
        totalNet: quote.totalNet.toString(),
        totalGross: quote.totalGross?.toString() ?? null,
        currency: quote.currency,
        expiresAt,
        createdBy: userId ?? null,
        signature: null,
    });
    await (0, publisher_1.publishEvent)('quote.calculated', {
        tenantId,
        quoteId,
        customerId: input.customerId,
        sku: input.sku,
        qty: input.qty,
        occurredAt: new Date().toISOString(),
    });
    return quote;
}
async function resolveBasePrice(tenantId, sku, qty) {
    const now = new Date();
    const [priceList] = await connection_1.db
        .select()
        .from(schema_1.priceLists)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.priceLists.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.priceLists.status, 'Active'), (0, drizzle_orm_1.lte)(schema_1.priceLists.validFrom, now), (0, drizzle_orm_1.or)((0, drizzle_orm_1.isNull)(schema_1.priceLists.validTo), (0, drizzle_orm_1.gte)(schema_1.priceLists.validTo, now))))
        .limit(1);
    if (!priceList) {
        throw new Error('No active price list found');
    }
    const lines = priceList.lines;
    const line = lines.find(l => l.sku === sku && l.active);
    if (!line) {
        throw new Error(`SKU ${sku} not found in price list`);
    }
    let price = line.basePrice;
    if (line.tierBreaks && line.tierBreaks.length > 0) {
        const applicableTier = line.tierBreaks
            .filter(t => qty >= t.minQty && (!t.maxQty || qty <= t.maxQty))
            .sort((a, b) => b.minQty - a.minQty)[0];
        if (applicableTier) {
            price = applicableTier.price;
        }
    }
    return {
        price: price * qty,
        components: [{
                type: 'Base',
                key: `Base-${sku}`,
                description: `${line.description || sku} @ ${price} ${line.currency}/${line.uom}`,
                value: price * qty,
                calculatedFrom: priceList.id,
            }],
    };
}
async function applyConditions(tenantId, input, basePrice) {
    const now = new Date();
    const sets = await connection_1.db
        .select()
        .from(schema_1.conditionSets)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.conditionSets.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.conditionSets.key, input.customerId), (0, drizzle_orm_1.eq)(schema_1.conditionSets.active, true), (0, drizzle_orm_1.lte)(schema_1.conditionSets.validFrom, now), (0, drizzle_orm_1.or)((0, drizzle_orm_1.isNull)(schema_1.conditionSets.validTo), (0, drizzle_orm_1.gte)(schema_1.conditionSets.validTo, now))))
        .orderBy(schema_1.conditionSets.priority);
    const components = [];
    let totalAdjustment = 0;
    for (const set of sets) {
        const rules = set.rules;
        for (const rule of rules) {
            if (!ruleApplies(rule, input))
                continue;
            let adjustment = 0;
            if (rule.method === 'ABS') {
                adjustment = rule.value * input.qty;
            }
            else if (rule.method === 'PCT') {
                adjustment = (basePrice + totalAdjustment) * (rule.value / 100);
            }
            components.push({
                type: 'Condition',
                key: `${rule.type}-${rule.scope}`,
                description: rule.description || `${rule.type} ${rule.value}${rule.method === 'PCT' ? '%' : ''}`,
                value: adjustment,
                basis: rule.method === 'PCT' ? basePrice + totalAdjustment : undefined,
                calculatedFrom: set.id,
            });
            if (set.conflictStrategy === 'Stack' || rule.stackable) {
                totalAdjustment += adjustment;
            }
            else if (set.conflictStrategy === 'MaxWins') {
                totalAdjustment = Math.max(totalAdjustment, adjustment);
            }
        }
    }
    return { adjustment: totalAdjustment, components };
}
function ruleApplies(rule, input) {
    if (rule.scope === 'SKU' && rule.selector?.sku && rule.selector.sku !== input.sku) {
        return false;
    }
    if (rule.minQty && input.qty < rule.minQty)
        return false;
    if (rule.maxQty && input.qty > rule.maxQty)
        return false;
    if (rule.channel && rule.channel !== 'All' && rule.channel !== input.channel)
        return false;
    if (rule.validFrom || rule.validTo) {
        const now = new Date();
        if (rule.validFrom && new Date(rule.validFrom) > now)
            return false;
        if (rule.validTo && new Date(rule.validTo) < now)
            return false;
    }
    return true;
}
async function applyDynamicFormula(tenantId, input, currentPrice) {
    const now = new Date();
    const [formula] = await connection_1.db
        .select()
        .from(schema_1.dynamicFormulas)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.dynamicFormulas.tenantId, tenantId), (0, drizzle_orm_1.or)((0, drizzle_orm_1.eq)(schema_1.dynamicFormulas.sku, input.sku), (0, drizzle_orm_1.eq)(schema_1.dynamicFormulas.commodity, input.sku.split('-')[0] || input.sku)), (0, drizzle_orm_1.eq)(schema_1.dynamicFormulas.active, true), (0, drizzle_orm_1.lte)(schema_1.dynamicFormulas.validFrom, now), (0, drizzle_orm_1.or)((0, drizzle_orm_1.isNull)(schema_1.dynamicFormulas.validTo), (0, drizzle_orm_1.gte)(schema_1.dynamicFormulas.validTo, now))))
        .limit(1);
    if (!formula)
        return null;
    const result = await (0, formula_engine_1.evaluateFormula)(formula, input.context || {});
    return {
        price: result.roundedValue * input.qty,
        components: [{
                type: 'Dynamic',
                key: `Dynamic-${formula.name}`,
                description: `Formula: ${formula.expression}`,
                value: result.roundedValue * input.qty,
                calculatedFrom: formula.id,
            }],
    };
}
async function applyCharges(tenantId, input, currentPrice) {
    const now = new Date();
    const charges = await connection_1.db
        .select()
        .from(schema_1.taxChargeRefs)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.active, true), (0, drizzle_orm_1.lte)(schema_1.taxChargeRefs.validFrom, now), (0, drizzle_orm_1.or)((0, drizzle_orm_1.isNull)(schema_1.taxChargeRefs.validTo), (0, drizzle_orm_1.gte)(schema_1.taxChargeRefs.validTo, now)), (0, drizzle_orm_1.or)((0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.type, 'Fee'), (0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.type, 'Levy'), (0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.type, 'Surcharge'))));
    const components = [];
    let total = 0;
    for (const charge of charges) {
        if (charge.scope === 'SKU' && charge.scopeValue !== input.sku)
            continue;
        if (charge.scope === 'Commodity' && !input.sku.startsWith(charge.scopeValue || ''))
            continue;
        let value = 0;
        if (charge.method === 'ABS') {
            value = parseFloat(charge.rateOrAmount.toString()) * input.qty;
        }
        else if (charge.method === 'PCT') {
            value = currentPrice * (parseFloat(charge.rateOrAmount.toString()) / 100);
        }
        components.push({
            type: 'Charge',
            key: `Charge-${charge.code}`,
            description: charge.name,
            value,
            calculatedFrom: charge.id,
        });
        total += value;
    }
    return { total, components };
}
async function applyTaxes(tenantId, input, netPrice) {
    const now = new Date();
    const taxes = await connection_1.db
        .select()
        .from(schema_1.taxChargeRefs)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.type, 'VAT'), (0, drizzle_orm_1.eq)(schema_1.taxChargeRefs.active, true), (0, drizzle_orm_1.lte)(schema_1.taxChargeRefs.validFrom, now), (0, drizzle_orm_1.or)((0, drizzle_orm_1.isNull)(schema_1.taxChargeRefs.validTo), (0, drizzle_orm_1.gte)(schema_1.taxChargeRefs.validTo, now))))
        .limit(1);
    if (taxes.length === 0) {
        return { total: 0, components: [] };
    }
    const tax = taxes[0];
    const value = netPrice * (parseFloat(tax.rateOrAmount.toString()) / 100);
    return {
        total: value,
        components: [{
                type: 'Tax',
                key: `Tax-${tax.code}`,
                description: tax.name,
                value,
                basis: netPrice,
                calculatedFrom: tax.id,
            }],
    };
}
async function getQuoteById(tenantId, quoteId) {
    const [quote] = await connection_1.db
        .select()
        .from(schema_1.priceQuotes)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.priceQuotes.id, quoteId), (0, drizzle_orm_1.eq)(schema_1.priceQuotes.tenantId, tenantId)))
        .limit(1);
    if (!quote)
        return null;
    if (new Date(quote.expiresAt) < new Date()) {
        logger.warn({ quoteId }, 'Quote expired');
        return null;
    }
    return {
        ...quote,
        totalNet: Number(quote.totalNet),
        totalGross: quote.totalGross ? Number(quote.totalGross) : undefined,
        calculatedAt: quote.calculatedAt.toISOString(),
        expiresAt: quote.expiresAt.toISOString(),
        createdBy: quote.createdBy ?? undefined,
        signature: quote.signature ?? undefined,
    };
}
//# sourceMappingURL=price-calculator.js.map