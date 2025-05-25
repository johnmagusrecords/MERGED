```javascript
  module.exports = {
    testEnvironment: 'node',
    testRunner: 'jest',
    moduleFileExtensions: ['js', 'jsx', 'json'],
    moduleNameMapper: {
      '^@/(.*)$': '<rootDir>/src/$1',
    },
    coverage: {
      provider: 'v8',
      lines: 90,
      functions: 90,
      branches: 90,
      statements: 90,
    },
    globals: {
      'ts-jest': {
        tsConfig: 'tsconfig.json',
      },
    },
  };
  ```;
