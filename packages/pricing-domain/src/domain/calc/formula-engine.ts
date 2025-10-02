import { Parser } from 'expr-eval';
import { FormulaInput } from '../entities/dynamic-formula';
import { RoundingConfig, PriceCaps } from '../entities/dynamic-formula';
import pino from 'pino';

const logger = pino({ name: 'formula-engine' });

const parser = new Parser();

/**
 * Evaluate Dynamic Formula
 * 
 * Safe evaluation using expr-eval library
 * Expression: "MATIF_NOV + BASIS - FREIGHT"
 */
export async function evaluateFormula(
  formula: { expression: string; inputs: any; rounding?: any; caps?: any },
  context: Record<string, any>
): Promise<{
  result: number;
  inputs: Record<string, number>;
  expression: string;
  cappedValue?: number;
  roundedValue: number;
  calculatedAt: string;
}> {
  logger.debug({ formulaExpression: formula.expression }, 'Evaluating formula');

  // Resolve inputs
  const resolvedInputs: Record<string, number> = {};
  
  for (const input of (formula.inputs as FormulaInput[])) {
    const value = await resolveFormulaInput(input, context);
    resolvedInputs[input.key] = value;
  }

  // Evaluate expression
  let result: number;
  try {
    const expr = parser.parse(formula.expression);
    result = expr.evaluate(resolvedInputs);
  } catch (error) {
    logger.error({ error, expression: formula.expression }, 'Formula evaluation failed');
    throw new Error(`Formula evaluation error: ${error}`);
  }

  // Apply caps
  let cappedValue: number | undefined;
  if (formula.caps) {
    const caps = formula.caps as PriceCaps;
    if (caps.min !== undefined && result < caps.min) {
      cappedValue = result;
      result = caps.min;
    }
    if (caps.max !== undefined && result > caps.max) {
      cappedValue = result;
      result = caps.max;
    }
  }

  // Apply rounding
  let roundedValue = result;
  if (formula.rounding) {
    const rounding = formula.rounding as RoundingConfig;
    if (rounding.step) {
      const factor = 1 / rounding.step;
      if (rounding.mode === 'up') {
        roundedValue = Math.ceil(result * factor) / factor;
      } else if (rounding.mode === 'down') {
        roundedValue = Math.floor(result * factor) / factor;
      } else {
        roundedValue = Math.round(result * factor) / factor;
      }
    }
  }

  const evaluationResult: any = {
    result,
    inputs: resolvedInputs,
    expression: formula.expression,
    roundedValue,
    calculatedAt: new Date().toISOString(),
  };

  if (cappedValue !== undefined) {
    evaluationResult.cappedValue = cappedValue;
  }

  return evaluationResult;
}

/**
 * Resolve single formula input
 */
async function resolveFormulaInput(
  input: FormulaInput,
  context: Record<string, any>
): Promise<number> {
  // Check if value provided in context
  if (context[input.key] !== undefined) {
    return context[input.key];
  }

  // Resolve from source
  switch (input.source) {
    case 'Index':
    case 'Futures':
      // TODO: Integration mit Marktdaten-Provider
      // Für jetzt: Fallback oder Mock
      logger.warn({ key: input.key, source: input.source }, 'Using fallback for market data');
      return input.fallback || getMockMarketData(input.key);

    case 'Basis':
      return input.fallback || 0;

    case 'FX':
      // TODO: Wechselkurs-API
      return input.fallback || 1.0;

    case 'Static':
      return input.fallback || 0;

    case 'Custom':
      return context[input.key] || input.fallback || 0;

    default:
      return input.fallback || 0;
  }
}

/**
 * Mock market data (Production: echte API)
 */
function getMockMarketData(key: string): number {
  const mockData: Record<string, number> = {
    'MATIF_NOV': 425.50,       // EUR/t Raps Nov
    'MATIF_MAY': 430.00,       // EUR/t Raps Mai
    'CBOT_DEC': 520.00,        // USD/t Soja Dez
    'BASIS': -15.00,           // Basis-Spread
    'FREIGHT': 12.50,          // Fracht
    'EUR_USD': 1.08,           // Wechselkurs
  };

  return mockData[key] || 0;
}
