module.exports = {
  root: true,
  extends: ['eslint:recommended'],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  env: {
    'es6': true,
    'node': true,
  },
  rules: {
    // General rules
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'prefer-const': 'error',
    'no-var': 'error',
    'no-unused-vars': 'off', // Turn off base rule as it can report incorrect errors
  },
  ignorePatterns: [
    'node_modules/',
    '.expo/',
    '.expo-shared/',
    'coverage/',
    '*.config.js',
    'jest.setup.js',
  ],
};