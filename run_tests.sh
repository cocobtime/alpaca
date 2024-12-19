#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies
pip install pytest pytest-cov coverage pytest-mock responses

# Run tests with coverage
python run_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "\nAll tests passed successfully!"
    exit 0
else
    echo "\nSome tests failed. Please check the output above."
    exit 1
fi
