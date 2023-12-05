# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------
from random import choice

# controls the depth of the search tree
DEPTH = 4

KNIGHT_SCORE = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

BISHOP_SCORE = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

ROOK_SCORE = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

QUEEN_SCORE = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

KING_SCORE = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

WHITE_PAWN_SCORE = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [.5, .5, 1, 2, 2, 1, .5, .5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

BLACK_PAWN_SCORE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [.5, .5, 1, 2, 2, 1, .5, .5],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8]
]

PIECE_SCORE = {
    'bN': KNIGHT_SCORE,
    'wN': KNIGHT_SCORE,
    'wB': BISHOP_SCORE,
    'bB': BISHOP_SCORE,
    'wR': ROOK_SCORE,
    'bR': ROOK_SCORE,
    'wQ': QUEEN_SCORE,
    'bQ': QUEEN_SCORE,
    'wK': KING_SCORE,
    'bK': KING_SCORE,
    'wp': WHITE_PAWN_SCORE,
    'bp': BLACK_PAWN_SCORE
}


def _random_move(moves):
    return choice(moves)


MATERIAL = {
    "p": 1,  # pawn
    "N": 3,  # knight
    "B": 3,  # bishop
    "R": 5,  # rook
    "Q": 10,  # queen
    "K": 0  # king
}


def _eval_material(board):
    score = 0

    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != "--":
                pos_score = PIECE_SCORE[piece][row][col] * .1

                if piece[0] == 'w':
                    score += MATERIAL[piece[1]] + pos_score
                elif piece[0] == 'b':
                    score -= (MATERIAL[piece[1]] + pos_score)

    return score


CHECKMATE = float('inf')
STALEMATE = 0


def _eval_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    return _eval_material(gs.board)


global next_move


def _minmax(gs, valid_moves, depth, white_to_move):
    global next_move

    if depth == 0:
        return _eval_material(gs.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = _minmax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = _minmax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


def _negamax(gs, valid_moves, depth, white_to_move):
    global next_move

    if depth == 0:
        return _eval_material(gs.board)

    max_score = -CHECKMATE

    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -_negamax(gs, next_moves, depth - 1, not white_to_move)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()

    return max_score


def _ab_negamax(gs, valid_moves, depth, turn_mult, alpha, beta):
    global next_move

    if depth == 0:
        return _eval_material(gs.board) * turn_mult

    max_score = -CHECKMATE

    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -_ab_negamax(gs, next_moves, depth - 1, -turn_mult, -beta, -alpha)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()

        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score


def smart_move(gs, moves, return_queue):
    global next_move
    next_move = None
    _ab_negamax(gs, moves, DEPTH, 1 if gs.white_to_move else -1, -CHECKMATE, CHECKMATE)
    return_queue.put(next_move)
