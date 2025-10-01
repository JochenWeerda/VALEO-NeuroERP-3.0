import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import supertest from 'supertest';
import server, { start, stop } from '../../src/app/server';

describe('Quality Workflow E2E Tests', () => {
  const tenantId = '123e4567-e89b-12d3-a456-426614174000';
  let qualityPlanId: string;
  let sampleId: string;
  let ncId: string;
  let capaId: string;

  beforeAll(async () => {
    // Start server
    // await start();
  });

  afterAll(async () => {
    // Stop server
    // await stop();
  });

  describe('Complete Quality Flow: Plan → Sample → Analysis → NC → CAPA', () => {
    it('Step 1: Create Quality Plan', async () => {
      const response = await supertest(server.server)
        .post('/quality/api/v1/plans')
        .set('x-tenant-id', tenantId)
        .send({
          name: 'Rapsöl Standardprüfung',
          commodity: 'RAPE_OIL',
          active: true,
          rules: [
            {
              analyte: 'Moisture',
              method: 'Karl-Fischer',
              unit: '%',
              min: 0,
              max: 0.1,
              frequency: 'perBatch',
              retainSample: true,
              retentionDays: 180,
            },
            {
              analyte: 'FFA',
              method: 'Titration',
              unit: '%',
              min: 0,
              max: 2.0,
              frequency: 'perBatch',
              retainSample: false,
            },
          ],
        });

      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe('Rapsöl Standardprüfung');
      
      qualityPlanId = response.body.id;
    });

    it('Step 2: Create Sample', async () => {
      const response = await supertest(server.server)
        .post('/quality/api/v1/samples')
        .set('x-tenant-id', tenantId)
        .send({
          batchId: '456e4567-e89b-12d3-a456-426614174001',
          source: 'Production',
          takenAt: new Date().toISOString(),
          takenBy: 'user-001',
          takenLocation: 'Silo 3, Top',
          planId: qualityPlanId,
          retained: true,
          retainedLocation: 'Kühlschrank A, Fach 3',
          retainedUntil: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000).toISOString(),
        });

      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
      expect(response.body).toHaveProperty('sampleCode');
      expect(response.body.sampleCode).toMatch(/^S-\d{4}-\d{6}$/);
      
      sampleId = response.body.id;
    });

    it('Step 3: Add Sample Results (Pass)', async () => {
      // Add Moisture result
      const response1 = await supertest(server.server)
        .post(`/quality/api/v1/samples/${sampleId}/results`)
        .set('x-tenant-id', tenantId)
        .send({
          analyte: 'Moisture',
          value: 0.08,
          unit: '%',
          method: 'Karl-Fischer',
          labId: 'Lab-A',
          analyzedAt: new Date().toISOString(),
          analyzedBy: 'lab-tech-001',
          result: 'Pass',
          limits: { min: 0, max: 0.1 },
        });

      expect(response1.status).toBe(201);

      // Add FFA result
      const response2 = await supertest(server.server)
        .post(`/quality/api/v1/samples/${sampleId}/results`)
        .set('x-tenant-id', tenantId)
        .send({
          analyte: 'FFA',
          value: 1.5,
          unit: '%',
          method: 'Titration',
          labId: 'Lab-A',
          analyzedAt: new Date().toISOString(),
          analyzedBy: 'lab-tech-001',
          result: 'Pass',
          limits: { min: 0, max: 2.0 },
        });

      expect(response2.status).toBe(201);
    });

    it('Step 4: Analyze Sample (Should Release)', async () => {
      const response = await supertest(server.server)
        .post(`/quality/api/v1/samples/${sampleId}/analyze`)
        .set('x-tenant-id', tenantId)
        .send({});

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('Released');
      expect(response.body.allPass).toBe(true);
    });

    it('Step 5: Create Sample with Failed Result', async () => {
      const createResponse = await supertest(server.server)
        .post('/quality/api/v1/samples')
        .set('x-tenant-id', tenantId)
        .send({
          batchId: '456e4567-e89b-12d3-a456-426614174002',
          source: 'Production',
          takenAt: new Date().toISOString(),
          takenBy: 'user-001',
          takenLocation: 'Silo 5',
          planId: qualityPlanId,
          retained: true,
        });

      const failedSampleId = createResponse.body.id;

      // Add failed result
      await supertest(server.server)
        .post(`/quality/api/v1/samples/${failedSampleId}/results`)
        .set('x-tenant-id', tenantId)
        .send({
          analyte: 'Moisture',
          value: 0.15, // Out of spec (max 0.1)
          unit: '%',
          method: 'Karl-Fischer',
          result: 'Fail',
          limits: { min: 0, max: 0.1 },
        });

      // Analyze (should reject)
      const analyzeResponse = await supertest(server.server)
        .post(`/quality/api/v1/samples/${failedSampleId}/analyze`)
        .set('x-tenant-id', tenantId)
        .send({});

      expect(analyzeResponse.body.status).toBe('Rejected');
      expect(analyzeResponse.body.allPass).toBe(false);
    });

    it('Step 6: Create Non-Conformity', async () => {
      const response = await supertest(server.server)
        .post('/quality/api/v1/ncs')
        .set('x-tenant-id', tenantId)
        .send({
          batchId: '456e4567-e89b-12d3-a456-426614174002',
          type: 'SpecOut',
          severity: 'Major',
          title: 'Feuchtigkeit außerhalb Spezifikation',
          description: 'Probe zeigte 0.15% Feuchtigkeit (Spec: max 0.1%)',
          detectedAt: new Date().toISOString(),
          detectedBy: 'user-001',
        });

      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
      expect(response.body).toHaveProperty('ncNumber');
      expect(response.body.ncNumber).toMatch(/^NC-\d{4}-\d{5}$/);
      
      ncId = response.body.id;
    });

    it('Step 7: Create CAPA linked to NC', async () => {
      const response = await supertest(server.server)
        .post('/quality/api/v1/capas')
        .set('x-tenant-id', tenantId)
        .send({
          linkedNcIds: [ncId],
          type: 'Corrective',
          title: 'Überprüfung Trocknungsprozess',
          description: 'Trocknungsprozess überprüfen und anpassen',
          action: 'Temperatur und Verweilzeit im Trockner erhöhen',
          rootCauseAnalysis: 'Unzureichende Trocknung aufgrund zu niedriger Temperatur',
          preventionStrategy: 'Regelmäßige Kalibrierung der Trocknungsparameter',
          responsibleUserId: 'user-002',
          responsibleDepartment: 'Produktion',
          dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        });

      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
      expect(response.body).toHaveProperty('capaNumber');
      expect(response.body.capaNumber).toMatch(/^CAPA-\d{4}-\d{5}$/);
      
      capaId = response.body.id;
    });

    it('Step 8: Link NC to CAPA', async () => {
      const response = await supertest(server.server)
        .post(`/quality/api/v1/ncs/${ncId}/link-capa`)
        .set('x-tenant-id', tenantId)
        .send({
          capaId,
        });

      expect(response.status).toBe(200);
      expect(response.body.capaId).toBe(capaId);
    });

    it('Step 9: Implement CAPA', async () => {
      const response = await supertest(server.server)
        .post(`/quality/api/v1/capas/${capaId}/implement`)
        .set('x-tenant-id', tenantId)
        .send({});

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('Implemented');
      expect(response.body.implementedAt).toBeDefined();
    });

    it('Step 10: Verify CAPA', async () => {
      const response = await supertest(server.server)
        .post(`/quality/api/v1/capas/${capaId}/verify`)
        .set('x-tenant-id', tenantId)
        .send({
          effectivenessCheck: true,
          effectivenessComment: 'Feuchtigkeit jetzt konstant unter 0.1%',
        });

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('Verified');
      expect(response.body.effectivenessCheck).toBe(true);
    });

    it('Step 11: Close NC', async () => {
      const response = await supertest(server.server)
        .post(`/quality/api/v1/ncs/${ncId}/close`)
        .set('x-tenant-id', tenantId)
        .send({
          comment: 'CAPA erfolgreich umgesetzt, Problem behoben',
        });

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('Closed');
      expect(response.body.closedAt).toBeDefined();
    });

    it('Step 12: Close CAPA', async () => {
      const response = await supertest(server.server)
        .post(`/quality/api/v1/capas/${capaId}/close`)
        .set('x-tenant-id', tenantId)
        .send({
          closureComment: 'Maßnahme erfolgreich abgeschlossen',
        });

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('Closed');
      expect(response.body.closedAt).toBeDefined();
    });
  });

  describe('Pagination & Filtering', () => {
    it('should list samples with pagination', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/samples?page=1&limit=10')
        .set('x-tenant-id', tenantId);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('page');
      expect(response.body).toHaveProperty('limit');
      expect(Array.isArray(response.body.data)).toBe(true);
    });

    it('should list NCs with filtering', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/ncs?severity=Major&status=Closed')
        .set('x-tenant-id', tenantId);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data.every((nc: any) => nc.severity === 'Major')).toBe(true);
    });

    it('should list CAPAs with search', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/capas?search=Trocknungsprozess')
        .set('x-tenant-id', tenantId);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('data');
    });
  });

  describe('Statistics', () => {
    it('should get NC statistics', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/ncs/stats')
        .set('x-tenant-id', tenantId);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('byStatus');
      expect(response.body).toHaveProperty('bySeverity');
      expect(response.body).toHaveProperty('byType');
    });

    it('should get CAPA statistics', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/capas/stats')
        .set('x-tenant-id', tenantId);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('byStatus');
      expect(response.body).toHaveProperty('byType');
      expect(response.body).toHaveProperty('overdue');
      expect(response.body).toHaveProperty('averageTimeToClose');
    });
  });

  describe('Error Handling', () => {
    it('should return 404 for non-existent sample', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/samples/00000000-0000-0000-0000-000000000000')
        .set('x-tenant-id', tenantId);

      expect(response.status).toBe(404);
    });

    it('should return 400 for missing tenant-id', async () => {
      const response = await supertest(server.server)
        .get('/quality/api/v1/samples');

      expect(response.status).toBe(400);
    });

    it('should validate required fields on create', async () => {
      const response = await supertest(server.server)
        .post('/quality/api/v1/ncs')
        .set('x-tenant-id', tenantId)
        .send({
          type: 'SpecOut',
          // Missing required fields
        });

      expect(response.status).toBe(400);
    });
  });
});
