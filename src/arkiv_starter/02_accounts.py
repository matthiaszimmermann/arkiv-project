"""
Example 1: Named Account Management

This example demonstrates:
- Creating new accounts (in-memory)
- Loading accounts from private keys
- Loading accounts from mnemonic phrases
- Saving accounts as encrypted wallet files
- Loading accounts from encrypted wallet files

SECURITY PRINCIPLES:
- ❌ NEVER store private keys or mnemonics in plain text at rest
- ❌ NEVER commit wallet files or passwords to git
- ✅ ALWAYS use encrypted wallet format (keystore JSON)
- ✅ ALWAYS load passwords from environment variables
- ⚠️  Wallet files are encrypted but still sensitive!

Run this example: uv run python -m arkiv_starter.01_accounts
"""

import os
import shutil
from pathlib import Path
from arkiv import NamedAccount

WALLETS_DIR = Path("wallets")  # Should be in .gitignore!


print("=" * 70)
print("PATTERN 1: Creating a New Account (In-Memory)")
print("=" * 70)
print("\n🚀 Creating a fresh account...")
print("   - Generates new private key")
print("   - Perfect for local dev and testing\n")

account = NamedAccount.create("alice")

print(f"✅ Account created!")
print(f"   Name:    {account.name}")
print(f"   Address: {account.address}")
print(f"   Key:     {'*' * 20} (never display in real code!)\n")


print("=" * 70)
print("PATTERN 2: Loading from Existing Private Key")
print("=" * 70)
print("\n🚀 Loading account from private key...")
print("   - Import existing account from another wallet")
print("   - ⚠️  Never hardcode keys in source code!\n")

# For demo only - in production, load from environment or secure storage
demo_private_key = account.key  # .key returns private key as bytes

imported_account = NamedAccount.from_private_key("alice-imported", demo_private_key)

print(f"✅ Account imported!")
print(f"   Name:    {imported_account.name}")
print(f"   Address: {imported_account.address}")
print(f"   Matches original: {imported_account.address == account.address}\n")

print("   ⚠️  In production, load private key from environment:")
print('      private_key = os.getenv("PRIVATE_KEY")')
print('      account = NamedAccount.from_private_key("name", private_key)\n')


print("=" * 70)
print("PATTERN 3: Loading from Mnemonic Phrase")
print("=" * 70)
print("\n🚀 Loading account from mnemonic (seed phrase)...")
print("   - HD wallet derivation (BIP-44)")
print("   - Use account_path to derive different accounts from same mnemonic")
print("   - ⚠️  Never hardcode mnemonics in source code!\n")

# Standard 12-word test mnemonic (DO NOT use in production!)
demo_mnemonic = "test test test test test test test test test test test junk"

# Default path: m/44'/60'/0'/0/0
mnemonic_account_0 = NamedAccount.from_mnemonic("hd-wallet-0", demo_mnemonic)

# Different account path: m/44'/60'/0'/0/1
mnemonic_account_1 = NamedAccount.from_mnemonic(
    "hd-wallet-1", 
    demo_mnemonic, 
    account_path="m/44'/60'/0'/0/1"
)

print(f"✅ Accounts derived from mnemonic!")
print(f"   Index 0: {mnemonic_account_0.address}")
print(f"   Index 1: {mnemonic_account_1.address}")
print(f"   Different addresses: {mnemonic_account_0.address != mnemonic_account_1.address}\n")

print("   ⚠️  In production, load mnemonic from secure storage:")
print('      mnemonic = os.getenv("MNEMONIC")')
print('      account = NamedAccount.from_mnemonic("name", mnemonic)\n')


print("=" * 70)
print("PATTERN 4: Saving Account as Encrypted Wallet")
print("=" * 70)
print("\n🚀 Saving account to encrypted wallet file...")
print("   - Uses Ethereum keystore v3 format")
print("   - AES-128-CTR encryption with scrypt KDF")
print("   - Standard format compatible with other wallets\n")

# Create wallets directory
WALLETS_DIR.mkdir(exist_ok=True)

# Encrypt and save
password = "DemoPassword123!"  # In production: os.getenv("WALLET_PASSWORD")!
wallet_json = account.export_wallet(password)
wallet_path = WALLETS_DIR / f"{account.name}.json"
wallet_path.write_text(wallet_json)

print(f"✅ Wallet saved!")
print(f"   Path: {wallet_path}")
print(f"   Encrypted: Yes (AES-128-CTR)")
print(f"   Password protected: Yes\n")

print("   ⚠️  In production:")
print('      password = os.getenv("WALLET_PASSWORD")')
print("      wallet_json = account.export_wallet(password)\n")


print("=" * 70)
print("PATTERN 5: Loading Account from Encrypted Wallet")
print("=" * 70)
print("\n🚀 Loading account from encrypted wallet file...")
print("   - Decrypts keystore with password")
print("   - Restores full account with private key\n")

# Load wallet file
loaded_wallet_json = wallet_path.read_text()

# In production, get password from environment
password_from_env = os.getenv("WALLET_PASSWORD")
if password_from_env:
    print("✅ Using password from WALLET_PASSWORD environment variable")
    decrypt_password = password_from_env
else:
    print("ℹ️  WALLET_PASSWORD not set, using demo password")
    decrypt_password = password

# Decrypt and load
loaded_account = NamedAccount.from_wallet(
    "alice-loaded",
    loaded_wallet_json,
    decrypt_password
)

print(f"\n✅ Account loaded from wallet!")
print(f"   Name:    {loaded_account.name}")
print(f"   Address: {loaded_account.address}")
print(f"   Matches original: {loaded_account.address == account.address}\n")

print("   Production pattern:")
print('      password = os.getenv("WALLET_PASSWORD")')
print("      if not password:")
print('          raise ValueError("WALLET_PASSWORD required")')
print('      account = NamedAccount.from_wallet("name", wallet_json, password)\n')


print("=" * 70)
print("SUMMARY: Account Creation Methods")
print("=" * 70)
print("""
┌─────────────────────────────────────────────────────────────────────┐
│ Method                          │ Use Case                          │
├─────────────────────────────────┼───────────────────────────────────┤
│ NamedAccount.create()           │ New account for dev/testing       │
│ NamedAccount.from_private_key() │ Import existing account           │
│ NamedAccount.from_mnemonic()    │ HD wallet / seed phrase recovery  │
│ NamedAccount.from_wallet()      │ Load encrypted keystore           │
│ account.export_wallet()         │ Save encrypted keystore           │
└─────────────────────────────────┴───────────────────────────────────┘

🔒 SECURITY CHECKLIST:
   ✅ Add wallets/ to .gitignore
   ✅ Load passwords from environment variables
   ✅ Never hardcode private keys or mnemonics
   ✅ Use encrypted wallet format for persistence
   ✅ Backup wallet files to secure storage
""")


print("=" * 70)
print("CLEANUP")
print("=" * 70)

if WALLETS_DIR.exists():
    shutil.rmtree(WALLETS_DIR)
    print(f"\n🗑️  Removed demo wallets directory: {WALLETS_DIR}")

print("\n✅ Example complete!\n")
