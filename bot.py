import time

from events import *


class Bot:
    """
    This class implements a simple bot that plays the game by responding to game events.

    The strategy is to look for the next available space going from top to bottom, left to right in the board.
    """
    def __init__(self, game_instance, player_id):
        self.game = game_instance
        self.player_id = player_id
        self.turn = None
        self.board = [[None] * 7 for _ in range(7)]
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

    def do_move(self):
        """
        Place a piece on the board looking for the first available space, top to bottom, left to right.
        """
        for i in range(7):
            for j in range(7):
                if self.board[i][j] is None:
                    self.game.place_piece(self.player_id, i, 'L')
                    return

    def _handle_piece_placed(self, ev: PiecePlaced):
        """
        Update the bot state with the given message, and do a move if it's the bot turn.
        """
        row = ev.row
        direction = range(7) if ev.side == 'L' else range(6, -1, -1)
        for i in direction:
            if self.board[row][i] is None:
                self.board[row][i] = ev.player
                break
        if ev.player != self.player_piece:
            self.do_move()
