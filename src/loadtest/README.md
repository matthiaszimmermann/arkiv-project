# Arkiv Load Testing

Load testing tools for Arkiv networks using [Locust](https://locust.io/).

## Overview

This module provides:
- **ArkivUser**: Custom Locust user class that uses the Arkiv SDK
- **Multiple test profiles**: Balanced, write-heavy, and read-heavy
- **Demo script**: Quick smoke test without full Locust setup

## Quick Start

### 1. Install Locust

```bash
uv add locust
```

### 2. Run the Demo (Smoke Test)

```bash
# Quick test against the Mendoza testnet
uv run python -m loadtest.demo

# With custom options
uv run python -m loadtest.demo --iterations 20
```

### 3. Run Locust (Full Load Test)

```bash
# Web UI mode - opens at http://localhost:8089
uv run locust -f src/loadtest/locustfile.py \
    --host=https://mendoza.hoodi.arkiv.network/rpc

# Headless mode
uv run locust -f src/loadtest/locustfile.py \
    --host=https://mendoza.hoodi.arkiv.network/rpc \
    --headless \
    --users 10 \
    --spawn-rate 2 \
    --run-time 1m
```

## Test Profiles

### ArkivLoadTest (Default)
Balanced mix of operations:
- **create_entity** (weight 5): Create new entities
- **read_entity** (weight 3): Read existing entities
- **query_entities** (weight 2): Query by attributes
- **entity_exists** (weight 1): Check existence

### WriteHeavyLoadTest
90% writes, 10% reads. Use for testing:
- Transaction throughput
- Block propagation
- Gas consumption patterns

### ReadHeavyLoadTest  
20% writes, 80% reads/queries. Use for testing:
- Query performance
- Read scalability
- Cache effectiveness

## Usage Examples

```bash
# Default balanced test
uv run locust -f src/loadtest/locustfile.py \
    --host=https://mendoza.hoodi.arkiv.network/rpc

# Write-heavy stress test
uv run locust -f src/loadtest/locustfile.py \
    --host=https://mendoza.hoodi.arkiv.network/rpc \
    WriteHeavyLoadTest

# Read-heavy test  
uv run locust -f src/loadtest/locustfile.py \
    --host=https://mendoza.hoodi.arkiv.network/rpc \
    ReadHeavyLoadTest

# Multiple user types (advanced)
uv run locust -f src/loadtest/locustfile.py \
    --host=https://mendoza.hoodi.arkiv.network/rpc \
    ArkivLoadTest WriteHeavyLoadTest
```

## Important Notes

### Account Funding
Each Locust user creates a unique Arkiv account. For successful transactions, accounts need ETH:
- **Testnet**: May have a faucet or pre-funded accounts
- **Local node**: Accounts are auto-funded
- **Production**: You'll need to fund accounts beforehand

### Metrics Interpretation
Locust reports these metrics for each Arkiv operation:
- **Response time**: Time for the operation to complete (includes block confirmation for writes)
- **Requests/sec**: Throughput (note: writes are limited by block time)
- **Failures**: Transaction errors, network issues, or validation failures

### Expected Performance
- **Writes**: Limited by block time (typically 2-12 seconds depending on network)
- **Reads**: Should be fast (<100ms for local, <500ms for remote)
- **Queries**: Depends on data volume and query complexity

## Customization

### Custom User Class

```python
from loadtest.arkiv_user import ArkivUser
from locust import task

class MyCustomTest(ArkivUser):
    @task(10)
    def my_custom_operation(self):
        # Your custom Arkiv operations here
        if self.client:
            entity_key, _ = self.client.arkiv.create_entity(
                payload=b"custom payload",
                expires_in=3600
            )
```

### Environment Variables

You can configure the target via environment:

```bash
export ARKIV_RPC_URL=https://your-network.arkiv.network/rpc
uv run locust -f src/loadtest/locustfile.py --host=$ARKIV_RPC_URL
```

## Troubleshooting

### "Account has zero balance"
Accounts need ETH to submit transactions. Options:
1. Use a testnet faucet
2. Pre-fund accounts in your test setup
3. Use a local node (auto-funds accounts)

### Slow write operations
Write operations include block confirmation time. This is expected behavior - Arkiv uses blockchain consensus.

### Connection errors
- Check the RPC URL is correct and reachable
- Verify network connectivity
- Check if the node is synced
