"""
Tic Tac Toe Game Logic

Pure game logic - no Arkiv dependencies here.
"""

from dataclasses import dataclass
from typing import Optional, Literal

Player = Literal["X", "O"]
Cell = Optional[Player]

# Winning combinations (indices into the board)
WINNING_LINES = [
    [0, 1, 2],  # Top row
    [3, 4, 5],  # Middle row
    [6, 7, 8],  # Bottom row
    [0, 3, 6],  # Left column
    [1, 4, 7],  # Middle column
    [2, 5, 8],  # Right column
    [0, 4, 8],  # Diagonal top-left to bottom-right
    [2, 4, 6],  # Diagonal top-right to bottom-left
]


@dataclass
class GameState:
    """Represents the state of a Tic Tac Toe game."""
    
    board: list[Cell]  # 9 cells, indexed 0-8
    current_player: Player
    winner: Optional[Player]
    game_over: bool
    winning_line: Optional[list[int]]  # Indices of winning cells
    
    @classmethod
    def new_game(cls) -> "GameState":
        """Create a new game with empty board, X goes first."""
        return cls(
            board=[None] * 9,
            current_player="X",
            winner=None,
            game_over=False,
            winning_line=None,
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """Create GameState from a dictionary."""
        return cls(
            board=data["board"],
            current_player=data["current_player"],
            winner=data.get("winner"),
            game_over=data.get("game_over", False),
            winning_line=data.get("winning_line"),
        )
    
    def to_dict(self) -> dict:
        """Convert GameState to a dictionary for storage."""
        return {
            "board": self.board,
            "current_player": self.current_player,
            "winner": self.winner,
            "game_over": self.game_over,
            "winning_line": self.winning_line,
        }
    
    def make_move(self, position: int, player: Player) -> tuple[bool, str]:
        """
        Attempt to make a move.
        
        Args:
            position: Board position (0-8)
            player: The player making the move
            
        Returns:
            (success, message) tuple
        """
        # Validate game state
        if self.game_over:
            return False, "Game is already over!"
        
        if player != self.current_player:
            return False, f"It's {self.current_player}'s turn, not {player}'s!"
        
        # Validate position
        if not 0 <= position <= 8:
            return False, f"Invalid position {position}. Use 1-9."
        
        if self.board[position] is not None:
            return False, f"Position {position + 1} is already taken!"
        
        # Make the move
        self.board[position] = player
        
        # Check for winner
        winner, winning_line = self._check_winner()
        if winner:
            self.winner = winner
            self.winning_line = winning_line
            self.game_over = True
            return True, f"🎉 {winner} wins!"
        
        # Check for draw
        if all(cell is not None for cell in self.board):
            self.game_over = True
            return True, "🤝 It's a draw!"
        
        # Switch player
        self.current_player = "O" if player == "X" else "X"
        return True, f"Move accepted. {self.current_player}'s turn."
    
    def _check_winner(self) -> tuple[Optional[Player], Optional[list[int]]]:
        """Check if there's a winner. Returns (winner, winning_line) or (None, None)."""
        for line in WINNING_LINES:
            cells = [self.board[i] for i in line]
            if cells[0] is not None and cells[0] == cells[1] == cells[2]:
                return cells[0], line
        return None, None
    
    def render(self, highlight_last_move: Optional[int] = None) -> str:
        """
        Render the board as a string.
        
        Args:
            highlight_last_move: Position to highlight (optional)
        """
        lines = []
        lines.append("")
        lines.append("     1   2   3")
        lines.append("   ┌───┬───┬───┐")
        
        for row in range(3):
            row_label = ["A", "B", "C"][row]
            cells = []
            for col in range(3):
                idx = row * 3 + col
                cell = self.board[idx]
                
                if cell is None:
                    display = " "
                elif self.winning_line and idx in self.winning_line:
                    # Highlight winning cells
                    display = f"\033[1;32m{cell}\033[0m"  # Green bold
                elif idx == highlight_last_move:
                    # Highlight last move
                    display = f"\033[1;33m{cell}\033[0m"  # Yellow bold
                else:
                    display = cell
                
                cells.append(f" {display} ")
            
            lines.append(f" {row_label} │{'│'.join(cells)}│")
            
            if row < 2:
                lines.append("   ├───┼───┼───┤")
        
        lines.append("   └───┴───┴───┘")
        lines.append("")
        
        return "\n".join(lines)


def parse_position(input_str: str) -> tuple[Optional[int], str]:
    """
    Parse a position input like "A1", "B2", "C3" or "1", "5", "9".
    
    Returns:
        (position, error_message) - position is 0-8 or None if invalid
    """
    input_str = input_str.strip().upper()
    
    if not input_str:
        return None, "Please enter a position."
    
    # Try parsing as letter+number (A1, B2, etc.)
    if len(input_str) == 2 and input_str[0] in "ABC" and input_str[1] in "123":
        row = "ABC".index(input_str[0])
        col = int(input_str[1]) - 1
        return row * 3 + col, ""
    
    # Try parsing as single number (1-9)
    if input_str.isdigit():
        num = int(input_str)
        if 1 <= num <= 9:
            return num - 1, ""
        return None, "Position must be 1-9."
    
    return None, "Invalid format. Use A1-C3 or 1-9."
