"""
Arkiv Tic Tac Toe - Two-Player Game

A blockchain-based Tic Tac Toe game where game state is stored on Arkiv.
Players connect to a shared node and take turns making moves.

Architecture:
- Game state stored as an Arkiv entity (board, current player, winner)
- Server runs the shared Arkiv node
- Clients connect to make moves (each player in their own terminal)
- Real-time updates via event watchers

Usage:
    # Start the game server (Terminal 1)
    uv run python -m tictactoe server
    
    # Player X joins (Terminal 2)
    uv run python -m tictactoe join <rpc_url> X
    
    # Player O joins (Terminal 3)
    uv run python -m tictactoe join <rpc_url> O
    
    # Or run a local demo
    uv run python -m tictactoe demo
"""

__version__ = "0.1.0"
