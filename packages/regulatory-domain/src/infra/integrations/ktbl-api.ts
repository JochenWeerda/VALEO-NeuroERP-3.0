import axios from 'axios';
import pino from 'pino';

const logger = pino({ name: 'ktbl-api' });

/**
 * KTBL BEK (Berechnungsstandard für einzelbetriebliche Klimabilanzen)
 * 
 * Source: https://www.ktbl.de/webanwendungen/bek-parameter
 * 
 * Liefert Parameter und Begleitwerte zur Bilanzierung von Treibhausgasemissionen:
 * - Direkte Emissionen (unmittelbar im landwirtschaftlichen Prozess)
 * - Indirekte Emissionen (aus Umsetzungen emittierter Substanzen)
 * - Vorgelagerte Emissionen (aus Herstellung von Betriebsmitteln)
 * 
 * Status: Aktuell offline (werden überarbeitet)
 * TODO: Aktivieren sobald KTBL-Webanwendung wieder verfügbar
 */

const KTBL_API_BASE_URL = process.env.KTBL_API_URL ?? 'https://www.ktbl.de/webanwendungen/bek-parameter';
const KTBL_API_ENABLED = process.env.KTBL_API_ENABLED === 'true';

/**
 * KTBL Emission Category
 */
export interface KTBLEmissionCategory {
  direct: number;      // Direkte Emissionen (kg CO2eq/t)
  indirect: number;    // Indirekte Emissionen
  upstream: number;    // Vorgelagerte Emissionen (Betriebsmittel)
  total: number;       // Gesamt
}

/**
 * KTBL Crop Parameters
 */
export interface KTBLCropParameters {
  crop: string;                     // z.B. "Raps", "Weizen", "Mais"
  region?: string;                  // NUTS-2 Region
  yieldPerHa: number;              // t/ha
  nitrogenFertilizer: number;      // kg N/ha
  emissions: KTBLEmissionCategory;
  source: string;                   // KTBL BEK Version/Jahr
  calculatedAt: string;
}

/**
 * Fetch emission parameters from KTBL BEK database
 * 
 * @param crop - Crop/Commodity (z.B. "Raps", "Weizen")
 * @param region - NUTS-2 Region (z.B. "DE21" für Oberbayern)
 * @returns KTBL emission parameters or null
 */
export async function fetchKTBLEmissionParameters(
  crop: string,
  region?: string
): Promise<KTBLCropParameters | null> {
  if (KTBL_API_ENABLED === undefined || KTBL_API_ENABLED === null) {
    logger.warn('KTBL API is disabled, using fallback data');
    return getKTBLFallbackData(crop, region);
  }

  try {
    logger.info({ crop, region }, 'Fetching KTBL BEK parameters');

    // TODO: Implementiere echte KTBL-API-Calls sobald verfügbar
    // Die KTBL-Webanwendung bietet aktuell keine REST-API
    // Mögliche Optionen:
    // 1. Web-Scraping (wenn wieder online)
    // 2. CSV-Export-Import
    // 3. Lizensierte API-Zugang anfragen
    // 4. KTBL-Kontakt: ktbl@ktbl.de

    const response = await axios.get(`${KTBL_API_BASE_URL}/api/crop-emissions`, {
      params: {
        crop,
        region,
      },
      timeout: 10000,
    });

    return response.data;

  } catch (error) {
    logger.error({ error, crop, region }, 'Failed to fetch KTBL parameters, using fallback');
    return getKTBLFallbackData(crop, region);
  }
}

/**
 * Fallback data based on literature values
 * (Verwendet bis KTBL-Webanwendung wieder verfügbar)
 * 
 * Quellen:
 * - KTBL-Schrift (alte Versionen)
 * - Literaturwerte aus Studien
 * - RED II Default-Werte als Basis
 */
function getKTBLFallbackData(crop: string, region?: string): KTBLCropParameters {
  const cropLower = crop.toLowerCase();

  // Fallback-Werte basierend auf Literatur und RED II
  const fallbackDatabase: Record<string, KTBLEmissionCategory> = {
    'raps': {
      direct: 420,      // kg CO2eq/t (Anbau, N2O aus Düngung)
      indirect: 180,    // Indirekte N2O-Emissionen
      upstream: 250,    // Dünger, Pestizide, Diesel
      total: 850,       // Gesamt
    },
    'weizen': {
      direct: 380,
      indirect: 160,
      upstream: 220,
      total: 760,
    },
    'mais': {
      direct: 400,
      indirect: 170,
      upstream: 240,
      total: 810,
    },
    'soja': {
      direct: 350,
      indirect: 150,
      upstream: 200,
      total: 700,
    },
    'sonnenblume': {
      direct: 390,
      indirect: 165,
      upstream: 230,
      total: 785,
    },
  };

  const emissions = fallbackDatabase[cropLower] || {
    direct: 400,
    indirect: 170,
    upstream: 230,
    total: 800,
  };

  return {
    crop,
    region: region ?? 'DE-Generic',
    yieldPerHa: 3.5, // Generic average
    nitrogenFertilizer: 150, // kg N/ha (generic)
    emissions,
    source: 'Fallback Values (KTBL offline)',
    calculatedAt: new Date().toISOString(),
  };
}

