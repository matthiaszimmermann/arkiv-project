"""
Example 0: Hello World! - Your First Steps with Arkiv SDK for Python

This is the simplest possible Arkiv program.
It stores a message on-chain and reads it back.

Run this example: uv run python -m arkiv_starter.00_hello_world
"""

from arkiv import Arkiv

# Create client (sets up everything automatically!)
client = Arkiv()

print("👋 Hello Arkiv! Storing your first message on-chain...\n")

# Store a message (returns the message's address and receipt)
key, _ = client.arkiv.create_entity(
    payload=b"Hello world!",
    expires_in=3600  # Keep for 1 hour (3600 seconds)
)

print(f"✅ Message stored on-chain!")
print(f"   Message key: {key}")

# Read it back
entity = client.arkiv.get_entity(key)
if entity.payload:
    message = entity.payload.decode('utf-8')
    print(f"📖 Message retrieved: '{message}'")

print("\n🎉 Congratulations! You just used blockchain storage!")
print("   Your message is now permanently recorded on-chain.\n")

# Summary
print("=" * 60)
print("WHAT YOU JUST DID:")
print("=" * 60)
print("1. Created an Arkiv client (one line!)")
print("2. Stored data on the blockchain (secure, queryable)")
print("3. Retrieved the data back (instant read)")
print("\nNext: Try 01_clients.py to learn more patterns!")
print("=" * 60)
