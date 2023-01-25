from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys
import random
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
from PyQt5.QtCore import QSize
"""
Импорт модуля генератора карт
"""
import mapgen


def load_image(name, color_key=None):
    """
    Функция возвращает изображение при получении пути к нему. Она
    может заменить монотонный фон на прозрачный при передаче
    color_key=-1
    """
    try:
        image = pygame.image.load(name)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Blader(pygame.sprite.Sprite):
    def __init__(self, group, number):
        image_1 = load_image("data/others/anim_blade1.png")
        image_2 = load_image("data/others/anim_blade2.png")
        super().__init__(group)
        if number == 1:
            self.image = image_1
        else:
            self.image = image_2
        self.rect = self.image.get_rect()
        if number == 1:
            self.rect.x = 189
            self.rect.y = 50
        else:
            self.rect.x = 940
            self.rect.y = 50
        self.number = number

    def update(self, *args):
        if self.number == 1:
            self.rect = self.rect.move(4, 0)
        else:
            self.rect = self.rect.move(-4, 0)

def map_generation():
    """
    Генератор карт комнат для игры. Возращает двумерный массив из символов.
    """
    movable = '1245678'
    all_objects = '000000000000000+-11224567889.'
    void = '0'
    Y_size = random.randint(20, 50)
    X_size = random.randint(20, 50)
    field = [["." for t in range(X_size)] for i in range(Y_size)]
    Y_hero = random.randint(1, Y_size - 2)
    X_hero = random.randint(1, X_size - 2)
    field[Y_hero][X_hero] = "&"
    number = random.randint(1, 4)
    X_boofer = X_hero
    Y_boofer = Y_hero
    if number == 1:
        X_boofer -= 1
        while X_boofer > 0:
            number = random.randint(0, 1)
            if number == "0":
                field[Y_boofer][X_boofer] = '0'
            else:
                field[Y_boofer][X_boofer] = random.choice(movable)
            X_boofer -= 1
    elif number == 2:
        X_boofer += 1
        while X_boofer < X_size - 1:
            number = random.randint(0, 1)
            if number == "0":
                field[Y_boofer][X_boofer] = '0'
            else:
                field[Y_boofer][X_boofer] = random.choice(movable)
            X_boofer += 1
    elif number == 3:
        Y_boofer -= 1
        while Y_boofer > 0:
            number = random.randint(0, 1)
            if number == "0":
                field[Y_boofer][X_boofer] = '0'
            else:
                field[Y_boofer][X_boofer] = random.choice(movable)
            Y_boofer -= 1
    else:
        Y_boofer += 1
        while Y_boofer < Y_size - 1:
            number = random.randint(0, 1)
            if number == "0":
                field[Y_boofer][X_boofer] = '0'
            else:
                field[Y_boofer][X_boofer] = random.choice(movable)
            Y_boofer += 1
    field[Y_boofer][X_boofer] = "?"
    rare_counter = 0
    for i in range(Y_size):
        for m in range(X_size):
            if field[i][m] != '.':
                continue
            addable = random.choice(all_objects)
            if addable == "9":
                if rare_counter:
                    while addable == "9":
                        addable = random.choice(all_objects)
                else:
                    rare_counter = 1
            field[i][m] = addable
    return field


def battle(playerHP, mobHP, playerAT, playerDF, mobAT, mobDF, mobTY):
    """
    Пошаговая обработка боевых событий. Происходит при взаимодействии игрока
    с любым враждебным мобом.
    """
    bool_continue = True
    result = 0
    while bool_continue:
        damage = playerAT - mobDF
        if damage < 2:
            damage = 2
        mobHP -= damage
        if mobHP <= 0:
            bool_continue = False
            result = 1
            break
        damage = mobAT - playerDF
        if mobTY == "2":
            if damage < 4:
                damage = 4
        else:
            if damage < 2:
                damage = 2
        playerHP -= damage
        if playerHP <= 0:
            bool_continue = False
            result = 2
            break
    return (playerHP, result)


