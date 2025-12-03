"""
Arkiv Load Test Demo

A simple demonstration of the load testing capability without running full Locust.
This script performs a quick smoke test against the target Arkiv network.

Usage:
    # Use local node (when ARKIV_RPC_URL is not set in .env)
    uv run python -m loadtest.demo
    
    # Use specific RPC endpoint
    uv run python -m loadtest.demo --rpc-url https://mendoza.hoodi.arkiv.network/rpc
    
    # Custom iterations
    uv run python -m loadtest.demo --iterations 20
"""

import argparse
import getpass
import json
import os
import statistics
import time
import uuid
from typing import Optional, cast

from dotenv import load_dotenv

from web3.providers.base import BaseProvider

from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode
from arkiv.provider import ProviderBuilder
from arkiv.types import Attributes

# Load environment variables from .env file
load_dotenv()

# Get RPC URL from environment (None if not set)
DEFAULT_RPC_URL: Optional[str] = os.getenv("ARKIV_RPC_URL")

# Get wallet file path from environment (None if not set)
DEFAULT_WALLET_FILE: Optional[str] = os.getenv("WALLET_FILE")


def load_account_from_wallet(wallet_path: str) -> NamedAccount:
    """
    Load an account from an encrypted wallet file.
    Prompts the user for the password to decrypt.
    
    Args:
        wallet_path: Path to the encrypted wallet JSON file
        
    Returns:
        NamedAccount loaded from the wallet
        
    Raises:
        FileNotFoundError: If wallet file doesn't exist
        ValueError: If password is incorrect or wallet is invalid
    """
    if not os.path.exists(wallet_path):
        raise FileNotFoundError(f"Wallet file not found: {wallet_path}")
    
    print(f"🔐 Loading wallet from: {wallet_path}")
    
    # Read wallet file
    with open(wallet_path, "r") as f:
        wallet_json = f.read()
    
    # Prompt for password (hidden input)
    password = getpass.getpass("   Enter wallet password: ")
    
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Load account from wallet
    account_name = os.path.splitext(os.path.basename(wallet_path))[0]
    account = NamedAccount.from_wallet(account_name, wallet_json, password)
    
    print(f"   ✅ Wallet loaded successfully!")
    return account


