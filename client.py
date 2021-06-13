from client_network import NetworkClient
import pygame
import math
import time
import pickle
from pprint import pprint

GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class GameClient:
    def __init__(self):

        self.WIDTH = 500
        self.SPACER = 50
        self.WIN_WIDTH = self.WIDTH * 2 + self.SPACER
        self.HEIGHT = 600
        self.ROWS = 10
        self.COLUMNS = self.ROWS

        self.pygame = pygame
        self.pygame.init()
        self.win = self.pygame.display.set_mode((self.WIN_WIDTH, self.HEIGHT))
        self.win.fill(WHITE)

        self.ships = [
            {'cells': 1, 'coords': [{'x': None, 'y': None} for i in range(1)]},
            {'cells': 1, 'coords': [{'x': None, 'y': None} for i in range(1)]},
            {'cells': 1, 'coords': [{'x': None, 'y': None} for i in range(1)]},
            {'cells': 1, 'coords': [{'x': None, 'y': None} for i in range(1)]},
            {'cells': 2, 'coords': [{'x': None, 'y': None} for i in range(2)]},
            {'cells': 2, 'coords': [{'x': None, 'y': None} for i in range(2)]},
            {'cells': 2, 'coords': [{'x': None, 'y': None} for i in range(2)]},
            {'cells': 3, 'coords': [{'x': None, 'y': None} for i in range(3)]},
            {'cells': 3, 'coords': [{'x': None, 'y': None} for i in range(3)]},
            {'cells': 4, 'coords': [{'x': None, 'y': None} for i in range(4)]},
        ]

        self.game_stages = ['placing', 'waiting', 'game', 'end']
        self.game_stage = self.game_stages[0]

        self.END_FONT = pygame.font.SysFont('Comic Sans MS', 20)

        self.game_field = [[{'x': col, 'y': row, 'colored': False} for col in range(self.COLUMNS)] for row in
                           range(self.ROWS)]

        self.game_field_enemy = [[{'x': col, 'y': row, 'colored': False, 'hit': False} for col in range(self.COLUMNS)] for row in
                                 range(self.ROWS)]

        self.network = NetworkClient()
        self.network.connect()

    def render(self):
        self.draw_grid()
        self.draw_cells()
        self.show_game_info()
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

        for i in range(self.ROWS):
            x = i * cell_width

            self.pygame.draw.line(self.win, GRAY,
                                  (x + self.WIDTH + self.SPACER, self.HEIGHT - self.WIDTH),
                                  (x + self.WIDTH + self.SPACER, self.HEIGHT), 3)  # вертикальные линии
            self.pygame.draw.line(self.win, GRAY,
                                  (0 + self.WIDTH + self.SPACER, x + self.HEIGHT - self.WIDTH),
                                  (self.WIDTH + self.WIDTH + self.SPACER, x + self.HEIGHT - self.WIDTH),
                                  3)  # горизонтальные

    def show_game_info(self):
        if self.game_stage == self.game_stages[0]:
            ship = self.get_current_empty_ship()
            if ship is not None:
                text = f'Расположите корабль с {ship["cells"]} палубами'
                textsurface = self.END_FONT.render(text, False, BLACK)
                self.win.blit(textsurface, (10, 10))
        if self.game_stage == self.game_stages[1]:
            text = f'Ожидание второго игрока'
            textsurface = self.END_FONT.render(text, False, BLACK)
            self.win.blit(textsurface, (10, 10))

        if self.game_stage == self.game_stages[2]:
            text = f'Ваш ход'
            textsurface = self.END_FONT.render(text, False, GREEN)
            self.win.blit(textsurface, (10, 10))

    def draw_cells(self):
        for x, col in enumerate(self.game_field):
            for y, cell in enumerate(col):
                if cell['colored']:
                    cell_width = self.WIDTH // self.COLUMNS
                    self.pygame.draw.rect(self.win, GREEN,
                                          [cell_width * x, self.HEIGHT - self.WIDTH + cell_width * y,
                                           cell_width,
                                           cell_width])

        for y, col in enumerate(self.game_field_enemy):
            for x, cell in enumerate(col):
                if cell['colored']:
                    cell_width = self.WIDTH // self.COLUMNS
                    self.pygame.draw.rect(self.win, RED if cell['hit'] else GRAY,
                                          [self.WIDTH + self.SPACER + cell_width * x, self.HEIGHT - self.WIDTH + cell_width * y,
                                           cell_width,
                                           cell_width])

    def handle_click(self):
        m_x, m_y = self.pygame.mouse.get_pos()
        cell_width = self.WIDTH // self.COLUMNS
        if self.game_stage == self.game_stages[0]:  # закраска своего поля
            x = 0
            while m_x > x * cell_width:
                x += 1

            y = 0
            while m_y > y * cell_width + self.HEIGHT - self.WIDTH:
                y += 1

            x -= 1
            y -= 1

            self.color_cell(x, y)

        if self.game_stage == self.game_stages[2]:  # лупим противника
            x = 0
            while m_x > x * cell_width + self.WIDTH + self.SPACER:
                x += 1
            y = 0
            while m_y > y * cell_width + self.HEIGHT - self.WIDTH:
                y += 1
            x -= 1
            y -= 1

            print(x, y)
            self.hit_emeny(x, y)

    def hit_emeny(self, x, y):
        print('hit', x, y)
        if 0 <= x < self.COLUMNS and 0 <= y < self.COLUMNS:
            if self.game_field_enemy[y][x]['colored']:
                print(x, y, 'already colored')
                print(self.game_field_enemy[x])
                return  # игнорируем уже закрашенные

            res = self.network.send_hit(x, y)
            print(res)

    def color_cell(self, x, y):
        if 0 <= x < self.COLUMNS and 0 <= y < self.COLUMNS:
            if self.game_field[x][y]['colored']: return  # игнорируем уже закрашенные
            # {'cells': 1, 'coords': [{'x': None, 'y': None} for i in range(1)]},
            if self.game_stage == self.game_stages[0]:
                for ship in self.ships:
                    for coord in ship['coords']:
                        if coord['x'] is None:
                            adding_new_ship = self.is_current_ship_new()
                            if not self.have_neighbors(x, y,
                                                       only_diagonal=not adding_new_ship):
                                self.game_field[x][y]['colored'] = True
                                coord['x'] = x
                                coord['y'] = y
                                return
                            else:
                                return

    def get_current_empty_ship(self):
        for ship in self.ships:
            empty = False
            for coord in ship['coords']:
                if coord['x'] is None:
                    empty = True
            if empty:
                return ship
        return None

    def get_all_ships(self):
        ships = []
        for ship in self.ships:
            for coord in ship['coords']:
                if coord['x'] is not None:
                    ships.append(ship)
                    break
        return ships

    def is_current_ship_new(self):
        ships = self.get_all_ships()
        for ship in ships:
            if ship['cells'] > len([True for i in ship['coords'] if i['x'] is not None]):
                return False
        return True

    def have_neighbors(self, x, y, only_diagonal=False):
        for x_n in range(x - 1, x + 2, 1):
            for y_n in range(y - 1, y + 2, 1):
                try:
                    if x < 0 or y < 0:
                        pass

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
        return False

    def check_game_status(self):
        if self.game_stage == self.game_stages[0]:
            ships = self.get_all_ships()
            ships = [ship for ship in ships if
                     len([coord for coord in ship['coords'] if coord['x'] is not None]) == ship['cells']]
            if len(ships) == 4 + 3 + 2 + 1:
                self.game_stage = self.game_stages[1]
                print('new game stage:', self.game_stage)
                pprint(ships)
                res = self.network.init_ships_server(ships)
                if not res['waiting']:
                    self.game_stage = self.game_stages[2]
                    print('GAME START!!!')

        if self.game_stage == self.game_stages[1]:
            res = self.network.is_opponent_ready()
            if not res['waiting']:
                self.game_stage = self.game_stages[2]
                print('GAME START!!!')

        if self.game_stage == self.game_stages[2]:
            res = self.network.get_fields()
            self.game_field_enemy = [[{
                'x': el['x'],
                'y': el['y'],
                'colored': el['colored'],
                'hit': self.is_hited_by_coord(res['enemy_ships'], el['x'], el['y'])
            } for el in line] for line in res['enemy_field']]


    @staticmethod
    def is_hited_by_coord(ships, x, y):
        for ship in ships:
            for coord in ship['coords']:
                if coord['x'] == x and coord['y'] == y:
                    return True

        return False




    def events_loop(self):
        while True:
            time.sleep(0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()

            self.check_game_status()
            self.render()


def main():
    game = GameClient()
    game.events_loop()


if __name__ == '__main__':
    main()
