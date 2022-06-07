import logging
import uuid
from json import dumps, loads

from bot import Bot
from events import *
from sidestacker import SideStacker


class GameConnectionHandler:
    """
    This class is expected to be a Singleton that holds games, their players and their
    websocket connections.

    Its responsibilities are:
    - Creating new game instances
    - Connecting players to their game instances
    - Sending messages from the game instance to the respective players
    - Sending messages from the players to their respective game instance
    """

    def __init__(self, logger=logging.getLogger('GameConnectionHandler')):
        self.games = {}
        self._log = logger

    def new_game(self, is_against_bot = False):
        game_id = str(uuid.uuid4())
        self._log.debug('[gId: %s] A new game was created' % game_id)
        game_instance = self._create_sidestacker_instance(game_id)
        self.games[game_id] = {
            'game': game_instance,
            'players': {},
            'is_against_bot': is_against_bot
        }

        return game_instance

    def has_game(self, game_id):
        return game_id in self.games

    def add_connection(self, game_id, ws, player_id):
        if game_id not in self.games:
            raise ValueError('Invalid game_id')

        self._log.debug('[gId: %s][pId: %s] A player connected' % (game_id, player_id))

        game = self.games[game_id]
        game['players'][player_id] = ws

        ss = game['game']
        ss.connect(player_id)

        if game['is_against_bot']:
            bot_id = str(uuid.uuid4()).split('-')[-1]
            bot = Bot(ss, bot_id)
            game['players'][bot_id] = bot

            ss.add_observer(bot.process_game_events)
            ss.connect(bot_id)

    def handle_client_message(self, game_id, player_id, message):
        """
        Handle messages sent by the client.
        At this time the only message type is 'piece-placement'
        """
        json = loads(message)
        if 'type' not in json:
            self._log.error("json message doesn't have a type field: %s" % message)
            return

        if json['type'] == 'piece-placement':
            self._log.debug('[gId: %s][pId: %s] A player placed a piece' % (game_id, player_id))
            ss = self.games[game_id]['game']
            ss.place_piece(player_id, json['row'], json['side'])
        else:
            self._log.warning("Unable to handle message of unknown type '%s' of message: '%s'" % (json['type'], message))

    def close_connection(self, game_id, player_id):
        game = self.games[game_id]['game']
        game.disconnec(player_id)

    def _create_sidestacker_instance(self, game_id):
        ss = SideStacker(game_id)
        ss.add_observer(self._process_game_events)
        return ss

    def _process_game_events(self, ev):
        if isinstance(ev, PlayerConnected):
            self._on_connect(ev)
        elif isinstance(ev, PlayerDisconnected):
            self._on_disconnect(ev)
        elif isinstance(ev, PlayerInfo):
            self._on_player_info(ev)
        elif isinstance(ev, GameOver):
            self._on_game_over(ev)
        elif isinstance(ev, PiecePlaced):
            self._on_piece_placed(ev)
        elif isinstance(ev, PiecePlacedError):
            self._on_piece_placed_error(ev)

    def _on_connect(self, ev: PlayerConnected):
        game = self.games[ev.game_id]
        ws = game['players'][ev.player_id]
        ws.send(dumps({
            'type': 'connection',
            'player': ev.player,
            'turn': ev.turn_order
        }))

    def _on_disconnect(self, ev: PlayerDisconnected):
        game = self.games[ev.game_id]
        for (_, ws) in game['players'].items():
            ws.send(dumps({
                'type': 'disconnection',
                'player': ev.player
            }))

    def _on_player_info(self, ev: PlayerInfo):
        game = self.games[ev.game_id]
        for (_, ws) in game['players'].items():
            ws.send(dumps({
                'type': 'player_info',
                'players': ev.players
            }))

    def _on_game_over(self, ev: GameOver):
        game = self.games[ev.game_id]
        for (_, ws) in game['players'].items():
            ws.send(dumps({
                'type': 'game_over',
                'winner': ev.winner
            }))
            ws.close()

    def _on_piece_placed(self, ev: PiecePlaced):
        game = self.games[ev.game_id]
        for (_, ws) in game['players'].items():
            ws.send(dumps({
                'type': 'piece_placed',
                'player': ev.player,
                'row': ev.row,
                'side': ev.side,
                'turn': ev.turn
            }))

    def _on_piece_placed_error(self, ev: PiecePlacedError):
        game = self.games[ev.game_id]
        # Send the error to the player only
        ws = game['players'][ev.player_id]
        ws.send(dumps({
            'type': 'piece_placed_error',
            'turn': ev.turn
        }))
