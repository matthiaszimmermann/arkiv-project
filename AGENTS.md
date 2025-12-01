# AGENTS.md

AI coding agent instructions for the Arkiv Python Starter template.

This file provides context for AI coding tools (GitHub Copilot, Cursor, Aider, Gemini CLI, RooCode, etc.) working with the Arkiv SDK.

---

## ⚡ Quick Reference

**🚨 FIRST: Categorize Your App Type 🚨**

**Before writing ANY code, determine if your app is multi-user or single-user:**

**Multi-User = REQUIRES Server + Client Pattern:**
- 🗨️ **Chat/Messaging** - Users send messages to each other
- 👥 **Social Media** - Users interact with posts/profiles
- 🎮 **Multiplayer Games** - Players in shared game world
- 🤝 **Collaborative Tools** - Real-time editing/voting
- ⚠️ **If users in different terminals/processes need to see each other's data = MULTI-USER**

**📁 MANDATORY: Study `07_agents.py` BEFORE building multi-user apps!**
```bash
# Read the reference implementation first:
cat src/arkiv_starter/07_agents.py

# Run it to understand how it works:
uv run python -m arkiv_starter.07_agents demo
```
This file contains the **canonical patterns** for multi-user apps:
- `ArkivChain` class → Server pattern (runs shared blockchain node)
- `Client` class → Client pattern (connects to shared node)
- `run_demo()` → Shows how multiple clients interact on same chain

**Single-User = Can Use Simple Pattern:**
- 📊 **Personal Storage** - One user's data
- 🤖 **Automation/Bots** - Scripts run alone
- 🧪 **Tests** - Use pytest fixtures
- 🎯 **Single-Player Games** - No interaction between processes

**Critical Rule for AI Assistants:**
When user says "chat", "social", "multiplayer", "collaborative" → **STOP** → **Read `07_agents.py` first** → Use that as your template. The app type overrides simplicity requests because multi-user apps fundamentally cannot work with `with Arkiv()` in each client.

---

**Critical conventions to remember:**
- Python SDK: `snake_case` (entity_key, content_type, expires_in)
- Query syntax: `snake_case` with `$` prefix for system attributes ($owner, $content_type)
- Contract events: `camelCase` (entityKey, ownerAddress, expirationBlock)
- Entity attributes: `snake_case` (entity.key, entity.payload, entity.owner)

**Return values:**
- `create_entity()` → tuple: `(entity_key, receipt)`
- `update_entity()` / `delete_entity()` → just `receipt`

**Prefer these patterns:**
- ✅ `client.arkiv.entity_exists(key)` → check existence (returns bool)
- ✅ `client.arkiv.watch_entity_*()` → event watchers (not raw contract filters)
- ✅ `client.switch_to(name)` → switch accounts (not multiple clients)
- ✅ `client.current_signer` → track current account name for switching back
- ✅ `NamedAccount.create(name)` → for local dev (not Account.create())

