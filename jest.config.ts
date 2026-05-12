import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/packages/erp-domain/tests', '<rootDir>/domains/finance/tests', '<rootDir>/src', '<rootDir>/packages/erp-domain/src'],
  testMatch: ['**/*.spec.ts', '**/*.test.ts'],
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
      diagnostics: false,
    }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js'],
  moduleNameMapper: {
    '^@packages/(.*)$': '<rootDir>/packages/$1/src',
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@domains/(.*)$': '<rootDir>/domains/$1/src',
    '^@finance/(.*)$': '<rootDir>/domains/finance/src/$1',
    '^@erp/(.*)$': '<rootDir>/packages/erp-domain/src/$1',
    '^@valero-neuroerp/finance-domain/(.*)$': '<rootDir>/domains/finance/src/$1',
    '^@valero-neuroerp/erp-domain/(.*)$': '<rootDir>/packages/erp-domain/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
};

export default config;