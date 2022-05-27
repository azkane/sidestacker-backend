from typing import Literal


class SideStackerEvent:
    """
    This base class represents an event of a sidestacker game
    """
    pass


class PlayerConnected(SideStackerEvent):
    def __init__(self, player: Literal['X', 'C'], turn_order: Literal[0, 1]):
        self.player = player
        self.turn_order = turn_order


class PlayerDisconnected(SideStackerEvent):
    def __init__(self, player: Literal['X', 'C']):
        self.player = player


class PlayerWon(SideStackerEvent):
    def __init__(self, player: Literal['X', 'C']):
        self.player = player


class PiecePlaced(SideStackerEvent):
    def __init__(self, player: Literal['X', 'C'], row: int, side: Literal['L', 'R'], turn: int):
        self.player = player
        self.row = row
        self.side = side
        self.turn = turn

