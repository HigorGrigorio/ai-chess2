# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------
from random import choice

SPECIAL_MOVE = {
    'is_castle_move': 1,
    'is_pawn_promotion': 1,
    'is_enpassant_move': 1
}

# controls the depth of the search tree
DEPTH = 3


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

    for row in board:
        for piece in row:
            if piece[0] == 'w':
                score += MATERIAL[piece[1]]
            elif piece[0] == 'b':
                score -= MATERIAL[piece[1]]

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
        return _eval_board(gs)

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
        return _eval_board(gs)

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


def ab_negamax(gs, valid_moves, depth, white_to_move, alpha, beta):
    global next_move

    if depth == 0:
        return _eval_board(gs)

    max_score = -CHECKMATE

    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -ab_negamax(gs, next_moves, depth - 1, not white_to_move, -beta, -alpha)
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


def smart_move(gs, moves):
    global next_move
    next_move = None
    _negamax(gs, moves, DEPTH, gs.white_to_move)
    return next_move
