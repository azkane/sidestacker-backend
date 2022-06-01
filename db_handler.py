from sqlite3 import Connection

from events import GameOver, PiecePlaced
from sidestacker import SideStacker


class DBHandler:
    """
    This class manages a sqlite database where games are saved.

    It's made as an observer that can be notified of SideStacker events.
    Depending on the event the respective method is called to save the data.

    """
    def __init__(self, file="db.sqlite"):
        self.file = file
        self.initialize()

    def initialize(self):
        with Connection(self.file) as con:
            with open('init-db.sql') as f:
                script = f.read()
                cur = con.cursor()
                cur.executescript(script)
                cur.close()

    def manage_game(self, sidestackerInstance: SideStacker):
        sidestackerInstance.add_observer(self._process_game_events)
        self.create_game(sidestackerInstance.id)

    def create_game(self, game_id):
        with Connection(self.file) as con:
            cur = con.cursor()
            cur.execute('insert into game(game_id) values (?)', (game_id,))
            cur.close()

    def add_move(self, game_id, row, side, piece, turn):
        with Connection(self.file) as con:
            cur = con.cursor()
            cur.execute('insert into game_moves (game_id, row, side, piece, turn) values (?, ?, ?, ?, ?)',
                        (game_id, row, side, piece, turn))
            cur.close()

    def save_winner(self, game_id, winner):
        with Connection(self.file) as con:
            cur = con.cursor()
            cur.execute('update game set winner = ? where game_id = ?', (winner, game_id))
            cur.close()

    def _process_game_events(self, ev):
        if isinstance(ev, GameOver):
            self.save_winner(ev.game_id, 'tie' if ev.winner is None else ev.winner)
        elif isinstance(ev, PiecePlaced):
            self.add_move(ev.game_id, ev.row, ev.side, ev.player, ev.turn)