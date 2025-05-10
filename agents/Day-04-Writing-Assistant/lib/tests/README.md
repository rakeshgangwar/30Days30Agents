# Writing Assistant Connector Library Tests

This directory contains tests for the Writing Assistant connector library.

## Test Structure

The tests are organized as follows:

- `services/`: Tests for the API service and related functionality
  - `ApiService.test.ts`: Basic tests for the ApiService class
  - `ApiService.edge.test.ts`: Edge case tests for the ApiService class
  - `ApiError.test.ts`: Tests for the ApiError class
- `models/`: Tests for the data models
  - `DataModel.test.ts`: Basic tests for the data models
  - `DataModel.edge.test.ts`: Edge case tests for the data models
- `integration/`: Integration tests that combine multiple components
  - `WritingAssistant.test.ts`: Tests that simulate real-world usage
- `index.test.ts`: Tests for the main exports

## Running Tests

You can run the tests using the following npm scripts:

```bash
# Run all tests
npm test

# Run tests with coverage report
npm run test:coverage

# Run tests in watch mode (useful during development)
npm run test:watch
```

## Coverage Requirements

The library has the following coverage requirements:

- Branches: 80%
- Functions: 90%
- Lines: 90%
- Statements: 90%

These thresholds are enforced by the Jest configuration in `jest.config.js`.

## Test Patterns

The tests follow these patterns:

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Edge Case Tests**: Test boundary conditions and error handling
3. **Integration Tests**: Test how components work together

## Mocking

The tests use Jest's mocking capabilities to mock external dependencies:

- `axios` is mocked to avoid making real HTTP requests
- `setTimeout` is mocked in some tests to control timing

## Adding New Tests

When adding new functionality to the library, please follow these guidelines:

1. Add unit tests for the new functionality
2. Add edge case tests for boundary conditions and error handling
3. Update integration tests if the new functionality affects how components work together
4. Ensure that coverage requirements are still met
