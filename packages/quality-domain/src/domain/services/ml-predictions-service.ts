import { db } from '../../infra/db/connection';
import { nonConformities, samples, sampleResults } from '../../infra/db/schema';
import { eq, and, gte, desc, sql } from 'drizzle-orm';
import { publishEvent } from '../../infra/messaging/publisher';
import pino from 'pino';

const logger = pino({ name: 'ml-predictions' });

/**
 * ML-Model Interface (Placeholder - in Produktion würde hier TensorFlow.js o.ä. verwendet)
 */
interface MLModel {
  predict(features: number[]): number;
  confidence: number;
}

/**
 * NC Risk Prediction
 * Vorhersage der Wahrscheinlichkeit einer NC basierend auf historischen Daten
 */
export async function predictNcRisk(
  tenantId: string,
  context: {
    commodity?: string;
    supplierId?: string;
    productionLine?: string;
  }
): Promise<{
  riskScore: number; // 0-100
  confidence: number; // 0-1
  factors: Array<{ factor: string; impact: number }>;
  recommendation: string;
}> {
  logger.info({ tenantId, context }, 'Predicting NC risk');

  // Lade historische NC-Daten (letzte 90 Tage)
  const startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
  
  const historicalNcs = await db
    .select()
    .from(nonConformities)
    .where(
      and(
        eq(nonConformities.tenantId, tenantId),
        gte(nonConformities.detectedAt, startDate)
      )
    )
    .orderBy(desc(nonConformities.detectedAt));

  // Feature-Extraktion
  const features = extractFeatures(historicalNcs, context);
  
  // ML-Vorhersage (Simplified - in Produktion: TensorFlow.js, ONNX Runtime, etc.)
  const prediction = calculateRiskScore(features);
  
  return {
    riskScore: prediction.riskScore,
    confidence: prediction.confidence,
    factors: prediction.factors,
    recommendation: generateRecommendation(prediction.riskScore),
  };
}

/**
 * Feature-Extraktion für ML-Model
 */
function extractFeatures(ncs: any[], context: any): Record<string, number> {
  const total = ncs.length;
  
  // Berechne Features
  const criticalRate = ncs.filter(nc => nc.severity === 'Critical').length / (total || 1);
  const majorRate = ncs.filter(nc => nc.severity === 'Major').length / (total || 1);
  const specOutRate = ncs.filter(nc => nc.type === 'SpecOut').length / (total || 1);
  const contaminationRate = ncs.filter(nc => nc.type === 'Contamination').length / (total || 1);
  
  // Durchschnittliche Zeit bis zur Schließung (in Tagen)
  const closedNcs = ncs.filter(nc => nc.closedAt);
  const avgClosureTime = closedNcs.length > 0
    ? closedNcs.reduce((sum, nc) => {
        const days = Math.floor((new Date(nc.closedAt).getTime() - new Date(nc.detectedAt).getTime()) / (1000 * 60 * 60 * 24));
        return sum + days;
      }, 0) / closedNcs.length
    : 0;
  
  // Trend: Steigend/Fallend
  const lastMonth = ncs.filter(nc => new Date(nc.detectedAt) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)).length;
  const monthBefore = ncs.filter(nc => {
    const date = new Date(nc.detectedAt);
    return date > new Date(Date.now() - 60 * 24 * 60 * 60 * 1000) && date <= new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  }).length;
  const trend = monthBefore > 0 ? (lastMonth - monthBefore) / monthBefore : 0;

  return {
    total,
    criticalRate,
    majorRate,
    specOutRate,
    contaminationRate,
    avgClosureTime,
    trend,
  };
}

/**
 * Risk-Score-Berechnung (Simplified ML-Model)
 */
function calculateRiskScore(features: Record<string, number>): {
  riskScore: number;
  confidence: number;
  factors: Array<{ factor: string; impact: number }>;
} {
  // Gewichtete Faktoren
  const weights = {
    criticalRate: 40,
    majorRate: 25,
    specOutRate: 15,
    contaminationRate: 15,
    trend: 20,
    avgClosureTime: 10,
  };

  const factors = [
    { factor: 'Critical NC Rate', impact: Math.round((features.criticalRate ?? 0) * weights.criticalRate) },
    { factor: 'Major NC Rate', impact: Math.round((features.majorRate ?? 0) * weights.majorRate) },
    { factor: 'Spec Violations', impact: Math.round((features.specOutRate ?? 0) * weights.specOutRate) },
    { factor: 'Contamination Rate', impact: Math.round((features.contaminationRate ?? 0) * weights.contaminationRate) },
    { factor: 'Trend (increasing)', impact: Math.round(Math.max(0, features.trend ?? 0) * weights.trend) },
    { factor: 'Slow Closure Time', impact: Math.round(Math.min(1, (features.avgClosureTime ?? 0) / 30) * weights.avgClosureTime) },
  ];

  const riskScore = Math.min(100, factors.reduce((sum, f) => sum + f.impact, 0));
  
  // Confidence basierend auf Datenmenge
  const confidence = Math.min(1, (features.total ?? 0) / 50); // Mindestens 50 NCs für hohe Confidence

  return { riskScore, confidence, factors };
}

