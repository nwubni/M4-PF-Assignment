# Test Data and Golden Data

This folder contains test cases with golden data (expected inputs and outputs) to ensure the multi-agent system works as expected.

## Structure

- `golden_data.json` - Test cases with expected inputs and outputs
- `test_runner.py` - Main test runner that executes tests and validates against golden data
- `test_single_queries.py` - Tests for single-agent queries
- `test_multi_queries.py` - Tests for multi-agent queries

## Running Tests

### Run All Tests

```bash
python -m src.test_data.test_runner
```

Or from the project root:

```bash
cd src/test_data
python test_runner.py
```

### Run Single Query Tests Only

```bash
python -m src.test_data.test_single_queries
```

### Run Multi-Query Tests Only

```bash
python -m src.test_data.test_multi_queries
```

## Test Case Format

Each test case in `golden_data.json` has the following structure:

```json
{
  "id": "test_001",
  "name": "Test description",
  "query": "User query text",
  "expected_agent": "bank",  // For single queries
  "expected_category": "check_balance",
  "expected_response_contains": ["keyword1", "keyword2"],
  "expected_followup": false,  // Optional
  "expected_amount": 100.0,  // Optional
  "is_multi_query": false,
  "expected_agents": ["agent1", "agent2"],  // For multi-queries
  "expected_sub_queries": 2  // For multi-queries
}
```

## Validation

The test runner validates:

1. **Multi-query detection**: Checks if the orchestrator correctly identifies multi-part queries
2. **Agent routing**: Verifies that queries are routed to the correct agents
3. **Response content**: Checks if responses contain expected keywords/phrases
4. **Followup questions**: Validates that followup questions are generated when needed
5. **Sub-query decomposition**: For multi-queries, verifies correct decomposition

## Adding New Test Cases

To add a new test case:

1. Open `golden_data.json`
2. Add a new entry to the `test_cases` array
3. Follow the existing format
4. Run the tests to validate

Example:

```json
{
  "id": "test_011",
  "name": "New Test Case",
  "query": "Your test query here",
  "expected_agent": "faq",
  "expected_category": "faq",
  "expected_response_contains": ["expected", "keywords"],
  "is_multi_query": false
}
```

## Test Results

The test runner provides:
- ✅ Pass/Fail status for each test
- Error messages for failed tests
- Warnings for potential issues
- Summary statistics

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```bash
# Exit code 0 if all tests pass, 1 if any fail
python -m src.test_data.test_runner
```

