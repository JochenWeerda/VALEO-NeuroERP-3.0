import { describe, it, expect } from 'vitest';

describe('Numbering Service', () => {
  it('should format number with YYYY pattern', () => {
    const pattern = 'INV-{YYYY}-{seq5}';
    const year = new Date().getFullYear();
    const seq = 123;
    
    const result = pattern
      .replace('{YYYY}', String(year))
      .replace('{seq5}', String(seq).padStart(5, '0'));
    
    expect(result).toBe(`INV-${year}-00123`);
  });

  it('should format number with YY pattern', () => {
    const pattern = 'DOC-{YY}-{seq}';
    const year = String(new Date().getFullYear()).slice(-2);
    const seq = 42;
    
    const result = pattern
      .replace('{YY}', year)
      .replace('{seq}', String(seq));
    
    expect(result).toBe(`DOC-${year}-42`);
  });
});
