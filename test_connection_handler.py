from connection_handler import GameConnectionHandler
from sidestacker import SideStacker


def test_new_game_adds_new_game():
    gch = GameConnectionHandler()
    game = gch.new_game()
    assert game.id in gch.games
    assert isinstance(game, SideStacker)
    assert game == gch.games[game.id]['game']


def test_has_game_for_existant_game():
    gch = GameConnectionHandler()
    game = gch.new_game()
    assert gch.has_game(game.id) == True


def test_has_game_for_unexistant_game():
    gch = GameConnectionHandler()
    assert gch.has_game('test') == False
