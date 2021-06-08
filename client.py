from client_network import NetworkClient
import pygame
import math
import time
import pickle
from pprint import pprint

GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


class GameClient:
    def __init__(self):

        self.WIDTH = 500
        self.HEIGHT = 600
        self.ROWS = 10
        self.COLUMNS = self.ROWS

        self.pygame = pygame
        self.pygame.init()
        self.win = self.pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.win.fill(WHITE)

        self.ships = {
            1: {'amount': 4, 'placed': 0},
            2: {'amount': 3, 'placed': 0},
            3: {'amount': 2, 'placed': 0},
            4: {'amount': 1, 'placed': 0},
        }

        self.current_ship = 0

        self.END_FONT = pygame.font.SysFont('Comic Sans MS', 20)

        self.game_field = [[{'x': col, 'y': row, 'colored': False} for col in range(self.COLUMNS)] for row in range(self.ROWS)]
        pprint(self.game_field)

    def render(self):
        self.draw_grid()
        self.draw_cells()
        self.pygame.display.update()

    def draw_grid(self):
        self.win.fill(WHITE)
        cell_width = self.WIDTH // self.COLUMNS
        x = 0
        y = 0
        x_pos = 0
        for i in range(self.ROWS):
            x = i * cell_width

            self.pygame.draw.line(self.win, GRAY,
                                  (x, self.HEIGHT - self.WIDTH),
                                  (x, self.HEIGHT), 3)  # вертикальные линии
            self.pygame.draw.line(self.win, GRAY,
                                  (0, x + self.HEIGHT - self.WIDTH),
                                  (self.WIDTH, x + self.HEIGHT - self.WIDTH), 3)  # горизонтальные

            text = self.END_FONT.render(f'({x_pos};{i})', False, GRAY)
            self.win.blit(text, (x, self.HEIGHT - self.WIDTH))

    def draw_cells(self):
        for x, col in enumerate(self.game_field):
            for y, cell in enumerate(col):
                if cell['colored']:
                    cell_width = self.WIDTH // self.COLUMNS
                    self.pygame.draw.rect(self.win, RED,
                                          [cell_width * x, self.HEIGHT - self.WIDTH + cell_width * y,
                                           cell_width,
                                           cell_width])

    def handle_click(self):
        m_x, m_y = self.pygame.mouse.get_pos()
        print(f'x: {m_x}; y: {m_y}')

        cell_width = self.WIDTH // self.COLUMNS

        x = 0
        while m_x > x * cell_width:
            x += 1

        y = 0
        while m_y > y * cell_width + self.HEIGHT - self.WIDTH:
            y += 1

        x -= 1
        y -= 1

        print(f'({x};{y})')

        self.color_cell(x, y)

    def color_cell(self, x, y):

        if self.current_ship == 0:
            if not self.have_neighbors(x, y, only_diagonal=True):
                self.game_field[x][y]['colored'] = True

    def have_neighbors(self, x, y, only_diagonal=False):
        for x_n in range(x-1, x+2, 1):
            for y_n in range(y-1, y+2, 1):
                try:
                    if self.game_field[x_n][y_n]['colored']:
                        if only_diagonal:
                            if x_n != x and y_n != y:
                                print(f'({x};{y}) have neighbor ({x_n},{y_n})')
                                return True
                        else:
                            print(f'({x};{y}) have neighbor ({x_n},{y_n})')
                            return True
                except IndexError:
                    pass

        # if x == 0:
        #     if only_diagonal:
        #         return self.game_field[x + 1][y + 1]['colored']
        #     if y == 0:
        #         return self.game_field[x + 1][y]['colored'] and self.game_field[x][y + 1]['colored']
        #     return self.game_field[x + 1][y]['colored'] and self.game_field[x][y + 1]['colored'] and \
        #            self.game_field[x][y - 1]['colored']





    def events_loop(self):
        while True:
            time.sleep(0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()
            self.render()


def main():
    game = GameClient()
    game.events_loop()


if __name__ == '__main__':
    main()
