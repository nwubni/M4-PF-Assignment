"""
Test single query scenarios with golden data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.test_data.test_runner import TestRunner


def test_single_queries():
    """Test all single query scenarios."""
    runner = TestRunner()

    # Filter single query tests
    single_query_tests = [
        tc
        for tc in runner.golden_data["test_cases"]
        if not tc.get("is_multi_query", False)
    ]

    print(f"\n{'='*80}")
    print("SINGLE QUERY TESTS")
    print(f"{'='*80}")

    results = []
    for test_case in single_query_tests:
        result = runner.run_test(test_case)
        results.append(result)

    # Print summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*80}")
    print(f"Single Query Tests: {passed}/{total} passed")
    print(f"{'='*80}\n")

    return results


if __name__ == "__main__":
    test_single_queries()
