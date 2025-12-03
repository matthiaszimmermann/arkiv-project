# Arkiv Tic Tac Toe 🎮

A blockchain-based two-player Tic Tac Toe game using the Arkiv SDK.

## Overview

This game demonstrates multi-user interaction on Arkiv:
- **Server** creates and owns the game state entity
- **Players** submit moves by creating MOVE entities
- **Server** watches for moves and updates the game state
- **Players** watch for game updates in real-time

This architecture is required because in Arkiv, only the entity owner can update it.

## Quick Start

### Run the Demo

```bash
uv run python -m tictactoe demo
```

This runs a quick automated game showing X winning with a diagonal.

### Play a Real Game (3 Terminals)

**Terminal 1 - Start the server:**
```bash
uv run python -m tictactoe server
```

The server will display an RPC URL (e.g., `http://127.0.0.1:8545`).

**Terminal 2 - Player X joins:**
```bash
uv run python -m tictactoe join http://127.0.0.1:8545 X
```

Copy the displayed address and paste it into the server terminal to fund the player.

**Terminal 3 - Player O joins:**
```bash
uv run python -m tictactoe join http://127.0.0.1:8545 O
```

Fund this player too, then start playing!

## How to Play

Enter moves using either format:
- **Grid notation**: `A1`, `B2`, `C3`, etc.
- **Number notation**: `1`-`9`

```
Board positions:

    1   2   3
  ┌───┬───┬───┐
A │ 1 │ 2 │ 3 │
  ├───┼───┼───┤
B │ 4 │ 5 │ 6 │
  ├───┼───┼───┤
C │ 7 │ 8 │ 9 │
  └───┴───┴───┘
```

- X always goes first
- Players take turns
- First to get 3 in a row (horizontal, vertical, or diagonal) wins!

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ARKIV BLOCKCHAIN                          │
│                                                              │
│  ┌──────────────────┐     ┌──────────────────┐              │
│  │   GAME ENTITY    │     │   MOVE ENTITIES   │             │
│  │  (owned by       │     │  (created by      │             │
│  │   server)        │     │   players)        │             │
│  │                  │     │                   │             │
│  │  - board state   │ ←── │  - player: X/O    │             │
│  │  - current turn  │     │  - position: 0-8  │             │
│  │  - winner        │     │  - game_id        │             │
│  └──────────────────┘     └──────────────────┘             │
│           ↑                        ↑                        │
│           │                        │                        │
│     watches for            creates moves                    │
│     updates                                                 │
│           │                        │                        │
└───────────┼────────────────────────┼────────────────────────┘
            │                        │
    ┌───────┴───────┐        ┌───────┴───────┐
    │    SERVER     │        │    PLAYERS    │
    │               │        │               │
    │ - Creates     │        │ - Find game   │
    │   game entity │        │ - Submit      │
    │ - Watches     │        │   moves       │
    │   for moves   │        │ - Watch for   │
    │ - Updates     │        │   updates     │
    │   game state  │        │               │
    │ - Faucet      │        │               │
    └───────────────┘        └───────────────┘
```

## Why This Pattern?

In Arkiv, only the **owner** of an entity can update or delete it. Since we want both players to affect the game state, we use this pattern:

1. **Server owns the game state** - Only server can update it
2. **Players create move entities** - Anyone can create new entities
3. **Server watches for moves** - Processes valid moves and updates game
4. **Players watch for game updates** - See the result of their moves

This is a common pattern for multi-user applications on Arkiv (chat apps, games, etc.).

## Files

- `__init__.py` - Module metadata
- `__main__.py` - Entry point for `python -m tictactoe`
- `game.py` - Pure game logic (no Arkiv dependencies)
- `arkiv_game.py` - Server and player classes using Arkiv