def run_load_test_demo(rpc_url: Optional[str], iterations: int = 10, wallet_file: Optional[str] = None) -> None:
    """
    Run a simple load test demo against an Arkiv network.
    
    Args:
        rpc_url: The RPC endpoint to test (None = use local node)
        iterations: Number of create/read cycles to perform
        wallet_file: Path to encrypted wallet file (required for remote RPC)
    """
    print("=" * 70)
    print("ARKIV LOAD TEST DEMO")
    print("=" * 70)
    
    local_node: Optional[ArkivNode] = None
    
    if rpc_url:
        print(f"\n🎯 Target: {rpc_url}")
    else:
        print("\n🎯 Target: Local Arkiv Node (no ARKIV_RPC_URL configured)")
    print(f"📊 Iterations: {iterations}\n")
    
    # Initialize client
    print("🚀 Initializing Arkiv client...")
    
    if rpc_url:
        # Connect to remote RPC endpoint
        provider = cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build())
        
        if wallet_file:
            # Load account from encrypted wallet
            try:
                account = load_account_from_wallet(wallet_file)
            except Exception as e:
                print(f"❌ Failed to load wallet: {e}")
                return
        else:
            # No wallet provided - create a random account (will have zero balance)
            print("⚠️  No wallet file provided - creating random account")
            print("   Set WALLET_FILE in .env or use --wallet-file to use a funded account")
            user_id = f"demo-{uuid.uuid4().hex[:8]}"
            account = NamedAccount.create(user_id)
        
        client = Arkiv(provider=provider, account=account)
    else:
        # Spin up a local node using default constructor
        print("   Starting local Arkiv node...")
        client = Arkiv()
        local_node = client.node
        account = None  # Use default account from client
    
    # Get current account address
    current_account = client.eth.default_account
    balance = client.eth.get_balance(current_account)
    
    print(f"✅ Connected!")
    if local_node:
        print(f"   Local Node: {local_node.http_url}")
    print(f"   Account: {current_account}")
    print(f"   Balance: {balance / 10**18:.6f} ETH\n")
    
    if balance == 0:
        print("⚠️  WARNING: Account has zero balance!")
        print("   Transactions will fail without funds.")
        print("   For testing, you may need to fund this account or use a local node.\n")
    
    # Track metrics
    create_times: list[float] = []
    read_times: list[float] = []
    query_times: list[float] = []
    created_keys: list[str] = []
    errors: list[str] = []
    
    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    
    # Create operations
    print(f"\n📝 Phase 1: Creating {iterations} entities...")
    for i in range(iterations):
        try:
            start = time.time()
            
            payload = json.dumps({
                "test_id": uuid.uuid4().hex,
                "iteration": i,
                "timestamp": time.time(),
            }).encode()
            
            entity_key, receipt = client.arkiv.create_entity(
                payload=payload,
                content_type="application/json",
                expires_in=client.arkiv.to_seconds(hours=1),
                attributes=Attributes({"test_type": "demo", "iteration": i})
            )
            
            elapsed = (time.time() - start) * 1000
            create_times.append(elapsed)
            created_keys.append(entity_key)
            
            print(f"   [{i+1:3}/{iterations}] Created in {elapsed:7.1f}ms | Block: {receipt.block_number}")
            
        except Exception as e:
            errors.append(f"Create #{i}: {e}")
            print(f"   [{i+1:3}/{iterations}] ❌ Error: {e}")
    
    # Read operations
    if created_keys:
        print(f"\n📖 Phase 2: Reading {len(created_keys)} entities...")
        for i, key in enumerate(created_keys):
            try:
                start = time.time()
                entity = client.arkiv.get_entity(key)
                elapsed = (time.time() - start) * 1000
                read_times.append(elapsed)
                
                payload_size = len(entity.payload) if entity and entity.payload else 0
                print(f"   [{i+1:3}/{len(created_keys)}] Read in {elapsed:7.1f}ms | Size: {payload_size} bytes")
                
            except Exception as e:
                errors.append(f"Read {key[:16]}...: {e}")
                print(f"   [{i+1:3}/{len(created_keys)}] ❌ Error: {e}")
    
    # Query operations
    print(f"\n🔍 Phase 3: Running {iterations} queries...")
    for i in range(iterations):
        try:
            start = time.time()
            entities = list(client.arkiv.query_entities('test_type = "demo"'))
            elapsed = (time.time() - start) * 1000
            query_times.append(elapsed)
            
            print(f"   [{i+1:3}/{iterations}] Query in {elapsed:7.1f}ms | Found: {len(entities)} entities")
            
        except Exception as e:
            errors.append(f"Query #{i}: {e}")
            print(f"   [{i+1:3}/{iterations}] ❌ Error: {e}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    def print_stats(name: str, times: list[float]) -> None:
        if times:
            print(f"\n{name}:")
            print(f"   Count:   {len(times)}")
            print(f"   Min:     {min(times):7.1f}ms")
            print(f"   Max:     {max(times):7.1f}ms")
            print(f"   Mean:    {statistics.mean(times):7.1f}ms")
            print(f"   Median:  {statistics.median(times):7.1f}ms")
            if len(times) > 1:
                print(f"   StdDev:  {statistics.stdev(times):7.1f}ms")
        else:
            print(f"\n{name}: No successful operations")
    
    print_stats("📝 CREATE ENTITY", create_times)
    print_stats("📖 READ ENTITY", read_times)
    print_stats("🔍 QUERY ENTITIES", query_times)
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors[:10]:  # Show first 10
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    
    # Calculate throughput
    total_ops = len(create_times) + len(read_times) + len(query_times)
    total_time = sum(create_times) + sum(read_times) + sum(query_times)
    if total_time > 0:
        ops_per_sec = total_ops / (total_time / 1000)
        print(f"\n⚡ Throughput: {ops_per_sec:.1f} ops/sec (single client)")
    
    success_rate = (total_ops / (iterations * 3)) * 100 if iterations > 0 else 0
    print(f"✅ Success Rate: {success_rate:.1f}%")
    
    # Cleanup
    print("\n👋 Cleaning up...")
    client.arkiv.cleanup_filters()
    if local_node:
        print("   Stopping local node...")
        local_node.stop()
    print("Done!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Arkiv Load Test Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Use local node (when ARKIV_RPC_URL not set in .env)
    uv run python -m loadtest.demo
    
    # Use remote RPC with wallet file
    uv run python -m loadtest.demo --rpc-url https://mendoza.hoodi.arkiv.network/rpc --wallet-file ./wallet.json
    
    # Custom iterations
    uv run python -m loadtest.demo --iterations 20
        """
    )
    parser.add_argument(
        "--rpc-url",
        default=DEFAULT_RPC_URL,
        help="Arkiv RPC endpoint (default: from ARKIV_RPC_URL env var, or local node if not set)"
    )
    parser.add_argument(
        "--wallet-file",
        default=DEFAULT_WALLET_FILE,
        help="Path to encrypted wallet JSON file (default: from WALLET_FILE env var)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of test iterations (default: 10)"
    )
    
    args = parser.parse_args()
    run_load_test_demo(args.rpc_url, args.iterations, args.wallet_file)


if __name__ == "__main__":
    main()
