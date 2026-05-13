/** @type {import('jest').Config} */
/** `testMatch`: nur `*.spec.ts` (ehem. `node:test` unter `tests/` ist auf Jest umgestellt). */
const path = require('path')

// pnpm: Jest löst Unterabhängigkeiten von `inversify` oft nicht korrekt auf (fehlendes @inversifyjs/*).
function resolvePkgEntry(name) {
  return require.resolve(name, { paths: [path.join(__dirname)] })
}

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
    '^@inversifyjs/common$': resolvePkgEntry('@inversifyjs/common'),
    '^@inversifyjs/core$': resolvePkgEntry('@inversifyjs/core'),
    '^@inversifyjs/container$': resolvePkgEntry('@inversifyjs/container'),
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