/**
 * Empfehlung generieren basierend auf Risk-Score
 */
function generateRecommendation(riskScore: number): string {
  if (riskScore >= 80) {
    return 'KRITISCH: Sofortige Maßnahmen erforderlich. Quality-Audit und CAPA-Review durchführen.';
  } else if (riskScore >= 60) {
    return 'HOCH: Verstärkte Überwachung empfohlen. Ursachenanalyse für häufigste NC-Typen durchführen.';
  } else if (riskScore >= 40) {
    return 'MITTEL: Qualitätstrends überwachen. Präventive Maßnahmen in Erwägung ziehen.';
  } else if (riskScore >= 20) {
    return 'NIEDRIG: Aktuelle Qualitätsprozesse beibehalten. Regelmäßige Reviews durchführen.';
  } else {
    return 'SEHR NIEDRIG: Qualitätsprozesse funktionieren gut. Weiter so!';
  }
}

/**
 * Anomalie-Erkennung in Sample-Ergebnissen
 * Erkennt ungewöhnliche Muster die auf Probleme hindeuten
 */
export async function detectAnomalies(
  tenantId: string,
  analyte: string,
  timeWindowDays: number = 30
): Promise<{
  anomaliesDetected: boolean;
  anomalies: Array<{
    sampleId: string;
    value: number;
    expectedRange: { min: number; max: number };
    deviation: number;
    timestamp: string;
  }>;
  recommendation: string;
}> {
  logger.info({ tenantId, analyte, timeWindowDays }, 'Detecting anomalies');

  const startDate = new Date(Date.now() - timeWindowDays * 24 * 60 * 60 * 1000);

  // Lade Sample-Ergebnisse
  const results = await db
    .select()
    .from(sampleResults)
    .innerJoin(samples, eq(sampleResults.sampleId, samples.id))
    .where(
      and(
        eq(sampleResults.tenantId, tenantId),
        eq(sampleResults.analyte, analyte),
        gte(samples.takenAt, startDate)
      )
    )
    .orderBy(desc(samples.takenAt));

  if (results.length < 10) {
    return {
      anomaliesDetected: false,
      anomalies: [],
      recommendation: 'Zu wenige Daten für Anomalie-Erkennung. Mindestens 10 Messungen erforderlich.',
    };
  }

  // Statistik berechnen
  const values = results.map(r => parseFloat(r.sample_results.value.toString()));
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const stdDev = Math.sqrt(
    values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length
  );

  // Anomalien = Werte außerhalb von ±2 Standardabweichungen
  const anomalies = results
    .map((r, i) => {
      const value = values[i] ?? 0;
      const deviation = Math.abs(value - mean) / stdDev;
      
      if (deviation > 2) {
        return {
          sampleId: r.sample_results.sampleId,
          value,
          expectedRange: { min: mean - 2 * stdDev, max: mean + 2 * stdDev },
          deviation: Math.round(deviation * 100) / 100,
          timestamp: r.samples.takenAt.toISOString(),
        };
      }
      return null;
    })
    .filter(a => a !== null) as any[];

  const anomaliesDetected = anomalies.length > 0;
  
  let recommendation = '';
  if (anomaliesDetected) {
    const recentAnomalies = anomalies.filter(a => 
      new Date(a.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    );
    
    if (recentAnomalies.length >= 3) {
      recommendation = 'WARNUNG: Mehrere Anomalien in den letzten 7 Tagen. Prozess überprüfen!';
    } else {
      recommendation = 'Vereinzelte Anomalien erkannt. Beobachtung fortsetzen.';
    }
  } else {
    recommendation = 'Keine Anomalien erkannt. Werte im Normalbereich.';
  }

  return { anomaliesDetected, anomalies, recommendation };
}

/**
 * Supplier Quality Score
 * Berechnet einen Quality-Score für Lieferanten basierend auf NC-Historie
 */
export async function calculateSupplierQualityScore(
  tenantId: string,
  supplierId: string
): Promise<{
  score: number; // 0-100 (100 = perfekt)
  trend: 'improving' | 'stable' | 'declining';
  metrics: {
    totalNcs: number;
    criticalNcs: number;
    avgResponseTime: number; // in Tagen
    recurrenceRate: number; // 0-1
  };
  recommendation: string;
}> {
  logger.info({ tenantId, supplierId }, 'Calculating supplier quality score');

  const ncs = await db
    .select()
    .from(nonConformities)
    .where(
      and(
        eq(nonConformities.tenantId, tenantId),
        eq(nonConformities.supplierId, supplierId)
      )
    )
    .orderBy(desc(nonConformities.detectedAt));

  const totalNcs = ncs.length;
  const criticalNcs = ncs.filter(nc => nc.severity === 'Critical').length;
  
  // Response-Zeit berechnen
  const closedNcs = ncs.filter(nc => nc.closedAt);
  const avgResponseTime = closedNcs.length > 0
    ? closedNcs.reduce((sum, nc) => {
        const days = Math.floor((new Date(nc.closedAt!).getTime() - new Date(nc.detectedAt).getTime()) / (1000 * 60 * 60 * 24));
        return sum + days;
      }, 0) / closedNcs.length
    : 0;

  // Recurrence-Rate (gleiche NC-Typen wiederholen sich)
  const typeOccurrences: Record<string, number> = {};
  ncs.forEach(nc => {
    typeOccurrences[nc.type] = (typeOccurrences[nc.type] || 0) + 1;
  });
  const recurrenceRate = Object.values(typeOccurrences).filter(count => count > 1).length / Object.keys(typeOccurrences).length;

  // Score-Berechnung
  let score = 100;
  score -= totalNcs * 2; // -2 Punkte pro NC
  score -= criticalNcs * 10; // -10 Punkte pro Critical NC
  score -= Math.min(30, avgResponseTime); // Bis zu -30 Punkte für langsame Response
  score -= recurrenceRate * 20; // -20 Punkte bei 100% Recurrence
  score = Math.max(0, score);

  // Trend ermitteln (letzte 3 Monate vs. vorherige 3 Monate)
  const last3Months = ncs.filter(nc => new Date(nc.detectedAt) > new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)).length;
  const previous3Months = ncs.filter(nc => {
    const date = new Date(nc.detectedAt);
    return date > new Date(Date.now() - 180 * 24 * 60 * 60 * 1000) && date <= new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
  }).length;
  
  let trend: 'improving' | 'stable' | 'declining' = 'stable';
  if (previous3Months > 0) {
    const change = (last3Months - previous3Months) / previous3Months;
    if (change < -0.2) trend = 'improving';
    else if (change > 0.2) trend = 'declining';
  }

  // Empfehlung
  let recommendation = '';
  if (score >= 80) {
    recommendation = 'Exzellenter Lieferant. Keine Maßnahmen erforderlich.';
  } else if (score >= 60) {
    recommendation = 'Guter Lieferant. Vereinzelte Verbesserungen möglich.';
  } else if (score >= 40) {
    recommendation = 'Durchschnittlich. Lieferanten-Audit empfohlen.';
  } else {
    recommendation = 'KRITISCH: Lieferanten-Review und Qualitätsvereinbarungen neu verhandeln.';
  }

  return {
    score,
    trend,
    metrics: {
      totalNcs,
      criticalNcs,
      avgResponseTime,
      recurrenceRate,
    },
    recommendation,
  };
}

