"""
Example 7: Multi-Client Pattern (Clients connected to shared Chain/Node)

Demonstrates the foundational pattern for multi-user/agent applications:
- This is the basis for chat apps, social media, multiplayer games, etc.
- Run: uv run python -m arkiv_starter.07_agents (demo|chain|client <rpc_url> <name>)
"""

import sys
from typing import cast
from web3.providers.base import BaseProvider
from arkiv import Arkiv, NamedAccount
from arkiv.types import Attributes, EntityKey
from arkiv.provider import ProviderBuilder
from eth_typing import ChecksumAddress


class ArkivChain(Arkiv):
    """Server that runs a shared Arkiv node with interactive faucet."""
    
    def __init__(self):
        """Start the node and run interactive faucet."""
        print("")
        print("=" * 70)
        print("Agent Chain: Shared Blockchain Node")
        print("=" * 70)
        print("\n🚀 Starting Node...")

        super().__init__()
        self._faucet_thread = None
            
        print(f"✅ Node ready!")
        print(f"\n📡 Connection info:")
        assert self.node is not None
        print(f"   RPC URL: {self.node.http_url}")
        print(f"   Network ID: {self.eth.chain_id}")
    
    @property
    def http_url(self) -> str:
        """Get the HTTP URL of the node."""
        assert self.node is not None
        return cast(str, self.node.http_url)

    def fund(self, address: ChecksumAddress, amount: int = 10**18):
        """Fund an address using the server's faucet."""
        
        self.arkiv.transfer_eth(address, amount)

    
    def start_faucet_thread(self):
        """Run interactive faucet in a separate thread."""
        import threading
        
        def faucet_loop():
            print(f"\n💰 Interactive FAUCET running")
            print(f"   Clients need funding to send transactions")
            print(f"   Paste client addresses below to fund them\n")
            print("=" * 70)
            
            while True:
                user_input = input("Enter address to fund (or 'quit'): ").strip()
                if user_input.lower() in ['quit', 'q']:
                    print("\n🛑 Faucet stopped")
                    self.stop()
                    break
                
                try:
                    address = cast(ChecksumAddress, user_input.strip())
                    self.fund(address)                    
                    print(f"✅ Funded {address}")
                    print(f"   Balance: {self.eth.get_balance(address) / 10**18} ETH\n")
                except Exception as e:
                    print(f"❌ Error: {e}\n")
        
        faucet_thread = threading.Thread(target=faucet_loop, daemon=True)
        faucet_thread.start()
        return faucet_thread
    
    def stop(self):
        print("\n🛑 Stopping Chain...")
        if self.node:
            self.node.stop()
        print("✅ Server stopped\n")


class Client(Arkiv):
    """Client/agent that connects to an Arkiv chain."""
    
    def __init__(self, rpc_url: str, username: str):
        """Initialize client and connect to chain.
        
        Args:
            rpc_url: A RPC endpoint of an Arkiv chain (e.g., http://127.0.0.1:8545)
            username: Name for this client (creates account)
        """
        
        print(f"\n🤖 Initializing client: {username}")
        print(f"📡 Connecting to: {rpc_url}")
        self.username = username.strip()

        super().__init__(
            provider=cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build()), 
            account=NamedAccount.create(self.username))
        
        print(f"🔑 Fund the account linked to '{self.username}' before executing transactions:")
        print(f"   {self.eth.default_account}\n")
    
    def wait_for_funding(self, min_balance: float = 0.001):
        """Wait for account to be funded by server."""
        import time
        
        print(f"⏳ Waiting for funding (need {min_balance} ETH)...")
        while True:
            balance = self.eth.get_balance(self.eth.default_account)
            balance_eth = balance / 10**18
            
            if balance_eth >= min_balance:
                print(f"\n✅ Funded! Client for '{self.username}' ready to interact with the chain!\n")
                break
            
            time.sleep(1)
    
    def send_message(self, message: str, recipient: str, print_message: bool = True) -> EntityKey:
        """Create a message entity."""

        entity_key, _ = self.arkiv.create_entity(
            payload=message.encode('utf-8'),
            content_type="text/plain",
            expires_in=self.arkiv.to_seconds(hours=1),
            attributes=cast(Attributes, {"type": "message", "user": self.username, "recipient": recipient})
        )
        if print_message:
            print(f"[{self.username} -> {recipient}] {message}")

        return entity_key
    
    def watch_messages(self):
        """Watch for messages addressed to this client and print them in real-time."""
        from arkiv.types import CreateEvent, TxHash
        
        def on_message_created(event: CreateEvent, tx_hash: TxHash) -> None:
            """Callback for when a message entity is created."""

            entity = self.arkiv.get_entity(event.key)            
            if entity.attributes:
                recipient = entity.attributes.get("recipient", "")
                sender = entity.attributes.get("user", "unknown")
                
                # Only print if message is for us
                if recipient == self.username:
                    if entity.payload:
                        message_text = entity.payload.decode('utf-8')
                        print(f"\n📨 New message from {sender}: {message_text}")
        
        # Set up the watcher
        watcher = self.arkiv.watch_entity_created(on_message_created)
        print(f"👂 Watching for incoming messages...\n")
        return watcher

