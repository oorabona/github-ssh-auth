import os
import pytest

def pytest_configure(config):
    # Check that we have the required environment variables
    # for the tests to run (ACCESS_TOKEN and GITHUB_ORG)
    # If not present, skip all tests
    if not os.environ.get("ACCESS_TOKEN") or not os.environ.get("GITHUB_ORG"):
        pytest.skip("ACCESS_TOKEN and GITHUB_ORG environment variables are required to run tests.")
        