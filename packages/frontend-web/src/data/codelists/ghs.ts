/**
 * GHS Piktogramme (CLP-VO 2025)
 * Quelle: BAuA, Umweltbundesamt
 */

export interface GHSPiktogramm {
  code: string;
  label: string;
  icon: string;
  description: string;
  hSaetze: string[]; // Typische H-Sätze für dieses Piktogramm
  pSaetze: string[]; // Typische P-Sätze für dieses Piktogramm
}

export const GHS_PIKTOGRAMME: GHSPiktogramm[] = [
  {
    code: 'GHS01',
    label: 'Explosiv',
    icon: 'explosive',
    description: 'Explosionsgefährliche Stoffe und Gemische',
    hSaetze: ['H200', 'H201', 'H202', 'H203', 'H204', 'H205'],
    pSaetze: ['P210', 'P230', 'P240', 'P250', 'P280']
  },
  {
    code: 'GHS02',
    label: 'Entzündbar',
    icon: 'flame',
    description: 'Entzündbare Gase, Flüssigkeiten und Feststoffe',
    hSaetze: ['H220', 'H221', 'H222', 'H223', 'H224', 'H225', 'H226', 'H228'],
    pSaetze: ['P210', 'P211', 'P220', 'P222', 'P223', 'P231', 'P232', 'P240', 'P241', 'P242', 'P243', 'P280', 'P285']
  },
  {
    code: 'GHS03',
    label: 'Oxidierend',
    icon: 'oxidizing',
    description: 'Oxidierende Gase, Flüssigkeiten und Feststoffe',
    hSaetze: ['H240', 'H241', 'H242', 'H250', 'H251', 'H252', 'H270', 'H271', 'H272'],
    pSaetze: ['P210', 'P220', 'P221', 'P280', 'P283', 'P370', 'P378']
  },
  {
    code: 'GHS04',
    label: 'Gase unter Druck',
    icon: 'gas-cylinder',
    description: 'Gase unter Druck',
    hSaetze: ['H280', 'H281'],
    pSaetze: ['P202', 'P210', 'P222', 'P244', 'P260', 'P264', 'P271', 'P272', 'P273', 'P280', 'P285', 'P410', 'P411', 'P420']
  },
  {
    code: 'GHS05',
    label: 'Ätzend',
    icon: 'corrosive',
    description: 'Ätzende Stoffe',
    hSaetze: ['H290', 'H314', 'H318'],
    pSaetze: ['P260', 'P264', 'P280', 'P301', 'P302', 'P303', 'P304', 'P305', 'P306', 'P307', 'P308', 'P309', 'P310', 'P311', 'P312', 'P313', 'P314', 'P315', 'P316', 'P317', 'P318', 'P319', 'P320', 'P321', 'P322', 'P330', 'P331', 'P332', 'P333', 'P334', 'P335', 'P336', 'P337', 'P338', 'P340', 'P341', 'P342', 'P343', 'P344', 'P345', 'P346', 'P347', 'P348', 'P349', 'P350', 'P351', 'P352', 'P353', 'P354', 'P355', 'P356', 'P357', 'P358', 'P359', 'P360', 'P361', 'P362', 'P363', 'P364', 'P365', 'P366', 'P367', 'P368', 'P369', 'P370', 'P371', 'P372', 'P373', 'P374', 'P375', 'P376', 'P377', 'P378', 'P379', 'P380', 'P381', 'P390', 'P391', 'P401', 'P402', 'P403', 'P404', 'P405', 'P406', 'P407', 'P408', 'P409', 'P410', 'P411', 'P412', 'P413', 'P414', 'P420', 'P422', 'P501']
  },
  {
    code: 'GHS06',
    label: 'Giftig',
    icon: 'skull',
    description: 'Giftige Stoffe',
    hSaetze: ['H300', 'H301', 'H302', 'H310', 'H311', 'H312', 'H314', 'H330', 'H331', 'H332', 'H334'],
    pSaetze: ['P260', 'P261', 'P262', 'P263', 'P264', 'P270', 'P271', 'P272', 'P273', 'P280', 'P281', 'P282', 'P283', 'P284', 'P285', 'P301', 'P302', 'P303', 'P304', 'P305', 'P306', 'P307', 'P308', 'P309', 'P310', 'P311', 'P312', 'P313', 'P314', 'P315', 'P316', 'P317', 'P318', 'P319', 'P320', 'P321', 'P322', 'P330', 'P331', 'P332', 'P333', 'P334', 'P335', 'P336', 'P337', 'P338', 'P340', 'P341', 'P342', 'P343', 'P344', 'P345', 'P346', 'P347', 'P348', 'P349', 'P350', 'P351', 'P352', 'P353', 'P354', 'P355', 'P356', 'P357', 'P358', 'P359', 'P360', 'P361', 'P362', 'P363', 'P364', 'P365', 'P366', 'P367', 'P368', 'P369', 'P370', 'P371', 'P372', 'P373', 'P374', 'P375', 'P376', 'P377', 'P378', 'P379', 'P380', 'P381', 'P390', 'P391', 'P401', 'P402', 'P403', 'P404', 'P405', 'P406', 'P407', 'P408', 'P409', 'P410', 'P411', 'P412', 'P413', 'P414', 'P420', 'P422', 'P501']
  },
  {
    code: 'GHS07',
    label: 'Reizend',
    icon: 'exclamation',
    description: 'Reizende und sensibilisierende Stoffe',
    hSaetze: ['H302', 'H312', 'H314', 'H315', 'H317', 'H318', 'H319', 'H332', 'H334', 'H335', 'H336'],
    pSaetze: ['P261', 'P262', 'P263', 'P264', 'P270', 'P271', 'P272', 'P273', 'P280', 'P281', 'P282', 'P283', 'P284', 'P285', 'P301', 'P302', 'P303', 'P304', 'P305', 'P306', 'P307', 'P308', 'P309', 'P310', 'P311', 'P312', 'P313', 'P314', 'P315', 'P316', 'P317', 'P318', 'P319', 'P320', 'P321', 'P322', 'P330', 'P331', 'P332', 'P333', 'P334', 'P335', 'P336', 'P337', 'P338', 'P340', 'P341', 'P342', 'P343', 'P344', 'P345', 'P346', 'P347', 'P348', 'P349', 'P350', 'P351', 'P352', 'P353', 'P354', 'P355', 'P356', 'P357', 'P358', 'P359', 'P360', 'P361', 'P362', 'P363', 'P364', 'P365', 'P366', 'P367', 'P368', 'P369', 'P370', 'P371', 'P372', 'P373', 'P374', 'P375', 'P376', 'P377', 'P378', 'P379', 'P380', 'P381', 'P390', 'P391', 'P401', 'P402', 'P403', 'P404', 'P405', 'P406', 'P407', 'P408', 'P409', 'P410', 'P411', 'P412', 'P413', 'P414', 'P420', 'P422', 'P501']
  },
  {
    code: 'GHS08',
    label: 'Gesundheitsschädlich',
    icon: 'health-hazard',
    description: 'Gesundheitsschädliche und umweltgefährliche Stoffe',
    hSaetze: ['H300', 'H301', 'H302', 'H310', 'H311', 'H312', 'H314', 'H317', 'H318', 'H330', 'H331', 'H332', 'H334', 'H335', 'H336', 'H340', 'H341', 'H350', 'H351', 'H360', 'H361', 'H362', 'H370', 'H371', 'H372', 'H373'],
    pSaetze: ['P201', 'P202', 'P260', 'P261', 'P262', 'P263', 'P264', 'P270', 'P271', 'P272', 'P273', 'P280', 'P281', 'P282', 'P283', 'P284', 'P285', 'P301', 'P302', 'P303', 'P304', 'P305', 'P306', 'P307', 'P308', 'P309', 'P310', 'P311', 'P312', 'P313', 'P314', 'P315', 'P316', 'P317', 'P318', 'P319', 'P320', 'P321', 'P322', 'P330', 'P331', 'P332', 'P333', 'P334', 'P335', 'P336', 'P337', 'P338', 'P340', 'P341', 'P342', 'P343', 'P344', 'P345', 'P346', 'P347', 'P348', 'P349', 'P350', 'P351', 'P352', 'P353', 'P354', 'P355', 'P356', 'P357', 'P358', 'P359', 'P360', 'P361', 'P362', 'P363', 'P364', 'P365', 'P366', 'P367', 'P368', 'P369', 'P370', 'P371', 'P372', 'P373', 'P374', 'P375', 'P376', 'P377', 'P378', 'P379', 'P380', 'P381', 'P390', 'P391', 'P401', 'P402', 'P403', 'P404', 'P405', 'P406', 'P407', 'P408', 'P409', 'P410', 'P411', 'P412', 'P413', 'P414', 'P420', 'P422', 'P501']
  },
  {
    code: 'GHS09',
    label: 'Umweltgefährlich',
    icon: 'environment',
    description: 'Umweltgefährliche Stoffe',
    hSaetze: ['H400', 'H401', 'H402', 'H410', 'H411', 'H412', 'H413', 'H420'],
    pSaetze: ['P273', 'P391', 'P501']
  }
];

export const getGHSPiktogramm = (code: string): GHSPiktogramm | undefined => {
  return GHS_PIKTOGRAMME.find(p => p.code === code);
};

export const getGHSPiktogrammeForHSaetze = (hSaetze: string[]): string[] => {
  const relevantPiktos = new Set<string>();

  GHS_PIKTOGRAMME.forEach(pikto => {
    if (pikto.hSaetze.some(h => hSaetze.includes(h))) {
      relevantPiktos.add(pikto.code);
    }
  });

  return Array.from(relevantPiktos);
};