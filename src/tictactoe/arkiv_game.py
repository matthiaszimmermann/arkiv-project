"""
Arkiv-based Tic Tac Toe Server and Client

Architecture:
- Server creates and OWNS the game entity (only owner can update)
- Players create MOVE entities to submit their moves
- Server watches for MOVE entities and updates the game state
- Players watch for game state updates via entity_updated events

This pattern is required because in Arkiv, only the entity owner can update it.
"""

import json
import sys
import time
from typing import Optional, cast

from web3.providers.base import BaseProvider

from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder
from arkiv.types import Attributes, EntityKey, CreateEvent, UpdateEvent, TxHash

from .game import GameState, Player, parse_position


# Entity type constants
GAME_TYPE = "tictactoe_game"
MOVE_TYPE = "tictactoe_move"


class TicTacToeServer(Arkiv):
    """
    Server that hosts a Tic Tac Toe game on Arkiv.
    
    The server:
    1. Creates and owns the game state entity
    2. Watches for move entities from players
    3. Validates and applies moves, updating the game state
    4. Provides a faucet to fund player accounts
    """
    
    def __init__(self):
        print("")
        print("=" * 70)
        print("🎮 TIC TAC TOE SERVER")
        print("=" * 70)
        print("\n🚀 Starting Arkiv node...")
        
        super().__init__()
        
        assert self.node is not None
        self._rpc_url = self.node.http_url
        self._game_key: Optional[EntityKey] = None
        self._game_state: Optional[GameState] = None
        self._move_watcher = None
        self._processed_moves: set[EntityKey] = set()
        
        print(f"✅ Node ready!")
        print(f"\n📡 Connection info for players:")
        print(f"   RPC URL: {self._rpc_url}")
    
    @property
    def rpc_url(self) -> str:
        return cast(str, self._rpc_url)
    
    @property
    def game_key(self) -> Optional[EntityKey]:
        return self._game_key
    
    def create_game(self) -> EntityKey:
        """Create a new game entity owned by the server."""
        self._game_state = GameState.new_game()
        
        entity_key, _ = self.arkiv.create_entity(
            payload=json.dumps(self._game_state.to_dict()).encode("utf-8"),
            content_type="application/json",
            expires_in=self.arkiv.to_seconds(hours=2),
            attributes=cast(Attributes, {
                "type": GAME_TYPE,
                "status": "playing",
            })
        )
        
        self._game_key = entity_key
        print(f"\n🎲 New game created!")
        print(f"   Game ID: {entity_key[:16]}...")
        print(self._game_state.render())
        
        return entity_key
    
    def watch_for_moves(self) -> None:
        """Watch for move entities and process them."""
        
        def on_move_created(event: CreateEvent, tx_hash: TxHash) -> None:
            # Avoid processing the same move twice
            if event.key in self._processed_moves:
                return
            
            try:
                entity = self.arkiv.get_entity(event.key)
                if not entity or not entity.attributes:
                    return
                
                # Check if this is a move for our game
                if entity.attributes.get("type") != MOVE_TYPE:
                    return
                if entity.attributes.get("game_id") != self._game_key:
                    return
                
                # Extract move data
                player = entity.attributes.get("player")
                position = entity.attributes.get("position")
                
                if player not in ("X", "O") or position is None:
                    return
                
                self._processed_moves.add(event.key)
                self._process_move(cast(Player, player), int(position), event.owner_address)
                
            except Exception as e:
                print(f"❌ Error processing move: {e}")
        
        self._move_watcher = self.arkiv.watch_entity_created(on_move_created)
        print("👂 Watching for player moves...")
    
    def _process_move(self, player: Player, position: int, player_address: str) -> None:
        """Process a move from a player."""
        if not self._game_state or not self._game_key:
            return
        
        print(f"\n📥 Move received: {player} -> position {position + 1}")
        
        # Apply the move
        success, message = self._game_state.make_move(position, player)
        
        if success:
            print(f"✅ {message}")
            # Update the game entity
            self.arkiv.update_entity(
                entity_key=self._game_key,
                payload=json.dumps(self._game_state.to_dict()).encode("utf-8"),
                content_type="application/json",
                expires_in=self.arkiv.to_seconds(hours=2),
            )
            print(self._game_state.render())
        else:
            print(f"❌ Invalid move: {message}")
    
    def fund_player(self, address: str, amount: float = 1.0) -> None:
        """Fund a player's account."""
        self.arkiv.transfer_eth(cast(str, address), int(amount * 10**18))
    
    def run_interactive(self) -> None:
        """Run interactive mode with faucet."""
        self.watch_for_moves()
        
        print(f"\n💰 FAUCET - Fund players to let them make moves")
        print(f"   Paste player addresses below\n")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("Enter address to fund (or 'quit'): ").strip()
                
                if user_input.lower() in ['quit', 'q']:
                    print("\n🛑 Server shutting down...")
                    break
                
                if user_input.startswith("0x") and len(user_input) == 42:
                    self.fund_player(user_input)
                    balance = self.eth.get_balance(user_input)
                    print(f"✅ Funded! Balance: {balance / 10**18:.4f} ETH\n")
                else:
                    print("❌ Invalid address format. Expected 0x... (42 chars)\n")
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n")
                break
        
        self.stop()
    
    def stop(self) -> None:
        """Stop the server."""
        print("\n🛑 Stopping server...")
        if self._move_watcher:
            self._move_watcher.uninstall()
        if self.node:
            self.node.stop()
        print("✅ Server stopped")


