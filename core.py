import pygame as pg
from time import sleep


class Tile:

    def __init__(self, length, width, field, num_x, num_y, game_dimension):
        self.length = length
        self.width = width
        self.field = field
        self.num_x = num_x
        self.num_y = num_y
        self.pos_x, self.pos_y = None, None
        self.status = 'empty'
        self.dimension = game_dimension

    # отрисовка тайла на поле
    def draw(self, startpoint: list, img, size):
        self.pos_x = startpoint[0] + self.num_x * size
        self.pos_y = startpoint[1] + self.num_y * size
        self.field.blit(img, (self.pos_x, self.pos_y))

    # проверка, был ли сделан клик по тайлу
    def is_collide(self, click_pos):
        if self.pos_x <= click_pos[0] <= self.pos_x + self.length and self.pos_y <= click_pos[1] <= \
                self.pos_y + self.width:
            return True
        else:
            return False

    # возвращение тайла к дефолт значению
    def restart_tile(self):
        self.status = 'empty'


class Window:

    def __init__(self, field, dimension):
        self.field = field
        self.dimension = dimension
        self.tile_size = 150
        self.tiles = []
        self.player_turn = True
        self.startpoint = [75, 100]
        self.free_fields = dimension ** 2
        self.main_diag = []
        self.side_diag = []
        self.game_over = False

        # добавление надписей
        self.font = pg.font.Font(None, 24)
        self.status = self.font.render('Игра началась!', 1, (180, 0, 0))
        self.field.blit(self.status, (10, 50))
        self.settings = self.font.render('Нажмите 3, 4 или 5 для выбора размерности.', 1, (180, 0, 0))
        self.field.blit(self.settings, (225, 50))
        for i in range(dimension):
            self.main_diag.append([i, i])
            self.side_diag.append([i, dimension - i - 1])

    # создание списка тайлов
    def create_tiles(self):
        for tile in self.tiles:
            tile.restart_tile()
        self.tiles = []
        for x in range(self.dimension):
            for y in range(self.dimension):
                self.tiles.append(Tile(self.tile_size, self.tile_size, self.field, x, y, self.dimension))
        self.fill_field(self.tiles)

    # заполнение игрового поля
    def fill_field(self, tiles):
        empty_field = pg.image.load('img/empty_field.png')
        empty_field = pg.transform.scale(empty_field, (self.tile_size, self.tile_size))
        for tile in tiles:
            tile.draw(self.startpoint, empty_field, self.tile_size)

    # поиск тайла по индексам
    def find_tile(self, num_x, num_y):
        for tile in self.tiles:
            if tile.num_x == num_x and tile.num_y == num_y:
                return tile

    # ход компьютера
    def make_turn(self):
        max_cross = 0
        max_zero = 0
        best_tile = None
        best_free_lines = 0
        zero = pg.image.load('img/nolik.png')
        zero = pg.transform.scale(zero, (self.tile_size, self.tile_size))

        # обработка ничьи и перезапуск игры
        if self.free_fields == 0:
            pg.draw.rect(self.field, [150, 150, 150], self.status.get_rect(topleft=(10, 50)))
            self.status = self.font.render('Ничья!', 1, (180, 0, 0))
            self.field.blit(self.status, (10, 50))
            pg.display.flip()
            sleep(1)
            pg.draw.rect(self.field, [150, 150, 150], self.status.get_rect(topleft=(10, 50)))
            self.status = self.font.render('Игра началась!', 1, (180, 0, 0))
            for tile in self.tiles:
                tile.restart_tile()
            return

        # нахождение лучшего тайла для хода
        for tile in self.tiles:
            if best_tile is None and tile.status == 'empty':
                best_tile = tile
                best_free_lines = self.check_free_lines(best_tile)
            coords = [tile.num_x, tile.num_y]
            if tile.status == 'empty':
                temp_cross = 1
                temp_zero = 1
                for idx in range(self.dimension):
                    temp_tile = self.find_tile(idx, tile.num_y)
                    temp_cross, temp_zero = self.update_temp(temp_tile, temp_cross, temp_zero)
                max_cross, max_zero, best_tile, best_free_lines = \
                    self.update_max(max_cross, max_zero, temp_cross, temp_zero, tile, best_tile, best_free_lines)
                temp_cross = 1
                temp_zero = 1
                for idx in range(self.dimension):
                    temp_tile = self.find_tile(tile.num_x, idx)
                    temp_cross, temp_zero = self.update_temp(temp_tile, temp_cross, temp_zero)
                max_cross, max_zero, best_tile, best_free_lines = \
                    self.update_max(max_cross, max_zero, temp_cross, temp_zero, tile, best_tile, best_free_lines)
                temp_cross = 1
                temp_zero = 1
                if coords in self.main_diag:
                    for elem in self.main_diag:
                        temp_tile = self.find_tile(elem[0], elem[1])
                        temp_cross, temp_zero = self.update_temp(temp_tile, temp_cross, temp_zero)
                        max_cross, max_zero, best_tile, best_free_lines = \
                            self.update_max(max_cross, max_zero, temp_cross, temp_zero, tile, best_tile, best_free_lines)
                temp_cross = 1
                temp_zero = 1
                if coords in self.side_diag:
                    for elem in self.side_diag:
                        temp_tile = self.find_tile(elem[0], elem[1])
                        temp_cross, temp_zero = self.update_temp(temp_tile, temp_cross, temp_zero)
                        max_cross, max_zero, best_tile, best_free_lines = \
                            self.update_max(max_cross, max_zero, temp_cross, temp_zero, tile, best_tile, best_free_lines)
        # отрисовка лучшего найденного тайла
        if self.free_fields > 0:
            best_tile.draw(self.startpoint, zero, self.tile_size)
            best_tile.status = 'zero'
            self.player_turn = True
            self.free_fields -= 1

            # обработка ничьи после хода компьютера
            if self.free_fields == 0:
                pg.draw.rect(self.field, [150, 150, 150], self.status.get_rect(topleft=(10, 50)))
                self.status = self.font.render('Ничья!', 1, (180, 0, 0))
                self.field.blit(self.status, (10, 50))
                pg.display.flip()
                sleep(1)
                pg.draw.rect(self.field, [150, 150, 150], self.status.get_rect(topleft=(10, 50)))
                self.status = self.font.render('Игра началась!', 1, (180, 0, 0))
                self.field.blit(self.status, (10, 50))
                self.free_fields = self.dimension ** 2
                self.create_tiles()
                self.player_turn = True

            # обработка победы компьютера
            if self.scan_field() != 2:
                pg.draw.rect(self.field, [150, 150, 150], self.status.get_rect(topleft=(10, 50)))
                self.status = self.font.render('Компьютер победил!', 1, (180, 0, 0))
                self.field.blit(self.status, (10, 50))
                pg.display.flip()
                sleep(1)
                pg.draw.rect(self.field, [150, 150, 150], self.status.get_rect(topleft=(10, 50)))
                self.status = self.font.render('Игра началась!', 1, (180, 0, 0))
                self.field.blit(self.status, (10, 50))
                self.free_fields = self.dimension ** 2
                self.create_tiles()
                self.player_turn = True
        else:
            # запасная проверка для исключения ошибок
            self.game_over = True
            sleep(1)
            self.game_over = False
            for tile in self.tiles:
                tile.restart_tile()

    # обновление временного максимума крестиков и ноликов по линиям
    @staticmethod
    def update_temp(tile, temp_c, temp_z):
        if tile.status == 'cross':
            temp_c += 1
        elif tile.status == 'zero':
            temp_z += 1
        return temp_c, temp_z

    # обновление наилучшего тайла
    def update_max(self, max_c, max_z, temp_c, temp_z, tile, best_tile, best_free_lines):
        if temp_c >= max_c and best_free_lines != 999 and tile.status == 'empty':
            max_c = temp_c
            # если выиграть следующим ходом не получается, и есть угроза проигрыша, то алгоритм будет пытаться
            # предотвратить ее
            if max_c == self.dimension:
                best_tile = tile
                best_free_lines = 999
        if ((temp_z >= max_z and max_c != self.dimension) or temp_z == self.dimension) and tile.status == 'empty':
            max_z = temp_z
            # наиболее предпочтителен тайл, который имеет большее кол-во свободных от крестиков линий
            # если есть выбор среди нескольких
            if self.check_free_lines(tile) > best_free_lines:
                best_tile = tile
                best_free_lines = self.check_free_lines(tile)
            # реализует возможность выигрыша следующим ходом
            if max_z == self.dimension:
                best_tile = tile
                best_free_lines = 999
        return max_c, max_z, best_tile, best_free_lines

    # поиск свободных от крестиков линий для тайла
    def check_free_lines(self, tile):
        count = 0
        temp = 0
        for num in range(self.dimension):
            if self.find_tile(num, tile.num_y).status != 'cross':
                temp += 1
            if temp == self.dimension:
                count += 1
        temp = 0
        for num in range(self.dimension):
            if self.find_tile(tile.num_x, num).status != 'cross':
                temp += 1
            if temp == self.dimension:
                count += 1
        temp = 0
        if [tile.num_x, tile.num_y] in self.main_diag:
            for elem in self.main_diag:
                if self.find_tile(elem[0], elem[1]).status != 'cross':
                    temp += 1
                if temp == self.dimension:
                    count += 1
        temp = 0
        if [tile.num_x, tile.num_y] in self.side_diag:
            for elem in self.side_diag:
                if self.find_tile(elem[0], elem[1]).status != 'cross':
                    temp += 1
                if temp == self.dimension:
                    count += 1
        return count

    # сканирование поля на предмет выигрыша одной из сторон
    # 0 - победа игрока, 1 - победа компьютера, 2 - продолжение игры
    def scan_field(self):
        for tile in self.tiles:
            cross_count, zero_count = 0, 0
            match tile.status:
                case 'cross':
                    for idx in range(self.dimension):
                        if self.find_tile(tile.num_x, idx).status == 'cross':
                            cross_count += 1
                        if cross_count == self.dimension:
                            return 0
                    cross_count = 0
                    for idx in range(self.dimension):
                        if self.find_tile(idx, tile.num_y).status == 'cross':
                            cross_count += 1
                        if cross_count == self.dimension:
                            return 0
                    cross_count = 0
                    if [tile.num_x, tile.num_y] in self.main_diag:
                        for elem in self.main_diag:
                            if self.find_tile(elem[0], elem[1]).status == 'cross':
                                cross_count += 1
                            if cross_count == self.dimension:
                                return 0
                    cross_count = 0
                    if [tile.num_x, tile.num_y] in self.side_diag:
                        for elem in self.side_diag:
                            if self.find_tile(elem[0], elem[1]).status == 'cross':
                                cross_count += 1
                            if cross_count == self.dimension:
                                return 0
                case 'zero':
                    for idx in range(self.dimension):
                        if self.find_tile(tile.num_x, idx).status == 'zero':
                            zero_count += 1
                        if zero_count == self.dimension:
                            return 1
                    zero_count = 0
                    for idx in range(self.dimension):
                        if self.find_tile(idx, tile.num_y).status == 'zero':
                            zero_count += 1
                        if zero_count == self.dimension:
                            return 1
                    zero_count = 0
                    if [tile.num_x, tile.num_y] in self.main_diag:
                        for elem in self.main_diag:
                            if self.find_tile(elem[0], elem[1]).status == 'zero':
                                zero_count += 1
                            if zero_count == self.dimension:
                                return 1
                    zero_count = 0
                    if [tile.num_x, tile.num_y] in self.side_diag:
                        for elem in self.side_diag:
                            if self.find_tile(elem[0], elem[1]).status == 'zero':
                                zero_count += 1
                            if zero_count == self.dimension:
                                return 1
        return 2
