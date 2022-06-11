from bot import Bot

def test_get_first_and_last_free_index_on_empty_board():

    b = Bot(None, 'player_id')
    expected = [
        ('L', 0, 0),
        ('L', 1, 0),
        ('L', 2, 0),
        ('L', 3, 0),
        ('L', 4, 0),
        ('L', 5, 0),
        ('L', 6, 0),
        ('R', 0, 6),
        ('R', 1, 6),
        ('R', 2, 6),
        ('R', 3, 6),
        ('R', 4, 6),
        ('R', 5, 6),
        ('R', 6, 6),
    ]
    actual = b.get_available_moves()

    for e in expected:
        assert e in actual


def test_should_return_winning_move_on_almost_winning_board():
    b = [['C', 'C', 'C', None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         ]
    b = Bot(None, 'player_id', b)
    b.player_piece = 'C'
    am = b.get_available_moves()
    assert ('L', 0, 3) in am
    wm = b.get_winning_moves(am)
    assert ('L', 0) in wm


def test_should_return_blocking_move():
    b = [['C', 'C', 'C', None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         ]
    b = Bot(None, 'player_id', b)
    b.player_piece = 'X'
    am = b.get_available_moves()
    assert ('L', 0, 3) in am
    bm = b.get_blocking_moves(am)
    assert ('L', 0) in bm

