"""
Example 2: Entity CRUD Operations

This example demonstrates:
- Creating entities (storing data on-chain)
- Reading entities by entity key (their ID)
- Updating existing entities
- Extending entity expiration
- Changing entity owner
- Deleting entities

Note: For client initialization patterns, see 01_clients.py

Run this example: uv run python -m arkiv_starter.02_entity_crud
"""

from arkiv import Arkiv

# Simple setup - see 01_clients.py for detailed client initialization patterns
print("🚀 Setting up Arkiv client...")
client = Arkiv()
print(f"✅ Client ready with account: {client.eth.default_account}\n")

print("📝 Step 1: Creating entity...")
data = b"Hello, Arkiv! This is my first entity."
entity_key, receipt = client.arkiv.create_entity(
    payload=data,
    content_type="text/plain",
    expires_in=3600,  # Expires in 1 hour (3600 seconds)
)
print(f"✅ Entity created!")
print(f"   Entity Key: {entity_key}")
print(f"   Block: {receipt.block_number}")
print(f"   Exists: {client.arkiv.entity_exists(entity_key)}\n")

print("📖 Step 2: Reading entity...")
entity = client.arkiv.get_entity(entity_key)
assert entity is not None
print("✅ Retrieved entity:")
print(f"   Key: {entity.key}")
print(f"   Owner: {entity.owner}")
if entity.payload:
    print(f"   Payload: {entity.payload.decode('utf-8')}")
print(f"   Content Type: {entity.content_type}")
print(f"   Expires At Block: {entity.expires_at_block}\n")

print("🔄 Step 3: Updating entity...")
new_data = b"Updated content - Arkiv makes data management easy!"
receipt = client.arkiv.update_entity(
    entity_key=entity_key,
    payload=new_data,
    content_type="text/plain",
    expires_in=7200,  # Extend expiration to 2 hours
)
print(f"✅ Entity updated!")
print(f"   Block: {receipt.block_number}")

# Verify the update
updated_entity = client.arkiv.get_entity(entity_key)
assert updated_entity is not None
if updated_entity.payload:
    print(f"   Updated payload: {updated_entity.payload.decode('utf-8')}")
print(f"   New expiration: {updated_entity.expires_at_block}\n")

print("⏱️  Step 4: Extending entity lifetime...")
extend_by = client.arkiv.to_seconds(hours=1)
receipt = client.arkiv.extend_entity(entity_key, extend_by=extend_by)
print(f"✅ Entity extended!")
print(f"   Block: {receipt.block_number}")

# Verify the extension
extended_entity = client.arkiv.get_entity(entity_key)
assert extended_entity is not None
print(f"   Extended expiration: {extended_entity.expires_at_block}\n")

print("👤 Step 5: Changing entity owner...")
# Track original signer before switching
original_signer = client.current_signer
print(f"   Current signer: {original_signer}")

# Create a new account to transfer ownership to
from arkiv import NamedAccount
new_owner_account = NamedAccount.create("new-owner")
node = client.node
assert node is not None
node.fund_account(new_owner_account)

receipt = client.arkiv.change_owner(entity_key, new_owner=new_owner_account.address)
print(f"✅ Entity owner changed!")
print(f"   Block: {receipt.block_number}")
print(f"   Old owner: {client.eth.default_account}")
print(f"   New owner: {new_owner_account.address}\n")

# Verify the ownership transfer
transferred_entity = client.arkiv.get_entity(entity_key)
assert transferred_entity is not None
print(f"   Verified new owner: {transferred_entity.owner}\n")

print("🗑️  Step 6: Deleting entity (as new owner)...")
# Switch to new owner to delete (only owner can delete)
print(f"   Switching from '{client.current_signer}' to 'new-owner' account...")
client.accounts["new-owner"] = new_owner_account
client.switch_to("new-owner")
print(f"   Current signer: {client.current_signer}")

receipt = client.arkiv.delete_entity(entity_key)
print(f"✅ Entity deleted!")
print(f"   Block: {receipt.block_number}")

# Verify deletion
if client.arkiv.entity_exists(entity_key):
    print("   ⚠️  Entity still exists (unexpected)\n")
else:
    print("   Confirmed: Entity no longer exists\n")

print("✅ CRUD operations complete!")

