"""
Test runner for the bank application using golden data.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.messages import HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.agent_state import AgentState
from src.main import create_multi_agent_system


class TestRunner:
    """Test runner that validates against golden data."""

    def __init__(self, golden_data_path: str = None):
        """Initialize test runner with golden data."""
        if golden_data_path is None:
            golden_data_path = Path(__file__).parent / "golden_data.json"

        with open(golden_data_path, "r") as f:
            self.golden_data = json.load(f)

        self.workflow = create_multi_agent_system()
        self.results = []

    def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case and return results.

        Args:
            test_case: Test case from golden data

        Returns:
            Dictionary with test results
        """
        query = test_case["query"]
        test_id = test_case["id"]
        test_name = test_case["name"]

        print(f"\n{'='*80}")
        print(f"Test {test_id}: {test_name}")
        print(f"Query: {query}")
        print(f"{'='*80}")

        try:
            # Run the workflow
            result = self.workflow.invoke(
                AgentState(messages=[HumanMessage(content=query)])
            )

            # Validate results
            validation = self._validate_result(test_case, result)

            # Store results
            test_result = {
                "test_id": test_id,
                "test_name": test_name,
                "query": query,
                "passed": validation["passed"],
                "errors": validation["errors"],
                "warnings": validation["warnings"],
                "result": result,
            }

            self.results.append(test_result)

            # Print results
            if validation["passed"]:
                print(f"✅ PASSED")
            else:
                print(f"❌ FAILED")
                for error in validation["errors"]:
                    print(f"  - {error}")

            if validation["warnings"]:
                print(f"⚠️  Warnings:")
                for warning in validation["warnings"]:
                    print(f"  - {warning}")

            return test_result

        except Exception as e:
            error_result = {
                "test_id": test_id,
                "test_name": test_name,
                "query": query,
                "passed": False,
                "errors": [f"Exception occurred: {str(e)}"],
                "warnings": [],
                "result": None,
            }
            self.results.append(error_result)
            print(f"❌ FAILED with exception: {str(e)}")
            return error_result

    def _validate_result(
        self, test_case: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate test result against golden data expectations.

        Args:
            test_case: Test case from golden data
            result: Actual result from workflow

        Returns:
            Validation results with passed flag, errors, and warnings
        """
        errors = []
        warnings = []

        # Check if result has messages
        if not result.get("messages"):
            errors.append("No messages in result")
            return {"passed": False, "errors": errors, "warnings": warnings}

        # Get final response
        final_message = result["messages"][-1]
        if not hasattr(final_message, "content"):
            errors.append("Final message has no content")
            return {"passed": False, "errors": errors, "warnings": warnings}

        response_content = final_message.content

        # Check multi-query flag
        result_state = result.get("result", {})
        is_multi_query = result_state.get("is_multi_query", False)

        if test_case.get("is_multi_query") != is_multi_query:
            errors.append(
                f"Multi-query mismatch: expected {test_case.get('is_multi_query')}, got {is_multi_query}"
            )

        # For multi-query tests
        if test_case.get("is_multi_query"):
            expected_agents = test_case.get("expected_agents", [])
            sub_queries = result_state.get("sub_queries", [])

            if len(sub_queries) != test_case.get("expected_sub_queries", 0):
                errors.append(
                    f"Sub-query count mismatch: expected {test_case.get('expected_sub_queries')}, got {len(sub_queries)}"
                )

            # Check if expected agents were called
            actual_agents = [sq.get("agent") for sq in sub_queries]
            for expected_agent in expected_agents:
                if expected_agent not in actual_agents:
                    errors.append(
                        f"Expected agent '{expected_agent}' not in sub-queries"
                    )

        # For single query tests
        else:
            expected_agent = test_case.get("expected_agent")
            # Note: We can't directly check which agent was called in single queries
            # without modifying the agents to return metadata, but we can check the response

        # Check response content
        expected_contains = test_case.get("expected_response_contains", [])
        for expected_text in expected_contains:
            if expected_text.lower() not in response_content.lower():
                errors.append(
                    f"Response does not contain expected text: '{expected_text}'"
                )

        # Check for followup
        if test_case.get("expected_followup"):
            # Check if orchestrator returned a followup
            orchestrator_msg = None
            for msg in result["messages"]:
                if hasattr(msg, "content") and "followup" in msg.content.lower():
                    orchestrator_msg = msg.content
                    break

            if not orchestrator_msg:
                errors.append("Expected followup question but none found")

        # Check amount extraction
        if "expected_amount" in test_case:
            # This would require checking the orchestrator's classification
            # For now, we'll just check if the response mentions the amount
            expected_amount = test_case["expected_amount"]
            if str(expected_amount) not in response_content:
                warnings.append(
                    f"Expected amount {expected_amount} not found in response"
                )

        passed = len(errors) == 0
        return {"passed": passed, "errors": errors, "warnings": warnings}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases from golden data."""
        print(f"\n{'='*80}")
        print("RUNNING ALL TESTS")
        print(f"{'='*80}")

        test_cases = self.golden_data.get("test_cases", [])

        for test_case in test_cases:
            self.run_test(test_case)

        # Print summary
        self._print_summary()

        return {
            "total": len(test_cases),
            "passed": sum(1 for r in self.results if r["passed"]),
            "failed": sum(1 for r in self.results if not r["passed"]),
            "results": self.results,
        }

    def _print_summary(self):
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print(f"{'='*80}\n")

        if failed > 0:
            print("Failed Tests:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    for error in result["errors"]:
                        print(f"    Error: {error}")


def main():
    """Main function to run tests."""
    runner = TestRunner()
    summary = runner.run_all_tests()

    # Exit with error code if any tests failed
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
