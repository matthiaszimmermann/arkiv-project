# Arkiv - The Web3 Database - Python Starter

**Get started with Arkiv in under 5 minutes!** 🚀

This starter template provides everything you need to build applications with the Arkiv SDK for Python. No complex setup required—just clone, open, and run.

## Table of Contents

- [What is Arkiv?](#what-is-arkiv)
- [Quick Start](#quick-start)
- [👶 For Beginners](#-for-beginners)
- [Understanding Entities](#understanding-entities)
- [Examples](#examples)
- [Development Guide](#development-guide)
  - [Project Structure](#project-structure)
  - [Naming Conventions](#naming-conventions)
  - [Common Tasks](#common-tasks)
  - [Troubleshooting](#troubleshooting)
- [Deploying to Production](#deploying-to-production)
- [Resources](#resources)

---

## What is Arkiv?

Arkiv is a Web3 database that solves the Web3 data trilemma.
Store, query, and manage data on-chain with the simplicity of a traditional database, but with blockchain guarantees.

**Key Features:**
- 📦 **On-chain Storage** - Data lives on the blockchain, not centralized servers
- 🔍 **Rich Queries** - Filter, sort, and paginate like a traditional database
- ⚡ **Real-time Events** - Subscribe to data changes as they happen
- 🔗 **Web3 Compatible** - Just a simple extension of the web3.py library

## Quick Start

**Before you begin, make sure you have:**
- Git
- Docker (running)
- VS Code with Dev Containers extension
- GitHub Copilot (optional, but recommended for learning)

### 1. Create Your Project from Template

**Option A: Use GitHub's "Use this template" button**
1. Click the green **"Use this template"** button at the top of this repository
2. Choose "Create a new repository"
3. Give your project a name and click "Create repository"
4. Clone your new repository:
   ```bash
   git clone https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>
   cd <YOUR-REPO-NAME>
   code .
   ```

**Option B: Clone directly (for quick testing)**
```bash
git clone https://github.com/Arkiv-Network/starter-template-python
cd starter-template-python
code .
```

### 2. Reopen in Dev Container

When VS Code prompts you, click **"Reopen in Container"** (or use Command Palette: `Dev Containers: Reopen in Container`)

The dev container will:
- Install Python 3.12 (supports 3.10-3.14, optimized for broad compatibility)
- Set up Docker-in-Docker for local Arkiv nodes
- Install the Arkiv SDK and dependencies
- Configure your Python environment

**This takes 1-2 minutes on first run.**

### 3. Run Your First Example

```bash
uv run python -m arkiv_starter.01_clients
```

You should see output like:
```
🚀 Starting local Arkiv node...
✅ Node running at http://127.0.0.1:...
💰 Created account: 0x...
✅ Account funded with 1000000000000000000 wei
📝 Creating entity...
✅ Entity created! Transaction: 0x...
📦 Entity ID: 1
...
```

**That's it!** You're now running Arkiv locally and performing CRUD operations on-chain.

### Built for AI-Assisted Development

This template includes an [`AGENTS.md`](https://agents.md/) file to work seamlessly with AI coding assistants (GitHub Copilot, Cursor, Aider, Gemini CLI, etc.). The `AGENTS.md` helps AI agents understand Arkiv's conventions, common patterns, and potential pitfalls. 

---

## 👶 For Beginners

**New to blockchain or Arkiv?** We've created special materials just for you!

### Start Here (5 minutes)
👉 **[START_HERE.md](START_HERE.md)** - Your step-by-step first experience

This guide will take you from zero to storing data on blockchain in 5 minutes. No prior experience needed.

### Build with AI (Recommended!)
👉 **[PROMPTS.md](PROMPTS.md)** - Copy-paste project ideas for AI assistants

Don't want to write code? Let GitHub Copilot or Cursor build for you! We've prepared conversation starters for:
- Todo list
- Message board
- Voting system
- Event RSVP
- Leaderboard
- Bookmark manager

### Why Beginners Love This

- ✅ **Zero blockchain setup** - Dev container handles everything
- ✅ **15-line first example** - See results in 30 seconds (`00_hello_arkiv.py`)
- ✅ **Plain English docs** - No jargon (glossary in START_HERE.md)
- ✅ **AI-powered** - Build with Copilot, learn by experimenting
- ✅ **Safe sandbox** - Can't break anything, local blockchain resets

### Quick Answers

**Do I need Python experience?** Basic helps, but AI can write code for you  
**Is this real blockchain?** Locally it's simulated, deploys to real blockchain later  
**Will it cost money?** Not for learning! Local + testnet are free  

**Ready?** Go to **[START_HERE.md](START_HERE.md)** now! 🚀

---

## Understanding Entities

In Arkiv, **entities** are records stored on-chain with queryable attributes.

### Core Components

**1. Payload** - Your actual data (bytes)
```python
payload = b"Hello, Arkiv!"  # Text
payload = json.dumps({"name": "Alice"}).encode()  # JSON
```

**2. Attributes** - Metadata for querying
- **System attributes** (auto-managed, prefixed with `$` in queries): `$key`, `$owner`, `$content_type`, `$created_at`, `$expires_at`
- **Custom attributes** (your metadata, no `$`): `type`, `status`, `userId`, etc.

```python
# Create with custom attributes
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    content_type="application/json",  # Python: snake_case
    expires_in=to_seconds(days=7),
    attributes={"type": "profile", "status": "active"}  # Custom
)

# Query using system attributes (with $)
entities = client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'  # Query: $snake_case
)

# Query using custom attributes (no $)
entities = client.arkiv.query_entities('type = "profile" AND status = "active"')
```

**3. Expires In** - TTL in seconds (required)
```python
expires_in=to_seconds(hours=1)      # Short-lived
expires_in=to_seconds(days=30)      # Longer storage
expires_in=to_seconds(hours=2, minutes=30)  # Combined
```

### Transaction Size Limits

⚠️ **Maximum transaction size: ~100KB** (payload + attributes + metadata)

**Safe limits:**
- Single entity: ~90KB payload
- Multiple entities: Total size must fit in 100KB
- Many attributes reduce available payload space

For larger files, store on IPFS/Arweave and save the hash in Arkiv.

## Examples

The template includes **8 progressive tutorials**, each building on the previous:

Each example:
- Starts a local Arkiv node in Docker (no external dependencies)
- Creates and funds test accounts
- Demonstrates specific features
- Cleans up automatically

### Example 1: Hello World (2 min)
**File:** `src/arkiv_starter/01_hello_world.py`

Your first Arkiv program - store and retrieve data in 15 lines:

```bash
uv run python -m arkiv_starter.01_hello_world
```

### Example 2: Account Management (5 min)
**File:** `src/arkiv_starter/02_accounts.py`

Learn secure account handling:
- Create new accounts (in-memory)
- Load from private keys
- Load from mnemonic phrases
- Save/load encrypted wallet files

```bash
uv run python -m arkiv_starter.02_accounts
```

### Example 3: Client Initialization (5 min)
**File:** `src/arkiv_starter/03_clients.py`

Learn different ways to initialize the Arkiv client:
- Default client (simplest)
- Custom provider (specific RPC endpoints)
- Custom account (specific private keys)
- Multiple accounts with `switch_to()`
- Node reference for utilities

```bash
uv run python -m arkiv_starter.03_clients
```

### Example 4: Entity CRUD Operations (5 min)
**File:** `src/arkiv_starter/04_entity_crud.py`

Master entity lifecycle:
- Create entities (store data on-chain)
- Read entities by key
- Update entities
- Extend entity lifetime
- Change ownership
- Delete entities

```bash
uv run python -m arkiv_starter.04_entity_crud
```

### Example 5: Querying Entities (5 min)
**File:** `src/arkiv_starter/05_queries.py`

Data retrieval and filtering:
- Query by owner
- Filter by content type and custom attributes
- Combine conditions
- Pagination

```bash
uv run python -m arkiv_starter.05_queries
```

### Example 6: Real-Time Events (10 min)
**File:** `src/arkiv_starter/06_events.py`

Monitor blockchain events:
- Watch entity lifecycle events (created, updated, deleted)
- Typed event callbacks
- Account switching for ownership changes

```bash
uv run python -m arkiv_starter.06_events
```

### Example 7: Multi-Client Pattern (15 min)
**File:** `src/arkiv_starter/07_agents.py`

Build multi-user/agent applications:
- **Chain mode**: Run a local blockchain with interactive faucet
- **Client mode**: Connect clients to a shared chain
- **Demo mode**: See multiple clients messaging each other

This is the foundation for chat apps, social media, multiplayer games, etc.

```bash
# Run the demo (all-in-one)
uv run python -m arkiv_starter.07_agents demo

# Or run separately:
# Terminal 1: Start the chain
uv run python -m arkiv_starter.07_agents chain

# Terminal 2: Connect as Alice
uv run python -m arkiv_starter.07_agents client http://127.0.0.1:8545 alice

# Terminal 3: Connect as Bob
uv run python -m arkiv_starter.07_agents client http://127.0.0.1:8545 bob
```

### Example 8: Web3 Integration (5 min)
**File:** `src/arkiv_starter/08_web3_integration.py`

Combine Arkiv with standard Web3 operations:
- Access block data and balances
- Mix Arkiv entity operations with Web3 calls
- Get transaction metadata

```bash
uv run python -m arkiv_starter.08_web3_integration
```

---

## Development Guide

### Project Structure

This template follows the **src-layout** pattern (modern Python standard):

```
arkiv-python-starter/
├── src/
│   └── arkiv_starter/          # Examle code 
│       ├── 01_hello_world.py
│       ├── 02_accounts.py
│       ├── 03_clients.py
│       ├── 04_entity_crud.py
│       ├── 05_queries.py
│       ├── 06_events.py
│       ├── 07_agents.py
│       └── 08_web3_integration.py
├── tests/                      # Test files
│   ├── conftest.py
│   ├── test_03_clients.py
│   ├── test_04_entity_crud.py
│   └── test_05_queries.py
├── .devcontainer/              # Dev container config
├── .vscode/                    # VS Code settings
├── pyproject.toml              # Dependencies & tools
└── .python-version             # Python version (3.12)
```

**Why src-layout?**
- ✅ Prevents accidental imports of uninstalled code
- ✅ Matches published Python package structure
- ✅ Clear separation between source and tooling
- ✅ Industry standard for modern Python projects

**To build your app:** Replace or extend the numbered examples with your own modules.

### Naming Conventions

Arkiv uses **three different naming conventions** depending on context:

#### Python SDK → snake_case
```python
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    content_type="text/plain",
    expires_in=3600,
    attributes={"user_id": "123"}
)
```

#### Query Syntax → snake_case with `$`
```python
# System attributes with $ prefix
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'
))

# User attributes without $ prefix
entities = list(client.arkiv.query_entities(
    'type = "user_profile" AND status = "active"'
))
```

#### Contract Events → camelCase
```python
event_filter = arkiv_contract.events.ArkivEntityCreated.create_filter(from_block="latest")
for event in event_filter.get_all_entries():
    entity_key = hex(event['args']['entityKey'])      # camelCase!
    owner = event['args']['ownerAddress']             # camelCase!
    expiration = event['args']['expirationBlock']     # camelCase!
```

#### Entity Attributes → snake_case
```python
print(entity.key)              # Not entity.id
print(entity.payload)          # Not entity.content
print(entity.owner)
print(entity.content_type)
print(entity.expires_at_block)
print(entity.created_at_block)
```

**Why three conventions?**
- Python SDK follows Python naming standards (PEP 8)
- Query syntax prioritizes readability and SQL-like familiarity
- Contract events follow Solidity conventions (cannot be changed)

See `AGENTS.md` for complete naming convention details and common pitfalls.

### Common Tasks

#### Install Additional Dependencies

```bash
uv add <package-name>
```

#### Run Python REPL with Arkiv

```bash
uv run ipython
```

Then in IPython:
```python
from arkiv import Arkiv
from arkiv.node import ArkivNode
# ... experiment interactively
```

#### Check Arkiv SDK Version

```bash
uv run python -c "import arkiv; print(arkiv.__version__)"
```

#### Run Tests

The starter includes automated tests:

```bash
uv run pytest
```

For faster parallel execution:

```bash
uv run pytest -n auto
```

This verifies:
- ✅ Basic CRUD operations work correctly
- ✅ Query functionality performs as expected
- ✅ Utility functions produce correct results
- ✅ Field masks work for selective retrieval

Tests use a local Arkiv node and run automatically - no configuration needed!

#### Change Python Version

The template uses Python 3.12 by default (recommended for compatibility). To use a different version:

1. Edit `.python-version` (e.g., change to `3.11`, `3.13`, or `3.14`)
2. Rebuild container: Command Palette → `Dev Containers: Rebuild Container`
3. UV will automatically install the specified Python version

**Why Python 3.12?**
- Broad package compatibility (most wheels available)
- Stable and well-tested in production
- Long-term support until October 2028
- Modern features without bleeding-edge risks

### Troubleshooting

#### Dev Container Won't Start

**Problem:** Docker issues or container build failures

**Solution:**
- Ensure Docker is running: `docker ps`
- Try rebuilding: Command Palette → `Dev Containers: Rebuild Container`

#### Import Errors in IDE

**Problem:** Red import lines or `ModuleNotFoundError`

**Solution:**
```bash
uv sync
```

Then: `Ctrl+Shift+P` → `Python: Select Interpreter` → choose `.venv`

#### Node Connection Errors

**Problem:** Can't connect to Arkiv node

**Solution:**
- Check Docker: `docker ps`
- Examples start nodes automatically—wait for "Node running" message
- First run downloads Docker images (one-time delay)

#### Examples Run Slowly

**Problem:** Operations take a long time

**Solution:**
- First run downloads images (one-time)
- Subsequent runs are faster
- Local nodes are slower than production (expected)

---

## Deploying to Production

Once you've mastered local development, connect to the Mendoza testnet:

### Mendoza Testnet Connection

```python
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder

# Configure provider for Mendoza testnet
provider = ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc").build()

# Load your account (create one if you don't have it)
account = NamedAccount.from_private_key("my-account", "0x...")
# Or from wallet file:
# with open('wallet.json') as f:
#     account = NamedAccount.from_wallet("my-account", f.read(), "password")

# Initialize client
client = Arkiv(provider=provider, account=account)

# Now use normally - same API as local development!
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Hello from Mendoza!",
    content_type="text/plain",
    attributes={"env": "testnet"},
    expires_in=client.arkiv.to_seconds(days=7)
)
```

### Key Differences: Local vs. Testnet

| Aspect | Local Development | Mendoza Testnet |
|--------|------------------|-----------------|
| **Provider** | `ProviderBuilder().node()` | `ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc")` |
| **Account Funding** | `node.fund_account()` | Request from faucet (Discord) |
| **Data Persistence** | Lost when node stops | Permanent on testnet |
| **Block Time** | ~1-2 seconds | ~2 seconds |
| **Network Access** | Local only | Public internet |

### Environment Variables Pattern

For production apps, use environment variables:

```python
import os
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder

# Configure from environment
RPC_URL = os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc")
PRIVATE_KEY = os.getenv("ARKIV_PRIVATE_KEY")

provider = ProviderBuilder().custom(RPC_URL).build()
account = NamedAccount.from_private_key("app", PRIVATE_KEY)
client = Arkiv(provider=provider, account=account)
```

### Getting Testnet Funds

To use Mendoza testnet, you need test tokens:

1. **Create an account**:
   ```python
   account = NamedAccount.create("my-testnet-account")
   print(f"Address: {account.address}")
   ```

2. **Request funds**: Join [Discord](https://discord.gg/arkiv) and request testnet tokens for your address

3. **Verify balance**:
   ```python
   balance = client.eth.get_balance(account.address)
   print(f"Balance: {balance / 10**18} ETH")
   ```

---

- 🐍 [Arkiv Getting Started](hhttps://arkiv.network/getting-started/python)
- 🐍 [Arkiv SDK for Python on Github](https://github.com/Arkiv-Network/arkiv-sdk-python)
- 📖 SDK Source Code - Check `.venv/lib/python3.12/site-packages/arkiv/module_base.py` for method documentation
- 💬 [Discord Community](https://discord.gg/arkiv) - Get help and share projects
- 🐦 [Twitter/X](https://twitter.com/ArkivNetwork) - Latest updates and announcements

## Next Steps

Once you've completed the examples:

1. **Experiment** - Modify examples to understand the API
2. **Build** - Create your own application using these patterns
3. **Deploy** - Move to Mendoza testnet when ready
4. **Share** - Join Discord and show the community what you've built

## Contributing

Found a bug or have a suggestion? Please open an issue or submit a PR!

## License

MIT License - See LICENSE file for details

---

**Happy building with Arkiv! 🚀**
