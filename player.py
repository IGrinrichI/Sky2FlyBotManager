import datetime
import json
import math
import random
import time
import os
import sys
import cv2
import numpy as np
import win32con


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


coord_imgs = {
    "0": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_0.bmp'))),
    "1": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_1.bmp'))),
    "2": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_2.bmp'))),
    "3": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_3.bmp'))),
    "4": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_4.bmp'))),
    "5": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_5.bmp'))),
    "6": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_6.bmp'))),
    "7": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_7.bmp'))),
    "8": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_8.bmp'))),
    "9": cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_9.bmp'))),
    ':': cv2.imread(resource_path(os.path.join('images', 'radar_coordinate_split.bmp'))),
}
enemy_locked_on = cv2.imread(resource_path(os.path.join('images', 'enemy_locked_on.bmp')))
service_button = cv2.imread(resource_path(os.path.join('images', 'service.bmp')))
service_all_button = cv2.imread(resource_path(os.path.join('images', 'service_all.bmp')))
take_all_button = cv2.imread(resource_path(os.path.join('images', 'take_all.bmp')))
storage_button = cv2.imread(resource_path(os.path.join('images', 'storage.bmp')))
all_to_storage_button = cv2.imread(resource_path(os.path.join('images', 'all_to_storage.bmp')))
tunnel_img = cv2.imread(resource_path(os.path.join('images', 'tunnel.bmp')))
tunnel_window_title = cv2.imread(resource_path(os.path.join('images', 'tunnel_window_title.bmp')))
tunnel_window_base_title = cv2.imread(resource_path(os.path.join('images', 'tunnel_window_base_title.bmp')))


