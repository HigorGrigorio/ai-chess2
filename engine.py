# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------
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

        self.move_functions = {'p': self._get_pawn_moves,
                               'R': self._get_rook_moves,
                               'N': self._get_knight_moves,
                               'B': self._get_bishop_moves,
                               'Q': self._get_queen_moves,
                               'K': self._get_king_moves}

        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = self.stalemate = self.checkmate = False
        self.pins = []
        self.checks = []
        self.en_passant_possible = ()  # coordinates for the square where en passant capture is possible
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # update the king's location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + move.pawn_promotion_piece

        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'  # capturing the pawn

        # en passant
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advances
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else:  # queen side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'

        # update castling rights - whenever it is a rook or a king move
        self.update_castle_rights(move)

        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # update the king's location
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # undo en passant
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)

            # undo 2 square pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen side castle
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            # undo castling rights
            self.castle_rights_log.pop()  # get rid of the new castle rights from the move we are undoing
            # set the current castle rights to the last one in the list
            self.current_castling_rights = self.castle_rights_log[-1]

            self.checkmate = self.stalemate = False

    def get_valid_moves(self):
        temp_en_passant_possible = self.en_passant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = []
        self.in_check, self.pins, self.checks = self._check_for_pins_and_checks()
        if self.white_to_move:
            king_row, king_col = self.white_king_location
        else:
            king_row, king_col = self.black_king_location

        if self.in_checkmate():
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self._get_all_possible_moves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                # if knight, must capture knight or move king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # go through backwards when removing elements from a list
                    if moves[i].piece_moved[1] != 'K':  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self._get_king_moves(king_row, king_col, moves)
        else:  # not in check so all moves are fine
            moves = self._get_all_possible_moves()

        self._get_castle_moves(king_row, king_col, moves)

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True

        self.en_passant_possible = temp_en_passant_possible
        self.current_castling_rights = temp_castle_rights

        return moves

    def _check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False

        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row, start_col = self.white_king_location
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row, start_col = self.black_king_location

        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (
                                        enemy_color == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():
                                # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break

        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks

    def in_checkmate(self):
        if self.white_to_move:
            return self._is_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self._is_under_attack(self.black_king_location[0], self.black_king_location[1])

    def _is_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move  # switch to opponent's turn
        opponent_moves = self._get_all_possible_moves()  # get their moves
        self.white_to_move = not self.white_to_move  # switch turns back

        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                return True

        return False

    def _get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)

        return moves

    def get_possible_pawn_promotions(self):
        return ['Q', 'R', 'B', 'N']

    def _get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        pawn_promotion = False

        def _append_move(move):
            # consider pawn promotion, if not a pawn promotion, just append the move
            # if pawn promotion, append 4 moves promoting to each piece type
            if pawn_promotion:
                for promotion in self.get_possible_pawn_promotions():
                    new_move = Move((r, c), (move.end_row, move.end_col), self.board, is_pawn_promotion=True)
                    new_move.pawn_promotion_piece = promotion
                    moves.append(new_move)
            else:
                moves.append(move)

        if self.white_to_move:  # white pawn moves
            move_amount = -1
            start_row = 6
            enemy_color = 'b'
            back_row = 0
            king_row, king_col = self.white_king_location
        else:  # black pawn moves
            move_amount = 1
            start_row = 1
            enemy_color = 'w'
            back_row = 7
            king_row, king_col = self.black_king_location

        if self.board[r + move_amount][c] == '--':  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                if r + move_amount == back_row:  # if piece gets to back row, it's a promotion
                    pawn_promotion = True
                _append_move(Move((r, c), (r + move_amount, c), self.board))
                if r == start_row and self.board[r + 2 * move_amount][c] == '--':
                    _append_move(Move((r, c), (r + 2 * move_amount, c), self.board))
        if c - 1 >= 0:
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    if r + move_amount == back_row:
                        pawn_promotion = True
                        attacking_piece = blocking_piece = False
                        if king_row == r:
                            if king_col < c:
                                # inside range between king and pawn
                                inside_range = range(king_col + 1, c - 1)
                                outside_range = range(c + 1, 8)
                            else:
                                inside_range = range(king_col - 1, c, -1)
                                outside_range = range(c - 2, -1, -1)
                            for i in range(len(self.board)):
                                if i in inside_range:
                                    if self.board[r][i] != '--':
                                        blocking_piece = True
                                elif i in outside_range:
                                    if self.board[r][i] != '--':
                                        attacking_piece = True
                        if not attacking_piece or blocking_piece:
                            moves.append(Move((r, c), (r + move_amount, c - 1), self.board, is_en_passant_move=True))
                elif (r + move_amount, c - 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if r == 3:
                        attacking_piece = self.board[r][c - 1] == 'wp'
                        blocking_piece = self.board[r - 1][c - 1] == 'wp'
                    elif r == 4:
                        attacking_piece = self.board[r][c - 1] == 'bp'
                        blocking_piece = self.board[r + 1][c - 1] == 'bp'
                    if attacking_piece and blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c - 1), self.board, is_en_passant_move=True))
        if c + 1 <= 7:
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    if r + move_amount == back_row:
                        pawn_promotion = True
                    _append_move(Move((r, c), (r + move_amount, c + 1), self.board))
                elif (r + move_amount, c + 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if r == 3:
                        attacking_piece = self.board[r][c + 1] == 'wp'
                        blocking_piece = self.board[r - 1][c + 1] == 'wp'
                    elif r == 4:
                        attacking_piece = self.board[r][c + 1] == 'bp'
                        blocking_piece = self.board[r + 1][c + 1] == 'bp'
                    if attacking_piece and blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c + 1), self.board, is_en_passant_move=True))

    def _get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][
                    1] != 'Q':  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def _get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def _get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def _get_queen_moves(self, r, c, moves):
        self._get_rook_moves(r, c, moves)
        self._get_bishop_moves(r, c, moves)

    def _get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    # place king on end square and check for checks
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self._check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == 'w':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

    def _get_castle_moves(self, r, c, moves):
        if self._is_under_attack(r, c):
            return

        if (self.white_to_move and self.current_castling_rights.wks) or (
                not self.white_to_move and self.current_castling_rights.bks):
            self._get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (
                not self.white_to_move and self.current_castling_rights.bqs):
            self._get_queenside_castle_moves(r, c, moves)

    def _get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self._is_under_attack(r, c + 1) and not self._is_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def _get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self._is_under_attack(r, c - 1) and not self._is_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # white king side castle
        self.bks = bks  # black king side castle
        self.wqs = wqs  # white queen side castle
        self.bqs = bqs  # black queen side castle


class Move:
    rank_to_row = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}

    row_to_rank = {v: k for k, v in rank_to_row.items()}

    file_to_col = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}

    col_to_file = {v: k for k, v in file_to_col.items()}

    promotion_to_int = {'Q': 1, 'R': 2, 'B': 3, 'N': 4, None: 0}

    int_to_promotion = {v: k for k, v in promotion_to_int.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant_move=False, is_pawn_promotion=False,
                 is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.pawn_promotion_piece = None  # used for pawn promotion
        self.is_pawn_promotion = is_pawn_promotion

        self.is_enpassant_move = is_en_passant_move

        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.is_castle_move = is_castle_move

    @property
    def move_id(self):
        return self.promotion_to_int[self.pawn_promotion_piece] * 10000 + \
            self.start_row * 1000 + \
            self.start_col * 100 + \
            self.end_row * 10 + \
            self.end_col

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.col_to_file[col] + self.row_to_rank[row]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
