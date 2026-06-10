/** @type {import('jest').Config} */
/** `testMatch`: nur `*.spec.ts` (ehem. `node:test` unter `tests/` ist auf Jest umgestellt). */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.spec.ts'],
  modulePathIgnorePatterns: ['<rootDir>/dist'],
  moduleNameMapper: {
    '^@valero-neuroerp/data-models$': '<rootDir>/../data-models/src/index.ts',
    '^@valero-neuroerp/data-models/(.*)$': '<rootDir>/../data-models/src/$1',
    '^@valero-neuroerp/utilities$': '<rootDir>/../utilities/src/index.ts',
    '^@valero-neuroerp/utilities/(.*)$': '<rootDir>/../utilities/src/$1',
  },
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: '<rootDir>/tsconfig.tests.json',
      },
    ],
  },
}
