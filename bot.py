import random
import time

from sidestacker import is_move_legal, get_next_free_position, evaluate_move
from events import *


class Bot:
    """
    This class implements a simple bot that plays the game by responding to game events.

    The strategy is to look for the next available space going from top to bottom, left to right in the board.
    """
    def __init__(self, game_instance, player_id, board = None):
        self.game = game_instance
        self.player_id = player_id
        self.turn = None
        self.board = board or [[None] * 7 for _ in range(7)]
        self.player_piece = None

    def send(self, ev):
        """
        As the bot is saved in the GameConnectionHandler class as a fake WebSocket object
        define this method and the close method to avoid errors.
        Communication with the instance could be done with these, but for brevity use
        the existing notification strategy already used.
        """
        pass

    def close(self):
        pass

    def process_game_events(self, ev):
        if isinstance(ev, PlayerConnected):
            self._handle_player_connected(ev)
        elif isinstance(ev, PlayerDisconnected):
            pass
        elif isinstance(ev, PlayerInfo):
            self._handle_player_info(ev)
            pass
        elif isinstance(ev, GameOver):
            pass
        elif isinstance(ev, PiecePlaced):
            self._handle_piece_placed(ev)
        elif isinstance(ev, PiecePlacedError):
            print('Piece placed error: %s' % ev.detail)
            pass

    def _handle_player_connected(self, ev: PlayerConnected):
        """
        Initialize the bot state with the given parameters.

        Once this bot connects to the game instance, this is the first event that
        should be received.
        """
        self.player_piece = ev.player
        self.turn = ev.turn_order

    def _handle_player_info(self, ev: PlayerInfo):
        """
        Check if the bot has the first turn and if it does, do the first move.

        This should be the second event received, if the bot is first to move the
        client UI might not be ready to process piece placements, so we delay a second
        the first move.
        """
        if self.turn == 0:
            # Delay piece placement until client UI is ready
            time.sleep(1)
            self.do_move()

    def get_available_moves(self):
        """
        Get a list of legal moves for the current board
        """
        available_moves = set()

        for r in range(7):
            if is_move_legal(self.board, r, 'L'):
                col = get_next_free_position(self.board, r, 'L')
                available_moves.add(('L', r, col))

            if is_move_legal(self.board, r, 'R'):
                col = get_next_free_position(self.board, r, 'R')
                available_moves.add(('R', r, col))

        return available_moves

    def get_winning_moves_for_piece(self, available_moves, piece):
        """
        Get all winning moves that win the game for the given piece
        """
        winning_moves = set()

        for (side, row, col) in available_moves:
            if evaluate_move(self.board, row, col, piece):
                winning_moves.add((side, row))

        return winning_moves


    def get_winning_moves(self, available_moves):
        """
        Get all the moves that win the game for this player
        """
        return self.get_winning_moves_for_piece(available_moves, self.player_piece)

    def get_blocking_moves(self, available_moves):
        """
        Get all the moves that block another player from winning.
        A blocking move is a winning move done by the oposite player. By playing the
        same move, the oposite player is unable to make that move.
        """
        return self.get_winning_moves_for_piece(available_moves,
                                                'X' if self.player_piece == 'C' else 'C')

    def do_move(self):
        """
        Place a piece on the board looking for the first available space, top to bottom, left to right.
        """
        am = self.get_available_moves()
        wm = self.get_winning_moves(am)
        if len(wm) > 0:
            (side, row) = wm.pop()
            self.game.place_piece(self.player_id, row, side)
            return

        bm = self.get_blocking_moves(am)
        if len(bm) > 0:
            (side, row) = bm.pop()
            self.game.place_piece(self.player_id, row, side)
            return

        rm = random.choice(tuple(am))
        self.game.place_piece(self.player_id, rm[1], rm[0])


    def _handle_piece_placed(self, ev: PiecePlaced):
        """
        Update the bot state with the given message, and do a move if it's the bot turn.
        """
        row = ev.row
        col = get_next_free_position(self.board, row, ev.side)
        self.board[row][col] = ev.player

        if ev.player != self.player_piece:
            self.do_move()