class TicTacToePlayer(Arkiv):
    """
    Client that plays Tic Tac Toe as X or O.
    
    The player:
    1. Finds the game entity
    2. Creates MOVE entities to submit moves (server processes them)
    3. Watches for game state updates
    """
    
    def __init__(self, rpc_url: str, player: Player):
        self.player = player
        self._game_key: Optional[EntityKey] = None
        self._game_state: Optional[GameState] = None
        self._last_move: Optional[int] = None
        self._watcher = None
        
        print(f"\n🎮 Joining as Player {player}")
        print(f"📡 Connecting to: {rpc_url}")
        
        # Create account for this player
        account = NamedAccount.create(f"player-{player}")
        provider = cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build())
        
        super().__init__(provider=provider, account=account)
        
        print(f"\n🔑 Your address (give to server for funding):")
        print(f"   {self.eth.default_account}\n")
    
    def wait_for_funding(self, min_balance: float = 0.01) -> None:
        """Wait for the account to be funded."""
        print(f"⏳ Waiting for funding (need {min_balance} ETH)...")
        
        while True:
            balance = self.eth.get_balance(self.eth.default_account)
            if balance / 10**18 >= min_balance:
                print(f"✅ Funded! Balance: {balance / 10**18:.4f} ETH\n")
                break
            time.sleep(1)
    
    def find_game(self) -> Optional[EntityKey]:
        """Find an active game on the network."""
        games = list(self.arkiv.query_entities(f'type = "{GAME_TYPE}"'))
        
        if not games:
            print("❌ No active games found. Ask the server to create one.")
            return None
        
        # Use the first active game
        game = games[0]
        self._game_key = game.key
        
        if game.payload:
            self._game_state = GameState.from_dict(json.loads(game.payload.decode("utf-8")))
        
        print(f"✅ Found game: {game.key[:16]}...")
        return game.key
    
    def _reload_game_state(self) -> None:
        """Reload game state from the chain."""
        if not self._game_key:
            return
        
        entity = self.arkiv.get_entity(self._game_key)
        if entity and entity.payload:
            self._game_state = GameState.from_dict(json.loads(entity.payload.decode("utf-8")))
    
    def watch_game(self) -> None:
        """Watch for game updates and display them."""
        
        def on_update(event: UpdateEvent, tx_hash: TxHash) -> None:
            if event.key != self._game_key:
                return
            
            self._reload_game_state()
            self._display_game_update()
        
        self._watcher = self.arkiv.watch_entity_updated(on_update)
    
    def _display_game_update(self) -> None:
        """Display the current game state."""
        if not self._game_state:
            return
        
        # Clear some space
        print("\n" + "=" * 40)
        
        state = self._game_state
        print(state.render(self._last_move))
        
        if state.game_over:
            if state.winner:
                if state.winner == self.player:
                    print("🎉 YOU WIN! 🎉")
                else:
                    print(f"😔 {state.winner} wins. Better luck next time!")
            else:
                print("🤝 It's a draw!")
        else:
            if state.current_player == self.player:
                print(f"👉 YOUR TURN ({self.player})")
            else:
                print(f"⏳ Waiting for {state.current_player}...")
    
    def make_move(self, position: int) -> bool:
        """
        Submit a move by creating a MOVE entity.
        
        Args:
            position: Board position (0-8)
            
        Returns:
            True if move was submitted, False otherwise
        """
        if not self._game_key:
            print("❌ No game loaded!")
            return False
        
        # Reload latest state
        self._reload_game_state()
        
        if not self._game_state:
            print("❌ Could not load game state!")
            return False
        
        # Validate move locally first
        if self._game_state.game_over:
            print("❌ Game is already over!")
            return False
        
        if self._game_state.current_player != self.player:
            print(f"❌ It's {self._game_state.current_player}'s turn, not yours!")
            return False
        
        if not 0 <= position <= 8:
            print(f"❌ Invalid position. Use 1-9.")
            return False
        
        if self._game_state.board[position] is not None:
            print(f"❌ Position {position + 1} is already taken!")
            return False
        
        # Create a MOVE entity (server will process it)
        try:
            move_key, _ = self.arkiv.create_entity(
                payload=b"",  # No payload needed
                content_type="application/json",
                expires_in=self.arkiv.to_seconds(minutes=30),
                attributes=cast(Attributes, {
                    "type": MOVE_TYPE,
                    "game_id": self._game_key,
                    "player": self.player,
                    "position": position,
                })
            )
            
            self._last_move = position
            print(f"✅ Move submitted! Waiting for server to process...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to submit move: {e}")
            return False
    
    def play_interactive(self) -> None:
        """Run interactive game loop."""
        if not self.find_game():
            return
        
        self.watch_game()
        self._display_game_update()
        
        print("\n📝 Enter moves as A1-C3 or 1-9 (or 'quit' to exit)")
        print("   Board positions:")
        print("       1 2 3")
        print("     A . . .")
        print("     B . . .")
        print("     C . . .")
        print("")
        
        while True:
            try:
                if self._game_state and self._game_state.game_over:
                    print("\nGame over! Press Enter to exit...")
                    input()
                    break
                
                user_input = input(f"[{self.player}] Your move: ").strip()
                
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                position, error = parse_position(user_input)
                
                if position is None:
                    print(f"❌ {error}")
                    continue
                
                self.make_move(position)
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
        
        if self._watcher:
            self._watcher.uninstall()


