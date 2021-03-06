from itertools import repeat

from events import PiecePlacedError
from sidestacker import SideStacker, get_next_free_position, check_range, evaluate_move


# Connect
def test_connect_return_x_or_o_pieces_and_0_or_1_turn():
    ss = SideStacker()
    (pieces, turn) = ss.connect('abc')
    assert pieces in ('X', 'C')
    assert turn in (0, 1)


def test_connect_two_players_returns_different_pieces_and_turn():
    ss = SideStacker()
    (p1_pieces, p1_turn) = ss.connect('abc')
    (p2_pieces, p2_turn) = ss.connect('xyz')
    assert p1_pieces != p2_pieces
    assert p1_turn != p2_turn


def test_connect_more_than_two_returns_none():
    ss = SideStacker()
    ss.connect('abc')
    ss.connect('dcb')
    assert ss.connect('xyz') is None


def test_connect_with_same_id_does_nothing():
    ss = SideStacker()
    player_id = 'abc'
    ss.connect(player_id)
    assert ss.connect(player_id) is None


# Disconnect

def test_player_deleted_after_disconnect():
    ss = SideStacker()
    player_id = 'abc'
    ss.connect(player_id)
    ss.disconnect(player_id)
    assert len(ss.players) == 0


# Place piece

def test_place_piece_adds_piece_to_board():
    (ss, first_turn_player, second_turn_player) = new_sidestacker_game()

    assert ss.board[0][0] is None

    # Place piece with the player with the first turn
    ss.place_piece(first_turn_player[0], 0, 'L')
    # Check that the piece placed belongs to the right player
    assert ss.board[0][0] == first_turn_player[1]

    assert ss.board[0][1] is None
    # Placing in the same row in the same side should stack
    ss.place_piece(second_turn_player[0], 0, 'L')
    # Check that the previously added piece is still the same
    assert ss.board[0][0] == first_turn_player[1]
    # Check that the new piece was stacked correctly
    assert ss.board[0][1] == second_turn_player[1]

    # Place pieces in the opposing side
    assert ss.board[0][6] is None
    ss.place_piece(first_turn_player[0], 0, 'R')
    assert ss.board[0][6] == first_turn_player[1]

    # Pieces should stack as expected on the opposing side
    ss.place_piece(second_turn_player[0], 0, 'R')
    assert ss.board[0][6] == first_turn_player[1]
    assert ss.board[0][5] == second_turn_player[1]

    # Place pieces on the remaining spaces of the first row to test placing in a full row
    ss.place_piece(first_turn_player[0], 0, 'R')
    ss.place_piece(second_turn_player[0], 0, 'R')
    ss.place_piece(first_turn_player[0], 0, 'R')

    # If theres no space available, raise exception, maintain current turn
    current_turn = ss.turn

    notification = None

    def observer(ev):
        nonlocal notification
        notification = ev

    ss.add_observer(observer)
    ss.place_piece(second_turn_player[0], 0, 'R')
    assert isinstance(notification, PiecePlacedError)
    assert notification.turn == current_turn
    assert notification.detail == 'Theres no available space in the selected row'


def test_place_piece_on_wrong_turn_should_notify():
    (ss, first_turn_player, second_turn_player) = new_sidestacker_game()
    notification = None

    def observer(ev):
        nonlocal notification
        notification = ev

    ss.add_observer(observer)
    ss.place_piece(first_turn_player[0], 0, 'L')
    ss.place_piece(first_turn_player[0], 0, 'L')
    assert isinstance(notification, PiecePlacedError)
    assert notification.turn == ss.turn
    assert notification.detail == 'Players should place pieces on their own turn'


def test_place_piece_without_two_players_should_notify():
    ss = SideStacker()
    p1 = ss.connect('abc')

    notification = None

    def observer(ev):
        nonlocal notification
        notification = ev

    ss.add_observer(observer)
    ss.place_piece(p1[0], 0, 'L')

    assert isinstance(notification, PiecePlacedError)
    assert notification.detail == 'There should be two players to start the game'

# Evaluation with move

