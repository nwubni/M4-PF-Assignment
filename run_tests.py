#!/usr/bin/env python3
"""
Convenience script to run all tests from the project root.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.test_data.test_runner import TestRunner


def main():
    """Run all tests."""
    print("=" * 80)
    print("BANK APPLICATION TEST SUITE")
    print("=" * 80)

    runner = TestRunner()
    summary = runner.run_all_tests()

    # Exit with appropriate code
    if summary["failed"] > 0:
        print(f"\n❌ {summary['failed']} test(s) failed")
        sys.exit(1)
    else:
        print(f"\n✅ All {summary['total']} test(s) passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
