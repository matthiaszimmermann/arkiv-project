"""
Example 5: Web3.py Integration

This example demonstrates:
- Using Arkiv alongside standard web3.py operations
- Accessing Web3 functionality (blocks, balances, chain info)
- Combining Arkiv SDK convenience methods with Web3 calls
- Full entity lifecycle with Web3 context

Run this example: uv run python -m arkiv_starter.05_web3_integration
"""

from arkiv.provider import ProviderBuilder
from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode
from web3 import Web3
from typing import cast
from web3.providers.base import BaseProvider
from eth_account.signers.local import LocalAccount

# Setup: Start node and create client
print("🚀 Starting local Arkiv node and client...")
client = Arkiv()
print("   Extract the signer account (LocalAccount) from the client...")
account_name = next(iter(client.accounts.keys()))
account: LocalAccount = client.accounts[account_name].local_account

# Verify account matches default account (web3 signer account for Arkiv client)
assert account.address == client.eth.default_account
print(f"✅ Account ready: {account.address}\n")

# ============================================================================
# Part 1: Standard Web3 Operations
# ============================================================================
print("🌐 Part 1: Standard Web3 Operations")
print("=" * 60)

# Get block information
latest_block = client.eth.get_block("latest")
print(f"📦 Latest Block Number: {latest_block['number']}")
print(f"   Timestamp: {latest_block['timestamp']}")
print(f"   Transaction Count: {len(latest_block['transactions'])}\n")

# Check account balance
balance_wei = client.eth.get_balance(account.address)
balance_eth = Web3.from_wei(balance_wei, "ether")
print("💰 Account Balance:")
print(f"   {balance_wei} wei")
print(f"   {balance_eth} ETH\n")

# Get chain ID
chain_id = client.eth.chain_id
print(f"🔗 Chain ID: {chain_id}\n")

# ============================================================================
# Part 2: Arkiv-Specific Entity Creation
# ============================================================================
print("📦 Part 2: Arkiv-Specific Operations")
print("=" * 60)

# Create entity
print("📝 Creating entity with Arkiv...")
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Web3 integration example", 
    expires_in=3600, 
    content_type="text/plain"
)
print(f"✅ Entity Created: Key {entity_key}")
print(f"   Transaction Hash: {receipt.tx_hash}")
print(f"   Block Number: {receipt.block_number}\n")

# ============================================================================
# Part 3: Standard Web3 Operations on Arkiv Transaction
# ============================================================================

# Get transaction details using Web3
print("🔍 Part 3: Retrieving transaction metadata with Web3...")
print("=" * 60)
tx = client.eth.get_transaction(receipt.tx_hash)
print(f"   From: {tx['from']}")
print(f"   To: {tx['to']}")
print(f"   Gas: {tx['gas']}")
print(f"   Gas Price: {Web3.from_wei(tx['gasPrice'], 'gwei')} gwei")
print(f"   Nonce: {tx['nonce']}")

# Get transaction receipt with Web3
tx_receipt = client.eth.get_transaction_receipt(receipt.tx_hash)
print(f"\n📄 Transaction Receipt:")
print(f"   Gas Used: {tx_receipt['gasUsed']}")
print(f"   Cumulative Gas Used: {tx_receipt['cumulativeGasUsed']}")
print(f"   Status: {'Success' if tx_receipt['status'] == 1 else 'Failed'}")
print(f"   Logs Count: {len(tx_receipt['logs'])}\n")

# ============================================================================
# Part 4: Accessing Contract Information
# ============================================================================
print("🔧 Part 4: Accessing Contract Information")
print("=" * 60)

# Access the Arkiv contract address
arkiv_contract = client.arkiv.contract
print(f"📜 Arkiv Contract Address: {arkiv_contract.address}")

# Read entity using Arkiv's convenience methods
entity = client.arkiv.get_entity(entity_key)
print(f"📖 Entity Details (via Arkiv SDK):")
print(f"   Key: {entity_key}")
print(f"   Owner: {entity.owner}")
print(f"   Content Type: {entity.content_type}")
print(f"   Expires At Block: {entity.expires_at_block}")
if entity.payload:
    print(f"   Content Length: {len(entity.payload)} bytes")
    print(f"   Content: {entity.payload.decode('utf-8')}\n")
else:
    print(f"   No payload content\n")

# ============================================================================
# Summary
# ============================================================================
print("=" * 60)
print("📋 Summary:")
print("   ✅ Standard Web3 operations work seamlessly with Arkiv")
print("   ✅ Access transaction metadata using Web3 methods")
print("   ✅ Arkiv SDK provides convenient entity management")
print("   ✅ Combine Web3 context with Arkiv storage operations")
print("=" * 60)
print("\n💡 Note: Arkiv SDK simplifies entity operations.")
print("   Direct contract interaction is complex - use SDK methods!")

