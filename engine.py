# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

class GameState:
    def __init__(self):
        # the default chessboard is a 8x8 board with the initial
        # chessboard configuration (see domain/chessboard.py). The
        # first character of each string represents the color of the
        # peace (W for white and B for black) and the second character
        # represents the type of the peace (R for rook, N for knight,
        # B for bishop, Q for queen, K for king and P for pawn).
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

        # the white_to_move variable is a boolean that indicates if
        # the white player is the next to move
        self.white_to_move = True

        # the move_log variable is a list of Movement objects that
        # represents the history of the game
        self.move_log = []
