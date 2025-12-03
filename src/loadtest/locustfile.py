"""
Arkiv Load Test - Locust Configuration

This is the main entry point for running Arkiv load tests with Locust.

Usage:
    # Web UI mode (recommended for exploration)
    uv run locust -f src/loadtest/locustfile.py --host=https://mendoza.hoodi.arkiv.network/rpc

    # Headless mode (for CI/automated testing)
    uv run locust -f src/loadtest/locustfile.py \
        --host=https://mendoza.hoodi.arkiv.network/rpc \
        --headless \
        --users 10 \
        --spawn-rate 2 \
        --run-time 1m

    # Write-heavy test
    uv run locust -f src/loadtest/locustfile.py \
        --host=https://mendoza.hoodi.arkiv.network/rpc \
        --headless \
        --users 5 \
        --spawn-rate 1 \
        --run-time 30s \
        WriteHeavyLoadTest

Test Classes Available:
    - ArkivLoadTest: Balanced mix of operations (default)
    - WriteHeavyLoadTest: 90% writes, 10% reads
    - ReadHeavyLoadTest: 20% writes, 80% reads
"""

from loadtest.arkiv_user import ArkivUser, ArkivWriteHeavyUser, ArkivReadHeavyUser


class ArkivLoadTest(ArkivUser):
    """
    Default balanced load test.
    
    Task weights:
        - create_entity: 5 (most frequent - test write capacity)
        - read_entity: 3
        - query_entities: 2
        - entity_exists: 1
    """
    pass


class WriteHeavyLoadTest(ArkivWriteHeavyUser):
    """
    Write-heavy load test for testing transaction throughput.
    Use this to stress-test the chain's write capacity.
    """
    pass


class ReadHeavyLoadTest(ArkivReadHeavyUser):
    """
    Read-heavy load test for testing query performance.
    Use this to test the chain's read/query capacity.
    """
    pass
