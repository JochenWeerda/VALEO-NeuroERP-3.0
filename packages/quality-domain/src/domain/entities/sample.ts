import { z } from 'zod';

/**
 * Sample Source - Herkunft der Probe
 */
export const SampleSourceEnum = z.enum([
  'Production',    // Aus Produktion (Batch)
  'Contract',      // Aus Vertrag (Lieferung/Abnahme)
  'Inbound',       // Wareneingang
  'Outbound',      // Warenausgang
  'Quarantine',    // Quarantäne-Nachprüfung
  'RetainCheck',   // Rückstellprobe-Überprüfung
]);

export type SampleSource = z.infer<typeof SampleSourceEnum>;

/**
 * Sample Status
 */
export const SampleStatusEnum = z.enum([
  'Pending',       // Warte auf Analyse
  'InProgress',    // In Analyse
  'Analyzed',      // Analysiert
  'Retained',      // Als Rückstellprobe aufbewahrt
  'Disposed',      // Entsorgt
]);

export type SampleStatus = z.infer<typeof SampleStatusEnum>;

/**
 * Sample - Probe zur Qualitätsprüfung
 */
export const SampleSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Context
  batchId: z.string().uuid().optional(), // Referenz zu production-domain
  contractId: z.string().uuid().optional(), // Referenz zu contracts-domain
  lotId: z.string().uuid().optional(), // Referenz zu inventory-domain
  source: SampleSourceEnum,
  
  // Identifikation
  sampleCode: z.string().min(1, 'Sample code is required'), // z.B. "S-2025-001234"
  description: z.string().optional(),
  
  // Probenahme
  takenAt: z.string().datetime(),
  takenBy: z.string().min(1, 'Taken by is required'), // User ID
  takenLocation: z.string().optional(), // z.B. "Silo 3, Top"
  
  // Prüfplan
  planId: z.string().uuid().optional(),
  
  // Rückstellprobe
  retained: z.boolean().default(false),
  retainedLocation: z.string().optional(), // z.B. "Kühlschrank A, Fach 3"
  retainedUntil: z.string().datetime().optional(),
  
  // Status
  status: SampleStatusEnum.default('Pending'),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
  disposedAt: z.string().datetime().optional(),
  disposedBy: z.string().optional(),
});

export type Sample = z.infer<typeof SampleSchema>;

/**
 * Sample Result - Einzelnes Analyseergebnis
 */
export const SampleResultStatusEnum = z.enum([
  'Pass',          // Innerhalb Spezifikation
  'Fail',          // Außerhalb Spezifikation
  'Investigate',   // Grenzwertig, weitere Prüfung nötig
  'NA',            // Nicht anwendbar
]);

export type SampleResultStatus = z.infer<typeof SampleResultStatusEnum>;

export const SampleResultSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  sampleId: z.string().uuid(),
  
  // Analyse
  analyte: z.string().min(1, 'Analyte is required'), // z.B. "Moisture", "Protein"
  value: z.number(),
  unit: z.string().min(1, 'Unit is required'), // z.B. "%", "ppm"
  method: z.string().min(1, 'Method is required'), // z.B. "HPLC", "Karl-Fischer"
  
  // Laborinfo
  labId: z.string().optional(), // Internes oder externes Labor
  analyzedAt: z.string().datetime().optional(),
  analyzedBy: z.string().optional(), // User ID oder Labor-Techniker
  
  // Bewertung
  result: SampleResultStatusEnum,
  limits: z.object({
    min: z.number().optional(),
    max: z.number().optional(),
    target: z.number().optional(),
  }).optional(),
  
  // Kommentar
  comment: z.string().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
});

export type SampleResult = z.infer<typeof SampleResultSchema>;

/**
 * Create Sample DTO
 */
export const CreateSampleSchema = SampleSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  disposedAt: true,
  disposedBy: true,
});

export type CreateSample = z.infer<typeof CreateSampleSchema>;

/**
 * Create Sample Result DTO
 */
export const CreateSampleResultSchema = SampleResultSchema.omit({
  id: true,
  createdAt: true,
});

export type CreateSampleResult = z.infer<typeof CreateSampleResultSchema>;
