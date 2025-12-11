"""
Test multi-query scenarios with golden data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.test_data.test_runner import TestRunner


def test_multi_queries():
    """Test all multi-query scenarios."""
    runner = TestRunner()

    # Filter multi-query tests
    multi_query_tests = [
        tc for tc in runner.golden_data["test_cases"] if tc.get("is_multi_query", False)
    ]

    print(f"\n{'='*80}")
    print("MULTI-QUERY TESTS")
    print(f"{'='*80}")

    results = []
    for test_case in multi_query_tests:
        result = runner.run_test(test_case)
        results.append(result)

    # Print summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*80}")
    print(f"Multi-Query Tests: {passed}/{total} passed")
    print(f"{'='*80}\n")

    return results


if __name__ == "__main__":
    test_multi_queries()