def test_winning_horizontal_stack_should_win():
    w = [['C', 'C', 'C', 'C', None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         ]
    assert evaluate_move(w, 0, 0, 'C')
    assert evaluate_move(w, 0, 3, 'C')


def test_winning_vertical_stack_should_win():
    w = [[None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, 'C', None, None, None],
         [None, None, None, 'C', None, None, None],
         [None, None, None, 'C', None, None, None],
         [None, None, None, 'C', None, None, None],
         ]
    assert evaluate_move(w, 3, 3, 'C')
    assert evaluate_move(w, 6, 3, 'C')


def test_winning_diagonal_br_stack_should_win():
    w = [['X', None, None, None, None, None, None],
         [None, 'X', None, None, None, None, None],
         [None, None, 'X', None, None, None, None],
         [None, None, None, 'X', None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         ]
    assert evaluate_move(w, 0, 0, 'X')
    assert evaluate_move(w, 3, 3, 'X')


def test_winning_diagonal_bl_stack_should_win():
    w = [[None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, 'X'],
         [None, None, None, None, None, 'X', None],
         [None, None, None, None, 'X', None, None],
         [None, None, None, 'X', None, None, None],
         ]
    assert evaluate_move(w, 6, 3, 'X')
    assert evaluate_move(w, 3, 6, 'X')


def test_every_winning_horizontal_stack_should_win_with_last_move():
    for i in range(0, 7):
        for j in range(0, 4):
            w = [[None] * 7 for _ in range(7)]
            for x in range(j, j + 4):
                w[i][x] = 'C'
            # Should win if placed at the start or end
            assert evaluate_move(w, i, j, 'C')
            assert evaluate_move(w, i, j + 4, 'C')


def test_every_winning_vertical_stack_should_win_with_last_move():
    for i in range(0, 4):
        for j in range(0, 7):
            w = [[None] * 7 for _ in range(7)]
            for x in range(i, i + 4):
                w[x][j] = 'C'

            assert evaluate_move(w, i, j, 'C')
            assert evaluate_move(w, i + 3, j, 'C')


def test_every_winning_diagonal_stack_should_win_with_last_move():
    for i in range(0, 7):
        for j in range(0, 7):
            # try to add a diagonal in the top-right
            if i - 3 >= 0 and j + 3 < 7:
                w = [[None] * 7 for _ in range(7)]
                for (di, dj) in zip(range(i, i - 4, -1), range(j, j + 4)):
                    w[di][dj] = 'C'
                assert evaluate_move(w, i, j, 'C')
                assert evaluate_move(w, i - 3, j + 3, 'C')
            # try to add a diagonal in the top-left
            if i - 3 >= 0 and j - 3 >= 0:
                w = [[None] * 7 for _ in range(7)]
                for (di, dj) in zip(range(i, i - 4, -1), range(j, j - 4, -1)):
                    w[di][dj] = 'C'
                assert evaluate_move(w, i, j, 'C')
                assert evaluate_move(w, i - 3, j - 3, 'C')


# utils
def new_sidestacker_game(p1_id='abc', p2_id='xyz'):
    """"
    Creates a new Sidestacker instance with two players.
    returns a tuple of the form (instance, first_turn_player, second_turn_player)
    """
    ss = SideStacker()
    p1_id = p1_id
    p2_id = p2_id
    p1 = (p1_id,) + ss.connect(p1_id)
    p2 = (p2_id,) + ss.connect(p2_id)

    first_turn_player = p1 if p1[2] < p2[2] else p2
    second_turn_player = p1 if first_turn_player == p2 else p2

    return (ss, first_turn_player, second_turn_player)


def test_next_free_position_left_should_be_0():
    empty_board = [[None] * 7 for _ in range(7)]
    assert get_next_free_position(empty_board, 0, 'L') == 0


def test_next_free_position_right_should_be_6():
    empty_board = [[None] * 7 for _ in range(7)]
    assert get_next_free_position(empty_board, 0, 'R') == 6


def test_check_range_should_return_true_when_all_match():
    b = [['X', 'X', 'X', 'X']]
    assert check_range(b, zip(repeat(0, 4), range(0, 4)), 'X')


def test_check_range_should_return_false_when_some_dont_match():
    b = [['X', 'X', 'C', 'X']]
    assert not check_range(b, zip(repeat(0, 4), range(0, 4)), 'X')