/**
 * Predictive Maintenance Alert
 * Vorhersage wann Equipment/Prozesse gewartet werden sollten
 */
export async function predictMaintenanceNeeds(
  tenantId: string,
  productionLine: string
): Promise<{
  maintenanceRecommended: boolean;
  urgency: 'low' | 'medium' | 'high';
  estimatedDaysUntilFailure: number;
  indicators: string[];
}> {
  logger.info({ tenantId, productionLine }, 'Predicting maintenance needs');

  // Lade NCs für diese Produktionslinie
  const ncs = await db
    .select()
    .from(nonConformities)
    .where(
      and(
        eq(nonConformities.tenantId, tenantId),
        sql`${nonConformities.detectedLocation} LIKE ${`%${productionLine}%`}`
      )
    )
    .orderBy(desc(nonConformities.detectedAt))
    .limit(100);

  // Analyse: ProcessDeviation-Rate steigt = Maintenance nötig
  const processDeviations = ncs.filter(nc => nc.type === 'ProcessDeviation');
  const last7Days = processDeviations.filter(nc => 
    new Date(nc.detectedAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  ).length;

  const maintenanceRecommended = last7Days >= 3;
  
  let urgency: 'low' | 'medium' | 'high' = 'low';
  let estimatedDaysUntilFailure = 90;
  
  if (last7Days >= 5) {
    urgency = 'high';
    estimatedDaysUntilFailure = 7;
  } else if (last7Days >= 3) {
    urgency = 'medium';
    estimatedDaysUntilFailure = 14;
  }

  const indicators = [
    last7Days >= 3 ? 'Erhöhte ProcessDeviation-Rate' : null,
    ncs.filter(nc => nc.severity === 'Major').length > 5 ? 'Mehrere Major NCs' : null,
  ].filter(i => i !== null) as string[];

  return {
    maintenanceRecommended,
    urgency,
    estimatedDaysUntilFailure,
    indicators,
  };
}
