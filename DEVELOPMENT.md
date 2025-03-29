# Development Workflow

## Test-Driven Development (TDD) Guidelines

### 1. Red-Green-Refactor Cycle

1. **Red**: Write a failing test that describes the desired behavior

   - Start with a simple test case
   - Ensure the test fails (proves it's testing something)

2. **Green**: Write the minimum amount of code to pass the test

   - Focus on making the test pass
   - Don't add extra features or optimizations

3. **Refactor**: Improve the code while keeping tests passing
   - Clean up the implementation
   - Remove duplication
   - Improve naming
   - Optimize performance
   - Ensure all tests still pass

### 2. Test Organization

- Place tests in `hillbot/tests/` directory
- Use the naming convention `test_module_name.py`
- Group related tests in classes using `TestClassName`
- Use descriptive test function names: `test_description_of_behavior`

### 3. Testing Best Practices

- Write small, focused tests
- Use fixtures for shared setup
- Mock external dependencies
- Test one thing per test
- Use clear assertions
- Include error cases

### 4. Development Commands

- `make test`: Run all tests with coverage
- `make test-watch`: Run tests automatically when files change
- `make tdd`: Same as test-watch
- `make lint`: Check code style
- `make format`: Auto-format code

### 5. Code Quality Standards

- 100% test coverage for new code
- Clear, descriptive test names
- Proper error handling
- Type hints
- Logging for debugging
- Documentation for public APIs

### 6. Common Patterns

- Use async/await for Discord interactions
- Mock external APIs using `unittest.mock`
- Use fixtures for shared setup
- Parameterize tests for similar cases
- Use markers (`@pytest.mark`) to categorize tests

### 7. Troubleshooting

- If tests fail unexpectedly:
  1. Check test isolation
  2. Verify mocks are set up correctly
  3. Check for race conditions
  4. Review test dependencies

### 8. Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Discord.py testing guide](https://discordpy.readthedocs.io/en/stable/testing.html)
