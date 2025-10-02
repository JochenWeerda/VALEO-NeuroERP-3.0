/**
 * OpenAPI/Swagger Documentation
 */

export const openApiSpec = {
  openapi: '3.0.0',
  info: {
    title: 'Integration Domain API',
    version: '3.0.0',
    description: 'VALEO NeuroERP 3.0 - Integration Domain API for managing integrations, webhooks, and sync jobs',
    contact: {
      name: 'VALEO NeuroERP Team',
      email: 'neuroerp@valeo.com'
    },
    license: {
      name: 'Private',
      url: 'https://valeo.com'
    }
  },
  servers: [
    {
      url: 'http://localhost:3000',
      description: 'Development server'
    },
    {
      url: 'https://api.neuroerp.valeo.com',
      description: 'Production server'
    }
  ],
  tags: [
    {
      name: 'Integrations',
      description: 'Integration management endpoints'
    },
    {
      name: 'Health',
      description: 'Health check and monitoring endpoints'
    }
  ],
  paths: {
    '/health': {
      get: {
        tags: ['Health'],
        summary: 'Health check',
        description: 'Check the health status of the Integration Domain API',
        responses: {
          '200': {
            description: 'Service is healthy',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: {
                      type: 'object',
                      properties: {
                        status: { type: 'string', example: 'healthy' },
                        timestamp: { type: 'string', format: 'date-time' },
                        version: { type: 'string', example: '3.0.0' },
                        service: { type: 'string', example: 'integration-domain' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    '/api/integrations': {
      get: {
        tags: ['Integrations'],
        summary: 'List integrations',
        description: 'Retrieve a paginated list of integrations with optional filtering',
        parameters: [
          {
            name: 'page',
            in: 'query',
            description: 'Page number',
            schema: { type: 'integer', minimum: 1, default: 1 }
          },
          {
            name: 'limit',
            in: 'query',
            description: 'Number of items per page',
            schema: { type: 'integer', minimum: 1, maximum: 100, default: 10 }
          },
          {
            name: 'sortBy',
            in: 'query',
            description: 'Field to sort by',
            schema: { type: 'string', enum: ['name', 'type', 'status', 'createdAt', 'updatedAt'] }
          },
          {
            name: 'sortOrder',
            in: 'query',
            description: 'Sort order',
            schema: { type: 'string', enum: ['asc', 'desc'], default: 'desc' }
          },
          {
            name: 'type',
            in: 'query',
            description: 'Filter by integration type',
            schema: { type: 'string', enum: ['api', 'webhook', 'file', 'database', 'message-queue'] }
          },
          {
            name: 'status',
            in: 'query',
            description: 'Filter by status',
            schema: { type: 'string', enum: ['active', 'inactive', 'pending', 'error'] }
          },
          {
            name: 'tags',
            in: 'query',
            description: 'Filter by tags (comma-separated)',
            schema: { type: 'string' }
          },
          {
            name: 'isActive',
            in: 'query',
            description: 'Filter by active status',
            schema: { type: 'boolean' }
          }
        ],
        responses: {
          '200': {
            description: 'List of integrations retrieved successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: {
                      type: 'object',
                      properties: {
                        data: {
                          type: 'array',
                          items: { $ref: '#/components/schemas/Integration' }
                        },
                        pagination: { $ref: '#/components/schemas/Pagination' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      post: {
        tags: ['Integrations'],
        summary: 'Create integration',
        description: 'Create a new integration',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['name', 'type', 'config'],
                properties: {
                  name: { type: 'string', minLength: 1, maxLength: 255 },
                  type: { type: 'string', enum: ['api', 'webhook', 'file', 'database', 'message-queue'] },
                  config: { type: 'object', description: 'Integration-specific configuration' },
                  description: { type: 'string' },
                  tags: { type: 'array', items: { type: 'string' }, default: [] }
                }
              }
            }
          }
        },
        responses: {
          '201': {
            description: 'Integration created successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: { $ref: '#/components/schemas/Integration' }
                  }
                }
              }
            }
          },
          '409': {
            description: 'Integration with this name already exists',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Error' }
              }
            }
          },
          '422': {
            description: 'Validation error',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ValidationError' }
              }
            }
          }
        }
      }
    },
    '/api/integrations/{id}': {
      get: {
        tags: ['Integrations'],
        summary: 'Get integration',
        description: 'Retrieve a specific integration by ID',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Integration ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        responses: {
          '200': {
            description: 'Integration retrieved successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: { $ref: '#/components/schemas/Integration' }
                  }
                }
              }
            }
          },
          '404': {
            description: 'Integration not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Error' }
              }
            }
          }
        }
      },
      put: {
        tags: ['Integrations'],
        summary: 'Update integration',
        description: 'Update an existing integration',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Integration ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  name: { type: 'string', minLength: 1, maxLength: 255 },
                  config: { type: 'object' },
                  description: { type: 'string' },
                  tags: { type: 'array', items: { type: 'string' } },
                  status: { type: 'string', enum: ['active', 'inactive', 'pending', 'error'] },
                  isActive: { type: 'boolean' }
                }
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Integration updated successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: { $ref: '#/components/schemas/Integration' }
                  }
                }
              }
            }
          },
          '404': {
            description: 'Integration not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Error' }
              }
            }
          }
        }
      },
      delete: {
        tags: ['Integrations'],
        summary: 'Delete integration',
        description: 'Delete an integration',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Integration ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        responses: {
          '204': {
            description: 'Integration deleted successfully'
          },
          '404': {
            description: 'Integration not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Error' }
              }
            }
          }
        }
      }
    },
    '/api/integrations/{id}/activate': {
      post: {
        tags: ['Integrations'],
        summary: 'Activate integration',
        description: 'Activate an integration',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Integration ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        responses: {
          '200': {
            description: 'Integration activated successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: { $ref: '#/components/schemas/Integration' }
                  }
                }
              }
            }
          },
          '404': {
            description: 'Integration not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Error' }
              }
            }
          }
        }
      }
    },
    '/api/integrations/{id}/deactivate': {
      post: {
        tags: ['Integrations'],
        summary: 'Deactivate integration',
        description: 'Deactivate an integration',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Integration ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        responses: {
          '200': {
            description: 'Integration deactivated successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    data: { $ref: '#/components/schemas/Integration' }
                  }
                }
              }
            }
          },
          '404': {
            description: 'Integration not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Error' }
              }
            }
          }
        }
      }
    }
  },
  components: {
    schemas: {
      Integration: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
          name: { type: 'string' },
          type: { type: 'string', enum: ['api', 'webhook', 'file', 'database', 'message-queue'] },
          status: { type: 'string', enum: ['active', 'inactive', 'pending', 'error'] },
          config: { type: 'object' },
          description: { type: 'string', nullable: true },
          tags: { type: 'array', items: { type: 'string' } },
          isActive: { type: 'boolean' },
          createdAt: { type: 'string', format: 'date-time' },
          updatedAt: { type: 'string', format: 'date-time' },
          createdBy: { type: 'string' },
          updatedBy: { type: 'string' }
        },
        required: ['id', 'name', 'type', 'status', 'config', 'tags', 'isActive', 'createdAt', 'updatedAt', 'createdBy', 'updatedBy']
      },
      Pagination: {
        type: 'object',
        properties: {
          page: { type: 'integer' },
          limit: { type: 'integer' },
          total: { type: 'integer' },
          totalPages: { type: 'integer' },
          hasNext: { type: 'boolean' },
          hasPrev: { type: 'boolean' }
        },
        required: ['page', 'limit', 'total', 'totalPages', 'hasNext', 'hasPrev']
      },
      Error: {
        type: 'object',
        properties: {
          success: { type: 'boolean', example: false },
          error: {
            type: 'object',
            properties: {
              message: { type: 'string' },
              code: { type: 'string' },
              statusCode: { type: 'integer' },
              timestamp: { type: 'string', format: 'date-time' },
              details: { type: 'object' }
            },
            required: ['message', 'code', 'statusCode', 'timestamp']
          }
        }
      },
      ValidationError: {
        type: 'object',
        properties: {
          success: { type: 'boolean', example: false },
          error: {
            type: 'object',
            properties: {
              message: { type: 'string' },
              code: { type: 'string', example: 'VALIDATION_ERROR' },
              statusCode: { type: 'integer', example: 422 },
              validationErrors: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    field: { type: 'string' },
                    message: { type: 'string' },
                    value: { type: 'string' }
                  }
                }
              },
              timestamp: { type: 'string', format: 'date-time' }
            },
            required: ['message', 'code', 'statusCode', 'validationErrors', 'timestamp']
          }
        }
      }
    }
  }
};

