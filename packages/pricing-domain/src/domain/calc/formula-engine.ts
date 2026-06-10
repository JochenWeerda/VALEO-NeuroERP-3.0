import { FormulaInput, PriceCaps, RoundingConfig } from '../entities/dynamic-formula';
import pino from 'pino';

const logger = pino({ name: 'formula-engine' });

type Token = number | string;

const OPERATORS: Record<string, { precedence: number; apply: (_left: number, _right: number) => number }> = {
  '+': { precedence: 1, apply: (left, right) => left + right },
  '-': { precedence: 1, apply: (left, right) => left - right },
  '*': { precedence: 2, apply: (left, right) => left * right },
  '/': {
    precedence: 2,
    apply: (left, right) => {
      if (right === 0) throw new Error('Division by zero');
      return left / right;
    },
  },
};

function tokenize(expression: string): Token[] {
  const tokens: Token[] = [];
  const matcher = /\s*(?:(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|([()+\-*/]))/gy;
  let offset = 0;

  while (offset < expression.length) {
    matcher.lastIndex = offset;
    const match = matcher.exec(expression);
    if (!match) throw new Error(`Invalid token at position ${offset}`);
    if (match[1]) tokens.push(Number(match[1]));
    else if (match[2]) tokens.push(match[2]);
    else if (match[3]) tokens.push(match[3]);
    offset = matcher.lastIndex;
  }

  return tokens;
}

function evaluateExpression(expression: string, values: Record<string, number>): number {
  const output: Token[] = [];
  const operators: string[] = [];
  let expectsValue = true;

  for (const token of tokenize(expression)) {
    if (typeof token === 'number' || /^[A-Za-z_]/.test(token)) {
      if (!expectsValue) throw new Error('Missing operator');
      output.push(token);
      expectsValue = false;
      continue;
    }
    if (token === '(') {
      operators.push(token);
      expectsValue = true;
      continue;
    }
    if (token === ')') {
      while (operators.length && operators.at(-1) !== '(') {
        const operator = operators.pop();
        if (operator !== undefined) output.push(operator);
      }
      if (operators.pop() !== '(') throw new Error('Unbalanced parentheses');
      expectsValue = false;
      continue;
    }
    if (expectsValue && token === '-') output.push(0);
    else if (expectsValue) throw new Error('Operator without left operand');
    const currentOperator = OPERATORS[token];
    if (!currentOperator) throw new Error(`Unsupported operator: ${token}`);
    while (operators.length) {
      const candidate = operators.at(-1);
      if (candidate === undefined || candidate === '(') break;
      const candidateOperator = OPERATORS[candidate];
      if (!candidateOperator || candidateOperator.precedence < currentOperator.precedence) break;
      const operator = operators.pop();
      if (operator !== undefined) output.push(operator);
    }
    operators.push(token);
    expectsValue = true;
  }

  if (expectsValue) throw new Error('Incomplete expression');
  while (operators.length) {
    const operator = operators.pop();
    if (operator === undefined) break;
    if (operator === '(') throw new Error('Unbalanced parentheses');
    output.push(operator);
  }

  const stack: number[] = [];
  for (const token of output) {
    if (typeof token === 'number') stack.push(token);
    else {
      const operator = OPERATORS[token];
      if (!operator) {
        const value = values[token];
        if (value === undefined || !Number.isFinite(value)) {
          throw new Error(`Unknown or invalid variable: ${token}`);
        }
        stack.push(value);
        continue;
      }
      const right = stack.pop();
      const left = stack.pop();
      if (left === undefined || right === undefined) throw new Error('Invalid expression');
      stack.push(operator.apply(left, right));
    }
  }
  if (stack.length !== 1 || !Number.isFinite(stack[0])) throw new Error('Invalid result');
  const result = stack[0];
  if (result === undefined) throw new Error('Invalid result');
  return result;
}

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
    result = evaluateExpression(formula.expression, resolvedInputs);
  } catch (error) {
    logger.error({ error, expression: formula.expression }, 'Formula evaluation failed');
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Formula evaluation error: ${message}`);
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
