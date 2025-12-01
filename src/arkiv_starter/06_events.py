"""
Example 4: Real-Time Entity Events

This example demonstrates:
- Using Arkiv's convenience methods for event watching
- Subscribing to entity lifecycle events (create/update/delete)
- Real-time event monitoring with callbacks
- Processing event data with typed event objects

Run this example: uv run python -m arkiv_starter.04_events
"""

import time
from arkiv import Arkiv, NamedAccount
from arkiv.types import CreateEvent, UpdateEvent, DeleteEvent, ExtendEvent, ChangeOwnerEvent, TxHash

# Setup: Start node and create client
print("🚀 Starting local Arkiv node and client ...")
client = Arkiv()
account = client.eth.default_account
print(f"✅ Client ready with account: {account}\n")

# Define event callbacks
def on_entity_created(event: CreateEvent, tx_hash: TxHash) -> None:
    """Callback for entity creation events."""
    print("🎉 Entity Created! - on_entity_created(...)")
    print(f"     Entity Key: {event.key}")
    print(f"     Owner: {event.owner_address}")
    print(f"     Expires at Block: {event.expiration_block}")
    print(f"     Transaction: {tx_hash}\n")


def on_entity_updated(event: UpdateEvent, tx_hash: TxHash) -> None:
    """Callback for entity update events."""
    print("🔄 Entity Updated! - on_entity_updated(...)")
    print(f"     Entity Key: {event.key}")
    print(f"     Owner: {event.owner_address}")
    print(f"     Old Expiration: {event.old_expiration_block}")
    print(f"     New Expiration: {event.new_expiration_block}")
    print(f"     Transaction: {tx_hash}\n")


def on_entity_deleted(event: DeleteEvent, tx_hash: TxHash) -> None:
    """Callback for entity deletion events."""
    print("🗑️ Entity Deleted! - on_entity_deleted(...)")
    print(f"     Entity Key: {event.key}")
    print(f"     Owner: {event.owner_address}")
    print(f"     Transaction: {tx_hash}\n")


def on_entity_extended(event: ExtendEvent, tx_hash: TxHash) -> None:
    """Callback for entity extension events."""
    print("⏱️  Entity Extended! - on_entity_extended(...)")
    print(f"     Entity Key: {event.key}")
    print(f"     Owner: {event.owner_address}")
    print(f"     Old Expiration: {event.old_expiration_block}")
    print(f"     New Expiration: {event.new_expiration_block}")
    print(f"     Transaction: {tx_hash}\n")


def on_owner_changed(event: ChangeOwnerEvent, tx_hash: TxHash) -> None:
    """Callback for owner change events."""
    print("👤 Owner Changed! - on_owner_changed(...)")
    print(f"     Entity Key: {event.key}")
    print(f"     Old Owner: {event.old_owner_address}")
    print(f"     New Owner: {event.new_owner_address}")
    print(f"     Transaction: {tx_hash}\n")


print("👂 Step 1: Setting up event watchers with Arkiv convenience methods...")
created_watcher = client.arkiv.watch_entity_created(on_entity_created)
updated_watcher = client.arkiv.watch_entity_updated(on_entity_updated)
extended_watcher = client.arkiv.watch_entity_extended(on_entity_extended)
owner_changed_watcher = client.arkiv.watch_owner_changed(on_owner_changed)
# Note: watch_entity_deleted has a type hint bug in SDK, but works at runtime
deleted_watcher = client.arkiv.watch_entity_deleted(on_entity_deleted)  # type: ignore[arg-type]
print("   ✅ Watching for:")
print(f"    - Created: on_entity_created")
print(f"    - Updated: on_entity_updated")
print(f"    - Extended: on_entity_extended")
print(f"    - Owner Changed: on_owner_changed")
print(f"    - Deleted: on_entity_deleted\n")

print("📝 Step 2: Performing operations to trigger events...\n")

print("1️⃣  Operation 1: Creating entity...")
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Event monitoring test", content_type="text/plain", expires_in=3600
)
print(f"     Created entity: {entity_key}")

print("2️⃣  Operatio 2: Updating entity...")
receipt = client.arkiv.update_entity(
    entity_key=entity_key,
    payload=b"Updated content for event test",
    content_type="text/plain",
    expires_in=7200,
)
print(f"     Updated entity: {entity_key}")

print("3️⃣  Operation 3: Extending entity lifetime...")
seconds = client.arkiv.to_seconds(hours=1)
receipt = client.arkiv.extend_entity(entity_key, extend_by=seconds)
print(f"     Extended entity: {entity_key}")

print("4️⃣  Operation 4: Changing entity owner...")
original_signer = client.current_signer  # Track original account name
account_name = "new-owner"
new_account = NamedAccount.create(account_name)
receipt = client.arkiv.change_owner(entity_key, new_account.address)
print(f"     Changed owner of entity: {entity_key} to {new_account.address}")
print(f"     Original signer: {original_signer}")

print("5️⃣  Operation 5: Deleting entity (as new owner)...")
node = client.node
assert node is not None
node.fund_account(new_account)  # Fund the new account
client.accounts[account_name] = new_account  # Add to client accounts
print(f"     Switching from '{client.current_signer}' to '{account_name}' account...")
client.switch_to(account_name)  # Switch signing account to new owner
print(f"     Current signer: {client.current_signer}")
receipt = client.arkiv.delete_entity(entity_key)
print(f"     Deleted entity: {entity_key}")

print("\n✅ All operations complete! Check the event callbacks above.\n")

# Demonstrate cleanup
print(f"🧹 Active filters/event watchers: {len(client.arkiv.active_filters)}")
print("   Arkiv client automatically cleans up active filters/watchers")
print("   You can also manually stop and uninstall them:")
print(f"    - Either: Using client.arkiv.cleanup_filters()")
print(f"    - Or: call filter_xyz.uninstall() for each filter")
