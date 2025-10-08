import axios from 'axios';
import pino from 'pino';

const logger = pino({ name: 'bvl-api' });

const BVL_API_BASE_URL = process.env.BVL_API_URL ?? 'https://apps2.bvl.bund.de/psm/jsp';

/**
 * Fetch PSM data from BVL Online Database
 * 
 * Note: BVL bietet keine offizielle REST-API, daher Mock-Implementation
 * In Produktion: Web-Scraping oder manuelle Datenpflege nötig
 */
export async function fetchFromBVL(identifier: string): Promise<any | null> {
  logger.info({ identifier }, 'Fetching PSM from BVL (Mock)');

  try {
    // MOCK DATA - In Produktion würde hier echter BVL-Zugriff stattfinden
    // Die BVL-Datenbank ist aktuell nur per Web-Interface verfügbar
    
    const mockDatabase: Record<string, any> = {
      '024266-00': {
        bvlId: '024266-00',
        name: 'Roundup PowerFlex',
        activeSubstances: ['Glyphosat'],
        approvalStatus: 'Approved',
        approvalValidTo: '2025-12-31T23:59:59Z',
        approvalNumber: '024266-00',
        usageScope: 'Getreide, Raps, Mais',
        restrictions: ['Nicht in Wasserschutzgebieten'],
        sourceUrl: `${BVL_API_BASE_URL}/index.jsp?id=024266-00`,
      },
      'Roundup': {
        bvlId: '024266-00',
        name: 'Roundup PowerFlex',
        activeSubstances: ['Glyphosat'],
        approvalStatus: 'Approved',
        approvalValidTo: '2025-12-31T23:59:59Z',
        usageScope: 'Getreide, Raps, Mais',
        sourceUrl: `${BVL_API_BASE_URL}/index.jsp`,
      },
      '006498-00': {
        bvlId: '006498-00',
        name: 'Karate Zeon',
        activeSubstances: ['Lambda-Cyhalothrin'],
        approvalStatus: 'Approved',
        approvalValidTo: '2026-06-30T23:59:59Z',
        usageScope: 'Raps, Getreide',
        restrictions: [],
        sourceUrl: `${BVL_API_BASE_URL}/index.jsp?id=006498-00`,
      },
    };

    // Suche nach BVL-ID oder Name
    const result = mockDatabase[identifier];
    
    if (result) {
      logger.info({ identifier, bvlId: result.bvlId }, 'PSM found in BVL (Mock)');
      return result;
    }

    // Fallback: Partielle Name-Suche
    for (const [key, value] of Object.entries(mockDatabase)) {
      if (value.name.toLowerCase().includes(identifier.toLowerCase())) {
        logger.info({ identifier, found: value.name }, 'PSM found by partial match (Mock)');
        return value;
      }
    }

    logger.warn({ identifier }, 'PSM not found in BVL (Mock)');
    return null;

    // TODO: In Produktion
    // - Option 1: BVL-Webseite scrapen (problematisch, rechtlich unklar)
    // - Option 2: Manuelle CSV-Downloads + Import
    // - Option 3: Lizensierte PSM-Datenbank (z.B. NEPTUN)
    // - Option 4: Eigene Datenbank pflegen

  } catch (error) {
    logger.error({ error, identifier }, 'Failed to fetch PSM from BVL');
    return null;
  }
}

/**
 * Search PSM in BVL database
 */
export async function searchPSM(query: string, filters?: {
  activeSubstance?: string;
  crop?: string;
}): Promise<any[]> {
  logger.info({ query, filters }, 'Searching PSM in BVL (Mock)');

  // MOCK - würde in Produktion BVL-API/Scraping nutzen
  const mockResults = [
    {
      bvlId: '024266-00',
      name: 'Roundup PowerFlex',
      activeSubstances: ['Glyphosat'],
      approvalStatus: 'Approved',
      usageScope: 'Getreide, Raps, Mais',
    },
    {
      bvlId: '006498-00',
      name: 'Karate Zeon',
      activeSubstances: ['Lambda-Cyhalothrin'],
      approvalStatus: 'Approved',
      usageScope: 'Raps, Getreide',
    },
  ];

  let filtered = mockResults.filter(item =>
    item.name.toLowerCase().includes(query.toLowerCase())
  );

  if (filters?.activeSubstance) {
    filtered = filtered.filter(item =>
      item.activeSubstances.some(s => s.toLowerCase().includes(filters.activeSubstance!.toLowerCase()))
    );
  }

  if (filters?.crop) {
    filtered = filtered.filter(item =>
      item.usageScope.toLowerCase().includes(filters.crop!.toLowerCase())
    );
  }

  return filtered;
}

