# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

import pygame as pg

import ai
import engine

HEIGHT = 512
WIDTH = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
SQ_PROMOTION_SIZE = 86
MAX_FPS = 15
IMAGES = {}
COLORS = {
    'dark': pg.Color(118, 150, 86),
    'light': pg.Color(238, 238, 210),
    'highlight': pg.Color(255, 255, 0),
    'capture': pg.Color(255, 0, 0),
    'promotion': pg.Color(255, 0, 255),
    # gold
    'check': pg.Color(255, 215, 0),
    'focus': pg.Color(0, 0, 255),
    'castle': pg.Color(0, 255, 255)
}


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    return IMAGES


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(COLORS['light'])
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    load_images()
    running = True
    sq_selected = ()  # no square is selected, keep track of the last click of the user (tuple: (row, col))
    player_clicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    animate = False
    game_over = False
    single_player = True  # if True, the user plays against the computer; if False, the user plays against another user
    multi_player = False  # if True, the user plays against another user; if False, the user plays against the computer

    while running:
        human_turn = (gs.white_to_move and single_player) or (multi_player and gs.white_to_move)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = pg.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:  # after 2nd click

                        possible_pawn_promotion = False
                        start_row = player_clicks[0][0]
                        start_col = player_clicks[0][1]

                        if (row == 0 and gs.white_to_move and gs.board[start_row][start_col][1] == 'p') or \
                                (row == 7 and not gs.white_to_move and gs.board[start_row][start_col][1] == 'p'):
                            possible_pawn_promotion = True

                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board,
                                           is_pawn_promotion=possible_pawn_promotion)

                        if move.is_pawn_promotion:
                            promotion = draw_pawn_promotion(screen, gs)
                            if promotion is not None:  # if the user selects a promotion
                                move.pawn_promotion_piece = promotion

                        print(move.get_chess_notation())

                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []

                        if not move_made:
                            player_clicks = [sq_selected]

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                if event.key == pg.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        if not game_over and not human_turn:
            ai_move = ai.smart_move(gs, valid_moves)
            if ai_move is not None:
                gs.make_move(ai_move)
                move_made = True
                animate = True

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.checkmate:
            game_over = True
            draw_text(screen, 'Black wins by checkmate' if gs.white_to_move else 'White wins by checkmate')
        elif gs.stalemate:
            game_over = True
            draw_text(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        pg.display.flip()


def draw_text(screen, text):
    font = pg.font.SysFont('Arial', 32, True, False)
    text_object = font.render(text, 0, pg.Color('Black'))
    text_location = pg.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                      HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, pg.Color('Gray'))
    screen.blit(text_object, text_location.move(2, 2))


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):  # sq_selected is a piece that can be moved
            # highlight selected square
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(COLORS['highlight'])
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    if move.piece_captured != '--':
                        if move.piece_captured[1] == 'K':
                            # highlight check moves from that square
                            s.fill(COLORS['check'])
                        else:
                            # highlight capture moves from that square
                            s.fill(COLORS['capture'])
                    elif move.is_pawn_promotion:
                        # highlight promotion moves from that square
                        s.fill(COLORS['promotion'])
                    elif move.is_castle_move:
                        # highlight castle moves from that square
                        s.fill(COLORS['castle'])
                    else:
                        # highlight moves from that square
                        s.fill(COLORS['highlight'])

                    screen.blit(s, (SQ_SIZE * move.end_col, SQ_SIZE * move.end_row))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    colors = [COLORS['light'], COLORS['dark']]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pg.draw.rect(screen, color, pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animate_move(move, screen, board, clock):
    if move.is_castle_move:
        return

    global COLORS
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    piece = board[move.end_row][move.end_col]

    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = COLORS['light'] if (move.end_row + move.end_col) % 2 == 0 else COLORS['dark']
        end_square = pg.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pg.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[piece], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        clock.tick(60)


def draw_pawn_promotion(screen, gs):
    possible_promotions = gs.get_possible_pawn_promotions()

    # draw a rectangle on center of the screen with the possible promotions, each
    # one with a different color, if odd black, if even white

    middle = pg.Rect((WIDTH - SQ_PROMOTION_SIZE * 4) // 2, (HEIGHT - SQ_PROMOTION_SIZE) // 2,
                     SQ_PROMOTION_SIZE * 4, SQ_PROMOTION_SIZE)
    turn = 'w' if gs.white_to_move else 'b'

    # draw the possible promotions centered on squares
    for i in range(4):
        color = COLORS['light'] if i % 2 == 0 else COLORS['dark']
        pg.draw.rect(screen, color, pg.Rect(middle.x + i * SQ_PROMOTION_SIZE, middle.y,
                                            SQ_PROMOTION_SIZE, SQ_PROMOTION_SIZE))

        image_height = IMAGES[turn + possible_promotions[i]].get_height()
        image_width = IMAGES[turn + possible_promotions[i]].get_width()
        original_size = max(image_height, image_width)
        image_size_multiplier = SQ_PROMOTION_SIZE // original_size
        origin = (middle.x + i * SQ_PROMOTION_SIZE + (SQ_PROMOTION_SIZE - image_width * image_size_multiplier) // 2,
                  middle.y + (SQ_PROMOTION_SIZE - image_height * image_size_multiplier) // 2)
        screen.blit(pg.transform.scale(IMAGES[turn + possible_promotions[i]],
                                       (image_width * image_size_multiplier,
                                        image_height * image_size_multiplier)),
                    origin)

    # draw a border around the rectangle
    border_color = pg.Color(0, 0, 0)
    pg.draw.rect(screen, border_color, middle, 5)

    # draw the text "Promote to" on the top of the rectangle
    font = pg.font.SysFont('Arial', 30, bold=True)
    text = font.render('Promote to', True, border_color)
    text_rect = text.get_rect()
    text_rect.center = (middle.x + middle.width // 2, middle.y - 30)
    screen.blit(text, text_rect)

    # update the display
    pg.display.flip()

    # when the user clicks on one of the possible promotions, return the selected promotion
    # and finish the move
    # if the user clicks outside the rectangle, do nothing and wait for another click
    selected_promotion = None

    while selected_promotion is None:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()
                col = (location[0] - middle.x) // SQ_PROMOTION_SIZE
                row = (location[1] - middle.y) // SQ_PROMOTION_SIZE

                if row == 0:
                    selected_promotion = possible_promotions[col]
                    print(selected_promotion)
                    break
            if event.type == pg.KEYDOWN:  # if the user presses the z key, cancel the promotion
                if event.key == pg.K_z:
                    return None

            if event.type == pg.QUIT:  # if the user closes the window, quit the game
                pg.quit()
                exit()

    return selected_promotion


if __name__ == '__main__':
    main()
