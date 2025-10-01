import { describe, it, expect } from 'vitest';
import { fetchKTBLEmissionParameters, calculateCropEmissions, getKTBLStatus } from '../../src/infra/integrations/ktbl-api';

describe('KTBL Integration Tests', () => {
  describe('KTBL Status', () => {
    it('should return fallback status when KTBL offline', async () => {
      const status = await getKTBLStatus();
      
      expect(status).toHaveProperty('available');
      expect(status).toHaveProperty('fallbackActive');
      expect(status).toHaveProperty('message');
      expect(status.fallbackActive).toBe(true); // Aktuell sollte Fallback aktiv sein
    });
  });

  describe('Fetch KTBL Emission Parameters', () => {
    it('should return fallback data for Raps', async () => {
      const params = await fetchKTBLEmissionParameters('Raps', 'DE21');
      
      expect(params).toBeDefined();
      expect(params?.crop).toBe('Raps');
      expect(params?.emissions.total).toBe(850); // Fallback-Wert
      expect(params?.source).toContain('Fallback');
    });

    it('should return fallback data for Weizen', async () => {
      const params = await fetchKTBLEmissionParameters('Weizen');
      
      expect(params).toBeDefined();
      expect(params?.emissions.total).toBe(760);
    });

    it('should have emission breakdown', async () => {
      const params = await fetchKTBLEmissionParameters('Mais');
      
      expect(params?.emissions).toHaveProperty('direct');
      expect(params?.emissions).toHaveProperty('indirect');
      expect(params?.emissions).toHaveProperty('upstream');
      expect(params?.emissions).toHaveProperty('total');
      
      // Total sollte Summe der Komponenten sein
      const sum = params!.emissions.direct + params!.emissions.indirect + params!.emissions.upstream;
      expect(params?.emissions.total).toBe(sum);
    });
  });

  describe('Calculate Crop Emissions', () => {
    it('should calculate emissions for standard yield', async () => {
      const result = await calculateCropEmissions('Raps');
      
      expect(result.emissionsPerTon).toBeGreaterThan(0);
      expect(result.breakdown).toBeDefined();
      expect(result.dataSource).toContain('Fallback');
    });

    it('should adjust for higher yield (lower emissions per ton)', async () => {
      const baseline = await calculateCropEmissions('Raps', { yieldPerHa: 3.5 });
      const higherYield = await calculateCropEmissions('Raps', { yieldPerHa: 4.5 });
      
      expect(higherYield.emissionsPerTon).toBeLessThan(baseline.emissionsPerTon);
    });

    it('should adjust for higher fertilizer (higher N2O)', async () => {
      const baseline = await calculateCropEmissions('Raps', {
        yieldPerHa: 4.0,
        fertilizer: 150,
      });
      
      const moreFertilizer = await calculateCropEmissions('Raps', {
        yieldPerHa: 4.0,
        fertilizer: 200, // +50 kg N/ha
      });
      
      expect(moreFertilizer.emissionsPerTon).toBeGreaterThan(baseline.emissionsPerTon);
    });

    it('should include breakdown in result', async () => {
      const result = await calculateCropEmissions('Soja', {
        yieldPerHa: 3.2,
        fertilizer: 120,
        region: 'DE24',
      });
      
      expect(result.breakdown.direct).toBeGreaterThan(0);
      expect(result.breakdown.indirect).toBeGreaterThan(0);
      expect(result.breakdown.upstream).toBeGreaterThan(0);
    });
  });

  describe('Fallback Data Coverage', () => {
    const crops = ['Raps', 'Weizen', 'Mais', 'Soja', 'Sonnenblume'];

    crops.forEach(crop => {
      it(`should have fallback data for ${crop}`, async () => {
        const params = await fetchKTBLEmissionParameters(crop);
        
        expect(params).toBeDefined();
        expect(params?.crop).toBe(crop);
        expect(params?.emissions.total).toBeGreaterThan(0);
      });
    });

    it('should handle unknown crops with generic values', async () => {
      const params = await fetchKTBLEmissionParameters('UnknownCrop');
      
      expect(params).toBeDefined();
      expect(params?.emissions.total).toBe(800); // Generic default
    });
  });

  describe('IPCC N2O Factor', () => {
    it('should apply IPCC factor of 4.5 kg CO2eq per kg N', async () => {
      const baseline = await calculateCropEmissions('Raps', {
        yieldPerHa: 4.0,
        fertilizer: 150,
      });
      
      const plus10N = await calculateCropEmissions('Raps', {
        yieldPerHa: 4.0,
        fertilizer: 160, // +10 kg N
      });
      
      // Erwartete Differenz: 10 kg N * 4.5 kg CO2eq/kg N / 4.0 t/ha = ~11.25 kg CO2eq/t
      const diff = plus10N.emissionsPerTon - baseline.emissionsPerTon;
      expect(diff).toBeCloseTo(11, 1);
    });
  });
});