class Player:
    warp_bias = 7
    target_bias = 3
    stuck_delay = 3
    stuck_difference = 1.5
    direction_bias = 0.1
    radar_coords = (0, 0)
    target_coords = (0, 0)
    target_direction = (0, 0)
    target_angle = 0
    target_distance = 0
    player_direction = (0, 0)
    player_angle = 0
    player_direction_certain = False
    circle_area = True
    # Если зона - не круг
    area_points = []
    area_edges = []
    # Если зона - круг
    area_coords = (50, 50)
    area_direction = (0, 0)
    distance_to_area = 0
    min_distance_from_area = 7
    max_distance_away_from_area = 11

    farm_start_time = time.time()
    max_farm_time = 300

    abilities = []
    enemy_types = ['neutral', 'agressive', 'special']
    smart_targeting = True
    fire_when_smart_targeting = True
    stop_if_enemy_in_front_of_ship = True
    stop_at_destination = False
    jump_forward_on_lose_target = True
    enemy_focused = False
    last_time_enemy_focused = 0
    enemy_focusing_max_time = 1
    enemy_focused_at = 0
    enemy_kill_timeout = 10

    available_directions_to_undock = ['с', 'ю', 'в', 'з', 'св', 'сз', 'юв', 'юз']
    coords_to_undock = {
        'с': (-131, 33),
        'сз': (-180, 55),
        'з': (-198, 106),
        'юз': (-178, 159),
        'ю': (-133, 177),
        'юв': (-77, 155),
        'в': (-58, 104),
        'св': (-79, 58),
    }
    fly_trough_tunnel_tries_amount = 5

    radar_to_global_ratio = 10 / 90
    # cx = 1786.5
    cx = 1786.5 - 1920
    cy = 106.5
    _center = (cx, cy)
    r = 7.5
    w = 2.75
    wr = round(w + 2, 0)
    green_buff = 1.07

    press_esc_after_radar_action = False
    force_key = 'f'
    force_forward_key = 'q'
    force_left_key = 'x'
    force_right_key = 'c'
    forward_key = 'w'
    break_target_key = 'z'
    fire_key = ' '

    _ocr_reader = None

    def __init__(self, clicker):
        self.clicker = clicker

    def activate_abilities(self):
        for ability in self.abilities:
            self.clicker.keypress(f'^{ability}')
            time.sleep(.5)

    @property
    def ocr_reader(self):
        if self._ocr_reader is None:
            from easyocr import Reader
            self._ocr_reader = Reader(['ru'], gpu=False)
            # from paddleocr import PaddleOCR
        return self._ocr_reader

    def undock(self, available_directions_to_undock=None):
        available_directions_to_undock = available_directions_to_undock if available_directions_to_undock else self.available_directions_to_undock
        if available_directions_to_undock:
            direction = random.choice(available_directions_to_undock)
            direction = direction if direction in self.coords_to_undock else 'с'
            print(datetime.datetime.now(), f'Вылет в направлении "{direction}"')
            self.clicker.click(*self.coords_to_undock[direction])
        return True

    @property
    def center(self):
        return (
            self.clicker.screen_width + self.cx if self.cx < 0 else self.cx,
            self.clicker.screen_height + self.cy if self.cy < 0 else self.cy
        )

    def is_overweight(self):
        self.clicker.screen_lookup(window=(150, 0, 300, 40))
        return self.clicker.find_pixel(color=(205, 49, 55)) is not None

    def is_farming(self):
        return time.time() - self.farm_start_time < self.max_farm_time and not self.is_overweight()

    @property
    def in_combat(self):
        return time.time() - self.last_time_enemy_focused < self.enemy_focusing_max_time

    @in_combat.setter
    def in_combat(self, state):
        if state:
            self.last_time_enemy_focused = time.time()
        else:
            self.last_time_enemy_focused = 0

    def calc_edges(self):
        if not self.circle_area:
            area_points = self.area_points
            self.area_edges = [(p1, p2) for p1, p2 in zip(area_points[:-1], area_points[1:])]
            self.area_edges.append((area_points[-1], area_points[0]))

    def in_area(self, coord=None):
        if self.circle_area:
            if coord is None:
                self.lookup_coords()
                distance_to_area = self.distance_to_area
            else:
                distance_to_area = math.dist(coord, self.area_coords)
            return distance_to_area <= self.max_distance_away_from_area
        else:
            edges = self.area_edges
            if coord is None:
                xp, yp = self.radar_coords
            else:
                xp, yp = coord
            cross_count = 0

            for edge in edges:
                (x1, y1), (x2, y2) = edge
                if (yp < y1) != (yp < y2) and xp < x1 + ((yp - y1) / (y2 - y1)) * (x2 - x1):
                    cross_count += 1

            return cross_count % 2 == 1

    def store_resources_and_service(self):
        # Сервис
        self.clicker.screen_lookup(window=(-600, -75, -1, -1))
        service = self.clicker.find_image(service_button, threshold=.99)
        print(datetime.datetime.now(), 'Сервис')
        if service:
            self.clicker.click(*service[0])
        time.sleep(2)
        self.clicker.screen_lookup()
        service_all = self.clicker.find_image(service_all_button, threshold=.8)
        print(datetime.datetime.now(), 'Зарядить всё')
        if service_all:
            self.clicker.click(*service_all[0])
        time.sleep(2)
        # Склад
        self.clicker.screen_lookup(window=(-600, -75, -1, -1))
        storage = self.clicker.find_image(storage_button, threshold=.99)
        print(datetime.datetime.now(), 'Склад')
        if storage:
            self.clicker.click(*storage[0])
        time.sleep(2)
        self.clicker.screen_lookup(window=(0, -150, -1, -1))
        store_all = self.clicker.find_image(all_to_storage_button, threshold=.99)
        print(datetime.datetime.now(), 'Всё на склад')
        if store_all:
            self.clicker.click(*store_all[0])

    def break_target(self):
        self.clicker.keypress(self.break_target_key)
        self.enemy_focused = False

    def is_locked_on_enemy(self):
        self.clicker.screen_lookup(window=(400, 0, -325, 100))
        if self.clicker.find_image(enemy_locked_on, threshold=.99):
            self.enemy_focused = True
            return self.enemy_focused
        else:
            self.enemy_focused = False
            return self.enemy_focused

    def locate_enemies(self):
        if not self.enemy_types:
            return []
        # start = time.time()
        self.clicker.screen_lookup(window=(-225, 15, -40, 200))
        neutral_enemies = []
        if 'neutral' in self.enemy_types:
            enemy_replace_pixels = 5
            neutral_enemy = self.clicker.find_pixel(color=(221, 221, 221))
            while neutral_enemy:
                neutral_enemies.append(neutral_enemy)
                self.clicker.fill(
                    window=(neutral_enemy[0] - enemy_replace_pixels, neutral_enemy[1] - enemy_replace_pixels,
                            neutral_enemy[0] + enemy_replace_pixels, neutral_enemy[1] + enemy_replace_pixels),
                    color=(0, 0, 0)
                )
                neutral_enemy = self.clicker.find_pixel(color=(221, 221, 221))

        aggressive_enemies = []
        if 'agressive' in self.enemy_types:
            enemy_replace_pixels = 5
            aggressive_enemy = self.clicker.find_pixel(color=(255, 0, 0))
            while aggressive_enemy:
                if math.dist(aggressive_enemy, self.center) < 90:
                    valid_pixel = True
                    pxl = self.clicker.pixel(aggressive_enemy[0] - 1, aggressive_enemy[1])
                    any_dark_pixel = pxl[1] == pxl[2] and abs(pxl[0] + pxl[1] * 5) % 255 < pxl[1]
                    # any_dark_pixel = False
                    # pixels_to_check = [#(-1, -1), (-1, 0), (0, -1),
                    #                    (1, 0), (2, 0), (3, 0), (4, 0),
                    #                    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
                    #                    ]
                    # for pi in pixels_to_check:
                    #     pixel = self.clicker.pixel(aggressive_enemy[0] + pi[0], aggressive_enemy[1] + pi[1])
                    #     is_dark_pixel = ((pixel[0] - pixel[1] > 100 and pixel[0] - pixel[2] > 100)
                    #                      or (pixel[0] > 100 and pixel[1] < 50 and pixel[2] < 50)
                    #                      or (abs(pixel[0] - pixel[1]) < 15 and abs(pixel[0] - pixel[2]) < 15 and abs(pixel[1] - pixel[2]) < 15))
                    #     any_dark_pixel = any_dark_pixel or is_dark_pixel
                    #     if not (all(pixel == (255, 0, 0)) or is_dark_pixel):
                    #         valid_pixel = False
                    #         # print(pixel)
                    #         break
                    if valid_pixel and any_dark_pixel:
                        aggressive_enemies.append(aggressive_enemy)
                self.clicker.fill(
                    window=(aggressive_enemy[0] - enemy_replace_pixels, aggressive_enemy[1] - enemy_replace_pixels,
                            aggressive_enemy[0] + enemy_replace_pixels, aggressive_enemy[1] + enemy_replace_pixels),
                    color=(0, 0, 0)
                )
                aggressive_enemy = self.clicker.find_pixel(color=(255, 0, 0))

        special_enemies = []
        if 'special' in self.enemy_types:
            enemy_replace_pixels = 7
            special_enemy = self.clicker.find_pixel(color=(139, 0, 255))
            while special_enemy:
                special_enemies.append(special_enemy)
                self.clicker.fill(
                    window=(special_enemy[0] - enemy_replace_pixels, special_enemy[1] - enemy_replace_pixels,
                            special_enemy[0] + enemy_replace_pixels, special_enemy[1] + enemy_replace_pixels),
                    color=(0, 0, 0)
                )
                special_enemy = self.clicker.find_pixel(color=(139, 0, 255))

        enemies = neutral_enemies + aggressive_enemies + special_enemies

        directions = {coord: (coord[0] - self.center[0], coord[1] - self.center[1]) for coord in enemies}
        enemies = sorted(enemies, key=lambda coord: math.dist(coord, self.center) * (2 - np.dot(directions[coord] / np.linalg.norm(directions[coord]), self.player_direction)))
        # print(self.player_direction, [(enemy[0] - self.center[0], enemy[1] - self.center[1]) for enemy in enemies])
        # print(time.time() - start)
        # for index, enemy in enumerate(enemies):
        #     self.clicker.fill(window=(*enemy, *enemy),
        #                  color=(255 - int(255 / len(enemies)) * index, 0, 0))
        # cv2.imwrite('screen.png', self.clicker.screen)
        return enemies

    def is_enemy_valid(self, enemy_coord):
        # Проверка, что цель не находится за границей зоны фарма
        enemy_global_coord = (
            (enemy_coord[0] - self.center[0]) * self.radar_to_global_ratio + self.radar_coords[0],
            (enemy_coord[1] - self.center[1]) * self.radar_to_global_ratio + self.radar_coords[1]
        )
        if not self.in_area(enemy_global_coord):
            return False

        # Проверка, что цель находится не в черте города
        # Как правило, нужна только если мы где-то рядом с минимальной границей окружности
        # иначе триггерится на зону ветров
        if self.distance_to_area > self.min_distance_from_area:
            return True

        distance_to_enemy = math.dist(enemy_coord, self.center)
        enemy_direction = (
            (enemy_coord[0] - self.center[0]) / distance_to_enemy,
            (enemy_coord[1] - self.center[1]) / distance_to_enemy
        )
        cos_enemy_city = np.dot(self.area_direction, enemy_direction)
        if distance_to_enemy > 20 and cos_enemy_city > 0:
            for pixel_index in range(4, int(distance_to_enemy) - 10, 1):
                outer_target_pixel = self.clicker.pixel(
                    enemy_coord[0] - int(enemy_direction[0] * pixel_index),
                    enemy_coord[1] - int(enemy_direction[1] * pixel_index)
                )
                if all(outer_target_pixel != (0, 0, 0)):
                    pixel_is_city = (
                            -2 <= outer_target_pixel[1] - outer_target_pixel[0] <= 30
                            and abs(outer_target_pixel[1] - outer_target_pixel[2]) <= 30
                    )
                    if pixel_is_city:
                        # print('ILLEGAL', outer_target_pixel)
                        return False
        return True

    def target_and_kill(self):
        last_focus_state = self.enemy_focused
        locked_on_enemy = self.is_locked_on_enemy()

        if not last_focus_state and locked_on_enemy:
            self.enemy_focused_at = time.time()
        elif locked_on_enemy and time.time() - self.enemy_focused_at > self.enemy_kill_timeout:
            print(datetime.datetime.now(), 'Превышено время на убийство цели.')
            self.break_target()
            time.sleep(.3)
            locked_on_enemy = False

        jump = last_focus_state and not locked_on_enemy and self.jump_forward_on_lose_target
        # locate closest enemy (neutral)
        target_enemy = False
        if not locked_on_enemy:
            self.lookup_coords()
            self.lookup_direction()
            enemy_pixels = self.locate_enemies()
            for enemy_pixel in enemy_pixels:
                coord_to_click = (enemy_pixel[0], enemy_pixel[1] + 2)
                if self.is_enemy_valid(coord_to_click):
                    target_enemy = True
                    if self.smart_targeting:
                        self.clicker.move(*coord_to_click)
                        time.sleep(.01)
                        self.clicker.dblclick(*coord_to_click)
                        time.sleep(.01)
                    else:
                        self.clicker.keypress(self.fire_key)
                    break

            if jump:
                self.clicker.keypress(self.force_forward_key)

            if self.press_esc_after_radar_action:
                self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось
            self.clicker.dblclick(0, 0)  # Чтобы убрать курсор с радара и ускориться

        else:
            self.in_combat = True
            if self.smart_targeting:
                if self.fire_when_smart_targeting:
                    enemy_pixels = self.locate_enemies()
                    if not enemy_pixels or math.dist(enemy_pixels[0], self.center) < 30:
                        self.clicker.keypress(self.fire_key)
            else:
                self.clicker.keypress(self.fire_key)

        return locked_on_enemy or target_enemy

    def loot(self):
        loot_replace_radius = 4
        self.clicker.screen_lookup(window=(-225, 15, -40, 200))
        replace_color = (0, 0, 0)
        # locate loot
        loot_pixel = self.clicker.find_pixel(color=(255, 229, 0))
        looting = False  # loot_pixel is not None
        while loot_pixel:
            coord_to_click = (loot_pixel[0], loot_pixel[1] + 2)
            if math.dist(coord_to_click, self.center) < 30:
                looting = True
                self.clicker.move(*coord_to_click)
                time.sleep(.01)
                self.clicker.dblclick(*coord_to_click)
                time.sleep(.01)
            self.clicker.fill(
                window=(coord_to_click[0] - loot_replace_radius, coord_to_click[1] - loot_replace_radius,
                        coord_to_click[0] + loot_replace_radius, coord_to_click[1] + loot_replace_radius),
                color=replace_color
            )
            loot_pixel = self.clicker.find_pixel(color=(255, 229, 0))

        if looting:
            self.clicker.screen_lookup()
            take_all_coord = self.clicker.find_image(take_all_button, threshold=.99)
            if take_all_coord:
                print(datetime.datetime.now(), 'Взять всё')
                self.clicker.click(*take_all_coord[0])
                time.sleep(.3)
                if self.is_locked_on_enemy():
                    self.in_combat = True
                self.break_target()

            self.clicker.move(0, 0)  # Чтобы убрать курсор с радара
            if self.press_esc_after_radar_action:
                self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось
        return looting

    def lookup_coords(self):
        self.clicker.screen_lookup(binary=True, window=(-149, 209, -117, 213))
        result_coords = list()
        for key, image in coord_imgs.items():
            result_coords.extend((coord[0], key) for coord in self.clicker.find_image(image, threshold=.99))
        coords_str = ''.join(map(lambda coord_value: coord_value[1], sorted(result_coords, key=lambda x: x[0])))
        self.radar_coords = tuple(map(int, coords_str.split(':')))
        self.distance_to_area = math.dist(self.radar_coords, self.area_coords)
        if self.distance_to_area > 0:
            self.area_direction = (
                (self.area_coords[0] - self.radar_coords[0]) / self.distance_to_area,
                (self.area_coords[1] - self.radar_coords[1]) / self.distance_to_area
            )
        else:
            self.area_direction = (0, 0)

    def calculate_target_angle(self):
        self.lookup_coords()

        self.target_distance = math.dist(self.radar_coords, self.target_coords)

        if self.target_distance != 0:
            self.target_direction = ((self.target_coords[0] - self.radar_coords[0]) / self.target_distance,
                                (self.target_coords[1] - self.radar_coords[1]) / self.target_distance)

            asin = math.asin(self.target_direction[1])
            if asin == 0:
                asin_coef = -1
            else:
                asin_coef = asin / abs(asin)

            self.target_angle = (math.acos(self.target_direction[0]) * 180 / math.pi) * -asin_coef + 180 * (1 + asin_coef)

    def lookup_direction(self):
        self.clicker.screen_lookup(window=(-141, 99, -126, 114))
        # cv2.imwrite('screen.png', self.clicker.screen)
        coords_index_offset = 5
        coords_to_check = [(-127, 106), (-127, 107), (-127, 108), (-127, 109), (-127, 110), (-128, 110), (-128, 111), (-129, 111), (-129, 112), (-130, 112), (-130, 113), (-131, 113), (-132, 113), (-133, 113), (-134, 113), (-135, 113), (-136, 113), (-137, 113), (-137, 112), (-138, 112), (-138, 111), (-139, 111), (-139, 110), (-140, 110), (-140, 109), (-140, 108), (-140, 107), (-140, 106), (-140, 105), (-140, 104), (-140, 103), (-139, 103), (-139, 102), (-138, 102), (-138, 101), (-137, 101), (-137, 100), (-136, 100), (-135, 100), (-134, 100), (-133, 100), (-132, 100), (-131, 100), (-130, 100), (-130, 101), (-129, 101), (-129, 102), (-128, 102), (-128, 103), (-127, 103), (-127, 104), (-127, 105)]
        coords_to_check = coords_to_check[-coords_index_offset:] + coords_to_check
        person_borders = []
        skip_on_find = 12
        do_skip = 0
        for i in range(len(coords_to_check)):
            if do_skip:
                do_skip -= 1
                continue

            pixel = self.clicker.pixel(*coords_to_check[i])
            if pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]:
                continues_pixels = [i]
                for j in range(i + 1, min(i + coords_index_offset, len(coords_to_check))):
                    coord = coords_to_check[j]
                    pixel = self.clicker.pixel(*coord)
                    if pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]:
                        continues_pixels.append(j)
                        # self.clicker.fill(window=(coord[0], coord[1], coord[0], coord[1]), color=(0, 0, 255))
                if continues_pixels[-1] > coords_index_offset:
                    pixel_index = continues_pixels[int(len(continues_pixels) / 2)]
                    coord = coords_to_check[pixel_index]
                    self.clicker.fill(window=(coord[0] - self.wr, coord[1] - self.wr, coord[0] + self.wr, coord[1] + self.wr), color=(0, 0, 0))
                    self.clicker.fill(window=(coord[0], coord[1], coord[0], coord[1]), color=(0, 0, 255))
                    person_borders.append(coord)
                    do_skip = skip_on_find

        if len(person_borders) == 3:
            ab = math.dist(person_borders[0], person_borders[1])
            bc = math.dist(person_borders[1], person_borders[2])
            ac = math.dist(person_borders[0], person_borders[2])
            if ab > bc and ac > bc:
                pb = person_borders[0]
            elif bc > ac and ab > ac:
                pb = person_borders[1]
            else:#if ac > ab and bc > ab:
                pb = person_borders[2]
            d = math.dist((self.cx, self.cy), pb)
            self.player_direction = ((pb[0] - self.cx) / d, (pb[1] - self.cy) / d)

            asin = math.asin(self.player_direction[1])
            if asin == 0:
                asin_coef = -1
            else:
                asin_coef = asin / abs(asin)

            last_angle = self.player_angle
            self.player_angle = (math.acos(self.player_direction[0]) * 180 / math.pi) * -asin_coef + 180 * (1 + asin_coef)
            self.player_direction_certain = True
            # print(self.player_angle)
            # if last_angle > self.player_angle and last_angle < 350:
            #     cv2.imwrite('screen.png', self.clicker.screen)
            #     self.clicker.keypress(self.fire_key)
            #     raise SystemExit(0)
        else:
            self.player_direction_certain = False
            # print(person_borders)
            # cv2.imwrite('screen.png', self.clicker.screen)
            # self.clicker.keypress(self.fire_key)
            # raise SystemExit(0)

    def rotate_to_target(self):
        self.lookup_direction()
        rotate_to = None
        rotation_timeout = 1
        last_player_direction = self.player_direction
        rotation_time = time.time()

        while (math.dist(self.player_direction, self.target_direction) > self.direction_bias
               and self.player_direction_certain and time.time() - rotation_time < rotation_timeout):
            if ((0 < self.player_angle - self.target_angle < 180)
                    or (0 < self.player_angle + 360 - self.target_angle < 180)):
                if rotate_to == 'left':
                    break
                self.clicker.keyup(win32con.VK_LEFT)
                self.clicker.keydown(win32con.VK_RIGHT)
                rotate_to = 'right'
                if self.player_direction != last_player_direction:
                    last_player_direction = self.player_direction
                    rotation_time = time.time()
            else:
                if rotate_to == 'right':
                    break
                self.clicker.keyup(win32con.VK_RIGHT)
                self.clicker.keydown(win32con.VK_LEFT)
                rotate_to = 'left'
                if self.player_direction != last_player_direction:
                    last_player_direction = self.player_direction
                    rotation_time = time.time()
            time.sleep(0.05)
            self.lookup_direction()

        if time.time() - rotation_time >= rotation_timeout:
            print(datetime.datetime.now(), 'Залип поворот')
            self.clicker.reset_keyboard()
            self.clicker.keypress(win32con.VK_LEFT)
            self.clicker.keypress(win32con.VK_RIGHT)
        else:
            self.clicker.keyup(win32con.VK_LEFT)
            self.clicker.keyup(win32con.VK_RIGHT)

    def fly_to(self, x, y,
               mode=None,
               rotate_first=False,
               speed_up=True, loot=True,
               stop_at_destination=None,
               target_bias=None,
               stop_if_enemy_in_front_of_ship=None):
        if mode is not None:
            if mode == 'Переход между лабиринтами':
                target_bias = -1
                stop_at_destination = True
                stop_if_enemy_in_front_of_ship = False
            if mode == 'Быстро лететь к цели':
                stop_at_destination = True
                stop_if_enemy_in_front_of_ship = False
                speed_up = True
            if mode == 'Лететь к цели':
                stop_at_destination = True
                stop_if_enemy_in_front_of_ship = False
                speed_up = False

        target_bias = target_bias if target_bias is not None else self.target_bias
        stop_at_destination = stop_at_destination if stop_at_destination is not None else self.stop_at_destination
        stop_if_enemy_in_front_of_ship = stop_if_enemy_in_front_of_ship if stop_if_enemy_in_front_of_ship is not None else self.stop_if_enemy_in_front_of_ship
        self.break_target()  # Снимаем цель, чтобы случайно не развернуться
        self.clicker.keypress(win32con.VK_LEFT)  # Залипает поворот после снятия цели.
        if self.press_esc_after_radar_action:
            self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось

        self.target_coords = (x, y)
        self.calculate_target_angle()

        # Если уже находимся в точке назначения, то выходим
        if self.target_distance <= target_bias:
            return True

        if rotate_first:
            self.rotate_to_target()

        last_distance_to_target = self.target_distance
        last_distance_to_target_time = time.time()
        last_player_coord = self.radar_coords

        while self.target_distance > target_bias:
            self.clicker.keypress(self.force_key if speed_up else self.forward_key)
            if loot:
                self.loot()
            time.sleep(0.05)
            self.calculate_target_angle()

            # Если залетели куда-то, то выходим, считая, что место назначения достигнуто
            if math.dist(last_player_coord, self.radar_coords) >= self.warp_bias:
                if target_bias == -1:
                    print(datetime.datetime.now(), 'Прыжок в другой лабиринт')
                    self.clicker.keypress(win32con.VK_DOWN)
                    return True
                else:
                    print(datetime.datetime.now(), 'Прыжок в другой лабиринт (ошибка)')
                    self.clicker.keypress(win32con.VK_DOWN)
                    return False

            last_player_coord = self.radar_coords

            # Корректируем направление движения
            self.rotate_to_target()

            # Если мы не находимся за границей области, и враг напротив, то выходим
            if stop_if_enemy_in_front_of_ship and self.in_area():
                enemy_pixels = self.locate_enemies()
                for enemy_coord in enemy_pixels:
                    to_enemy_distance = math.dist(self.center, enemy_coord)
                    to_enemy_direction = (
                        (enemy_coord[0] - self.center[0]) / to_enemy_distance,
                        (enemy_coord[1] - self.center[1]) / to_enemy_distance
                    )
                    enemy_in_front_of_player = np.dot(self.player_direction, to_enemy_direction) > 0
                    if enemy_in_front_of_player and self.is_enemy_valid(enemy_coord):
                        return False

            # Если застряли где-то, то пробуем случайно ускориться влево/вправо
            if time.time() - last_distance_to_target_time > self.stuck_delay:
                if abs(last_distance_to_target - self.target_distance) <= self.stuck_difference:
                    if random.randint(0, 1):
                        self.clicker.keypress(self.force_left_key)
                    else:
                        self.clicker.keypress(self.force_right_key)

                last_distance_to_target_time = time.time()
                last_distance_to_target = self.target_distance

        if stop_at_destination:
            self.clicker.keypress(win32con.VK_DOWN)

        return True

    def fly_to_base_trough_tunnel(self, tries=None):
        tries = tries if tries is not None else self.fly_trough_tunnel_tries_amount
        result = False
        for i in range(7):
            self.clicker.keypress('^+')

        time.sleep(1)

        for i in range(tries):
            self.clicker.screen_lookup(window=(-225, 15, -40, 200))
            tunnel = next(iter(self.clicker.find_image(tunnel_img, threshold=.8)), None)

            if tunnel is None:
                print(datetime.datetime.now(), 'Туннель не обнаружен')
            else:
                click_coord = tunnel[0] + int(tunnel_img.shape[1] / 2), tunnel[1] + int(tunnel_img.shape[0] / 2)
                self.clicker.move(*click_coord)
                time.sleep(.1)
                self.clicker.dblclick(*click_coord)
                time.sleep(1)
                self.clicker.screen_lookup()
                tunnel_window_coord = next(iter(self.clicker.find_image(tunnel_window_title)), None)
                if tunnel_window_coord is None:
                    print(datetime.datetime.now(), 'Окно взаимодействия с туннелем не было найдено')
                else:
                    base_option_coord = next(iter(self.clicker.find_image(
                        tunnel_window_base_title,
                        window=(*tunnel_window_coord, tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400))), None)
                    if base_option_coord is None:
                        print(datetime.datetime.now(), 'База клана не найдена в списке окна взаимодействия с туннелем')
                    else:
                        result = True
                        self.clicker.move(*base_option_coord)
                        self.clicker.click(base_option_coord[0] + 1, base_option_coord[1] + 1)
                        print(datetime.datetime.now(), f'Выбран переход "База клана"')
                        time.sleep(1)
                        break

            self.clicker.move(0, 0)
            if i != tries - 1:
                time.sleep(1)

        for i in range(7):
            self.clicker.keypress('^-')

        return result

    def fly_from_tunnel_to(self, destination_name, tries=None):
        tries = tries if tries is not None else self.fly_trough_tunnel_tries_amount
        result = False
        for i in range(7):
            self.clicker.keypress('^+')

        time.sleep(1)

        for i in range(tries):
            self.clicker.screen_lookup(window=(-225, 15, -40, 200))
            tunnel = next(iter(self.clicker.find_image(tunnel_img, threshold=.8)), None)

            if tunnel is None:
                print(datetime.datetime.now(), 'Туннель не обнаружен')
            else:
                click_coord = tunnel[0] + int(tunnel_img.shape[1] / 2), tunnel[1] + int(tunnel_img.shape[0] / 2)
                self.clicker.move(*click_coord)
                time.sleep(.1)
                self.clicker.dblclick(*click_coord)
                time.sleep(1)
                self.clicker.screen_lookup()
                tunnel_window_coord = next(iter(self.clicker.find_image(tunnel_window_title)), None)
                if tunnel_window_coord is None:
                    print(datetime.datetime.now(), 'Окно взаимодействия с туннелем не было найдено')
                else:
                    # base_option_coord = next(iter(self.clicker.find_image(
                    #     tunnel_window_base_title,
                    #     window=(*tunnel_window_coord, tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400))), None)
                    # if base_option_coord is None:
                    #     print('База клана не найдена в списке окна взаимодействия с туннелем')
                    # else:
                    #     result = True
                    #     self.clicker.move(*base_option_coord)
                    #     self.clicker.click(base_option_coord[0] + 1, base_option_coord[1] + 1)
                    #     print(f'Выбран переход "База клана"')
                    #     time.sleep(1)
                    #     break

                    # [[b0, b1, b2, b3], str, float] window = (*b0, *b2)
                    window = (
                        tunnel_window_coord[0], tunnel_window_coord[1],
                        tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400
                    )
                    for bbox, text, accuracy in self.ocr_reader.readtext(
                            self.clicker.screen[window[1]:window[3], window[0]:window[2]]):
                        if text == destination_name:
                            result = True
                            x, y = bbox[0]
                            x += window[0]
                            y += window[1]
                            self.clicker.move(x, y)
                            self.clicker.click(x + 1, y + 1)
                            print(datetime.datetime.now(), f'Выбран переход "{destination_name}"')
                            break

            self.clicker.move(0, 0)
            if result:
                break
            if i != tries - 1:
                time.sleep(1)

        time.sleep(1)
        for i in range(7):
            self.clicker.keypress('^-')

        return result

    def fly_from_base_to(self, destination_name):
        result = False
        self.clicker.click(-130, 100)
        time.sleep(1)
        self.clicker.screen_lookup()
        tunnel_window_coord = next(iter(self.clicker.find_image(tunnel_window_title)), None)
        if tunnel_window_coord is None:
            print(datetime.datetime.now(), 'Окно взаимодействия с туннелем не было найдено')
        else:
            # [[b0, b1, b2, b3], str, float] window = (*b0, *b2)
            window = (
                tunnel_window_coord[0], tunnel_window_coord[1],
                tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400
            )
            for bbox, text, accuracy in self.ocr_reader.readtext(self.clicker.screen[window[1]:window[3], window[0]:window[2]]):
                if text == destination_name:
                    result = True
                    x, y = bbox[0]
                    x += window[0]
                    y += window[1]
                    self.clicker.move(x, y)
                    self.clicker.click(x + 1, y + 1)
                    print(datetime.datetime.now(), f'Выбран переход "{destination_name}"')
                    break

            if not result:
                print(datetime.datetime.now(), f'Переход "{destination_name}" не найден')

        return result

    def fly_route(self, route: list[((int, int), str)]):
        def act(action, attribute):
            if action == 'Вылет':
                return self.undock(available_directions_to_undock=attribute)
            elif action == 'Перелететь':
                return self.fly_from_base_to(destination_name=attribute)
            elif action == 'В туннель':
                return self.fly_from_tunnel_to(destination_name=attribute)
            elif type(action) in [tuple, list]:
                return self.fly_to(*action, mode=attribute)

        def delay(action):
            if action == 'Вылет':
                return time.sleep(10)
            elif action == 'Перелететь':
                return time.sleep(3)
            elif action == 'В туннель':
                return time.sleep(15)
            elif type(action) in [tuple, list]:
                return time.sleep(1)

        for index, route_point in enumerate(route):
            action, attribute = route_point
            while not act(action, attribute):
                delay(action)
                backup_action, backup_attribute = route[index - 1]
                act(backup_action, backup_attribute)

            delay(action)

    def load_preset(self, file_path):
        with open(file_path, 'r', encoding='utf8') as f:
            data = json.loads(f.read())
            for attribute, value in data.items():
                setattr(self, attribute, value)