class SettingsWindow(QMainWindow):
    def __init__(self):
        """
        Инициализация стартового окна настроек.
        """
        super().__init__()
        uic.loadUi('data/ui_files/settings.ui', self)
        self.setWindowIcon(QIcon('data/logo.png'))
        background = QImage('data/ui_files/background_settings.jpg')
        background_scaled = background.scaled(QSize(800, 600))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)
        self.start_but.clicked.connect(self.start_game)
        self.person = 2
        self.hero_switch.buttonClicked.connect(self.switcher)
        file = open("runs.txt", "r")
        spisok = []
        for x in file:
            element = x.rstrip("\n")
            element = element[0:len(element) - 1]
            number = ""
            for i in range(-1, -len(element), -1):
                if element[i] in "0123456789":
                    number = number + element[i]
            try:
                spisok.append([x.rstrip("\n"), int(number[::-1])])
            except ValueError:
                pass
        if spisok:
            spisok.sort(key=lambda x: x[1])
            self.linia.setText(spisok[-1][0])
        else:
            self.linia.setText("Нет")

    def start_game(self):
        """
        Обработка нажатия на кнопку "Начать", запуск pygame и закрытие
        окна настроек.
        """
        global executable, persona, name, now_hp, max_hp, damage, armor
        global counter
        persona = self.person
        if persona == 1:
            max_hp += 10
            now_hp += 10
            damage += 1
        elif persona == 2:
            armor += 2
        name = self.hero_name.text()
        counter = self.stage_counter.value()
        executable.close()
        start_pygame()

    def switcher(self):
        """
        Обработка взаимодействий с радиокнопками - нужны для выбора класса
        героя.
        """
        if self.rad_but_1.isChecked():
            self.person = 1
        elif self.rad_but_2.isChecked():
            self.person = 2
        elif self.rad_but_3.isChecked():
            self.person = 3