def run_chain():
    """Run an AgentChain node with interactive faucet."""

    print("=" * 70)
    print("Chain Server")
    print("  - Starts Local Blockchain Node with Interactive Faucet")

    arkiv_db_chain = ArkivChain()
    thread = arkiv_db_chain.start_faucet_thread()

    try:
        thread.join()
    except KeyboardInterrupt:
        print("\n\n⚠️  Keyboard interrupt received. Shutting down server...")
    finally:
        arkiv_db_chain.stop()

def run_client(rpc_url: str, username: str):
    """Run a Client/agent that connects to the specified RPC URL."""
    
    client = Client(rpc_url=rpc_url, username=username)
    client.wait_for_funding()
    client.watch_messages()

    print("💬 You can now send messages: <recipient>:<message> like bob:hi bob (or 'quit')")
    try:
        while True:
            user_input = input("")
            if user_input.lower() in ['quit', 'q']:
                print("\n🛑 Client stopped")
                break

            parts = user_input.split(":", maxsplit=1)
            if len(parts) < 2:
                print("❌ Invalid input. Please enter <recipient>:<message>.")
                continue

            recipient, message = parts
            client.send_message(message.strip(), recipient.strip(), print_message=False)

    except KeyboardInterrupt:
        print("\n\n⚠️  Keyboard interrupt received. Shutting down client...")
               
def run_demo():
    """Run a demo showing server + multiple clients/agents."""

    print("=" * 70)
    print("Multi-Agent Demo")
    print("  1. ONE server (shared blockchain)")
    print("  2. Multiple clients/agents (Alice, Bob)")
    print("  3. Clients/agents creating and reading each other's messages\n")
    input("Press Enter to start...")
    
    # Start server in main thread
    arkiv_db_chain = ArkivChain()

    # Start and fund clients
    rpc_url = arkiv_db_chain.http_url
    alice = Client(rpc_url=rpc_url, username="Alice")
    bob = Client(rpc_url=rpc_url, username="Bob")
    _fund_clients(arkiv_db_chain, [alice, bob])

    # Send messages between agents
    print("")
    alice.send_message("Hello Bob!", recipient="Bob")
    bob.send_message("Hi Alice!", recipient="Alice")

    # Print all message entities
    messages = list(arkiv_db_chain.arkiv.query_entities('type = "message"'))
    print(f"\n📨 All Messages on Chain:")
    print(*messages, sep="\n")

    # Cleanup
    arkiv_db_chain.stop()

def _fund_clients(chain: ArkivChain, clients: list[Client], min_balance: float = 1.0) -> None: # pyright: ignore[reportArgumentType]
    """Fund the client's account using the chain's faucet."""
    for client in clients:
        chain.fund(client.eth.default_account, amount=int(min_balance * 10**18))
        print(f"✅  Agent '{client.username}' is funded with: {client.eth.get_balance(client.eth.default_account) / 10**18} ETH")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Demo mode:   uv run python -m arkiv_starter.07_agents demo")
        print("  Chain mode:  uv run python -m arkiv_starter.07_agents chain")
        print("  Client mode: uv run python -m arkiv_starter.07_agents client <rpc_url> <name>")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "demo":
        run_demo()
    
    elif mode == "chain":
        run_chain()

    elif mode == "client":
        if len(sys.argv) < 4:
            print("Usage: uv run python -m arkiv_starter.07_agents client <rpc_url> <username>")
            sys.exit(1)
        
        rpc_url = sys.argv[2]
        username = sys.argv[3]
        run_client(rpc_url, username)

    else:
        print(f"❌ Unknown mode: {mode}")
        print("   Use: demo, chain, or client")
        sys.exit(1)
