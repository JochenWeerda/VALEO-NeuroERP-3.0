import { describe, it, expect } from 'vitest';
import { renderTemplate } from '../../src/domain/services/template-renderer';

describe('Template Renderer', () => {
  it('should render handlebars template with variables', async () => {
    const template = 'Hello {{name}}! Invoice: {{invoiceNumber}}';
    const result = await renderTemplate(template, {
      name: 'Müller GmbH',
      invoiceNumber: 'INV-2025-001',
    });
    expect(result).toBe('Hello Müller GmbH! Invoice: INV-2025-001');
  });

  it('should format currency', async () => {
    const template = 'Total: {{formatCurrency amount "EUR"}}';
    const result = await renderTemplate(template, { amount: 5250.5 });
    expect(result).toContain('5.250,50');
  });

  it('should format date', async () => {
    const template = 'Date: {{formatDate date "de-DE"}}';
    const result = await renderTemplate(template, { date: '2025-10-01T00:00:00.000Z' });
    expect(result).toMatch(/Date: \d{1,2}\.\d{1,2}\.\d{4}/);
  });
});
