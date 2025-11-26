import { db } from '../../infra/db/connection';
import { priceLists, conditionSets, dynamicFormulas, taxChargeRefs, priceQuotes } from '../../infra/db/schema';
import { CalcQuoteInput, PriceQuote, PriceComponent } from '../entities/price-quote';
import { PriceListLine, TierBreak } from '../entities/price-list';
import { ConditionRule } from '../entities/condition-set';
import { evaluateFormula } from '../calc/formula-engine';
import { publishEvent } from '../../infra/messaging/publisher';
import { SeasonalPricingService } from './seasonal-pricing-service';
import { eq, and, lte, gte, or, isNull } from 'drizzle-orm';
import { randomUUID } from 'crypto';
import pino from 'pino';

const logger = pino({ name: 'price-calculator' });

// Initialize seasonal pricing service
const seasonalPricingService = new SeasonalPricingService({});

/**
 * Calculate Price Quote
 * KERN-PIPELINE: Base → Conditions → Dynamic → Charges → Tax
 */
export async function calculateQuote(
  tenantId: string,
  input: CalcQuoteInput,
  userId?: string
): Promise<PriceQuote> {
  logger.info({ tenantId, sku: input.sku, customerId: input.customerId }, 'Calculating price quote');

  const components: PriceComponent[] = [];
  let runningTotal = 0;

  // 1. BASE: Resolve from PriceList
  const baseResult = await resolveBasePrice(tenantId, input.sku, input.qty);
  components.push(...baseResult.components);
  runningTotal = baseResult.price;

  // 1.5. SEASONAL: Apply seasonal pricing adjustment (based on OCA sale_agriculture pattern)
  const orderDate = input.context?.orderDate ? new Date(input.context.orderDate) : new Date();
  const seasonalResult = await applySeasonalPricing(tenantId, input, baseResult.price / input.qty, orderDate);
  if (seasonalResult) {
    components.push(...seasonalResult.components);
    runningTotal = seasonalResult.price;
  }

  // 2. CONDITIONS: Apply customer/segment conditions
  const conditionResult = await applyConditions(tenantId, input, runningTotal);
  components.push(...conditionResult.components);
  runningTotal += conditionResult.adjustment;

  // 3. DYNAMIC: Apply formula (if any)
  const dynamicResult = await applyDynamicFormula(tenantId, input, runningTotal);
  if (dynamicResult) {
    components.push(...dynamicResult.components);
    runningTotal = dynamicResult.price;
  }

  // 4. CHARGES: Apply fees/levies
  const chargeResult = await applyCharges(tenantId, input, runningTotal);
  components.push(...chargeResult.components);
  runningTotal += chargeResult.total;

  // 5. TAX: Apply VAT (nur als Referenz, keine Buchung!)
  const taxResult = await applyTaxes(tenantId, input, runningTotal);
  components.push(...taxResult.components);
  const totalGross = runningTotal + taxResult.total;

  // Create quote
  const quoteId = randomUUID();
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24h TTL

  const quote: PriceQuote = {
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

  // Save to DB (kurzlebig)
  await db.insert(priceQuotes).values({
    tenantId,
    inputs: input as any,
    components: components as any,
    totalNet: quote.totalNet.toString(),
    totalGross: quote.totalGross?.toString() ?? null,
    currency: quote.currency,
    expiresAt,
    createdBy: userId ?? null,
    signature: null,
  });

  // Publish event (ohne Preise!)
  await publishEvent('quote.calculated', {
    tenantId,
    quoteId,
    customerId: input.customerId,
    sku: input.sku,
    qty: input.qty,
    occurredAt: new Date().toISOString(),
  });

  return quote;
}

/**
 * Step 1: Resolve Base Price from PriceList
 */
async function resolveBasePrice(
  tenantId: string,
  sku: string,
  qty: number
): Promise<{ price: number; components: PriceComponent[] }> {
  // Find active price list
  const now = new Date();
  const [priceList] = await db
    .select()
    .from(priceLists)
    .where(
      and(
        eq(priceLists.tenantId, tenantId),
        eq(priceLists.status, 'Active'),
        lte(priceLists.validFrom, now),
        or(isNull(priceLists.validTo), gte(priceLists.validTo, now))!
      )
    )
    .limit(1);

  if (priceList === undefined || priceList === null) {
    throw new Error('No active price list found');
  }

  // Find SKU in lines
  const lines = priceList.lines as PriceListLine[];
  const line = lines.find(l => l.sku === sku && l.active);

  if (line === undefined || line === null) {
    throw new Error(`SKU ${sku} not found in price list`);
  }

  // Check tier breaks
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

/**
 * Step 1.5: Apply Seasonal Pricing (based on OCA sale_agriculture pattern)
 */
async function applySeasonalPricing(
  tenantId: string,
  input: CalcQuoteInput,
  baseUnitPrice: number,
  orderDate: Date
): Promise<{ price: number; components: PriceComponent[] } | null> {
  try {
    // Extract commodity from SKU (e.g., "WHEAT-11.5" -> "WHEAT")
    const commodity = input.sku.split('-')[0] || input.sku;
    
    const seasonalPrice = await seasonalPricingService.getSeasonalPrice(
      tenantId,
      input.sku,
      baseUnitPrice,
      orderDate,
      {
        commodity: commodity,
        category: input.context?.category
      }
    );

    // If no adjustment, return null
    if (seasonalPrice.adjustment === 0 || !seasonalPrice.appliedRule) {
      return null;
    }

    const adjustedTotalPrice = seasonalPrice.adjustedPrice * input.qty;

    return {
      price: adjustedTotalPrice,
      components: [{
        type: 'Seasonal',
        key: `Seasonal-${seasonalPrice.season}`,
        description: `Seasonal pricing (${seasonalPrice.season}): ${seasonalPrice.appliedRule.name} - ${seasonalPrice.adjustmentType === 'PERCENTAGE' ? `${seasonalPrice.appliedRule.adjustmentValue}%` : seasonalPrice.adjustmentType === 'MULTIPLIER' ? `×${seasonalPrice.appliedRule.adjustmentValue}` : `€${seasonalPrice.appliedRule.adjustmentValue}`}`,
        value: seasonalPrice.adjustment * input.qty,
        basis: baseUnitPrice * input.qty,
        calculatedFrom: seasonalPrice.appliedRule.id,
      }],
    };
  } catch (error) {
    logger.warn({ error, tenantId, sku: input.sku }, 'Failed to apply seasonal pricing, using base price');
    return null; // Fallback to base price if seasonal pricing fails
  }
}

/**
 * Step 2: Apply Conditions (Discounts/Markups)
 */
async function applyConditions(
  tenantId: string,
  input: CalcQuoteInput,
  basePrice: number
): Promise<{ adjustment: number; components: PriceComponent[] }> {
  // Find condition sets for customer or segment
  const now = new Date();
  const sets = await db
    .select()
    .from(conditionSets)
    .where(
      and(
        eq(conditionSets.tenantId, tenantId),
        eq(conditionSets.key, input.customerId), // TODO: Also check for segment
        eq(conditionSets.active, true),
        lte(conditionSets.validFrom, now),
        or(isNull(conditionSets.validTo), gte(conditionSets.validTo, now))!
      )
    )
    .orderBy(conditionSets.priority); // Higher priority first

  const components: PriceComponent[] = [];
  let totalAdjustment = 0;

  for (const set of sets) {
    const rules = set.rules as ConditionRule[];
    
    for (const rule of rules) {
      // Check if rule applies
      if (!ruleApplies(rule, input)) continue;

      // Calculate adjustment
      let adjustment = 0;
      if (rule.method === 'ABS') {
        adjustment = rule.value * input.qty;
      } else if (rule.method === 'PCT') {
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

      // Apply conflict strategy
      if (set.conflictStrategy === 'Stack' || rule.stackable) {
        totalAdjustment += adjustment;
      } else if (set.conflictStrategy === 'MaxWins') {
        totalAdjustment = Math.max(totalAdjustment, adjustment);
      }
    }
  }

  return { adjustment: totalAdjustment, components };
}

/**
 * Check if condition rule applies
 */
function ruleApplies(rule: ConditionRule, input: CalcQuoteInput): boolean {
  // Check scope
  if (rule.scope === 'SKU' && rule.selector?.sku && rule.selector.sku !== input.sku) {
    return false;
  }

  // Check quantity
  if (rule.minQty && input.qty < rule.minQty) return false;
  if (rule.maxQty && input.qty > rule.maxQty) return false;

  // Check channel
  if (rule.channel && rule.channel !== 'All' && rule.channel !== input.channel) return false;

  // Check time
  if (rule.validFrom || rule.validTo) {
    const now = new Date();
    if (rule.validFrom && new Date(rule.validFrom) > now) return false;
    if (rule.validTo && new Date(rule.validTo) < now) return false;
  }

  return true;
}

/**
 * Step 3: Apply Dynamic Formula (if any)
 */
async function applyDynamicFormula(
  tenantId: string,
  input: CalcQuoteInput,
  currentPrice: number
): Promise<{ price: number; components: PriceComponent[] } | null> {
  // Find active formula for SKU or commodity
  const now = new Date();
  const [formula] = await db
    .select()
    .from(dynamicFormulas)
    .where(
      and(
        eq(dynamicFormulas.tenantId, tenantId),
        or(eq(dynamicFormulas.sku, input.sku), eq(dynamicFormulas.commodity, input.sku.split('-')[0] || input.sku)),
        eq(dynamicFormulas.active, true),
        lte(dynamicFormulas.validFrom, now),
        or(isNull(dynamicFormulas.validTo), gte(dynamicFormulas.validTo, now))
      )!
    )
    .limit(1);

  if (formula === undefined || formula === null) return null;

  // Evaluate formula
  const result = await evaluateFormula(formula, input.context ?? {});

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

/**
 * Step 4: Apply Charges (Fees, Levies)
 */
async function applyCharges(
  tenantId: string,
  input: CalcQuoteInput,
  currentPrice: number
): Promise<{ total: number; components: PriceComponent[] }> {
  const now = new Date();
  const charges = await db
    .select()
    .from(taxChargeRefs)
    .where(
      and(
        eq(taxChargeRefs.tenantId, tenantId),
        eq(taxChargeRefs.active, true),
        lte(taxChargeRefs.validFrom, now),
        or(isNull(taxChargeRefs.validTo), gte(taxChargeRefs.validTo, now))!,
        // Only non-VAT charges
        or(
          eq(taxChargeRefs.type, 'Fee'),
          eq(taxChargeRefs.type, 'Levy'),
          eq(taxChargeRefs.type, 'Surcharge')
        )!
      )
    );

  const components: PriceComponent[] = [];
  let total = 0;

  for (const charge of charges) {
    // Check scope
    if (charge.scope === 'SKU' && charge.scopeValue !== input.sku) continue;
    if (charge.scope === 'Commodity' && !input.sku.startsWith(charge.scopeValue ?? '')) continue;

    let value = 0;
    if (charge.method === 'ABS') {
      value = parseFloat(charge.rateOrAmount.toString()) * input.qty;
    } else if (charge.method === 'PCT') {
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

/**
 * Step 5: Apply Taxes (nur Referenz!)
 */
async function applyTaxes(
  tenantId: string,
  input: CalcQuoteInput,
  netPrice: number
): Promise<{ total: number; components: PriceComponent[] }> {
  const now = new Date();
  const taxes = await db
    .select()
    .from(taxChargeRefs)
    .where(
      and(
        eq(taxChargeRefs.tenantId, tenantId),
        eq(taxChargeRefs.type, 'VAT'),
        eq(taxChargeRefs.active, true),
        lte(taxChargeRefs.validFrom, now),
        or(isNull(taxChargeRefs.validTo), gte(taxChargeRefs.validTo, now))!
      )
    )
    .limit(1); // Nur eine USt

  if (taxes.length === 0) {
    return { total: 0, components: [] };
  }

  const tax = taxes[0];
  const value = netPrice * (parseFloat(tax!.rateOrAmount.toString()) / 100);

  return {
    total: value,
    components: [{
      type: 'Tax',
      key: `Tax-${tax!.code}`,
      description: tax!.name,
      value,
      basis: netPrice,
      calculatedFrom: tax!.id,
    }],
  };
}

/**
 * Get quote by ID
 */
export async function getQuoteById(tenantId: string, quoteId: string): Promise<PriceQuote | null> {
  const [quote] = await db
    .select()
    .from(priceQuotes)
    .where(and(eq(priceQuotes.id, quoteId), eq(priceQuotes.tenantId, tenantId)))
    .limit(1);

  if (quote === undefined || quote === null) return null;

  // Check if expired
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
  } as PriceQuote;
}