**Multi-user interactive apps (chat/social/gaming):**
- 📁 **FIRST: Read `src/arkiv_starter/07_agents.py`** - This is your template!
- ✅ **Server + Client pattern** → Copy `ArkivChain` for server, `Client` for clients
- ✅ Clients use `ProviderBuilder().custom(url=rpc_url).build()` to connect to shared server
- ❌ **NEVER** `with Arkiv()` in multi-user client code (creates separate blockchains!)
- ❌ **NEVER** let "simple" override multi-user requirement (won't work at all!)

**Time conversion (methods, not imports):**
- ✅ `client.arkiv.to_seconds(days=7)` → method on arkiv module
- ✅ `client.arkiv.to_blocks(days=1)` → method on arkiv module
- ❌ `from arkiv import to_seconds` → WRONG, not exported

**Account and entity access:**
- ✅ `client.eth.default_account` → current account address (string)
- ✅ `entity.attributes` → dict of custom attributes (or None)
- ✅ `entity.payload` → bytes data (or None, always check!)
- ✅ `account.address` → when you have NamedAccount object

**Testing:**
- ✅ Use fixture name `arkiv_client` (not `client`)
- ✅ Use fixture name `arkiv_node` for node access
- ✅ Session-scoped fixtures = shared blockchain state
- ✅ Use unique identifiers (timestamps/UUIDs) for test isolation

**Environment Setup:**
- ✅ Dev container is ALREADY CONFIGURED - no setup needed
- ❌ DON'T call `configure_python_environment` - it's automatic
- ✅ Just run: `uv run python -m app.demo` or `uv run pytest`

**Run examples:** `uv run python -m arkiv_starter.03_clients` (etc., 01-08)

---

## 🏗️ Critical: Understanding Arkiv Architecture

### Client/Node Architecture

**⚠️ MOST IMPORTANT CONCEPT**: Arkiv uses a **Client → Node → Blockchain Network** architecture.

```
LOCAL DEVELOPMENT (Single Node):
┌─────────────┐      ┌─────────────────────────────┐
│   Client    │ ───→ │      Arkiv Node             │
│  (Arkiv)    │      │  (Full Blockchain Instance) │
└─────────────┘      └─────────────────────────────┘

PRODUCTION (Multi-Node Network):
                     ┌────────────────────────────────────────────────────────────────┐
                     │               BLOCKCHAIN (Network of nodes).                   │
┌─────────────┐      │  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│   Client    │ ───→ │  │ Arkiv Node 1 │ ←──→ │ Arkiv Node 2 │ ←──→ │ Arkiv Node 3 │  │
│  (Arkiv)    │      │  │  (Consensus) │      │  (Consensus) │      │  (Consensus) │  │
└─────────────┘      │  └──────────────┘      └──────────────┘      └──────────────┘  │
                     │              Shared Ledger (Replicated State)                  │
                     └────────────────────────────────────────────────────────────────┘
```

**Key Understanding:**
- **Client** = Python object that sends transactions/queries (lightweight)
- **Arkiv Node** = Full blockchain node running consensus, storage, and networking (heavyweight)
- **Local Node** = Complete, real blockchain node - NOT a simulation or mock
- **Production Network** = Multiple nodes running the same software, forming consensus

**Critical Insight:**
Your local `ArkivNode()` is **identical** to production nodes - same code, same blockchain logic, same storage. The only difference is that it runs **alone** (single node) instead of in a **network** (multiple nodes forming consensus). This means:
- ✅ Your local tests are running against **real blockchain code**
- ✅ Behavior is identical to production (just without network consensus)
- ✅ When you deploy, you're connecting to multiple copies of what you tested locally

**For Clients to Interact:**
- ⚠️ **Multiple clients MUST connect to the SAME node/blockchain**
- ⚠️ Each `Arkiv()` creates a separate blockchain - clients on different nodes CANNOT see each other's data
- ✅ Use shared node pattern (shown below) for multi-client communication

### Each `Arkiv()` Creates a NEW Node!

❌ **CRITICAL MISTAKE - Multiple Isolated Blockchains:**

```python
# This creates TWO separate blockchains that CANNOT communicate!
client1 = Arkiv()  # Starts Node 1 with Blockchain A
client2 = Arkiv()  # Starts Node 2 with Blockchain B (completely separate!)

# Alice and Bob are in different universes - no communication possible!
client1.arkiv.create_entity(...)  # Stored in Blockchain A
client2.arkiv.create_entity(...)  # Stored in Blockchain B
```

**Why this happens:**
- `Arkiv()` without parameters calls `ArkivNode().start()` internally
- Each node runs its own blockchain (like starting separate PostgreSQL instances)
- Coming from traditional APIs (where multiple clients → one server), this is counterintuitive

✅ **CORRECT Pattern 1 - Single Client, Multiple Accounts (Testing/Simulation Only):**

```python
# Use when ONE entity needs to sign transactions as DIFFERENT accounts
# Example: Testing ownership transfers, simulating multi-user scenarios
client = Arkiv()  # One node, one blockchain

# Create multiple accounts
alice = NamedAccount.create("alice")
bob = NamedAccount.create("bob")
client.node.fund_account(alice)
client.node.fund_account(bob)

# Add to client registry
client.accounts["alice"] = alice
client.accounts["bob"] = bob

# Switch signing account (same client controls both)
client.switch_to("alice")
client.arkiv.create_entity(...)  # Alice's message

client.switch_to("bob")
client.arkiv.create_entity(...)  # Bob's message (same blockchain!)
```

⚠️ **Important**: Pattern 1 is for single-client scenarios (tests, demos, automation). When simulating real multi-party interaction, use Pattern 2.

✅ **CORRECT Pattern 2 - Multiple Independent Clients, Shared Node (Multi-Party Interaction):**

```python
# Use when DIFFERENT parties need to interact with each other
# Each party maintains their own client and private key
# Critical: Parties MUST NOT share accounts - each has independent client

# Create ONE shared node
main_client = Arkiv()  # Starts the node
shared_node = main_client.node

# Create provider from shared node
from arkiv.provider import ProviderBuilder
from web3.providers.base import BaseProvider
from typing import cast

provider = cast(BaseProvider, ProviderBuilder().node(shared_node).build())

# Each party gets their own client with their own account
alice_account = NamedAccount.create("alice")
bob_account = NamedAccount.create("bob")
shared_node.fund_account(alice_account)
shared_node.fund_account(bob_account)

alice_client = Arkiv(provider=provider, account=alice_account)
bob_client = Arkiv(provider=provider, account=bob_account)

# Now Alice and Bob interact independently on the SAME blockchain
alice_client.arkiv.create_entity(...)  # Alice's action (Alice's private key)
bob_client.arkiv.create_entity(...)    # Bob's action (Bob's private key)
# They can see each other's data because they share the blockchain!
```

**Key Difference:**
- **Pattern 1**: ONE client switches between accounts (for testing/automation)
- **Pattern 2**: MULTIPLE independent clients, each with own account (for real multi-party interaction)

### Node Lifecycle Management

**⚠️ CRITICAL**: Nodes are long-running processes that MUST be cleaned up.

❌ **WRONG - Resource Leak:**

```python
def my_function():
    client = Arkiv()  # Starts node
    client.arkiv.create_entity(...)
    # Function ends, node keeps running! Memory leak!
```

You'll see this warning:
```
Arkiv client with managed node is being destroyed but node is still running.
Call arkiv.node.stop() or use context manager: 'with Arkiv() as arkiv:'
```

✅ **CORRECT Pattern 1 - Context Manager (Recommended):**

```python
# Node automatically stopped when exiting context
with Arkiv() as client:
    client.arkiv.create_entity(...)
    # ... do work ...
# Node stopped here automatically
```

✅ **CORRECT Pattern 2 - Explicit Cleanup:**

```python
client = Arkiv()
try:
    client.arkiv.create_entity(...)
    # ... do work ...
finally:
    if client.node:
        client.node.stop()  # Explicitly stop node
```

✅ **CORRECT Pattern 3 - Shared Node in Threads:**

```python
# Main thread owns the node
main_client = Arkiv()

def worker_thread(shared_node):
    provider = ProviderBuilder().node(shared_node).build()
    client = Arkiv(provider=provider, account=my_account)
    # Do work...
    client.arkiv.cleanup_filters()  # Clean up event watchers
    # DON'T call client.node.stop() - main thread owns the node!

# Later, in main thread:
main_client.node.stop()  # Only the owner stops the node
```

---

## 🌟 What is Arkiv? (For New AI Assistants)

**Arkiv is a Web3 database that solves the Web3 data trilemma: Decentralization + Queryability + Simplicity.**

### Core Value Proposition

**The Problem Arkiv Solves:**
- Traditional blockchains: Can store data, but querying requires downloading everything
- Indexers (The Graph): Queryable, but requires trust in indexer operators
- Off-chain databases: Simple and queryable, but centralized

**What Makes Arkiv Different:**

1. **Database-Like Queries on Blockchain Data**
   - Store data with queryable attributes on-chain
   - Rich filtering: `$owner = "..." AND type = "message" AND priority > 5`
   - No separate indexer infrastructure needed

2. **Automatic TTL (Time-To-Live)**
   - Data expires automatically (`expires_in` parameter)
   - Prevents blockchain bloat
   - Perfect for temporary/ephemeral data

3. **Web3.py Integration**
   - Extends familiar web3.py API
   - No new paradigm to learn
   - Works alongside existing Web3 code

4. **Real-Time Events**
   - Subscribe to entity lifecycle events (create/update/delete)
   - No polling required
   - Immediate notifications

5. **No Infrastructure Required**
   - Local dev: `ArkivNode().start()` - done!
   - Production: Just an RPC endpoint
   - No graph-node, PostgreSQL, or IPFS to manage

### Key Use Cases

**Perfect for:**
- On-chain social/messaging (queryable messages with metadata)
- Temporary KV store for dApps (session data, preferences)
- Gaming state/leaderboards (queryable by score, level, guild)
- Decentralized event management (RSVP lists, ticket metadata)
- Verifiable credentials with expiration (attestations, certifications)

**Not ideal for:**
- Large files (use IPFS/Arweave, store hash in Arkiv)
- Permanent archival (data has TTL, use Arweave for permanence)
- Complex SQL queries (simple filters only, no JOINs/aggregations)

### The Unfair Advantage

Arkiv gives you all three:
- ✅ **Decentralization** - On-chain storage, verifiable
- ✅ **Queryability** - Rich filters without full scans
- ✅ **Simplicity** - No infrastructure, familiar API

Most solutions force you to pick 2 of 3.

---

## 🎯 Critical: Naming Conventions

Arkiv uses **three different naming conventions** depending on context. Getting this wrong is the #1 mistake AI assistants make.

### Python SDK → `snake_case`

```python
# ✅ CORRECT
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    content_type="text/plain",
    expires_in=3600,
    attributes={"user_id": "123"}
)

# ❌ WRONG
entityKey, receipt = client.arkiv.createEntity(
    payload=b"data",
    contentType="text/plain",
    expiresIn=3600
)
```

**Key SDK parameters:**
- `entity_key` (not `entityKey`, not `entity_id`)
- `content_type` (not `contentType`)
- `expires_in` (not `expiresIn`)
- `from_block` (not `fromBlock`)

### Query Syntax → `snake_case` with `$` prefix

```python
# ✅ CORRECT - System attributes with $ and snake_case
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'
))

# ✅ CORRECT - User attributes without $
entities = list(client.arkiv.query_entities(
    'type = "user_profile" AND status = "active"'
))

# ❌ WRONG - camelCase in queries
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $contentType = "application/json"'
))
```

**System query attributes (with $):**
- `$key`, `$owner`, `$content_type`, `$created_at`, `$updated_at`, `$expires_at`

**User query attributes (without $):**
- Any custom name: `type`, `category`, `status`, `user_id`, etc.

### Contract Events → `camelCase`

```python
# ✅ CORRECT - Event args use camelCase
event_filter = arkiv_contract.events.ArkivEntityCreated.create_filter(from_block="latest")
for event in event_filter.get_all_entries():
    entity_key = hex(event['args']['entityKey'])      # camelCase!
    owner = event['args']['ownerAddress']             # camelCase!
    expiration = event['args']['expirationBlock']     # camelCase!

# ❌ WRONG - snake_case in event args
entity_key = hex(event['args']['entity_key'])  # Won't work
```

**Event names:**
- `ArkivEntityCreated`, `ArkivEntityUpdated`, `ArkivEntityDeleted`

**Event arguments (camelCase):**
- `entityKey`, `ownerAddress`, `expirationBlock`, `contentType`

### Entity Attributes → `snake_case`

```python
# ✅ CORRECT
print(entity.key)              # Not entity.id
print(entity.payload)          # Not entity.content
print(entity.owner)
print(entity.content_type)
print(entity.expires_at_block)
print(entity.created_at_block)

# ❌ WRONG - Old API
print(entity.id)       # Changed to entity.key
print(entity.content)  # Changed to entity.payload
```

---

## 🔧 API Return Values

### `create_entity()` Returns a Tuple

```python
# ✅ CORRECT - Unpack the tuple
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    expires_in=3600,
    content_type="text/plain"
)

# ❌ WRONG - Old API (pre-1.0)
tx_hash = client.arkiv.create_entity(...)  # No longer returns just tx_hash
receipt = client.eth.wait_for_transaction_receipt(tx_hash)  # Won't work
```

### `update_entity()` and `delete_entity()` Return Receipt Only

```python
# ✅ CORRECT - Just receipt, no tuple
receipt = client.arkiv.update_entity(
    entity_key,
    payload=b"updated data",
    expires_in=7200,
    content_type="text/plain"
)

receipt = client.arkiv.delete_entity(entity_key)

# ❌ WRONG - Don't try to unpack
key, receipt = client.arkiv.update_entity(...)  # TypeError
```

### Receipt Attributes

```python
# ✅ CORRECT - Receipt is a dataclass
print(receipt.tx_hash)        # Transaction hash (string)
print(receipt.block_number)   # Block number (int)
print(receipt.creates)        # List of created entity keys
print(receipt.updates)        # List of updated entity keys
print(receipt.deletes)        # List of deleted entity keys

# ❌ WRONG - Not a dict
print(receipt['transactionHash'])  # AttributeError
print(receipt.gas_used)            # Doesn't exist on Arkiv receipt
```

---

## 📦 Account Management

### Always Use `NamedAccount`

```python
# ✅ CORRECT - Use NamedAccount for local development
from arkiv import NamedAccount

account = NamedAccount.create("my-account")
node.fund_account(account)  # Works with NamedAccount

# ✅ CORRECT - Initialize client with account
client = Arkiv(provider, account=account)

# ❌ WRONG - Old API
from eth_account import Account
account = Account.create()  # LocalAccount won't work with node.fund_account()
```

### Account Attributes

```python
# ✅ CORRECT - When you have an account object
print(account.address)       # Ethereum address
print(account.key)           # Private key for signing (bytes)
print(account.name)          # Account name (NamedAccount only)

# ❌ WRONG
print(account.private_key)  # Use account.key instead
```

### Accessing the Current Account from Client

```python
# ✅ CORRECT - Get current account address from client
current_address = client.eth.default_account  # Returns address string

# ✅ CORRECT - Check if entity belongs to current user
entity = client.arkiv.get_entity(entity_key)
if entity.owner != client.eth.default_account:
    print("You don't own this entity")

# ❌ WRONG - These don't exist
client.account.address           # AttributeError
client.default_account.address   # AttributeError
```

### Managing Multiple Accounts

The Arkiv client can manage multiple accounts and switch between them:

```python
# ✅ CORRECT - Add accounts to client and switch between them
from arkiv import Arkiv, NamedAccount

# Start with one account
client = Arkiv()  # Uses default account
original_signer = client.current_signer  # Track original account name

# Create and add a second account
new_account = NamedAccount.create("second-account")
node = client.node
assert node is not None
node.fund_account(new_account)

# Add to client's account registry
client.accounts["second-account"] = new_account

# Switch active signing account
client.switch_to("second-account")
# Now all transactions use new_account

# Switch back to original using tracked signer name
if original_signer:
    client.switch_to(original_signer)  # Use account name, not address

# ❌ WRONG - Creating separate clients for each account
client1 = Arkiv(provider, account=account1)  # Unnecessary
client2 = Arkiv(provider, account=account2)  # Wasteful
# Better: Use one client and switch_to()
```

**Use cases for multiple accounts:**
- Testing ownership transfers (create entity with account A, transfer to account B)
- Multi-user scenarios (simulate different users in tests)
- Demonstrating permissions (only owner can update/delete)

---

## 🏃 Running Examples

### Module Execution (Correct)

```bash
# ✅ CORRECT - Run as modules
uv run python -m arkiv_starter.01_hello_world
uv run python -m arkiv_starter.02_accounts
uv run python -m arkiv_starter.03_clients
uv run python -m arkiv_starter.04_entity_crud
uv run python -m arkiv_starter.05_queries
uv run python -m arkiv_starter.06_events
uv run python -m arkiv_starter.07_agents
uv run python -m arkiv_starter.08_web3_integration

# ✅ CORRECT - Run tests
uv run pytest
uv run pytest -n auto  # Parallel execution
```

### Direct Execution (Wrong for this project)

```bash
# ❌ WRONG - Don't run files directly
python src/arkiv_starter/02_entity_crud.py  # Import errors
cd src && python -m arkiv_starter.02_entity_crud  # Wrong directory
```

---

## 🧪 Testing Patterns

### Available Test Fixtures

The project's `conftest.py` provides these fixtures:

```python
# ✅ CORRECT - Use these exact fixture names
def test_something(arkiv_client, arkiv_node):
    # arkiv_client: Arkiv instance (session-scoped, shared across tests)
    # arkiv_node: ArkivNode instance (session-scoped, already started)
    
    entity_key, receipt = arkiv_client.arkiv.create_entity(
        payload=b"test data",
        expires_in=3600,
        content_type="text/plain"
    )
    assert entity_key is not None

# ❌ WRONG - These fixture names don't exist
def test_something(client, account):  # NameError: fixture 'client' not found
```

### Test Isolation with Session-Scoped Fixtures

**⚠️ CRITICAL:** Session-scoped fixtures mean:
- All tests share the SAME node and blockchain
- Data created in one test is visible in other tests
- Tests run in order but share state

**Solutions for test isolation:**

```python
# ✅ Pattern 1: Unique identifiers per test
import pytest
import time

@pytest.fixture
def unique_channel():
    """Generate unique channel name for test isolation."""
    return f"test-{int(time.time() * 1000000)}"

def test_messages(arkiv_client, unique_channel):
    chat = ChatClient(arkiv_client, channel=unique_channel)
    # Now isolated from other tests

# ✅ Pattern 2: Function-scoped client for full isolation
from typing import cast
from web3.providers.base import BaseProvider
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder

@pytest.fixture
def isolated_client(arkiv_node):
    """Create a fresh client with unique account per test."""
    provider = cast(BaseProvider, ProviderBuilder().node(arkiv_node).build())
    account = NamedAccount.create(f"test-{int(time.time() * 1000000)}")
    arkiv_node.fund_account(account)
    client = Arkiv(provider, account=account)
    yield client
    client.arkiv.cleanup_filters()

def test_with_isolation(isolated_client):
    # Fresh client with unique account
    pass

# ✅ Pattern 3: Query with test-specific filters
def test_user_messages(arkiv_client, unique_channel):
    alice = ChatClient(arkiv_client, username="Alice", channel=unique_channel)
    alice.send_message("Test message")
    
    # Query may return messages from other tests too
    all_alice_msgs = alice.get_user_messages("Alice")
    
    # Filter for messages from THIS test
    test_msgs = [m for m in all_alice_msgs if "Test message" in m["text"]]
    assert len(test_msgs) == 1
```

### Testing Event Watchers

Event watchers require special timing considerations:

```python
import time

def test_event_watching(arkiv_client):
    received_events = []
    
    def on_event(event, tx_hash):
        received_events.append(event)
    
    # ✅ CORRECT - Set up watcher BEFORE creating entities
    watcher = arkiv_client.arkiv.watch_entity_created(on_event)
    
    # Give watcher time to initialize
    time.sleep(0.2)
    
    # Create entity
    entity_key, receipt = arkiv_client.arkiv.create_entity(
        payload=b"test",
        expires_in=3600,
        content_type="text/plain"
    )
    
    # Wait for event processing (local node needs time)
    time.sleep(1.0)
    
    # Now check events
    assert len(received_events) >= 1
    
    # Cleanup
    watcher.uninstall()

# ❌ WRONG - Common pitfalls
def test_event_watching_wrong(arkiv_client):
    # Create entity FIRST → miss the event!
    entity_key, _ = arkiv_client.arkiv.create_entity(...)
    
    # Set up watcher AFTER → too late!
    watcher = arkiv_client.arkiv.watch_entity_created(on_event)
    
    # No sleep → event not processed yet
    assert len(received_events) >= 1  # Fails!
```

### Type Hints for Arkiv Code

```python
# ✅ CORRECT - Standard type hint imports
from typing import Any, Callable, Optional, cast
from web3.providers.base import BaseProvider
from arkiv import Arkiv, NamedAccount
from arkiv.types import CreateEvent, DeleteEvent, TxHash

# Callback type hints
def setup_watcher(callback: Callable[[str, int], None]) -> None:
    pass

# Provider casting (avoids IDE errors)
provider = cast(BaseProvider, ProviderBuilder().node(node).build())

# ❌ WRONG - Old-style or incorrect
def setup_watcher(callback: callable) -> None:  # Use Callable, not callable
    pass
```

### Local Node Doesn't Support All Queries Yet

```python
# ⚠️ LIMITATION - Local node doesn't support $content_type queries yet
# Use client-side filtering instead:

# ❌ Won't work on local node
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'
))

# ✅ WORKAROUND - Filter client-side
all_entities = list(client.arkiv.query_entities(f'$owner = "{address}"'))
filtered = [e for e in all_entities if e.content_type == "application/json"]
```

---

## 📚 Common Patterns

### Creating Entities with Attributes

```python
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"message": "Hello"}).encode(),
    content_type="application/json",
    expires_in=client.arkiv.to_seconds(days=7),
    attributes={
        "type": "message",
        "user_id": "alice123",
        "channel": "general"
    }
)
```

### Checking Entity Existence

```python
# Check if entity exists (returns bool)
exists = client.arkiv.entity_exists(entity_key)
if exists:
    entity = client.arkiv.get_entity(entity_key)
    # Process entity...

# get_entity() raises ValueError if not found
try:
    entity = client.arkiv.get_entity(entity_key)
except ValueError:
    print("Entity not found")
```

### Accessing Entity Attributes

```python
# ✅ CORRECT - Attributes are directly on the entity object
entity = client.arkiv.get_entity(entity_key)
attr_dict = entity.attributes  # Returns dict or None

# Example: Get channel from attributes
if entity.attributes:
    channel = entity.attributes.get("channel", "default")
else:
    channel = "default"

# Example: Access payload safely
if entity.payload:
    data = entity.payload.decode('utf-8')
    
# ❌ WRONG - No separate method exists
attributes = client.arkiv.get_entity_attributes(entity_key)  # Doesn't exist!
```

### Querying Entities

```python
# By owner
entities = list(client.arkiv.query_entities(f'$owner = "{account.address}"'))

# By custom attributes
entities = list(client.arkiv.query_entities(
    'type = "message" AND channel = "general"'
))

# Combined conditions
entities = list(client.arkiv.query_entities(
    f'$owner = "{account.address}" AND type = "message"'
))
```

### Listening to Events

Arkiv provides high-level event watchers with typed callbacks. **Prefer these over raw contract filters:**

```python
# ✅ CORRECT - Use Arkiv's convenience methods with typed callbacks
from arkiv.types import CreateEvent, UpdateEvent, DeleteEvent, ExtendEvent, ChangeOwnerEvent, TxHash

def on_entity_created(event: CreateEvent, tx_hash: TxHash) -> None:
    print(f"Created: {event.key} by {event.owner_address}")
    print(f"Expires at block: {event.expiration_block}")

def on_entity_updated(event: UpdateEvent, tx_hash: TxHash) -> None:
    print(f"Updated: {event.key}")
    print(f"Expiration: {event.old_expiration_block} → {event.new_expiration_block}")

def on_entity_deleted(event: DeleteEvent, tx_hash: TxHash) -> None:
    print(f"Deleted: {event.key} by {event.owner_address}")

# Set up watchers (returns filter objects for cleanup)
created_watcher = client.arkiv.watch_entity_created(on_entity_created)
updated_watcher = client.arkiv.watch_entity_updated(on_entity_updated)
deleted_watcher = client.arkiv.watch_entity_deleted(on_entity_deleted)  # type: ignore[arg-type]

# Also available:
extended_watcher = client.arkiv.watch_entity_extended(callback)  # ExtendEvent
owner_changed_watcher = client.arkiv.watch_owner_changed(callback)  # ChangeOwnerEvent

# Cleanup (automatic on client close, or manual):
client.arkiv.cleanup_filters()  # Uninstall all watchers
# Or individually: created_watcher.uninstall()
```

**Event Types Available:**
- `CreateEvent`: `key`, `owner_address`, `expiration_block`
- `UpdateEvent`: `key`, `owner_address`, `old_expiration_block`, `new_expiration_block`
- `ExtendEvent`: `key`, `owner_address`, `old_expiration_block`, `new_expiration_block`
- `ChangeOwnerEvent`: `key`, `old_owner_address`, `new_owner_address`
- `DeleteEvent`: `key`, `owner_address`

**For advanced use cases (raw contract filters):**

```python
# ❌ DISCOURAGED - Low-level contract events (use watch_entity_* instead)
event_filter = client.arkiv.contract.events.ArkivEntityCreated.create_filter(
    from_block="latest"
)

for event in event_filter.get_new_entries():
    entity_key = hex(event['args']['entityKey'])  # camelCase!
    owner = event['args']['ownerAddress']          # camelCase!
    print(f"New entity: {entity_key} by {owner}")
```

### Time Conversions

```python
# ✅ CORRECT - to_seconds and to_blocks are METHODS on the client
expires_in = client.arkiv.to_seconds(days=7)
expires_in = client.arkiv.to_seconds(hours=2, minutes=30)

# Convert time to blocks (assuming 2s block time)
expires_in_blocks = client.arkiv.to_blocks(days=1, block_time=2)

# ❌ WRONG - Don't try to import them
from arkiv import to_seconds, to_blocks  # ImportError!
```

---

## 🎓 Learning Resources

- **README.md**: Comprehensive guide with table of contents
- **SDK Source Code**: Check `.venv/lib/python3.12/site-packages/arkiv/` for authoritative docstrings
  - `module_base.py`: All method signatures with detailed docstrings
  - Use `semantic_search("method_name implementation")` to find SDK code
  - SDK docstrings are the source of truth for parameters, return types, and behavior
- **src/arkiv_starter/**: 8 progressive tutorials (01→08)
- **tests/**: Working test patterns to learn from

---

## 🔍 Troubleshooting

### Import Errors
```bash
uv sync  # Reinstall dependencies
# Then: Ctrl+Shift+P → "Python: Select Interpreter" → choose .venv
```

### Transaction Failures
- Check balance: `client.eth.get_balance(account.address)`
- Check payload size: Must be < ~90KB (transaction limit ~100KB total)
- Verify entity key format in updates/deletes

### Entity Not Found
- Verify entity hasn't expired (`entity.expires_at_block`)
- Check entity key is correct format
- Use `client.arkiv.entity_exists(entity_key)` to check if entity exists (returns bool)
- `client.arkiv.get_entity(entity_key)` raises `ValueError` if entity not found

---

## 📝 Project Structure

```
src/arkiv_starter/     # Examples as runnable modules
tests/                 # Test suite with fixtures
.devcontainer/         # Dev container configuration
pyproject.toml         # Dependencies and tool config
.python-version        # Python 3.12 (supports 3.10-3.14)
```

---

## 🚨 Common Developer Misconceptions (AI: Help Prevent These!)

When developers first encounter Arkiv, they often have incorrect assumptions from traditional databases or Web3 APIs. As an AI assistant, proactively address these misconceptions:

### Misconception 0: "It's Another Dune/The Graph Competitor"
**Reality:** Arkiv is for **your app's live data**, not analyzing existing blockchain data

**What developers think:**
- "I can query all Uniswap trades like Dune Analytics"
- "I can index existing contracts like The Graph"
- "It's a blockchain indexer/analytics tool"

**What Arkiv actually is:**
- **Your app writes data TO Arkiv** (not indexing existing data)
- **Your app-specific entities** (messages, profiles, game state)
- **Ephemeral, queryable storage** that your dApp controls

**Key difference:**
```python
# ❌ NOT what Arkiv does (indexing existing contracts):
# "Index all transfers from USDC contract"
# "Query all NFT sales across OpenSea"
# "Analyze historical DeFi transactions"

# ✅ What Arkiv IS for (your app's live data):
# Store a chat message your app just created
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"from": "alice", "msg": "Hello!"}).encode(),
    content_type="application/json",
    expires_in=to_seconds(days=7),
    attributes={"channel": "general", "type": "message"}
)

# Query YOUR app's messages (not someone else's contract events)
messages = client.arkiv.query_entities('channel = "general"')
```

**When to use what:**

| Tool | Purpose | Use When |
|------|---------|----------|
| **Arkiv** | Store & query YOUR app's data | Building a dApp that needs on-chain state |
| **The Graph** | Index EXISTING smart contracts | Analyzing Uniswap trades, ENS registrations |
| **Dune Analytics** | Analyze blockchain history | Research, dashboards, historical analysis |

**Explain to developers:**
- Dune/Graph: "Read-only view of what's already on-chain"
- Arkiv: "Read-write storage for what YOUR app creates"
- You might use BOTH: Arkiv for your app's data, Dune for analytics about it

**Real-world analogy:**
- The Graph/Dune: Google Analytics (analyzing existing website traffic)
- Arkiv: Your app's database (storing user posts, profiles, game state)

### Misconception 1: "It's Just Another Database"
**Reality:** Blockchain storage with database-like queries

Developers expect:
- Instant writes (no confirmation needed)
- Unlimited storage
- Data persists forever
- Traditional ACID transactions

**What to explain:**
- Writes are blockchain transactions (confirmation required, check receipt.block_number)
- Transaction size limit ~100KB total (payload + attributes + metadata)
- Entities have TTL via `expires_in` parameter (data auto-expires)
- Each write costs gas (batch when possible)
- Reads are free, writes cost gas

**Correct the code:**
```python
# ❌ They write (no awareness of constraints):
client.arkiv.create_entity(payload=huge_file)  # May exceed 100KB limit

# ✅ Guide them to:
# 1. Check payload size before creating
# 2. Set appropriate expires_in
# 3. Consider chunking (or IPFS/Arweave for large files, store hash in Arkiv)
if len(payload) > 90_000:
    print("Payload too large, consider IPFS")
entity_key, receipt = client.arkiv.create_entity(
    payload=payload,
    expires_in=to_seconds(days=7),  # Set expiration!
    content_type="application/json"
)
```

### Misconception 2: "Naming Should Be Consistent"
**Reality:** Three different conventions + entity keys are hex strings (not integers)

**Wrong assumptions:**
- "If Python uses snake_case, everything should"
- "Entity IDs are sequential integers like database IDs"

```python
# ❌ Multiple naming mistakes:
entity_id = 123  # Not an integer!
entities = client.arkiv.query_entities('$contentType = "..."')  # Wrong case!
entity_key = event['args']['entity_key']  # Wrong case!
print(entity.id)  # Wrong attribute!

# ✅ Correct patterns:
entity_key = "0xabc123..."  # Hex string (blockchain address)
entities = client.arkiv.query_entities('$content_type = "..."')  # snake_case
entity_key = hex(event['args']['entityKey'])  # camelCase in events
print(entity.key)  # .key not .id
```

### Misconception 3: "create_entity() Returns Transaction Hash"
**Reality:** Returns tuple (entity_key, receipt) — See "API Return Values" section for details

```python
# ❌ Old web3.py pattern:
tx_hash = client.arkiv.create_entity(...)  # TypeError!

# ✅ Unpack the tuple:
entity_key, receipt = client.arkiv.create_entity(...)
print(f"Created: {entity_key} in block {receipt.block_number}")
```

### Misconception 4: "Storage Is Free/Unlimited"
**Reality:** ~100KB transaction limit, gas costs, and mandatory TTL

**Key constraints:**
- Transaction size: ~100KB total (payload + metadata)
- Each write costs gas (reads are free)
- Must set `expires_in` (auto-expiration prevents bloat)

```python
# ❌ Bad: Large files directly on-chain
with open("photo.jpg", "rb") as f:
    client.arkiv.create_entity(payload=f.read())  # May exceed 100KB!

# ✅ Good: Store hash, files on IPFS/Arweave
ipfs_hash = upload_to_ipfs(photo_bytes)
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ipfs_hash": ipfs_hash}).encode(),
    expires_in=to_seconds(days=30)  # Always set TTL!
)
```

### Misconception 5: "Queries Work Like SQL"
**Reality:** Simple attribute filters only (no JOINs/aggregations/GROUP BY)

```python
# ❌ SQL-style queries don't work:
entities = client.arkiv.query_entities('SELECT * FROM ... GROUP BY owner')

# ✅ Simple filters, client-side for complex logic:
entities = client.arkiv.query_entities(
    f'$owner = "{address}" AND type = "message"'
)
recent = [e for e in entities if e.created_at_block > block - 50400]
```

### Misconception 6: "I Can Update/Delete Any Entity + Deletion Is Permanent"
**Reality:** Only owner can modify; blockchain history is immutable

```python
# ❌ Can't modify entities you don't own:
client.arkiv.update_entity(other_users_entity_key, ...)  # Fails!

# ✅ Check ownership first:
entity = client.arkiv.get_entity(entity_key)
if entity.owner != account.address:
    print("Cannot update - you don't own this entity")

# ⚠️ Deletion removes from queries, but blockchain history is permanent!
client.arkiv.delete_entity(entity_key)  # Gone from queries, not from chain

# For sensitive data, encrypt before storing:
from cryptography.fernet import Fernet
encrypted = Fernet(key).encrypt(sensitive_data)
client.arkiv.create_entity(payload=encrypted, ...)
```

### Misconception 7: "Local Node === Production"
**Reality:** Local node doesn't support all query features yet (e.g., `$content_type`)

```python
# ⚠️ May not work on local node:
entities = client.arkiv.query_entities(
    f'$owner = "{addr}" AND $content_type = "application/json"'
)

# ✅ Workaround: Filter client-side
all_entities = list(client.arkiv.query_entities(f'$owner = "{addr}"'))
filtered = [e for e in all_entities if e.content_type == "application/json"]
```

### Misconception 8: "Account Management Is Like Web Auth"
**Reality:** Private keys, not passwords (no reset, no recovery)

**Critical warnings:**
- ❌ No password reset / "forgot password" flow
- ❌ Lose private key = lose access forever
- ❌ Never commit private keys to git
- ✅ Use `NamedAccount.create()` for local dev
- ✅ Use env vars / key vaults for production

### Misconception 9: "I Should Use Raw Contract Events"
**Reality:** Use `client.arkiv.watch_entity_*()` methods (typed, cleaner) — See "Listening to Events" section

```python
# ❌ Low-level (works but discouraged):
event_filter = client.arkiv.contract.events.ArkivEntityCreated.create_filter(...)
for event in event_filter.get_new_entries():
    entity_key = hex(event['args']['entityKey'])  # Manual parsing

# ✅ High-level convenience methods:
from arkiv.types import CreateEvent, TxHash

def on_entity_created(event: CreateEvent, tx_hash: TxHash) -> None:
    print(f"Created: {event.key} by {event.owner_address}")  # Typed!

client.arkiv.watch_entity_created(on_entity_created)
```

**Only use raw contract events for:**
- Historical queries with complex filters
- Custom indexing logic
- Non-Arkiv contracts

---

## ✨ Pro Tips for AI Assistants

1. **Check SDK source code for method details** - Use `semantic_search()` to find implementation in `.venv/lib/python3.12/site-packages/arkiv/module_base.py`
2. **SDK docstrings are source of truth** - All methods have comprehensive docs with examples
3. **Use the examples as templates** - they demonstrate correct patterns (01→08)
4. **Run tests after changes** - `uv run pytest -n auto`
5. **Check entity.payload is not None** before decoding - it's optional
6. **Use `cast(BaseProvider, provider)` for type checking** if IDE shows errors
7. **Remember: Python 3.12 is recommended** but 3.10-3.14 are supported
8. **Proactively address misconceptions** - Don't wait for the developer to make mistakes
9. **Explain blockchain constraints** - Size limits, gas costs, immutability
10. **Show correct patterns immediately** - Wrong code followed by correct code helps learning
11. **Prefer high-level event watchers** - Use `watch_entity_*()` methods over raw contract filters
12. **Note the watch_entity_deleted type bug** - Always add `# type: ignore[arg-type]` when using it
13. **Use `entity_exists()` to check existence** - Cleaner than try-except with `get_entity()`
14. **Test fixture names matter** - Use `arkiv_client` and `arkiv_node`, not `client` or `account`
15. **Session-scoped fixtures share state** - Use unique identifiers (timestamps, UUIDs) for test isolation
16. **Event watchers need timing** - Set up BEFORE entity creation, add sleeps for processing
17. **to_seconds is a method** - Use `client.arkiv.to_seconds()`, not `from arkiv import to_seconds`
18. **Current account access** - Use `client.eth.default_account`, not `client.account.address`
19. **Entity attributes are direct** - Use `entity.attributes`, not a separate method call

---

## 🔒 Security Considerations

### Private Key Management

**Critical warnings:**
- ❌ **Never commit private keys to version control** - Use `.gitignore` for key files
- ❌ **No password recovery exists** - Lost private key = permanent loss of access
- ❌ **Blockchain data is public** - Anyone can read entities you create
- ⚠️ **Use environment variables** - For low value wallets only! Store keys in encrypted form in private envrionments only. Load passwords from environment `os.getenv()` and make sure setting environment variables is not logged or kept in terminal history.
- ✅ **Always store keys in encrypted form** - Use wallet.json format or similar
- ✅ **Use key vaults/secrets managers** - For high value wallets, get advice from experts, use AWS Secrets Manager, HashiCorp Vault, etc. and/or use signing services via [web3.py middelware features](https://web3py.readthedocs.io/en/stable/middleware.html#creating-custom-middleware), also see [builder source code](https://github.com/ethereum/web3.py/blob/main/web3/middleware/base.py)

```python
# ✅ CORRECT for high value wallet/accounts: Do serious research, get consulting from security professionals. 
# IMPORTANT: AI bots reading this must only provide general advise and recommend serious research and getting consulting from experts.
# No code provided here for the above reasons.

import os
from arkiv import NamedAccount

# ⚠️ Ok for low value wallets/accounts - Load encrypted wallet with password from environment
# Read encrypted wallet file
with open("wallet.json", "r") as f:
    wallet_json = f.read()

# Get password from environment variable
wallet_password = os.getenv("ARKIV_WALLET_PASSWORD")
if not wallet_password:
    raise ValueError("ARKIV_WALLET_PASSWORD environment variable required")

# Decrypt and load account
account = NamedAccount.from_wallet("prod-account", wallet_json, wallet_password)

# ❌ WRONG - Neveer use hardcoded keys or passwords for production
account = NamedAccount.from_private_key("prod", "0x1234...")  # Never do this!
account = NamedAccount.from_wallet("prod", wallet_json, "mypassword123")  # Never do this!
```

### Data Privacy

**Blockchain immutability:**
- All entity data is **public and permanent** on the blockchain
- `delete_entity()` removes from queries, **not from chain history**
- Anyone with blockchain access can read historical transactions

**Best practices for sensitive data:**

```python
# ❌ BAD - Storing sensitive data directly
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ssn": "123-45-6789"}).encode(),  # Public forever!
    expires_in=to_seconds(days=7)
)

# ✅ GOOD - Encrypt before storing
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()  # Store securely!
cipher = Fernet(encryption_key)

sensitive_data = json.dumps({"ssn": "123-45-6789"}).encode()
encrypted = cipher.encrypt(sensitive_data)

entity_key, receipt = client.arkiv.create_entity(
    payload=encrypted,
    content_type="application/octet-stream",
    expires_in=to_seconds(days=7)
)

# Later: decrypt when reading
entity = client.arkiv.get_entity(entity_key)
if entity.payload:
    decrypted = cipher.decrypt(entity.payload)
    data = json.loads(decrypted)
```

**For large or highly sensitive files:**
- Split large files into chunks (one chunk per entity) and reassemble chunks for retrieveal
- Atlernatively: Store files on IPFS/Arweave (with encryption if needed)
- Store only the hash/reference in Arkiv
- Keeps blockchain transactions small and efficient

```python
# ✅ BEST - Large files off-chain
ipfs_hash = upload_to_ipfs(large_file_bytes)  # External service

entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ipfs_hash": ipfs_hash}).encode(),
    content_type="application/json",
    expires_in=to_seconds(days=30)
)
```

### Transaction Security

**Gas and balance checks:**
```python
# Check balance before transactions
balance = client.eth.get_balance(account.address)
if balance == 0:
    print("Account has no funds - transaction will fail")

# Payload size limits
if len(payload) > 90_000:  # ~90KB safe limit
    raise ValueError("Payload too large - use IPFS for large files")
```

---

## 🤖 AI-Generated Project Guidelines

When creating new applications using AI assistants (Copilot, Cursor, etc.), follow these critical patterns:

### Project Structure

**⚠️ IMPORTANT**: User code goes in `src/`, NOT in `src/arkiv_starter/`

```
src/
├── arkiv_starter/          # Template examples (READ-ONLY reference)
│   ├── 01_clients.py
│   ├── 02_entity_crud.py
│   └── ...
│
├── my_app/                 # ✅ Your application code here
│   ├── __init__.py
│   ├── core.py            # Core functionality
│   ├── models.py          # Data models
│   └── utils.py           # Helper functions
│
├── my_app_demo.py         # ✅ Demo script (imports from my_app/)
└── tests/
    └── test_my_app.py     # ✅ Tests for your app
```

❌ **WRONG - Polluting template examples:**
```python
# DON'T add your code to arkiv_starter/
src/arkiv_starter/my_chat_app.py  # Wrong location!
```

✅ **CORRECT - Separate user code:**
```python
# Put your code in its own module
src/chat/
├── __init__.py
├── client.py       # Chat client class
├── messages.py     # Message handling
└── demo.py         # Demo script
```

### Demo vs. Core Code Separation

**Key principle:** Demo code should USE your core functionality, not REPLICATE it.

❌ **WRONG - Code duplication:**
```python
# chat_demo.py - DON'T do this
def send_message(client, text):  # Reimplementing functionality
    # ... duplicate code ...

def watch_messages(client):      # Reimplementing functionality
    # ... duplicate code ...

# Demo uses duplicated code
send_message(client, "Hello")
```

✅ **CORRECT - Demo imports and uses core code:**
```python
# src/chat/client.py - Core functionality
class ChatClient:
    def send_message(self, text: str):
        # Implementation here
        pass
    
    def watch_messages(self):
        # Implementation here
        pass

# src/chat/demo.py - Demo uses core code
from chat.client import ChatClient

def main():
    chat = ChatClient()
    chat.send_message("Hello")
    chat.watch_messages()
```

### Environment Setup

**⚠️ CRITICAL**: This template repository uses a dev container with everything pre-configured.

- ✅ **Dev container is ALREADY CONFIGURED** - no setup needed
- ✅ Python 3.12, uv, all dependencies already installed
- ❌ **DON'T call `configure_python_environment`** - it's automatic
- ❌ **DON'T run `pip install` or `uv sync`** - already done
- ✅ **Just run**: `uv run python -m app.demo` or `uv run pytest`

The environment is ready to use immediately. If you try to set up the Python environment, it's redundant and wastes time.

### Initial Testing

**Always create a basic test** to verify your core functionality works:

```python
# tests/test_app.py
import pytest
from app.client import AppClient

def test_create_entity(arkiv_client):
    """Test that entities can be created successfully."""
    app = AppClient(arkiv_client)
    
    entity_key = app.create_item("Test data")
    
    assert entity_key is not None
    assert arkiv_client.arkiv.entity_exists(entity_key)

def test_retrieve_entities(arkiv_client):
    """Test that entities can be retrieved."""
    app = AppClient(arkiv_client)
    
    # Create an entity
    app.create_item("Test data")
    
    # Retrieve entities
    items = app.get_items()
    
    assert len(items) > 0
```

### 🚨 CRITICAL: Multi-User Interactive Applications (Social, Gaming, etc.)

**⚠️ STOP AND READ `07_agents.py` FIRST** if you're building:
- Any app where multiple independent users interact in real-time
- Social media/messaging apps  
- Multiplayer games

**📁 MANDATORY: Use `src/arkiv_starter/07_agents.py` as your template!**

```bash
# Step 1: Read the reference implementation
cat src/arkiv_starter/07_agents.py

# Step 2: Run it to see how it works
uv run python -m arkiv_starter.07_agents demo

# Step 3: Copy patterns from 07_agents.py into your app
```

**Key classes to copy from `07_agents.py`:**
- `ArkivChain` → Your server (runs ONE shared blockchain node)
- `Client` → Your client (connects to shared node via RPC URL)
- `run_demo()` → Shows complete multi-client interaction

**The Problem (why you MUST use the 07_agents.py pattern):**
When you run a demo script like `python -m app.demo` in multiple terminals, each creates its **own separate blockchain**. Users can't see each other!

❌ **WRONG - Separate Blockchains (Most Common Mistake):**

```python
# src/app/demo.py
def main():
    with Arkiv() as client:  # ← Creates NEW blockchain every time!
        app = AppClient(client, username=username)
        # ... user interacts but is alone in their own universe

if __name__ == "__main__":
    main()
```

**What happens:**
```bash
# Terminal 1
$ uv run python -m app.demo
# Enter username: Alice
# ← Alice creates Blockchain A

# Terminal 2  
$ uv run python -m app.demo
# Enter username: Bob
# ← Bob creates Blockchain B (completely separate!)

# Alice and Bob CANNOT see each other's data!
```

**Why this is tricky:**
- Each `Arkiv()` call starts a new blockchain node
- Different processes = different blockchains
- Tests work fine (shared fixtures), but real demo breaks
- This is THE #1 mistake for multi-user interactive apps

✅ **CORRECT Solution: Server + Client Architecture (See `07_agents.py`)**

**📁 The canonical implementation is in `src/arkiv_starter/07_agents.py`.**

For interactive multi-user apps, you need **TWO types of scripts**:

1. **Server Script** (`ArkivChain` class in `07_agents.py`) - Runs the shared node
2. **Client Script** (`Client` class in `07_agents.py`) - Connects to the shared node

```bash
# Study the reference implementation:
cat src/arkiv_starter/07_agents.py

# Run it to see server + client in action:
uv run python -m arkiv_starter.07_agents demo
```

**Key patterns from `07_agents.py`:**

```python
# SERVER: Create ONE shared blockchain node
class ArkivChain:
    def __init__(self):
        self._client = Arkiv()
        self._node = self._client.node
        # Node exposes: self._node.rpc_url (default: http://127.0.0.1:8545)

# CLIENT: Connect to shared node via RPC URL
class Client:
    def __init__(self, name: str, rpc_url: str = DEFAULT_RPC_URL):
        provider = cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build())
        self._account = NamedAccount.create(name)
        self._client = Arkiv(provider=provider, account=self._account)
        # Client shares blockchain with server!
```

**Copy these patterns from `07_agents.py` into your app!**

#### Usage Instructions (Add to README)

```markdown
## Multi-User Demo

### Step 1: Start the server (ONCE, in one terminal)

```bash
uv run python -m app.server
```

Keep this running! It hosts the shared blockchain.

### Step 2: Connect clients (multiple terminals)

**Terminal 2:**
```bash
uv run python -m app.demo
# Enter username: Alice
```

**Terminal 3:**
```bash
uv run python -m app.demo
# Enter username: Bob
```

**Terminal 4:**
```bash
uv run python -m app.demo
# Enter username: Charlie
```

Now Alice, Bob, and Charlie can all interact together in real-time! 🎉
```

#### Key Implementation Details

**Server Requirements:**
- ✅ Creates and keeps the Arkiv node running
- ✅ Exposes RPC endpoint (default: http://127.0.0.1:8545)
- ✅ Stays alive until Ctrl+C
- ✅ Only ONE instance should run

**Client Requirements:**
- ✅ Connects to existing server via HTTP provider
- ✅ Creates unique account per user
- ✅ Funds account from server (or pre-fund accounts)
- ✅ Multiple instances can run simultaneously
- ✅ Each user has their own client but shares the blockchain

**Account Funding:**
- Server node can fund accounts
- Or pre-create funded accounts in server startup
- Or use a faucet pattern (server endpoint to fund accounts)

### When to Use This Pattern

**Multi-User Interactive Apps (ALWAYS use server + client):**
- ✅ Chat/messaging applications (multiple users communicating)
- ✅ Social media apps (users posting/commenting/liking)
- ✅ Multiplayer games (players interacting in shared world)
- ✅ Collaborative tools (real-time editing/voting/planning)
- ✅ Any app where independent processes need to see each other's data
- ✅ Any CLI demo where you say "open multiple terminals"

**Single-User or Testing (can use simple `with Arkiv()`):**
- ✅ Personal data storage demos
- ✅ Automated scripts (cron jobs, bots)
- ✅ pytest tests (use fixtures)
- ✅ Single-player games
- ✅ Data import/export tools

### Complete AI Prompt Pattern

Use this template when asking AI to create a new application:

```
Create a [application name] using Arkiv SDK with the following:

1. Project Structure:
   - Core code in src/[app_name]/ with __init__.py
   - Main class in src/[app_name]/client.py
   - Tests in tests/test_[app_name].py
   - Demo scripts (see #2 below)

2. Demo Scripts (CRITICAL - Choose based on app type):
   
   **If Multi-User Interactive App (chat, social, multiplayer game):**
   - 📁 FIRST: Read src/arkiv_starter/07_agents.py as your template
   - Copy ArkivChain pattern for server.py
   - Copy Client pattern for demo.py
   - README must explain: "Start server first, then run demo in multiple terminals"
   
   **If Single-User App (personal storage, automation, single-player):**
   - src/[app_name]/demo.py - Simple `with Arkiv() as client` pattern
   - No server needed

3. Implementation Requirements:
   - For multi-user: Copy patterns from 07_agents.py (ArkivChain + Client classes)
   - For single-user: Use context manager pattern: with Arkiv() as client
   - Always call client.node.stop() or use context manager for cleanup
   - Add basic test that verifies core functionality

4. Code Organization:
   - Demo script should NOT duplicate core functionality
   - Demo should import from the main module
   - Include docstrings for all public methods

5. Testing:
   - Create at least 2 tests: one for creation, one for retrieval
   - Use fixtures from conftest.py (tests ALWAYS use shared fixtures)
   - Run with: uv run pytest tests/test_[app_name].py
```

### Example: Good Project Creation

**User prompt:**
```
Create a voting application using Arkiv. Follow the AI-Generated Project Guidelines 
in AGENTS.md. Include core functionality in src/voting/, demo in src/voting/demo.py, 
and tests in tests/test_voting.py.
```

**Expected AI output:**
```
src/voting/
├── __init__.py
├── poll.py          # Poll class with create_poll, vote, get_results
├── demo.py          # Demo that imports Poll and shows usage
tests/
└── test_voting.py   # Tests for Poll functionality
```

**Demo pattern:**
```python
# src/voting/demo.py
from voting.poll import Poll

def main():
    with Arkiv() as client:
        poll = Poll(client)
        
        # Create poll
        poll_id = poll.create("Favorite color?", ["Red", "Blue", "Green"])
        
        # Vote
        poll.vote(poll_id, "Blue")
        
        # Show results
        results = poll.get_results(poll_id)
        print(results)

if __name__ == "__main__":
    main()
```

---

*Last updated: 2025-06-02*
*This file works with all AI coding tools that support the AGENTS.md standard.*
