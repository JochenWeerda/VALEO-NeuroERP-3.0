/**
 * Simple HR Domain Server for VALEO NeuroERP 3.0
 * Simplified version without complex Fastify types
 */

import Fastify from 'fastify';
import { EmployeeService } from '../domain/services/employee-service';
import { PostgresEmployeeRepository } from '../infra/repo/postgres-employee-repository';

// Configuration
const PORT = Number(process.env.PORT || 3030);
const HOST = process.env.HOST || '0.0.0.0';

// Initialize services
const employeeRepository = new PostgresEmployeeRepository();
const eventPublisher = async (event: any) => {
  console.log('📤 Publishing domain event:', event.eventType, event.eventId);
};
const employeeService = new EmployeeService(employeeRepository, eventPublisher);

// Create Fastify instance
const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    transport: process.env.NODE_ENV === 'development' ? {
      target: 'pino-pretty',
      options: {
        colorize: true
      }
    } : undefined
  }
});

// Health check endpoints
fastify.get('/health', async (request, reply) => {
  return {
    ok: true,
    service: 'hr-domain',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  };
});

fastify.get('/ready', async (request, reply) => {
  return {
    ok: true,
    database: true,
    timestamp: new Date().toISOString()
  };
});

fastify.get('/live', async (request, reply) => {
  return {
    ok: true,
    timestamp: new Date().toISOString()
  };
});

// Employee routes (simplified)
fastify.post('/hr/api/v1/employees', async (request, reply) => {
  try {
    const body = request.body as any;
    const employee = await employeeService.createEmployee({
      tenantId: 'default-tenant', // TODO: Get from auth
      createdBy: 'system', // TODO: Get from auth
      ...body
    });
    return reply.code(201).send(employee);
  } catch (error) {
    console.error('Error creating employee:', error);
    return reply.code(400).send({ error: error instanceof Error ? error.message : 'Failed to create employee' });
  }
});

fastify.get('/hr/api/v1/employees/:id', async (request, reply) => {
  try {
    const params = request.params as { id: string };
    const employee = await employeeService.getEmployee('default-tenant', params.id);
    return reply.send(employee);
  } catch (error) {
    console.error('Error getting employee:', error);
    return reply.code(404).send({ error: error instanceof Error ? error.message : 'Employee not found' });
  }
});

fastify.get('/hr/api/v1/employees', async (request, reply) => {
  try {
    const employees = await employeeService.listEmployees('default-tenant');
    return reply.send(employees);
  } catch (error) {
    console.error('Error listing employees:', error);
    return reply.code(500).send({ error: 'Failed to list employees' });
  }
});

fastify.get('/hr/api/v1/employees/statistics', async (request, reply) => {
  try {
    const statistics = await employeeService.getEmployeeStatistics('default-tenant');
    return reply.send(statistics);
  } catch (error) {
    console.error('Error getting employee statistics:', error);
    return reply.code(500).send({ error: 'Failed to get employee statistics' });
  }
});

// Error handler
fastify.setErrorHandler(async (error, request, reply) => {
  fastify.log.error(error);
  return reply.code(500).send({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : 'An unexpected error occurred'
  });
});

// Graceful shutdown
async function gracefulShutdown() {
  console.log('🔄 Gracefully shutting down...');
  try {
    await fastify.close();
    console.log('✅ Server shut down successfully');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
}

// Handle shutdown signals
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Start server
async function start() {
  try {
    console.log('🚀 Starting VALEO NeuroERP 3.0 HR Domain Server...');
    
    await fastify.listen({ port: PORT, host: HOST });
    
    console.log(`✅ HR Domain Server running on http://${HOST}:${PORT}`);
    console.log(`❤️  Health Check: http://${HOST}:${PORT}/health`);
    console.log(`🔧 Ready Check: http://${HOST}:${PORT}/ready`);
    console.log(`💓 Live Check: http://${HOST}:${PORT}/live`);
    
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Start the server
if (require.main === module) {
  start();
}

export default fastify;