class Board:
    def __init__(self, texture_path='data/squares/floor_60p.png',
                 void_path='data/squares/void_60p.jpg',
                 ruin_path="data/squares/ruins.png",
                 potion_path='data/squares/potion.png',
                 door_path='data/squares/door.png',
                 artefact_path='data/squares/artefact.png',
                 goblin_path='data/squares/goblin.png',
                 skeleton_path='data/squares/skeleton.png',
                 ambrosia_path='data/squares/ambrosia.png',
                 armor_path='data/squares/armor.png',
                 barbarian_path='data/persons/barbarian.png',
                 thief_path='data/persons/thief.png',
                 knight_path='data/persons/knight.png',
                 health_path='data/others/health.png',
                 armor_ui_path='data/others/armor.png',
                 blade_path='data/others/blade.png',
                 size=60, skip=0):
        """
        Инициализация основного класса игры, подгрузка необходимой графики.
        """
        global persona
        self.lv = 0
        self.seed = random.choice(["alpha", "beta", "charlie", "delta"]) + "-" + str(random.randint(1, 88888888))
        self.map_size = [10,40]
        randomizer = random.randint(0, 1)
        if randomizer:
            self.all_map = map_generation()
        else:
            self.all_map = mapgen.mapgen(self.seed, self.lv, self.map_size)
        self.stroka = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.texture = load_image(texture_path)
        self.void = load_image(void_path)
        self.ruins = load_image(ruin_path, -1)
        self.potion = load_image(potion_path)
        self.door = load_image(door_path)
        self.artefact = load_image(artefact_path)
        self.goblin = load_image(goblin_path)
        self.skeleton = load_image(skeleton_path)
        self.ambrosia = load_image(ambrosia_path)
        self.armor = load_image(armor_path)
        self.health_heart = load_image(health_path)
        self.armor_ui = load_image(armor_ui_path)
        self.blade = load_image(blade_path)
        if persona == 1:
            self.game_model = load_image(barbarian_path, -1)
        elif persona == 2:
            self.game_model = load_image(knight_path, -1)
        elif persona == 3:
            self.game_model = load_image(thief_path)
        self.size = size
        self.skip = skip
        self.font = pygame.font.SysFont("bahnschrift", 32)
        self.output = self.font.render("", 1, (0xff, 0xff, 0xff))
        self.lenY = len(self.all_map)
        self.lenX = 0
        for x in self.all_map:
            length = len(x)
            if length > self.lenX:
                self.lenX = length
        stop_search = False
        for b in range(self.lenY):
            for n in range(self.lenX):
                if self.all_map[b][n] == "&":
                    self.playerX = n
                    self.playerY = b
                    stop_search = True
                    break
            if stop_search:
                break
        self.all_map[self.playerY][self.playerX] = "0"


    def render(self, screen):
        """
        Функция служит для отображения текущего состояния поля на экране.
        """
        global persona, now_hp, max_hp, damage, armor, name, score
        PX = screen_size[0] // 2
        PY = screen_size[1] // 2
        X = self.skip
        Y = 800 - self.lenY * (self.size + self.skip)        
        for a in range(self.lenY):
            for b in range(self.lenX):
                APX = (-self.playerX + b) * self.size
                APY = (-self.playerY + a) * self.size
                if self.all_map[a][b] in "0*":
                    screen.blit(self.texture, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "-":
                    screen.blit(self.void, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "+":
                    screen.blit(self.ruins, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] in "458":
                    screen.blit(self.potion, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "9":
                    screen.blit(self.artefact, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "1":
                    screen.blit(self.goblin, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "2":
                    screen.blit(self.skeleton, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "3":
                    pass  # Резерв для дополнительного монстра
                elif self.all_map[a][b] == "7":
                    screen.blit(self.ambrosia, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "6":
                    screen.blit(self.armor, (PX + APX, PY + APY, self.size, self.size))
                elif self.all_map[a][b] == "?":
                    screen.blit(self.door,
                                (PX + APX, PY + APY, self.size, self.size))
                if a == self.playerY and b == self.playerX:
                    screen.blit(self.game_model,
                                (PX, PY, self.size, self.size))
                X += self.size + self.skip
            X = self.skip
            Y += self.size + self.skip
        text = self.font.render(str(now_hp) + '/' +
                           str(max_hp), 1, (0xff, 0xff, 0xff))
        screen.blit(text, (60, 8))
        text = self.font.render(str(armor), 1, (0xff, 0xff, 0xff))
        screen.blit(text, (240, 8))
        text = self.font.render(str(damage), 1, (0xff, 0xff, 0xff))
        screen.blit(text, (350, 8))
        if persona == 1:
            output = str(name) + ", варвар"
        elif persona == 2:
            output = str(name) + ", рыцарь"
        elif persona == 3:
            output = str(name) + ", плут"
        text = self.font.render(output, 1, (0xff, 0xff, 0xff))
        screen.blit(text, (420, 8))
        text = self.font.render(str(score), 1, (0xff, 0xff, 0xff))
        screen.blit(text, (1100, 8))
        screen.blit(self.health_heart, (10, 10, self.size, self.size))
        screen.blit(self.armor_ui, (190, 10, self.size, self.size))
        screen.blit(self.blade, (295, 10, self.size, self.size))
        screen.blit(self.output, (15, 48 + 8))


    def move_hero(self, screen, side):
        """
        Функция отвечает за взаимодействие главного героя с полем и его
        перемещение.
        """
        global persona, now_hp, max_hp, damage, armor, name, score
        global counter, now_counter, screen_size
        if persona == 1:
            addtext = 'варвар'
        elif persona == 2:
            addtext = 'рыцарь'
        else:
            addtext = 'плут'
        output = f"{name}, {addtext} - счёт {score}."
        font = pygame.font.SysFont("bahnschrift", 24)
        text = font.render("", 1, (0xff, 0xff, 0xff))
        Y = self.playerY
        X = self.playerX
        try_Y = Y
        try_X = X
        if side == "right":
            try_X += 1
        elif side == "left":
            try_X -= 1
        elif side == "up":
            try_Y -= 1
        elif side == "down":
            try_Y += 1
        if try_X < 0 or try_Y < 0:
                return
        if try_X > self.lenX - 1 or try_Y > self.lenY - 1:
            return
        field_point = self.all_map[try_Y][try_X]
        if field_point in "0*":
            self.playerY = try_Y
            self.playerX = try_X
        elif field_point == "+":
            return
        elif field_point == "-":
            if persona == 3:
                return
            else:
                now_hp = 0
                self.playerY = try_Y
                self.playerX = try_X
                death_screen(screen, output)
                pygame.display.quit()
                pygame.quit()
                sys.exit()
        elif field_point in "123":
            if field_point == "1":
                mobHP = 24 + random.randint(-4, 5) + now_counter * 3
                mobAT = 8 + random.randint(-2, 3) + now_counter * 2
                mobDF = 7 + random.randint(-2, 3) + now_counter * 2
                mobTY = 1
                text = font.render(
                    "Вы сразились с гоблином!",
                    1, (0xff, 0xff, 0xff))
            elif field_point == "2":
                mobHP = 32 + random.randint(-4, 7) + now_counter * 3
                mobAT = 10 + random.randint(-2, 5) + now_counter * 2
                mobDF = 5 + random.randint(-2, 3) + now_counter * 2
                mobTY = 2
                text = font.render(
                    "Вы сразились со скелетом!",
                    1, (0xff, 0xff, 0xff))
            battle_result = battle(
                now_hp, mobHP, damage, armor, mobAT, mobDF, mobTY)
            now_hp = battle_result[0]
            if battle_result[1] == 1:
                if mobTY == 1:
                    score += 60 + random.randint(-10, 10)
                elif mobTY == 2:
                    score += 80 + random.randint(-10, 10)
                if persona == 3:
                    score += random.randint(1, 5)
                self.playerY = try_Y
                self.playerX = try_X
                self.all_map[self.playerY][self.playerX] = "0"
            else:
                death_screen(screen, output)
                pygame.display.quit()
                pygame.quit()
                sys.exit()                
        elif field_point == "4":
            now_hp += 30
            if now_hp > max_hp:
                now_hp = max_hp
            text = font.render(
                "Применено зелье регенерации (+30 к текущему здоровью)",
                1, (0xff, 0xff, 0xff))
            self.all_map[try_Y][try_X] = "0"
            self.playerY = try_Y
            self.playerX = try_X
            if persona == 3:
                score += 6
            else:
                score += 5
        elif field_point == "5":
            damage += 1
            text = font.render(
                "Применено зелье силы (+1 к урону по противникам)",
                1, (0xff, 0xff, 0xff))
            self.all_map[try_Y][try_X] = "0"
            self.playerY = try_Y
            self.playerX = try_X
            if persona == 3:
                score += 6
            else:
                score += 5
        elif field_point == "7":
            max_hp += 5
            now_hp = max_hp
            text = font.render(
                "Употреблена амброзия (+5 к максимальному здоровью,"
                + " полное восстановление текущего здоровья)",
                1, (0xff, 0xff, 0xff))
            self.all_map[try_Y][try_X] = "0"
            self.playerY = try_Y
            self.playerX = try_X
            if persona == 3:
                score += 8
            else:
                score += 6
        elif field_point == "6":
            armor += 1
            text = font.render(
                "Получено улучшение доспеха (+1 к броне)", 1, (0xff, 0xff, 0xff))
            self.all_map[try_Y][try_X] = "0"
            self.playerY = try_Y
            self.playerX = try_X
            score += 5
        elif field_point == "8":
            now_hp -= 30
            text = font.render(
                "Применено зелье отравления (-30 к текущему здоровью)",
                1, (0xff, 0xff, 0xff))
            self.all_map[try_Y][try_X] = "0"
            self.playerY = try_Y
            self.playerX = try_X
        elif field_point == "9":
            max_hp += 10
            armor += 1
            damage += 1
            text = font.render(
                "Найдено сокровище! (+10 к максимальному"
                + " здоровью, +1 к параметрам)",
                1, (0xff, 0xff, 0xff))
            self.all_map[try_Y][try_X] = "0"
            self.playerY = try_Y
            self.playerX = try_X
            if persona == 3:
                score += 160
            else:
                score += 150
        elif field_point == "?":
            if persona == 3:
                score += 110
            else:
                score += 100
            now_counter += 1
            if now_counter == counter:
                with open("runs.txt", "a") as myfile:
                    if persona == 1:
                        addtext = 'варвар'
                    elif persona == 2:
                        addtext = 'рыцарь'
                    else:
                        addtext = 'плут'
                    myfile.write(f"{name}, {addtext} - счёт {score}.\n")
                win_screen(screen, output)
                pygame.display.quit()
                pygame.quit()
                sys.exit()                
            self.change_map()
        elif field_point == ".":
            return
        if now_hp <= 0:
            death_screen(screen, output)
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        self.output = text

    def change_map(self, size=60, skip=5):
        """
        Функция вызывается при необходимости сменить карту при переходе в
        другую комнату.
        """
        self.lv += 1
        randomizer = random.randint(0, 1)
        if randomizer:
            self.all_map = map_generation()
        else:
            self.all_map = mapgen.mapgen(self.seed, self.lv, self.map_size)
        self.stroka = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.size = size
        self.skip = skip
        self.output = self.font.render("", 1, (0xff, 0xff, 0xff))
        self.lenY = len(self.all_map)
        self.lenX = 0
        for x in self.all_map:
            length = len(x)
            if length > self.lenX:
                self.lenX = length
        stop_search = False
        for b in range(self.lenY):
            for n in range(self.lenX):
                if self.all_map[b][n] == "&":
                    self.playerX = n
                    self.playerY = b
                    stop_search = True
                    break
            if stop_search:
                break
        self.all_map[self.playerY][self.playerX] = "0"        


def stop_running():
    """
    Функция вызывается для закрытия окна pygame и выхода из программы.
    """
    pygame.quit()
    sys.exit()


def start_screen(screen_size):
    """
    Функция отвечает за отображение стартового окна игры.
    """
    global bool_running
    background = pygame.transform.scale(load_image(
        'data/background.jpg'), screen_size)
    screen.blit(background, (0, 0))
    start_screen = True
    all_sprites = pygame.sprite.Group()
    Blader(all_sprites, 1)
    Blader(all_sprites, 2)
    booler = 0
    boofer = 0
    texture = load_image("data/others/megalogo.png")
    while start_screen:
        screen.blit(background, (0, 0))
        if booler:
            screen.blit(texture, (boofer, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start_screen = False
                bool_running = False
                pygame.quit()
                break
            elif (event.type == pygame.KEYDOWN
                  or event.type == pygame.MOUSEBUTTONDOWN):
                start_screen = False
                break
        if not start_screen:
            break
        all_sprites.draw(screen)
        all_sprites.update()
        rects = []
        for x in all_sprites:
            rects.append(x.rect.x)
        if rects:
            if rects[0] + 151 >= rects[1]:
                all_sprites = pygame.sprite.Group()
                screen.blit(texture, (rects[0] + 80, 50))
                booler = 1
                boofer = rects[0] + 80
        pygame.display.flip()
        clock.tick(FPS)


def death_screen(screen, output):
    """
    Функция отвечает за отображение окна смерти в случае проигрыша.
    """
    background = load_image('data/dead.png')
    screen.blit(background, (0, 0))
    death_screen = True
    font = pygame.font.SysFont("bahnschrift", 24)
    text = font.render(output, 1, (0xff, 0xff, 0xff))
    screen.blit(text, (30, 750))
    while start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                death_screen = False
                bool_running = False
                pygame.quit()
                return
            elif (event.type == pygame.KEYDOWN
                  or event.type == pygame.MOUSEBUTTONDOWN):
                death_screen = False
                bool_running = False
                pygame.quit()
                return
        if not death_screen:
            break
        pygame.display.flip()
        clock.tick(FPS)


def win_screen(screen, output):
    """
    Функция отвечает за отображение окна при победе игрока.
    """
    background = load_image('data/win.jpg')
    screen.blit(background, (0, 0))
    death_screen = True
    font = pygame.font.SysFont("bahnschrift", 24)
    text = font.render(output, 1, (0xff, 0xff, 0xff))
    screen.blit(text, (30, 750))
    while start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                death_screen = False
                bool_running = False
                pygame.quit()
                return
            elif (event.type == pygame.KEYDOWN
                  or event.type == pygame.MOUSEBUTTONDOWN):
                death_screen = False
                bool_running = False
                pygame.quit()
                return
        if not death_screen:
            break
        pygame.display.flip()
        clock.tick(FPS)


def start_pygame():
    """
    Функция инициализирует pygame и экран, создаёт экземпляр класса Board.
    """
    global screen, screen_size, icon, clock, FPS, bool_running
    global global_massage
    pygame.init()
    screen_size = (1280, 800)
    screen = pygame.display.set_mode(screen_size)
    icon = pygame.image.load('data/logo.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Magic Heroes')
    clock = pygame.time.Clock()
    FPS = 60
    start_screen(screen_size)
    if bool_running is False:
        return
    bool_can_move = True
    field = Board()
    back_texture = pygame.transform.scale(load_image(
        'data/ui_files/background.jpg'), screen_size)
    while bool_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bool_running = False
                pygame.quit()
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    field.move_hero(screen, 'up')
                elif event.key == pygame.K_DOWN:
                    field.move_hero(screen, 'down')
                elif event.key == pygame.K_LEFT:
                    field.move_hero(screen, 'left')
                elif event.key == pygame.K_RIGHT:
                    field.move_hero(screen, 'right')
        if not bool_running:
            break
        screen.blit(back_texture, (0, 0, *(screen_size)))
        field.render(screen)
        clock.tick(FPS)
        pygame.display.flip()


def except_hook(cls, exception, traceback):
    """
    Функция для захвата ошибок, используется для запуска с открытой консолью.
    """
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    bool_running = True
    persona = 0
    name = "NoName"
    now_hp = 100
    max_hp = 100
    damage = 8
    armor = 8
    score = 0
    counter = 0
    now_counter = 0
    application = QApplication(sys.argv)
    executable = SettingsWindow()
    executable.show()
    sys.excepthook = except_hook
    sys.exit(application.exec_())
    screen_size = (1280, 800)
    screen = 0
    icon = 0
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Magic Heroes')
    clock = 0
    FPS = 0
