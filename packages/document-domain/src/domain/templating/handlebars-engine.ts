import Handlebars from 'handlebars';
import pino from 'pino';

const logger = pino({ name: 'handlebars-engine' });

// Register helpers
Handlebars.registerHelper('formatCurrency', (value: number, currency: string = 'EUR') => {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(value);
});

Handlebars.registerHelper('formatDate', (date: string, locale: string = 'de-DE') => {
  return new Intl.DateTimeFormat(locale).format(new Date(date));
});

export async function renderTemplate(source: string, data: Record<string, any>): Promise<string> {
  try {
    const template = Handlebars.compile(source);
    return template(data);
  } catch (error) {
    logger.error({ error }, 'Template rendering failed');
    throw error;
  }
}
