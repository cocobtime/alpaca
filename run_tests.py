import unittest
import sys
import os
from datetime import datetime
import coverage

def run_tests_with_coverage():
    # Start code coverage monitoring
    cov = coverage.Coverage()
    cov.start()

    # Create test loader and suite
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Configure test runner
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )

    # Run the tests
    print(f"\nStarting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    result = runner.run(suite)

    # Stop coverage monitoring
    cov.stop()
    cov.save()

    # Generate coverage report
    print("\nCode Coverage Report:")
    print("-" * 70)
    cov.report()

    # Generate HTML coverage report
    cov.html_report(directory='coverage_html')

    return result

def main():
    result = run_tests_with_coverage()
    
    # Print summary
    print("\nTest Summary:")
    print("-" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    # Return appropriate exit code
    if not result.wasSuccessful():
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
