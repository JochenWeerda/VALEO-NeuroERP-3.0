***REMOVED***!/usr/bin/env node
"use strict";
/**
 * VALEO-NeuroERP-3.0 Main Application Entry Point
 * Clean Architecture + Domain-Driven Design Implementation
 */
Object.defineProperty(exports, "__esModule", { value: true });
require("reflect-metadata");
const app_1 = require("./app");
const logging_1 = require("./core/logging");
const config_1 = require("./core/config");
async function main() {
    try {
        logging_1.logger.info('🚀 Starting VALEO-NeuroERP-3.0', {
            version: '3.0.0',
            environment: config_1.config.environment,
            port: config_1.config.port
        });
        // Create and configure the application
        const app = await (0, app_1.createApp)();
        // Start the server
        const server = app.listen(config_1.config.port, config_1.config.host, () => {
            logging_1.logger.info('✅ VALEO-NeuroERP-3.0 server started successfully', {
                url: `http://${config_1.config.host}:${config_1.config.port}`,
                environment: config_1.config.environment,
                pid: process.pid
            });
        });
        // Graceful shutdown handling
        const gracefulShutdown = (signal) => {
            logging_1.logger.info(`🛑 Received ${signal}, initiating graceful shutdown...`);
            server.close(async () => {
                logging_1.logger.info('✅ Server closed successfully');
                // Close database connections, cleanup resources, etc.
                await cleanup();
                logging_1.logger.info('✅ Application shutdown complete');
                process.exit(0);
            });
            // Force shutdown after 30 seconds
            setTimeout(() => {
                logging_1.logger.error('❌ Forced shutdown after timeout');
                process.exit(1);
            }, 30000);
        };
        // Register shutdown handlers
        process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
        process.on('SIGINT', () => gracefulShutdown('SIGINT'));
        // Handle uncaught exceptions
        process.on('uncaughtException', (error) => {
            logging_1.logger.error('💥 Uncaught Exception:', error);
            process.exit(1);
        });
        process.on('unhandledRejection', (reason, promise) => {
            logging_1.logger.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
            process.exit(1);
        });
    }
    catch (error) {
        logging_1.logger.error('💥 Failed to start VALEO-NeuroERP-3.0:', error);
        process.exit(1);
    }
}
async function cleanup() {
    try {
        // Close database connections
        // Close external service connections
        // Flush logs
        // Cleanup temporary files
        logging_1.logger.info('🧹 Performing cleanup operations...');
    }
    catch (error) {
        logging_1.logger.error('❌ Error during cleanup:', error);
    }
}
// Start the application
main().catch((error) => {
    console.error('💥 Fatal error during startup:', error);
    process.exit(1);
});
