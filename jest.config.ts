import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/domains/erp/tests', '<rootDir>/domains/finance/tests', '<rootDir>/src'],
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
    '^@erp/(.*)$': '<rootDir>/domains/erp/src/$1',
    '^@valero-neuroerp/finance-domain/(.*)$': '<rootDir>/domains/finance/src/$1',
    '^@valero-neuroerp/erp-domain/(.*)$': '<rootDir>/domains/erp/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
};

export default config;