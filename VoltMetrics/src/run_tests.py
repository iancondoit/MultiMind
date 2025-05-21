#!/usr/bin/env python3
"""
Test runner for VoltMetrics.

This script runs all tests in the tests directory.
"""

import unittest
import sys
import os

if __name__ == "__main__":
    print("Running VoltMetrics tests...")
    
    # Discover and run all tests
    test_suite = unittest.defaultTestLoader.discover(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"),
        pattern="test_*.py"
    )
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Set exit code based on test results
    if result.wasSuccessful():
        print("All tests passed!")
        sys.exit(0)
    else:
        print(f"Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        sys.exit(1) 