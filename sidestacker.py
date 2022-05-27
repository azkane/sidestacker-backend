import random
import uuid
from typing import Optional, Tuple, Callable

from app.events import *


class SideStacker:
    """
    This class maintains an instance of the game known as Sidestacker.
    Sidestacker is game like connect-four with the following rules:
        - Is played with 2 players
        - Is played in a 7x7 board/grid
        - Players are allowed to add pieces to each side on their turn
        - The game ends when theres no more spaces left or player has
          four consecutive pieces on a diagonal, column or row.

    There are four main responsibilities for this class:
        - Maintaining the current state of the game
        - Handling player actions
        - Evaluating the current game state to determine if a player
         has won or reached a stalemate
        - Notifying other components of the current game state

    This class maintains the state of the game at any given time which is:
        - Game id
        - Players
        - Current turn
        - Player turn
        - Board state
    The game id is an unique identifier for this game.
    The players dict stores the currently connected players their id and turn as a tuple.
    The current turn is an integer counter of the current turn.
    The player turn states which player has the right to execute actions on the board, this can be 'None', 'C' or 'X'
    The board is represented as a 7x7 2d-array initialized with None.
    Each position in the array can be:
         - 'C' for circle tokens
         - 'X' for cross tokens
         - None for empty positions

    Each player can take actions, these can be:
        - Connect: Adds a player to the game and assigns them the circle or cross pieces.
        - Disconnect: Removes a player from the game
        - PlacePiece: Can only be executed on a player's turn, requires the row and
         the side the token is added. (eg: 0,R for row 0, right side. 4,L for row 4, left side.)

    The evaluation tries to find four consecutive pieces on a diagonal, column or row. This after
    every player's turn. If it founds it, the last player to have placed a piece wins the game.

    If a player disconnects while playing the game, the other player automatically wins.

    The game can start when theres two connected players.

    Each player has an id associated to their state, this is used to naively verify their plays.

    This class also implements the observer pattern to notify other subsystems of
    actions in the game. Each turn the observers are notified of state changes in
    the board.

    Each event is an instance of the `SideStackerEvent' class or subclasses.
    """

    def __init__(self, game_id=str(uuid.uuid4())):
        self.id = game_id
        self.board = [[None] * 7 for _ in range(7)]
        self.players = {}
        self.dependants = []
        self.turn = 0
        self.player_turn = None

    def connect(self, player_id: str) -> Optional[Tuple[str, int]]:
        """
        Adds a player to the game with the given token.
        Assigns them a token C, X and a turn (0 or 1).
        If there are more than two players or the id already exists, do nothing.
        """
        if len(self.players) >= 2: return None
        if player_id in self.players: return None
        if len(self.players) == 0:
            self.players[player_id] = ('X' if random.randint(0, 1) == 0 else 'C',
                                       random.randint(0, 1))
        else:
            p1 = next(iter(self.players.values()))
            p2_pieces = 'C' if p1[0] == 'X' else 'X'
            p2_turn = 0 if p1[1] == 1 else 1
            self.players[player_id] = (p2_pieces, p2_turn)
            self.turn = 0
            self.player_turn = p1[0] if p1[1] < p2_turn else p2_pieces

        self.notify(PlayerConnected(*self.players[player_id]))

        return self.players[player_id]

    def disconnect(self, player_id: str) -> None:
        """
        Disconnects a player.
        Removes player from the players dict and the other player automatically wins the game.
        """
        pieces = self.players[player_id]
        del self.players[player_id]
        self.notify(PlayerDisconnected(self.id, pieces))
        self.notify(PlayerWon(self.id, 'X' if pieces == 'C' else 'C'))

    def place_piece(self, player_id: str, row: int, side: Literal['L', 'R']) -> None:
        if len(self.players) < 2:
            raise ValueError('There should be two players to start the game')

        if self.players[player_id][0] != self.player_turn:
            raise ValueError('Players should place pieces on their own turn')

        # Create a range object iterating from 0 to 6 or 6 to 0 depending on the chosen side
        search_iter = range(0, 7) if side == 'L' else range(6, -1, -1)
        found = False
        for i in search_iter:
            if self.board[row][i] is None:
                self.board[row][i] = self.players[player_id][0]
                found = True
                break

        if not found: raise ValueError('Theres no available space in the selected row')

        winner = self.evaluate_game()
        if winner is not None:
            self.notify(PlayerWon(self.id, winner))
            return
        else:
            self.notify(PiecePlaced(self.id, self.player_turn, row, side, self.turn))
            self.turn += 1
            self.player_turn = 'X' if self.player_turn == 'C' else 'C'

    def evaluate_game(self, _board=None) -> Optional[Literal['X', 'C']]:
        """
        Evaluates a sidestacker board game.
        A sidestacker game is won when a player has four consecutive pieces in a row, column or diagonal.
        If such combination is found returns the piece which has won
        else return None if there aren't any winning combinations

        This method takes an optional board to evaluate for easier testing. If no such
        board is passed, the instance board is used.
        """
        board = _board or self.board

        # Starting from the top left of the array, try to find consecutive pieces
        for i in range(7):
            for j in range(7):
                if board[i][j] is None:
                    continue

                piece = board[i][j]
                # Try to find the same piece, horizontally:
                if j + 4 <= 7:
                    for x in range(j, j + 4):
                        if piece == board[i][x] and x == j + 3:
                            return piece
                        elif piece != board[i][x]:
                            break

                # Try to find the same piece, vertically:
                if i + 4 <= 7:
                    for x in range(i, i + 4):
                        if piece == board[x][j] and x == i + 3:
                            return piece
                        elif piece != board[x][j]:
                            break
                # Try to find the same piece, bottom-right direction:
                if i + 4 <= 7 and j + 4 <= 7:
                    for (x, y) in zip(range(i, i + 4), range(j, j + 4)):
                        if piece == board[x][y] and x == i + 3 and y == j + 3:
                            return piece
                        elif piece != board[x][y]:
                            break
                # Try to find the same piece, bottom-left direction:
                if i + 4 <= 7 and j - 3 >= 0:
                    for (x, y) in zip(range(i, i + 4), range(j, j - 4, -1)):
                        if piece == board[x][y] and x == i + 3 and y == j - 3:
                            return piece
                        elif piece != board[x][y]:
                            break

    def add_observer(self, cb: Callable[[SideStackerEvent], None]):
        self.dependants.append(cb)

    def notify(self, ev: SideStackerEvent):
        for cb in self.dependants:
            cb(ev)
