from typing import Literal, Optional


class SideStackerEvent:
    """
    This base class represents an event of a sidestacker game
    """

    def __init__(self, game_id: str):
        self.game_id = game_id


class PlayerConnected(SideStackerEvent):
    def __init__(self, game_id: str, player_id: str, player: Literal['X', 'C'], turn_order: Literal[0, 1]):
        super().__init__(game_id)
        self.player_id = player_id
        self.player = player
        self.turn_order = turn_order


class PlayerDisconnected(SideStackerEvent):
    def __init__(self, game_id: str, player: Literal['X', 'C']):
        super().__init__(game_id)
        self.player = player


class GameOver(SideStackerEvent):
    def __init__(self, game_id: str, winner: Optional[Literal['X', 'C']]):
        super().__init__(game_id)
        self.winner = winner


class PiecePlaced(SideStackerEvent):
    def __init__(self, game_id: str, player: Literal['X', 'C'], row: int, side: Literal['L', 'R'], turn: int):
        super().__init__(game_id)
        self.player = player
        self.row = row
        self.side = side
        self.turn = turn


class PiecePlacedError(SideStackerEvent):
    def __init__(self, game_id: str, player_id: str, turn: int, detail: str):
        super().__init__(game_id)
        self.player_id = player_id
        self.turn = turn
        self.detail = detail


class PlayerInfo(SideStackerEvent):
    def __init__(self, game_id: str, players):
        super().__init__(game_id)
        self.players = players
