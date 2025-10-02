"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.evaluateFormula = evaluateFormula;
const expr_eval_1 = require("expr-eval");
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'formula-engine' });
const parser = new expr_eval_1.Parser();
async function evaluateFormula(formula, context) {
    logger.debug({ formulaExpression: formula.expression }, 'Evaluating formula');
    const resolvedInputs = {};
    for (const input of formula.inputs) {
        const value = await resolveFormulaInput(input, context);
        resolvedInputs[input.key] = value;
    }
    let result;
    try {
        const expr = parser.parse(formula.expression);
        result = expr.evaluate(resolvedInputs);
    }
    catch (error) {
        logger.error({ error, expression: formula.expression }, 'Formula evaluation failed');
        throw new Error(`Formula evaluation error: ${error}`);
    }
    let cappedValue;
    if (formula.caps) {
        const caps = formula.caps;
        if (caps.min !== undefined && result < caps.min) {
            cappedValue = result;
            result = caps.min;
        }
        if (caps.max !== undefined && result > caps.max) {
            cappedValue = result;
            result = caps.max;
        }
    }
    let roundedValue = result;
    if (formula.rounding) {
        const rounding = formula.rounding;
        if (rounding.step) {
            const factor = 1 / rounding.step;
            if (rounding.mode === 'up') {
                roundedValue = Math.ceil(result * factor) / factor;
            }
            else if (rounding.mode === 'down') {
                roundedValue = Math.floor(result * factor) / factor;
            }
            else {
                roundedValue = Math.round(result * factor) / factor;
            }
        }
    }
    const evaluationResult = {
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
async function resolveFormulaInput(input, context) {
    if (context[input.key] !== undefined) {
        return context[input.key];
    }
    switch (input.source) {
        case 'Index':
        case 'Futures':
            logger.warn({ key: input.key, source: input.source }, 'Using fallback for market data');
            return input.fallback || getMockMarketData(input.key);
        case 'Basis':
            return input.fallback || 0;
        case 'FX':
            return input.fallback || 1.0;
        case 'Static':
            return input.fallback || 0;
        case 'Custom':
            return context[input.key] || input.fallback || 0;
        default:
            return input.fallback || 0;
    }
}
function getMockMarketData(key) {
    const mockData = {
        'MATIF_NOV': 425.50,
        'MATIF_MAY': 430.00,
        'CBOT_DEC': 520.00,
        'BASIS': -15.00,
        'FREIGHT': 12.50,
        'EUR_USD': 1.08,
    };
    return mockData[key] || 0;
}
//# sourceMappingURL=formula-engine.js.map