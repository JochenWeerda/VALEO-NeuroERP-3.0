import { z } from 'zod';

// GHS Piktogramme (Stand: CLP-VO 2025)
export const GHS_PIKTOGRAMME = [
  'GHS01', 'GHS02', 'GHS03', 'GHS04', 'GHS05',
  'GHS06', 'GHS07', 'GHS08', 'GHS09'
] as const;

// H-Sätze (Gefahrenhinweise) - Auszug aus CLP-VO
export const H_SAETZE = [
  'H200', 'H201', 'H202', 'H203', 'H204', 'H205',
  'H220', 'H221', 'H222', 'H223', 'H224', 'H225',
  'H226', 'H228', 'H240', 'H241', 'H242', 'H250',
  'H251', 'H252', 'H260', 'H261', 'H270', 'H271',
  'H272', 'H290', 'H300', 'H301', 'H302', 'H310',
  'H311', 'H312', 'H314', 'H315', 'H317', 'H318',
  'H319', 'H330', 'H331', 'H332', 'H334', 'H335',
  'H336', 'H340', 'H341', 'H350', 'H351', 'H360',
  'H361', 'H362', 'H370', 'H371', 'H372', 'H373',
  'H400', 'H401', 'H402', 'H410', 'H411', 'H412',
  'H413', 'H420'
] as const;

// P-Sätze (Sicherheitshinweise) - Auszug aus CLP-VO
export const P_SAETZE = [
  'P101', 'P102', 'P103', 'P201', 'P202', 'P210',
  'P211', 'P220', 'P221', 'P222', 'P223', 'P230',
  'P231', 'P232', 'P233', 'P234', 'P235', 'P240',
  'P241', 'P242', 'P243', 'P244', 'P250', 'P251',
  'P252', 'P253', 'P260', 'P261', 'P262', 'P263',
  'P264', 'P270', 'P271', 'P272', 'P273', 'P280',
  'P281', 'P282', 'P283', 'P284', 'P285', 'P301',
  'P302', 'P303', 'P304', 'P305', 'P306', 'P307',
  'P308', 'P309', 'P310', 'P311', 'P312', 'P313',
  'P314', 'P315', 'P320', 'P321', 'P322', 'P330',
  'P331', 'P332', 'P333', 'P334', 'P335', 'P336',
  'P337', 'P338', 'P340', 'P341', 'P342', 'P343',
  'P344', 'P345', 'P346', 'P347', 'P348', 'P349',
  'P350', 'P351', 'P352', 'P353', 'P354', 'P355',
  'P356', 'P357', 'P358', 'P360', 'P361', 'P362',
  'P363', 'P364', 'P365', 'P366', 'P367', 'P368',
  'P369', 'P370', 'P371', 'P372', 'P373', 'P374',
  'P375', 'P376', 'P377', 'P378', 'P379', 'P380',
  'P381', 'P382', 'P390', 'P391', 'P401', 'P402',
  'P403', 'P404', 'P405', 'P406', 'P407', 'P408',
  'P409', 'P410', 'P411', 'P412', 'P413', 'P414',
  'P420', 'P422', 'P501'
] as const;

// EUH-Sätze (Ergänzende Hinweise)
export const EUH_SAETZE = [
  'EUH001', 'EUH006', 'EUH014', 'EUH018', 'EUH019',
  'EUH044', 'EUH059', 'EUH066', 'EUH070', 'EUH071',
  'EUH201', 'EUH202', 'EUH203', 'EUH204', 'EUH205',
  'EUH206', 'EUH207', 'EUH208', 'EUH209', 'EUH210',
  'EUH401', 'EUH208', 'EUH209', 'EUH210'
] as const;

// Auflagen-Kategorien (BVL-Kodeliste Stand: Jan 2025)
export const AUFLAGEN_KATEGORIEN = [
  'NW', 'NG', 'NT', 'B', 'SF', 'SB', 'VA', 'SS', 'EUH', 'SONST'
] as const;

// PSM-Zulassungsstatus
export const ZULASSUNGS_STATUS = [
  'zugelassen', 'ruhend', 'widerrufen', 'abgelaufen'
] as const;

// Bienenschutz-Klassen
export const BIENENSCHUTZ_KLASSEN = [
  'B1', 'B2', 'B3', 'B4'
] as const;

// Anwendungszwecke
export const ANWENDUNGSZWECKE = [
  'Herbizid', 'Fungizid', 'Insektizid', 'Wachstumsregler',
  'Akarizid', 'Rodentizid', 'Sonstige'
] as const;

// Wirkstoff-Einheiten
export const WIRKSTOFF_EINHEITEN = [
  'g/l', 'g/kg', '%'
] as const;

// PSM Zod Schema
export const WirkstoffSchema = z.object({
  name: z.string().min(1, "Wirkstoffname ist erforderlich"),
  gehalt: z.number().positive("Gehalt muss positiv sein"),
  einheit: z.enum(WIRKSTOFF_EINHEITEN).default("g/l"),
  cas: z.string().optional(),
  echa_subst_id: z.string().optional(),
  ghs: z.array(z.enum(GHS_PIKTOGRAMME)).optional().default([]),
  h_saetze: z.array(z.enum(H_SAETZE)).optional().default([]),
  p_saetze: z.array(z.enum(P_SAETZE)).optional().default([]),
  euh_saetze: z.array(z.enum(EUH_SAETZE)).optional().default([]),
});

