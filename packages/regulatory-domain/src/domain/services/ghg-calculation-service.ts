import { db } from '../../infra/db/connection';
import { ghgPathways } from '../../infra/db/schema';
import { GHGCalculationInput, GHGPathway } from '../entities/ghg-pathway';
// REDII_DEFAULT_VALUES and GHGFactors removed - not exported from module
import { publishEvent } from '../../infra/messaging/publisher';
import { calculateCropEmissions, getKTBLStatus } from '../../infra/integrations/ktbl-api';
import { eq, and } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'ghg-calculation' });

/**
 * Calculate GHG emissions for a pathway
 */
export async function calculateGHG(
  tenantId: string,
  input: GHGCalculationInput,
  userId: string
): Promise<GHGPathway> {
  logger.info({ tenantId, commodity: input.commodity, method: input.method }, 'Calculating GHG emissions');

  let factors: any;
  let totalEmissions: number;
  let savingsVsFossil: number | undefined;
  const dataSources = [];

  if (input.method === 'Default') {
    // Use RED II Default Values
    const defaultKey = `${input.commodity}_BIODIESEL`;
    const REDII_DEFAULT_VALUES: any = {}; // TODO: Import from ghg-pathway
    const defaultValues = REDII_DEFAULT_VALUES[defaultKey];

    if (defaultValues === undefined || defaultValues === null) {
      throw new Error(`No RED II default values found for ${input.commodity}`);
    }

    totalEmissions = defaultValues.totalEmissions;
    savingsVsFossil = defaultValues.savingsVsFossil;

    factors = {
      cultivation: totalEmissions * 0.4, // Approximation
      processing: totalEmissions * 0.3,
      transport: totalEmissions * 0.2,
      landUseChange: totalEmissions * 0.1,
    };

    dataSources.push({
      factor: 'total',
      source: 'RED II Annex V Default Values',
      value: totalEmissions,
    });

  } else if (input.method === 'Actual' && input.actualData) {
    // Calculate from actual data with optional KTBL integration
    
    // Try to get KTBL data for cultivation emissions
    let cultivationEmissions = input.actualData.cultivationEmissions || 0;
    let cultivationSource = 'Operator Data';

    try {
      // Check if KTBL is available and use it for cultivation
      const ktblStatus = await getKTBLStatus();
      
      if (ktblStatus.available || ktblStatus.fallbackActive) {
        const ktblData = await calculateCropEmissions(input.commodity, {
          yieldPerHa: input.actualData.yieldPerHa,
          fertilizer: input.actualData.nitrogenFertilizer,
          region: (input as any).originRegion,
        } as any);
        
        // Convert kg CO2eq/t to gCO2eq/MJ (approximation)
        cultivationEmissions = ktblData.emissionsPerTon / 40; // ~40 MJ/kg für Öle
        cultivationSource = ktblData.dataSource;
        
        dataSources.push({
          factor: 'cultivation',
          source: `KTBL BEK: ${cultivationSource}`,
          value: cultivationEmissions,
        });
      }
    } catch (error) {
      logger.warn({ error }, 'KTBL integration failed, using operator data');
      // Fallback to operator data
    }
    
    factors = {
      cultivation: cultivationEmissions,
      processing: input.actualData.processingEmissions || 0,
      transport: calculateTransportEmissions(input.actualData.transportDistance, input.actualData.transportMode),
      landUseChange: input.actualData.landUseChange || 0,
    };

    totalEmissions = factors.cultivation + factors.processing + factors.transport + factors.landUseChange;

    // Savings vs Fossil (RED II: Fossil = 94 gCO2eq/MJ für Diesel)
    const fossilBaseline = 94;
    savingsVsFossil = Math.round(((fossilBaseline - totalEmissions) / fossilBaseline) * 100);

    if (!dataSources.find(ds => ds.factor === 'cultivation')) {
      dataSources.push(
        { factor: 'cultivation', source: cultivationSource, value: factors.cultivation }
      );
    }
    dataSources.push(
      { factor: 'processing', source: 'Operator Data', value: factors.processing },
      { factor: 'transport', source: 'Calculated', value: factors.transport }
    );

  } else {
    throw new Error('Invalid method or missing actualData for Actual calculation');
  }

  // RED II Compliance-Check
  const rediiThreshold = determineREDIIThreshold(new Date());
  const rediiCompliant = savingsVsFossil !== undefined && savingsVsFossil >= rediiThreshold;

  // Pathway-Key generieren
  const pathwayKey = generatePathwayKey(input.commodity, (input as any).originRegion, input.method);

  // Speichern
  const [pathway] = await db.insert(ghgPathways).values({
    tenantId,
    commodity: input.commodity,
    pathwayKey,
    method: input.method,
    standard: 'REDII',
    factors: factors as any,
    totalEmissions: totalEmissions.toString(),
    savingsVsFossil: savingsVsFossil?.toString(),
    rediiThreshold: rediiThreshold.toString(),
    rediiCompliant,
    dataSources: dataSources as any,
    calculatedAt: new Date(),
    calculatedBy: userId,
  } as any).returning();

  if (pathway === undefined || pathway === null) {
    throw new Error('Failed to create GHG pathway');
  }

  // Publish event
  await publishEvent('ghg.pathway.created', {
    tenantId,
    pathwayId: pathway.id,
    commodity: pathway.commodity,
    method: pathway.method,
    totalEmissions,
    savingsVsFossil,
    rediiCompliant,
    occurredAt: new Date().toISOString(),
  });

  return pathway as any as GHGPathway;
}

/**
 * Calculate transport emissions based on distance and mode
 */
function calculateTransportEmissions(distance?: number, mode?: string): number {
  if (distance === undefined || distance === null) return 0;

  // Emission factors in gCO2eq/t·km
  const emissionFactors: Record<string, number> = {
    'Truck': 0.062,
    'Train': 0.022,
    'Ship': 0.008,
    'Pipeline': 0.003,
  };

  const factor = emissionFactors[mode ?? 'Truck'] || 0.062;
  return distance * factor;
}

/**
 * Determine RED II threshold based on date
 * - Before 2021: 50%
 * - 2021-2025: 60%
 * - After 2025: 65%
 */
function determineREDIIThreshold(date: Date): number {
  const year = date.getFullYear();
  
  if (year < 2021) return 50;
  if (year < 2026) return 60;
  return 65;
}

/**
 * Generate pathway key
 */
function generatePathwayKey(commodity: string, region?: string, method?: string): string {
  const parts = [region ?? 'EU', commodity, method ?? 'Default'];
  return parts.join('-');
}

/**
 * Get GHG Pathways
 */
export async function getGHGPathways(
  tenantId: string,
  filters: {
    commodity?: string;
    method?: string;
  } = {}
): Promise<GHGPathway[]> {
  let query = db.select().from(ghgPathways).where(eq(ghgPathways.tenantId, tenantId));

  const results = await query;

  let filtered = results;
  if (filters.commodity) {
    filtered = filtered.filter(p => p.commodity === filters.commodity);
  }
  if (filters.method) {
    filtered = filtered.filter(p => p.method === filters.method);
  }

  return filtered as any as GHGPathway[];
}

