import { CalcQuoteInput, PriceQuote } from '../entities/price-quote';
export declare function calculateQuote(tenantId: string, input: CalcQuoteInput, userId?: string): Promise<PriceQuote>;
export declare function getQuoteById(tenantId: string, quoteId: string): Promise<PriceQuote | null>;
//# sourceMappingURL=price-calculator.d.ts.map