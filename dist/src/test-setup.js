"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("reflect-metadata");
// Test setup for Jest
// This file is executed before each test file
// Global test configuration
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-jwt-secret-key';
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/test_db';
// Mock console methods for cleaner test output (optional)
global.console = {
    ...console,
    // Uncomment to ignore console.log in tests
    // log: jest.fn(),
    // Uncomment to ignore console.warn in tests
    // warn: jest.fn(),
    // Uncomment to ignore console.error in tests
    // error: jest.fn(),
};