/**
 * Calculate total crop emissions per ton
 * 
 * @param crop - Crop type
 * @param yieldPerHa - Actual yield (optional, uses KTBL default otherwise)
 * @param fertilizer - N-Fertilizer used in kg/ha (optional)
 * @param region - NUTS-2 region (optional)
 */
export async function calculateCropEmissions(
  crop: string,
  options?: {
    yieldPerHa?: number;
    fertilizer?: number;
    region?: string;
  }
): Promise<{
  emissionsPerTon: number; // kg CO2eq/t
  breakdown: KTBLEmissionCategory;
  dataSource: string;
}> {
  const ktblData = await fetchKTBLEmissionParameters(crop, options?.region);

  if (ktblData === undefined || ktblData === null) {
    throw new Error(`No KTBL data available for crop: ${crop}`);
  }

  // Anpassung basierend auf tatsächlichem Ertrag
  let emissionsPerTon = ktblData.emissions.total;

  if (options?.yieldPerHa && ktblData.yieldPerHa) {
    // Höherer Ertrag = niedrigere Emissionen pro Tonne
    const yieldFactor = ktblData.yieldPerHa / options.yieldPerHa;
    emissionsPerTon = ktblData.emissions.total * yieldFactor;
  }

  // Anpassung basierend auf N-Düngung
  if (options?.fertilizer && ktblData.nitrogenFertilizer) {
    // Mehr N-Dünger = höhere N2O-Emissionen
    const fertilizerDiff = options.fertilizer - ktblData.nitrogenFertilizer;
    const additionalN2O = fertilizerDiff * 4.5; // ca. 4.5 kg CO2eq per kg N (IPCC-Faktor)
    emissionsPerTon += additionalN2O / (options.yieldPerHa || ktblData.yieldPerHa);
  }

  return {
    emissionsPerTon: Math.round(emissionsPerTon),
    breakdown: ktblData.emissions,
    dataSource: ktblData.source,
  };
}

/**
 * Get KTBL database status
 */
export async function getKTBLStatus(): Promise<{
  available: boolean;
  lastCheck: string;
  message: string;
  fallbackActive: boolean;
}> {
  if (KTBL_API_ENABLED === undefined || KTBL_API_ENABLED === null) {
    return {
      available: false,
      lastCheck: new Date().toISOString(),
      message: 'KTBL API is disabled in configuration',
      fallbackActive: true,
    };
  }

  try {
    // Probe-Request an KTBL
    const response = await axios.get(`${KTBL_API_BASE_URL}/status`, {
      timeout: 5000,
    });

    return {
      available: true,
      lastCheck: new Date().toISOString(),
      message: 'KTBL BEK-Parameter verfügbar',
      fallbackActive: false,
    };

  } catch (error) {
    logger.warn({ error }, 'KTBL service not available');
    
    return {
      available: false,
      lastCheck: new Date().toISOString(),
      message: 'KTBL BEK-Parameter werden überarbeitet (aktuell offline). Fallback-Daten werden verwendet.',
      fallbackActive: true,
    };
  }
}

/**
 * Cache KTBL data locally (für Performance)
 */
const ktblCache: Map<string, { data: KTBLCropParameters; timestamp: number }> = new Map();
const CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 Tage

export function getCachedKTBLData(crop: string, region?: string): KTBLCropParameters | null {
  const cacheKey = `${crop}:${region ?? 'default'}`;
  const cached = ktblCache.get(cacheKey);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
    logger.debug({ crop, region }, 'KTBL cache hit');
    return cached.data;
  }

  return null;
}

export function setCachedKTBLData(crop: string, region: string | undefined, data: KTBLCropParameters): void {
  const cacheKey = `${crop}:${region ?? 'default'}`;
  ktblCache.set(cacheKey, { data, timestamp: Date.now() });
}

