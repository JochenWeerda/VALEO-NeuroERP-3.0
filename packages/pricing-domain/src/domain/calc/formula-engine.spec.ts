import { describe, expect, it } from 'vitest';

import { evaluateFormula } from './formula-engine';

const input = (key: string, fallback: number) => ({
  key,
  source: 'Static' as const,
  fallback,
});

describe('evaluateFormula', () => {
  it('evaluates precedence and parentheses without executing arbitrary code', async () => {
    const result = await evaluateFormula(
      {
        expression: '(BASE + BASIS) * FACTOR - FREIGHT',
        inputs: [
          input('BASE', 100),
          input('BASIS', 5),
          input('FACTOR', 2),
          input('FREIGHT', 10),
        ],
      },
      {},
    );

    expect(result.roundedValue).toBe(200);
  });

  it('rejects unknown variables and division by zero', async () => {
    await expect(
      evaluateFormula(
        { expression: 'BASE + UNKNOWN', inputs: [input('BASE', 100)] },
        {},
      ),
    ).rejects.toThrow('Unknown or invalid variable');

    await expect(
      evaluateFormula(
        {
          expression: 'BASE / ZERO',
          inputs: [input('BASE', 100), input('ZERO', 0)],
        },
        {},
      ),
    ).rejects.toThrow('Division by zero');
  });
});
