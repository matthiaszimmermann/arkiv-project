"""
Example 1: Arkiv Client Initialization Patterns

This example demonstrates:
- Default client initialization (simplest approach)
- Custom provider configuration (for specific RPC endpoints)
- Custom account management (for specific private keys)
- Managing multiple accounts with switch_to()
- Accessing the node reference for funding and utilities

Run this example: uv run python -m arkiv_starter.01_clients
"""

import socket
from typing import Optional, cast
from web3.providers.base import BaseProvider
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder
from urllib.parse import urlparse

EXTERNAL_RPC_URL: str = "https://mendoza.hoodi.arkiv.network/rpc"

def is_rpc_reachable(rpc_url: str, timeout: float = 2.0) -> bool:
    """Check if RPC endpoint is reachable using a simple socket connection."""
    try:
        parsed = urlparse(rpc_url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 8545)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

print("=" * 70)
print("PATTERN 1: Default Constructor (Simplest)")
print("=" * 70)
print("\n🚀 Creating Arkiv client with default settings...")
print("   - Automatically starts a local node")
print("   - Creates and funds a default account")
print("   - Ready to use immediately\n")

client = Arkiv()
print(f"✅ Client created!")
print(f"   Default account: {client.eth.default_account}")
print(f"   Balance: {client.eth.get_balance(client.eth.default_account)/10**18} ETH")
print(f"   Node: {client.node.http_url if client.node else 'None'}")
print(f"   Accounts registry: {list(client.accounts.keys())}\n")

# Quick test
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Test from default client",
    content_type="text/plain",
    expires_in=3600
)
print(f"✅ Test entity created: {entity_key}\n")


print("=" * 70)
print("PATTERN 2: Custom Provider (Specific RPC Endpoint)")
print("=" * 70)
print("\n🚀 Creating client with custom provider...")
print("   - Connect to specific RPC URL")
print("   - Useful for remote nodes or specific configurations")
print("   - Fallback to local node if external node not reachable\n")

local_node = client.node
if is_rpc_reachable(EXTERNAL_RPC_URL):
    print(f"🌐 External RPC URL is reachable: {EXTERNAL_RPC_URL}\n")
    rpc_url = EXTERNAL_RPC_URL
else:
    print(f"⚠️  External RPC URL is NOT reachable: {EXTERNAL_RPC_URL}")
    assert local_node is not None, "Default client should have started a node"
    rpc_url = local_node.http_url
    print(f"   Falling back to local node RPC URL: {rpc_url}\n")

provider = cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build())
# Note: When only providing provider, client doesn't auto-create account
# You'll need to provide one or use accounts from original client
custom_provider_client = Arkiv(provider)

print(f"✅ Client with custom provider created!")
print(f"   Provider: {provider}")
print(f"   Note: No default account - you must provide one for transactions\n")

print("=" * 70)
print("PATTERN 3: Custom Account (Specific Private Key)")
print("=" * 70)
print("\n🚀 Creating client with custom provider AND custom account...")
print("   - Full control over provider and account")
print("   - Useful for production with specific keys\n")

account = NamedAccount.create("custom-account")
if local_node:
    local_node.fund_account(account)  # Fund the new account

custom_account_client = Arkiv(provider, account=account)
custom_account_balance = custom_account_client.eth.get_balance(account.address)

print(f"✅ Client with custom account created!")
print(f"   Account: {account.address}")
print(f"   Account name: {account.name}")
print(f"   Balance: {custom_account_balance/10**18} ETH\n")

# Quick test
if custom_account_balance > 0:
    print("💸 Creating test entity with custom account...")
    entity_key2, receipt2 = custom_account_client.arkiv.create_entity(
        payload=b"Test from custom account",
        content_type="text/plain",
        expires_in=3600
    )
    print(f"✅ Test entity created: {entity_key2}\n")


print("=" * 70)
print("PATTERN 4: Managing Multiple Accounts (switch_to)")
print("=" * 70)
print("\n🚀 Demonstrating multi-account management...")
print("   - Add accounts to client registry")
print("   - Switch signing account dynamically")
print("   - Useful for testing ownership transfers\n")

original_account = client.eth.default_account
original_signer = client.current_signer  # Track the current signer name
print(f"📋 Starting with account: {original_account}")
print(f"   Current signer name: {original_signer}")

# Create and add a second account
account_name = "second-account"
print(f"\n➕ Creating and adding a second account: {account_name}...")
second_account = NamedAccount.create(account_name)
assert client.node is not None
client.node.fund_account(second_account)
client.accounts[account_name] = second_account
print(f"✅ Added second account: {second_account.address}")
print(f"   Balance: {client.eth.get_balance(second_account.address)/10**18} ETH")
print(f"   Accounts registry: {list(client.accounts.keys())}\n")

# Switch to second account
print("🔄 Switching to second account...")
client.switch_to("second-account")
print(f"✅ Now signing with: {client.eth.default_account}")

# Create entity with second account
entity_key3, receipt3 = client.arkiv.create_entity(
    payload=b"Created by second account",
    content_type="text/plain",
    expires_in=3600
)
entity = client.arkiv.get_entity(entity_key3)
print(f"✅ Entity created: {entity_key3}")
print(f"   Owner: {entity.owner if entity else 'N/A'}\n")

# Switch back to original (use current_signer to track the name)
print("🔄 Switching back to original account...")
if original_signer:
    client.switch_to(original_signer)  # Use the saved signer name
    print(f"✅ Now signing with: {client.eth.default_account}")
    print(f"   Current signer name: {client.current_signer}\n")
else:
    print("⚠️  No original signer to switch back to\n")


print("=" * 70)
print("PATTERN 5: Accessing Node Reference")
print("=" * 70)
print("\n🚀 Using the node reference for utilities...")
print("   - Fund accounts")
print("   - Get node information")
print("   - Control node lifecycle\n")

node = client.node
if node:
    print(f"✅ Node reference available!")
    print(f"   HTTP URL: {node.http_url}")
    print(f"   WebSocket URL: {node.ws_url}")
    
    # Create a third account and fund it via node
    third_account = NamedAccount.create("third-account")
    node.fund_account(third_account)
    print(f"\n✅ Funded new account via node: {third_account.address}")
    print(f"   Balance: {client.eth.get_balance(third_account.address)/10**18} ETH")
else:
    print("⚠️  No node reference (client connected to external provider)")


print("\n" + "=" * 70)
print("SUMMARY: When to Use Each Pattern")
print("=" * 70)
print("""
1. DEFAULT (Arkiv()):
   ✅ Quick prototyping and examples
   ✅ Local development and testing
   ✅ Don't need specific configuration

2. CUSTOM PROVIDER (Arkiv(provider)):
   ✅ Connect to remote/production nodes
   ✅ Specific RPC endpoint configuration
   ✅ Custom provider settings

3. CUSTOM ACCOUNT (Arkiv(provider, account=account)):
   ✅ Use specific private keys
   ✅ Production deployments
   ✅ Full control over signing account

4. MULTIPLE ACCOUNTS (client.accounts[] + switch_to()):
   ✅ Testing ownership transfers
   ✅ Multi-user scenarios
   ✅ Demonstrating permissions
   💡 Use client.current_signer to track current account name

5. NODE REFERENCE (client.node):
   ✅ Fund test accounts
   ✅ Access node utilities
   ✅ Control node lifecycle
""")

print("✅ All client initialization patterns demonstrated!\n")
