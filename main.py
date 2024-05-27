
import sys

from core import *

pg.init()

# создание основного окна
screen = pg.display.set_mode((600, 600))
screen.fill([150, 150, 150])
window = Window(screen, 3)
window.create_tiles()

cross = pg.image.load('img/krestik.png')
cross = pg.transform.scale(cross, (window.tile_size, window.tile_size))

while True:

    for event in pg.event.get():

        # обработчик события выхода
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # обработчик нажатия мыши
        elif event.type == pg.MOUSEBUTTONDOWN:
            for tile in window.tiles:

                # поиск нажатого тайла
                if tile.is_collide(event.pos):

                    # если тайл свободен, то отрисовывается крестик и передается ход компьютеру
                    if window.player_turn and tile.status == 'empty' and not window.game_over:
                        tile.draw(window.startpoint, cross, window.tile_size)
                        tile.status = 'cross'
                        window.free_fields -= 1
                        window.player_turn = False

                        # обработка победы игрока
                        if window.scan_field() != 2:
                            pg.draw.rect(window.field, [150, 150, 150], window.status.get_rect(topleft=(10, 50)))
                            window.status = window.font.render('Вы победили!', 1, (180, 0, 0))
                            window.field.blit(window.status, (10, 50))
                            pg.display.flip()
                            sleep(1)
                            pg.draw.rect(window.field, [150, 150, 150], window.status.get_rect(topleft=(10, 50)))
                            window.status = window.font.render('Игра началась!', 1, (180, 0, 0))
                            window.field.blit(window.status, (10, 50))
                            window.create_tiles()
                            window.free_fields = window.dimension ** 2

                        # обработка ничьи
                        if window.free_fields == 0:
                            pg.draw.rect(window.field, [150, 150, 150], window.status.get_rect(topleft=(10, 50)))
                            window.status = window.font.render('Ничья!', 1, (180, 0, 0))
                            window.field.blit(window.status, (10, 50))
                            pg.display.flip()
                            sleep(1)
                            pg.draw.rect(window.field, [150, 150, 150], window.status.get_rect(topleft=(10, 50)))
                            window.status = window.font.render('Игра началась!', 1, (180, 0, 0))
                            window.field.blit(window.status, (10, 50))
                            window.create_tiles()
                            window.player_turn = True
                            window.free_fields = window.dimension ** 2

                        # ход компьютера
                        else:
                            window.make_turn()

                            # запасная обработка исключения
                            if window.scan_field() != 2:
                                window.game_over = True
                                sleep(1)
                                window.game_over = False
                                window.create_tiles()
                                window.free_fields = window.dimension ** 2

        # смена измерения
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_3:
                window.dimension = 3
                window.tile_size = 150
            elif event.key == pg.K_4:
                window.dimension = 4
                window.tile_size = 112.5
            elif event.key == pg.K_5:
                window.dimension = 5
                window.tile_size = 90
            else:
                continue

            # перезапуск игры после смены
            cross = pg.transform.scale(cross, (window.tile_size, window.tile_size))
            window.player_turn = True
            window.create_tiles()
            window.free_fields = window.dimension ** 2

    pg.display.flip()
