import random
import uuid

from itertools import repeat
from typing import Tuple, Callable

from events import *


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
        Adds a player to the game with the given id.
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

        self.notify(PlayerConnected(self.id, player_id, *self.players[player_id]))
        self.notify(PlayerInfo(self.id, [{'piece': p, 'turn': t} for (p, t) in self.players.values()]))

        return self.players[player_id]

    def disconnect(self, player_id: str) -> None:
        """
        Disconnects a player.
        Removes player from the players dict and the other player automatically wins the game.
        """
        pieces = self.players[player_id]
        del self.players[player_id]
        self.notify(PlayerDisconnected(self.id, pieces))
        self.notify(GameOver(self.id, 'X' if pieces == 'C' else 'C'))

    def place_piece(self, player_id: str, row: int, side: Literal['L', 'R']) -> None:
        if len(self.players) < 2:
            self.notify(PiecePlacedError(self.id,
                                         player_id,
                                         self.turn,
                                         'There should be two players to start the game'))
            return

        if self.players[player_id][0] != self.player_turn:
            self.notify(PiecePlacedError(self.id,
                                         player_id,
                                         self.turn,
                                         'Players should place pieces on their own turn'))
            return

        if not is_move_legal(self.board, row, side):
            self.notify(PiecePlacedError(self.id,
                                         player_id,
                                         self.turn,
                                         'Theres no available space in the selected row'))
            return

        col = get_next_free_position(self.board, row, side)
        self.board[row][col] = self.players[player_id][0]
        winner = evaluate_move(self.board, row, col, self.player_turn)

        if winner:
            self.notify(GameOver(self.id, self.player_turn))
            return
        elif self.turn == 7 * 7:
            self.notify(GameOver(self.id, None))
            return
        else:
            current_turn = self.turn
            current_player = self.player_turn
            self.turn += 1
            self.player_turn = 'X' if self.player_turn == 'C' else 'C'
            self.notify(PiecePlaced(self.id, current_player, row, side, current_turn))

    def add_observer(self, cb: Callable[[SideStackerEvent], None]):
        self.dependants.append(cb)

    def notify(self, ev: SideStackerEvent):
        for cb in self.dependants:
            cb(ev)


def get_next_free_position(board, row, side):
    """
    Get the next free position on a row from the given side
    """
    search_iter = range(0, 7) if side == 'L' else range(6, -1, -1)
    for i in search_iter:
        if board[row][i] is None:
            return i

    return None


def is_move_legal(board, row, side):
    """
    Check if the move is legal.
    A move is legal when the given row and side have a None value.
    """
    search_iter = range(0, 7) if side == 'L' else range(6, -1, -1)
    for i in search_iter:
        if board[row][i] is None:
            return True

    return False


def check_range(board, iter, piece):
    """
    Given a board, and iterator of (row, col) indexes and a piece
    Return true if all the indexes in the board are equal to piece
    """
    for (r, c) in iter:
        if board[r][c] != piece:
            return False
    return True


def evaluate_move(board, row, col, piece) -> bool:
    """
    Given a board, assume `col` and `row` is the last move by `piece`.
    Check if piece has won the game.

    The naive strategy to evaluate if a player has won is to check from every
    row and col pair, check if there's four consecutive pieces, vertically, horizontally or diagonally
    from that position.

    Considering that the pieces already placed can't be moved and a winning combination
    depends on the last placed piece, a more efficient strategy is to only check if
    there's four consecutive pieces from the last placed piece.

    We evaluate this here by creating an iterator of tuples of row, col pairs. Which
    indicate what positions need to have the same piece in order to have a winning combination.

    Since we have the piece that should be in the `row` and `col` position there's no need to add it
    to the iterator. This is helpful when evaluating possible piece placements without needing to copy
    the board.
    """
    consecutive_pieces_to_win = 4

    # Factories for iterators, using the given position
    increasing_i = lambda p: range(p + 1, p + consecutive_pieces_to_win)
    decreasing_i = lambda p: range(p - 1, p - consecutive_pieces_to_win, -1)
    fixed_i = lambda p: repeat(p, consecutive_pieces_to_win)

    bound_check_inc = lambda p: p + consecutive_pieces_to_win <= 7
    bound_check_dec = lambda p: p - (consecutive_pieces_to_win - 1) >= 0

    # Check combinations of ranges that can win:
    # Horizontally to the right:
    if bound_check_inc(col) and \
            check_range(board, zip(fixed_i(row), increasing_i(col)), piece):
        return True
    # Horizontally to the left:
    if bound_check_dec(col) and \
            check_range(board, zip(fixed_i(row), decreasing_i(col)), piece):
        return True
    # Vertically to the bottom
    if bound_check_inc(row) and \
            check_range(board, zip(increasing_i(row), fixed_i(col)), piece):
        return True
    # Vertically to the top
    if bound_check_dec(row) and \
            check_range(board, zip(decreasing_i(row), fixed_i(col)), piece):
        return True
    # Diagonally to top-left
    if bound_check_dec(row) and \
        bound_check_dec(col) and \
            check_range(board, zip(decreasing_i(row), decreasing_i(col)), piece):
        return True
    # Diagonally to bottom-left
    if bound_check_inc(row) and \
        bound_check_dec(col) and \
        check_range(board, zip(increasing_i(row), decreasing_i(col)), piece):
        return True
    # Diagonally to top right
    if bound_check_dec(row) and \
        bound_check_inc(col) and \
        check_range(board, zip(decreasing_i(row), increasing_i(col)), piece):
        return True
    # Diagonally to bottom right
    if bound_check_inc(row) and \
        bound_check_inc(col) and \
        check_range(board, zip(increasing_i(row), increasing_i(col)), piece):
        return True

    return False