# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

import pygame as pg

from engine import GameState

HEIGHT = 512
WIDTH = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
COLORS = {
    'dark': pg.Color(118, 150, 86),
    'light': pg.Color(238, 238, 210)
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
    gs = GameState()
    load_images()
    running = True
    sq_selected = ()  # no square is selected, keep track of the last click of the user (tuple: (row, col))
    player_clicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
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
                    move = gs.board.get_move(player_clicks[0], player_clicks[1])
                    sq_selected = ()
                    player_clicks = []

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()


def draw_game_state(screen, gs):
    draw_board(screen)
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


if __name__ == '__main__':
    main()