def run_server() -> None:
    """Run the game server."""
    server = TicTacToeServer()
    server.create_game()
    server.run_interactive()


def run_player(rpc_url: str, player: Player) -> None:
    """Run a player client."""
    if player not in ("X", "O"):
        print(f"❌ Invalid player: {player}. Must be X or O.")
        return
    
    client = TicTacToePlayer(rpc_url, player)
    client.wait_for_funding()
    client.play_interactive()


def run_demo() -> None:
    """Run a local demo showing the game mechanics."""
    print("")
    print("=" * 70)
    print("🎮 TIC TAC TOE DEMO")
    print("=" * 70)
    print("\nThis demo shows a quick game between X and O.\n")
    input("Press Enter to start...")
    
    # Start server
    server = TicTacToeServer()
    game_key = server.create_game()
    server.watch_for_moves()
    
    # Create players
    rpc_url = server.rpc_url
    player_x = TicTacToePlayer(rpc_url, "X")
    player_o = TicTacToePlayer(rpc_url, "O")
    
    # Fund players
    server.fund_player(player_x.eth.default_account)
    server.fund_player(player_o.eth.default_account)
    print("✅ Both players funded!\n")
    
    # Players find the game
    player_x.find_game()
    player_o.find_game()
    
    # Play a quick game - X wins with diagonal (top-left to bottom-right: 0, 4, 8)
    # Board positions: 0=A1, 1=A2, 2=A3, 3=B1, 4=B2(center), 5=B3, 6=C1, 7=C2, 8=C3
    moves = [
        (player_x, 0, "X takes top-left (A1)"),
        (player_o, 1, "O takes top-middle (A2)"),
        (player_x, 4, "X takes center (B2)"),
        (player_o, 2, "O takes top-right (A3)"),
        (player_x, 8, "X takes bottom-right (C3) - DIAGONAL WIN!"),
    ]
    
    for player, position, description in moves:
        print(f"\n{'='*50}")
        print(f"📍 {description}")
        
        # Reload state BEFORE making move to get latest
        player._reload_game_state()
        
        success = player.make_move(position)
        
        if success:
            # Wait for server to process
            time.sleep(1.5)
            
            # Reload states for both players
            player_x._reload_game_state()
            player_o._reload_game_state()
        
        if player_x._game_state and player_x._game_state.game_over:
            print(player_x._game_state.render())
            if player_x._game_state.winner:
                print(f"🎉 {player_x._game_state.winner} WINS! 🎉")
            break
            break
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
    
    # Cleanup
    server.stop()


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("🎮 Arkiv Tic Tac Toe")
        print("")
        print("Usage:")
        print("  Demo:   uv run python -m tictactoe demo")
        print("  Server: uv run python -m tictactoe server")
        print("  Player: uv run python -m tictactoe join <rpc_url> <X|O>")
        print("")
        print("Example (3 terminals):")
        print("  Terminal 1: uv run python -m tictactoe server")
        print("  Terminal 2: uv run python -m tictactoe join http://127.0.0.1:8545 X")
        print("  Terminal 3: uv run python -m tictactoe join http://127.0.0.1:8545 O")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "demo":
        run_demo()
    
    elif command == "server":
        run_server()
    
    elif command == "join":
        if len(sys.argv) < 4:
            print("Usage: uv run python -m tictactoe join <rpc_url> <X|O>")
            sys.exit(1)
        
        rpc_url = sys.argv[2]
        player = sys.argv[3].upper()
        
        if player not in ("X", "O"):
            print(f"❌ Player must be X or O, got: {player}")
            sys.exit(1)
        
        run_player(rpc_url, cast(Player, player))
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use: demo, server, or join")
        sys.exit(1)


if __name__ == "__main__":
    main()
