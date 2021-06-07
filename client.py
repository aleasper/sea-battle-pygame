from client_network import NetworkClient
import pygame
import math
import time
import pickle
from pprint import pprint


class GameClient:
    def __init__(self):

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.PURPLE = (60,25,60)

        self.client = NetworkClient()

        self.field_size = None
        self.selected_sign = None
        self.sign = None
        self.msg_bottom = ''
        self.winner = None
        self.end_game = False

        self.pygame = pygame

        self.pygame.init()
        self.END_FONT = pygame.font.SysFont('Comic Sans MS', 20)

        # Screen
        self.WIDTH = 500
        self.WIN_HEIGHT = self.WIDTH + 100
        self.ROWS = 3
        self.win = self.pygame.display.set_mode((self.WIDTH, self.WIN_HEIGHT))
        self.win.fill(self.WHITE)
        self.pygame.display.set_caption("Крестики-нолики, автор: Виктория Дьяченко, гр 485")

        self.game_field = [[None, None, None], [None, None, None], [None, None, None]]



        # Images
        self.X_IMAGE = pygame.transform.scale(pygame.image.load("X.png"), (150, 150))
        self.O_IMAGE = pygame.transform.scale(pygame.image.load("o.png"), (150, 150))

        self.game_images = []
        while self.sign is None:
            self.pygame.draw.rect(self.win, self.PURPLE, [self.WIDTH / 2 - 70, self.WIN_HEIGHT / 2 - 25, 140, 40])
            textsurface_X = self.END_FONT.render('Играть за X', False, self.WHITE)
            self.win.blit(textsurface_X, (self.WIDTH / 2 - 70 + 5, self.WIN_HEIGHT / 2 - 25))

            self.pygame.draw.rect(self.win, self.PURPLE, [self.WIDTH / 2 - 70, self.WIN_HEIGHT / 2 + 25, 140, 40])
            textsurface_O = self.END_FONT.render('Играть за O', False, self.WHITE)
            self.win.blit(textsurface_O, (self.WIDTH / 2 - 70 + 5, self.WIN_HEIGHT / 2 + 25))

            self.pygame.display.update()
            selecting_sign = True

            while selecting_sign:
                time.sleep(0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.handle_click_start() is not None:
                            selecting_sign = False

            self.sign = self.client.get_sign(self.selected_sign)

            if self.sign is None:
                self.show_msg(f'Игрок за {self.selected_sign} уже есть')

        temp = True
        while self.field_size is None and not self.client.get_select_status()['selecting']:

            # Один раз отправить инфу о выборе размера поля
            if temp is True:
                temp = False
                self.client.set_select_status()

            self.draw_select_size()
            selecting_field = True
            while selecting_field:
                time.sleep(0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.handle_click_select_size() is not None:
                            selecting_field = False
                            self.client.set_field_size(self.field_size)

        while self.field_size is None:
            print('waiting')
            time.sleep(0.5)
            self.field_size = self.client.get_field_size()['size']
            self.draw_waiting_screen()
            self.pygame.display.update()
        self.ROWS = self.field_size
        self.game_field = [[None for i in range(self.ROWS)] for i in range(self.ROWS)]
        img_size = 150 if self.ROWS == 3 else 75
        self.X_IMAGE = pygame.transform.scale(pygame.image.load("X.png"), (img_size, img_size))
        self.O_IMAGE = pygame.transform.scale(pygame.image.load("o.png"), (img_size, img_size))
        self.msg_top = f'Вы играете за "{self.sign}"'
        self.draw_info()

    def handle_click_start(self):
        m_x, m_y = pygame.mouse.get_pos()
        if self.WIDTH / 2 - 70 < m_x < self.WIDTH / 2 + 70:
            if self.WIN_HEIGHT / 2 + 25 < m_y < self.WIN_HEIGHT / 2 + 65:
                print(f'selected sign: o')
                self.selected_sign = 'o'
                return True
            if self.WIN_HEIGHT / 2 - 25 < m_y < self.WIN_HEIGHT / 2 + 15:
                print(f'selected sign: x')
                self.selected_sign = 'x'
                return True
        return None

    def handle_click_select_size(self):
        m_x, m_y = pygame.mouse.get_pos()
        if self.WIDTH / 2 - 70 < m_x < self.WIDTH / 2 + 70:
            if self.WIN_HEIGHT / 2 + 25 < m_y < self.WIN_HEIGHT / 2 + 65:
                print(f'selected size: 5')
                self.field_size = 5
                return True
            if self.WIN_HEIGHT / 2 - 25 < m_y < self.WIN_HEIGHT / 2 + 15:
                print(f'selected size: 3')
                self.field_size = 3
                return True
        return None

    def show_msg(self, msg, timeuot=2):
        self.pygame.draw.rect(self.win, self.PURPLE, [self.WIDTH / 2 - 70, self.WIN_HEIGHT / 2 - 70, self.END_FONT.size(msg)[0] + 10, self.END_FONT.size(msg)[1] + 10])
        textsurface = self.END_FONT.render(msg, False, self.WHITE)
        self.win.blit(textsurface, (self.WIDTH / 2 - 70 + 5, self.WIN_HEIGHT / 2 -70))
        self.pygame.display.update()
        time.sleep(timeuot)
        self.win.fill(self.WHITE)
        self.pygame.display.update()

    def draw_waiting_screen(self):
        self.win.fill(self.WHITE)
        height_of_info_block = self.WIN_HEIGHT - self.WIDTH
        self.pygame.draw.rect(self.win, self.PURPLE, [0, 200, self.WIDTH, height_of_info_block])
        textsurface = self.END_FONT.render('Напарник выбирает размер поля', False, self.WHITE)
        text_size = self.END_FONT.size('Напарник выбирает размер поля')
        self.win.blit(textsurface, (self.WIDTH / 2 - text_size[0] / 2, 200))

    def draw_info(self):
        height_of_info_block = self.WIN_HEIGHT - self.WIDTH
        self.pygame.draw.rect(self.win, self.PURPLE, [0, 0, self.WIDTH, height_of_info_block])
        textsurface = self.END_FONT.render(self.msg_top, False, self.WHITE)
        text_size = self.END_FONT.size(self.msg_top)
        self.win.blit(textsurface, (self.WIDTH/2 - text_size[0]/2, 0))

    def add_bottom_smg(self):
        height_of_info_block = self.WIN_HEIGHT - self.WIDTH
        # self.pygame.draw.rect(self.win, self.PURPLE, [0, 0, self.WIDTH, height_of_info_block])
        textsurface = self.END_FONT.render(self.msg_bottom, False, self.WHITE)
        text_size = self.END_FONT.size(self.msg_bottom)
        self.win.blit(textsurface, (self.WIDTH/2 - text_size[0]/2, 40))

    def draw_grid(self):
        gap = self.WIDTH // self.ROWS
        # Starting points
        x = 0
        y = 0

        for i in range(self.ROWS):
            x = i * gap

            self.pygame.draw.line(self.win, self.GRAY, (x, self.WIN_HEIGHT - self.WIDTH), (x, self.WIN_HEIGHT), 3) # вертикальные линии
            self.pygame.draw.line(self.win, self.GRAY, (0, x + self.WIN_HEIGHT - self.WIDTH), (self.WIDTH, x + self.WIN_HEIGHT - self.WIDTH), 3) # горизонтальные

    def draw_select_size(self):
        self.pygame.draw.rect(self.win, self.PURPLE, [self.WIDTH / 2 - 70, self.WIN_HEIGHT / 2 - 25, 140, 40])
        textsurface_3x3 = self.END_FONT.render('Поле 3х3', False, self.WHITE)
        self.win.blit(textsurface_3x3, (self.WIDTH / 2 - 70 + 5, self.WIN_HEIGHT / 2 - 25))

        self.pygame.draw.rect(self.win, self.PURPLE, [self.WIDTH / 2 - 70, self.WIN_HEIGHT / 2 + 25, 140, 40])
        textsurface_5x5 = self.END_FONT.render('Поле 5х5', False, self.WHITE)
        self.win.blit(textsurface_5x5, (self.WIDTH / 2 - 70 + 5, self.WIN_HEIGHT / 2 + 25))

        self.pygame.display.update()

    def render(self):
        self.update_game_field()
        self.win.fill(self.WHITE)
        self.draw_grid()
        self.draw_info()
        self.add_bottom_smg()

        # Drawing X's and O's
        for image in self.game_images:
            x, y, IMAGE = image
            self.win.blit(IMAGE, (x - IMAGE.get_width() // 2, y - IMAGE.get_height() // 2))

        self.pygame.display.update()
        if self.end_game:
            time.sleep(2)
            self.end_screen()

    def update_game_field(self):
        res = self.client.get_game_field(self.sign)
        if res['status'] == 'ok':
            self.game_field = res['game_field']
            for i in range(len(self.game_field)):
                for j in range(len(self.game_field[i])):
                    try:
                        x, y, char, can_play = self.game_field[i][j]
                        if char == 'x':
                            self.game_images.append((x, y, self.X_IMAGE))

                        if char == 'o':
                            self.game_images.append((x, y, self.O_IMAGE))
                    except Exception:
                        pass
            if 'game_status' in res:
                self.winner = res['game_status']['winner']
                if self.winner is not None:
                    if len(self.msg_bottom) == 0:
                        if self.winner == self.sign:
                            self.msg_bottom = 'Победа!!!'
                        else:
                            self.msg_bottom = 'Поражение...'
                        self.end_game = True
                elif res['game_status']['end']:
                    self.end_game = True
                    self.msg_bottom = 'Ничья'



    def end_screen(self):
        self.win.fill(self.WHITE)
        self.pygame.draw.rect(self.win, self.PURPLE,
                              [self.WIDTH / 2 - 70, self.WIN_HEIGHT / 2 - 25, 140, 40])
        textsurface = self.END_FONT.render('Начать заново', False, self.WHITE)
        self.win.blit(textsurface, (self.WIDTH / 2 - 70 + 2, self.WIN_HEIGHT / 2 - 25))

        self.pygame.display.update()
        user_select = True
        while user_select:
            time.sleep(0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    res = self.handle_click_end()
                    if  res is not None:
                        user_select = False

        self.__init__()



    def handle_click_end(self):
        m_x, m_y = pygame.mouse.get_pos()
        if self.WIDTH / 2 - 70 < m_x < self.WIDTH / 2 + 70:
            if self.WIN_HEIGHT / 2 - 70 < m_y < self.WIN_HEIGHT / 2 + 70:
                self.client.reinit_server()
                return True
        return None


    def handle_click(self):
        # Mouse position
        m_x, m_y = pygame.mouse.get_pos()
        res = self.client.set_point(m_x, m_y, self.sign)
        if res['status'] == 'ok':
            self.game_field = res['game_field']
            # print('___________')
            # print(f'sign: {self.sign}')
            # pprint(self.game_field)
            # self.update_game_field()


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