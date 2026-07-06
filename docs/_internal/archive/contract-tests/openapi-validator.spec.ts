/**
 * OpenAPI Contract Tests
 * Validiert, dass Backend-API dem OpenAPI-Schema entspricht
 */

import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as yaml from 'yaml'

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000'

test.describe('OpenAPI Contract Tests', () => {
  let openApiSpec: any

  test.beforeAll(async () => {
    // Load OpenAPI spec from backend
    const response = await fetch(`${BASE_URL}/openapi.json`)
    openApiSpec = await response.json()
    
    expect(openApiSpec).toBeDefined()
    expect(openApiSpec.openapi).toMatch(/^3\.[01]/)
  })

  test('OpenAPI spec is valid', () => {
    expect(openApiSpec).toHaveProperty('info')
    expect(openApiSpec).toHaveProperty('paths')
    expect(openApiSpec.info).toHaveProperty('title')
    expect(openApiSpec.info).toHaveProperty('version')
  })

  test('All documented endpoints exist', async () => {
    const paths = Object.keys(openApiSpec.paths)
    
    for (const path of paths) {
      const methods = Object.keys(openApiSpec.paths[path])
      
      for (const method of methods) {
        if (method === 'get' && !path.includes('{')) {
          // Test GET endpoints without parameters
          const url = `${BASE_URL}${path}`
          const response = await fetch(url)
          
          // Should not be 404 (endpoint exists)
          expect(response.status).not.toBe(404)
        }
      }
    }
  })

  test('Health endpoint matches spec', async () => {
    const response = await fetch(`${BASE_URL}/healthz`)
    const data = await response.json()
    
    expect(response.status).toBe(200)
    expect(data).toHaveProperty('status')
    expect(data.status).toBe('healthy')
  })

  test('Workflow endpoints match spec', async () => {
    const workflowPaths = Object.keys(openApiSpec.paths).filter(p => 
      p.startsWith('/api/workflow')
    )
    
    expect(workflowPaths.length).toBeGreaterThan(0)
    
    // Verify workflow status endpoint
    const statusPath = '/api/workflow/{domain}/{number}'
    expect(openApiSpec.paths).toHaveProperty(statusPath)
    expect(openApiSpec.paths[statusPath]).toHaveProperty('get')
  })

  test('Export endpoints require authentication', async () => {
    const response = await fetch(`${BASE_URL}/api/export/sales`)
    
    // Should be 401 or 403 without auth
    expect([401, 403]).toContain(response.status)
  })

  test('GDPR endpoints are documented', () => {
    const gdprPaths = Object.keys(openApiSpec.paths).filter(p => 
      p.includes('/gdpr')
    )
    
    expect(gdprPaths.length).toBeGreaterThan(0)
  })

  test('All endpoints have proper response schemas', () => {
    const paths = openApiSpec.paths
    
    for (const [path, pathItem] of Object.entries(paths)) {
      for (const [method, operation] of Object.entries(pathItem as any)) {
        if (typeof operation === 'object' && operation.responses) {
          // Check that 200 response has schema
          if (operation.responses['200']) {
            expect(operation.responses['200']).toHaveProperty('content')
          }
        }
      }
    }
  })

  test('Security schemes are defined', () => {
    expect(openApiSpec.components).toHaveProperty('securitySchemes')
    
    const securitySchemes = openApiSpec.components.securitySchemes
    expect(securitySchemes).toBeDefined()
    
    // Should have Bearer auth
    expect(Object.values(securitySchemes).some((scheme: any) => 
      scheme.type === 'http' && scheme.scheme === 'bearer'
    )).toBe(true)
  })

  test('No breaking changes in major endpoints', () => {
    // Critical endpoints that should never change
    const criticalEndpoints = [
      '/api/workflow/{domain}/{number}',
      '/api/documents/{domain}',
      '/api/export/{domain}',
      '/healthz',
      '/readyz',
    ]
    
    for (const endpoint of criticalEndpoints) {
      expect(openApiSpec.paths).toHaveProperty(endpoint)
    }
  })
})

