from typing import Literal


class SideStackerEvent:
    """
    This base class represents an event of a sidestacker game
    """
    def __init__(self, game_id: str):
        self.game_id = game_id
    pass


class PlayerConnected(SideStackerEvent):
    def __init__(self, game_id: str, player: Literal['X', 'C'], turn_order: Literal[0, 1]):
        super().__init__(game_id)
        self.player = player
        self.turn_order = turn_order


class PlayerDisconnected(SideStackerEvent):
    def __init__(self, game_id: str, player: Literal['X', 'C']):
        super().__init__(game_id)
        self.player = player


class PlayerWon(SideStackerEvent):
    def __init__(self, game_id: str, player: Literal['X', 'C']):
        super().__init__(game_id)
        self.player = player


class PiecePlaced(SideStackerEvent):
    def __init__(self, game_id: str, player: Literal['X', 'C'], row: int, side: Literal['L', 'R'], turn: int):
        super().__init__(game_id)
        self.player = player
        self.row = row
        self.side = side
        self.turn = turn