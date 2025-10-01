import { describe, it, expect } from 'vitest';
import { renderTemplate } from '../../src/domain/templating/handlebars-engine';

describe('Template Engine', () => {
  it('should render basic handlebars template', async () => {
    const template = '<h1>Hello {{name}}!</h1>';
    const result = await renderTemplate(template, { name: 'World' });
    expect(result).toBe('<h1>Hello World!</h1>');
  });

  it('should format currency with helper', async () => {
    const template = '{{formatCurrency price "EUR"}}';
    const result = await renderTemplate(template, { price: 1234.56 });
    expect(result).toContain('1.234,56');
  });

  it('should format date with helper', async () => {
    const template = '{{formatDate date "de-DE"}}';
    const result = await renderTemplate(template, { date: '2025-10-01T00:00:00.000Z' });
    expect(result).toMatch(/\d{1,2}\.\d{1,2}\.\d{4}/);
  });
});
