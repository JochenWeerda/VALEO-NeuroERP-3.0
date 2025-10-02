***REMOVED***!/usr/bin/env node

/**
 * VALEO-NeuroERP-3.0 Main Application Entry Point
 * Clean Architecture + Domain-Driven Design Implementation
 */

import 'reflect-metadata';
import { createApp } from './app';
import { logger } from './core/logging';
import { config } from './core/config';

async function main() {
  try {
    logger.info('🚀 Starting VALEO-NeuroERP-3.0', {
      version: '3.0.0',
      environment: config.environment,
      port: config.port
    });

    // Create and configure the application
    const app = await createApp();

    // Start the server
    const server = app.listen(config.port, config.host, () => {
      logger.info('✅ VALEO-NeuroERP-3.0 server started successfully', {
        url: `http://${config.host}:${config.port}`,
        environment: config.environment,
        pid: process.pid
      });
    });

    // Graceful shutdown handling
    const gracefulShutdown = (signal: string) => {
      logger.info(`🛑 Received ${signal}, initiating graceful shutdown...`);

      server.close(async () => {
        logger.info('✅ Server closed successfully');

        // Close database connections, cleanup resources, etc.
        await cleanup();

        logger.info('✅ Application shutdown complete');
        process.exit(0);
      });

      // Force shutdown after 30 seconds
      setTimeout(() => {
        logger.error('❌ Forced shutdown after timeout');
        process.exit(1);
      }, 30000);
    };

    // Register shutdown handlers
    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      logger.error('💥 Uncaught Exception:', error);
      process.exit(1);
    });

    process.on('unhandledRejection', (reason, promise) => {
      logger.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
      process.exit(1);
    });

  } catch (error) {
    logger.error('💥 Failed to start VALEO-NeuroERP-3.0:', error);
    process.exit(1);
  }
}

async function cleanup(): Promise<void> {
  try {
    // Close database connections
    // Close external service connections
    // Flush logs
    // Cleanup temporary files
    logger.info('🧹 Performing cleanup operations...');
  } catch (error) {
    logger.error('❌ Error during cleanup:', error);
  }
}

// Start the application
main().catch((error) => {
  console.error('💥 Fatal error during startup:', error);
  process.exit(1);
});