export const KulturAnwendungSchema = z.object({
  kulturCode: z.string().min(1, "Kultur-Code ist erforderlich"),
  kulturName: z.string().min(1, "Kultur-Name ist erforderlich"),
  zielorganismus: z.string().min(1, "Zielorganismus ist erforderlich"),
  anwendungszweck: z.enum(ANWENDUNGSZWECKE),
  bbchVon: z.string().regex(/^\d{1,3}$/, "BBCH-Code muss 1-3 Ziffern haben"),
  bbchBis: z.string().regex(/^\d{1,3}$/, "BBCH-Code muss 1-3 Ziffern haben"),
  aufwandmenge: z.string().min(1, "Aufwandmenge ist erforderlich"),
  maxAnzahlAnwendungen: z.number().int().min(0).default(1),
  wartezeit: z.string().optional(),
  bienenschutz: z.enum(BIENENSCHUTZ_KLASSEN).optional(),
}).refine((data) => {
  const von = parseInt(data.bbchVon);
  const bis = parseInt(data.bbchBis);
  return von <= bis;
}, {
  message: "BBCH 'von' muss kleiner oder gleich 'bis' sein",
  path: ["bbchVon"]
});

export const SicherheitSchema = z.object({
  psa: z.array(z.string()).optional().default([]),
  anwenderschutz: z.array(z.string()).optional().default([]),
  abstand_gewaesser: z.string().optional(),
  abstand_saumbiotop: z.string().optional(),
});

export const AuflageSchema = z.object({
  code: z.string().min(1, "Auflagen-Code ist erforderlich"),
  kategorie: z.enum(AUFLAGEN_KATEGORIEN).optional(),
  text: z.string().min(1, "Auflagen-Text ist erforderlich"),
  version: z.string().optional(),
});

export const ZulassungSchema = z.object({
  status: z.enum(ZULASSUNGS_STATUS).default("zugelassen"),
  statusSeit: z.string().optional(),
  gueltigBis: z.string().optional(),
  bvl_psm_id: z.string().optional(),
  letztePruefung: z.string().optional(),
});

export const PsmSchema = z.object({
  id: z.string().uuid().optional(),
  handelsname: z.string().min(2, "Handelsname muss mindestens 2 Zeichen haben"),
  zulassungsnummer: z.string().min(3, "Zulassungsnummer muss mindestens 3 Zeichen haben"),
  hersteller: z.string().min(2, "Hersteller muss mindestens 2 Zeichen haben"),
  formulierung: z.string().optional(),

  // Wirkstoffe & CLP
  wirkstoffe: z.array(WirkstoffSchema).min(1, "Mindestens ein Wirkstoff ist erforderlich"),

  // Kulturen & Anwendung
  kulturen: z.array(KulturAnwendungSchema).min(1, "Mindestens eine Kultur-Anwendung ist erforderlich"),

  // Sicherheit
  sicherheit: SicherheitSchema.default({}),

  // Auflagen
  auflagen: z.array(AuflageSchema).default([]),

  // Zulassung
  zulassung: ZulassungSchema.default({}),

  // Metadaten
  datenquelle: z.string().optional(),
});

export type PsmDto = z.infer<typeof PsmSchema>;
export type WirkstoffDto = z.infer<typeof WirkstoffSchema>;
export type KulturAnwendungDto = z.infer<typeof KulturAnwendungSchema>;
export type SicherheitDto = z.infer<typeof SicherheitSchema>;
export type AuflageDto = z.infer<typeof AuflageSchema>;
export type ZulassungDto = z.infer<typeof ZulassungSchema>;

// Codelisten für UI
export const GHS_LABELS: Record<string, string> = {
  GHS01: "Explosiv",
  GHS02: "Entzündbar",
  GHS03: "Oxidierend",
  GHS04: "Gase unter Druck",
  GHS05: "Ätzend",
  GHS06: "Giftig",
  GHS07: "Reizend",
  GHS08: "Gesundheitsschädlich",
  GHS09: "Umweltgefährlich"
};

export const AUFLAGEN_LABELS: Record<string, string> = {
  NW: "Wasserorganismen",
  NG: "Grundwasser",
  NT: "Nicht-Zielorganismen/Saumbiotope",
  B: "Bienenschutz",
  SF: "Sonstige Feldauflagen",
  SB: "Sonstige Betriebsauflagen",
  VA: "Verwendungsauflagen",
  SS: "Sonstige Sicherheitsauflagen",
  EUH: "EUH-Hinweise",
  SONST: "Sonstige"
};

export const BIENENSCHUTZ_LABELS: Record<string, string> = {
  B1: "Bienengefährlich (nicht auf blühende/beflogene Bestände)",
  B2: "Nur nach Ende Bienenflug bis 23 Uhr",
  B3: "Durch Zulassungsanwendung keine Gefährdung",
  B4: "Nicht bienengefährlich"
};