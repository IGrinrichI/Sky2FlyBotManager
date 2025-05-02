import datetime
import os
import random
import sys
import time
from threading import Thread

import cv2
import math

import numpy as np
import winsound
from pynput import keyboard

from clicker import Clicker
import win32con


def beep(freq=1000):
    def _beep():
        dur = 1000
        winsound.Beep(freq, dur)

    Thread(target=_beep, daemon=True).start()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
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


class Player:
    warp_bias = 5
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
    area_coords = (50, 50)
    area_direction = (0, 0)
    distance_to_area = 0
    min_distance_from_area = 7
    max_distance_away_from_area = 11
    farm_start_time = time.time()
    max_farm_time = 300

    abilities = list()
    smart_targeting = True
    stop_if_enemy_in_front_of_ship = True
    stop_at_destination = False
    jump_forward_on_lose_target = True
    enemy_focused = False
    last_time_enemy_focused = 0
    enemy_focusing_max_time = 1
    enemy_focused_at = 0
    enemy_kill_timeout = 10

    cx = 1786.5
    cy = 106.5
    center = (cx, cy)
    r = 7.5
    w = 2.75
    wr = round(w + 2, 0)
    green_buff = 1.07

    force_key = 'f'
    force_forward_key = 'q'
    force_left_key = 'x'
    force_right_key = 'c'
    forward_key = 'w'
    break_target_key = 'z'
    fire_key = ' '

    def is_overweight(self):
        clicker.screen_lookup(window=(150, 0, 300, 40))
        return clicker.find_pixel(color=(205, 49, 55)) is not None

    def is_farming(self):
        return time.time() - self.farm_start_time < self.max_farm_time and not self.is_overweight()

    @property
    def in_combat(self):
        self.lookup_coords()
        return time.time() - self.last_time_enemy_focused < self.enemy_focusing_max_time and self.distance_to_area <= self.max_distance_away_from_area

    @in_combat.setter
    def in_combat(self, state):
        if state:
            self.last_time_enemy_focused = time.time()
        else:
            self.last_time_enemy_focused = 0

    def store_resources_and_service(self):
        # Сервис
        clicker.screen_lookup(window=(-600, -75, -1, -1))
        service = clicker.find_image(service_button, threshold=.99)
        print(datetime.datetime.now(), 'Сервис')
        if service:
            clicker.click(*service[0])
        time.sleep(1)
        clicker.screen_lookup()
        service_all = clicker.find_image(service_all_button, threshold=.8)
        print(datetime.datetime.now(), 'Зарядить всё')
        if service_all:
            clicker.click(*service_all[0])
        time.sleep(1)
        # Склад
        clicker.screen_lookup(window=(-600, -75, -1, -1))
        storage = clicker.find_image(storage_button, threshold=.99)
        print(datetime.datetime.now(), 'Склад')
        if storage:
            clicker.click(*storage[0])
        time.sleep(1)
        clicker.screen_lookup(window=(0, -150, -1, -1))
        store_all = clicker.find_image(all_to_storage_button, threshold=.99)
        print(datetime.datetime.now(), 'Всё на склад')
        if store_all:
            clicker.click(*store_all[0])

    def break_target(self):
        clicker.keypress(self.break_target_key)
        self.enemy_focused = False

    def is_locked_on_enemy(self):
        clicker.screen_lookup(window=(400, 0, -325, 100))
        if clicker.find_image(enemy_locked_on, threshold=.99):
            self.enemy_focused = True
            return self.enemy_focused
        else:
            self.enemy_focused = False
            return self.enemy_focused

    def locate_enemies(self):
        # start = time.time()
        enemy_replace_pixels = 5
        clicker.screen_lookup(window=(-225, 15, -40, 200))
        neutral_enemies = []
        neutral_enemy = clicker.find_pixel(color=(221, 221, 221))
        while neutral_enemy:
            neutral_enemies.append(neutral_enemy)
            clicker.fill(
                window=(neutral_enemy[0] - enemy_replace_pixels, neutral_enemy[1] - enemy_replace_pixels,
                        neutral_enemy[0] + enemy_replace_pixels, neutral_enemy[1] + enemy_replace_pixels),
                color=(0, 0, 0)
            )
            neutral_enemy = clicker.find_pixel(color=(221, 221, 221))

        aggressive_enemies = []
        aggressive_enemy = clicker.find_pixel(color=(255, 0, 0))
        while aggressive_enemy:
            if math.dist(aggressive_enemy, self.center) < 90:
                valid_pixel = True
                any_dark_pixel = False
                for i in range(1, 5):
                    pixel = clicker.pixel(aggressive_enemy[0] + i, aggressive_enemy[1] + i)
                    is_dark_pixel = ((pixel[0] - pixel[1] > 100 and pixel[0] - pixel[2] > 100)
                                     or (pixel[0] > 100 and pixel[1] < 50 and pixel[2] < 50)
                                     or (abs(pixel[0] - pixel[1]) < 15 and abs(pixel[0] - pixel[2]) < 15 and abs(pixel[1] - pixel[2]) < 15))
                    any_dark_pixel = any_dark_pixel or is_dark_pixel
                    if not (all(pixel == (255, 0, 0)) or is_dark_pixel):
                        valid_pixel = False
                        # print(pixel)
                        break
                if valid_pixel and any_dark_pixel:
                    aggressive_enemies.append(aggressive_enemy)
            clicker.fill(
                window=(aggressive_enemy[0] - enemy_replace_pixels, aggressive_enemy[1] - enemy_replace_pixels,
                        aggressive_enemy[0] + enemy_replace_pixels, aggressive_enemy[1] + enemy_replace_pixels),
                color=(0, 0, 0)
            )
            aggressive_enemy = clicker.find_pixel(color=(255, 0, 0))
        # special_enemies = clicker.find_pixels(color=(139, 0, 255))
        enemies = neutral_enemies + aggressive_enemies

        directions = {coord: (coord[0] - self.center[0], coord[1] - self.center[1]) for coord in enemies}
        enemies = sorted(enemies, key=lambda coord: math.dist(coord, self.center) * (2 - np.dot(directions[coord] / np.linalg.norm(directions[coord]), self.player_direction)))
        # print(self.player_direction, [(enemy[0] - self.center[0], enemy[1] - self.center[1]) for enemy in enemies])
        # print(time.time() - start)
        # for index, enemy in enumerate(enemies):
        #     clicker.fill(window=(*enemy, *enemy),
        #                  color=(255 - int(255 / len(enemies)) * index, 0, 0))
        # cv2.imwrite('screen.png', clicker.screen)
        return enemies

    def is_enemy_valid(self, enemy_coord):
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
                outer_target_pixel = clicker.pixel(
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
            if self.smart_targeting:
                self.lookup_coords()
                self.lookup_direction()
                enemy_pixels = self.locate_enemies()
                # Если вдали от города, то нормально залетать в зону ветров
                for enemy_pixel in enemy_pixels:
                    coord_to_click = (enemy_pixel[0], enemy_pixel[1] + 2)
                    if self.is_enemy_valid(coord_to_click):
                        target_enemy = True
                        clicker.move(*coord_to_click)
                        time.sleep(.01)
                        clicker.dblclick(*coord_to_click)
                        time.sleep(.01)
                        break
            else:
                clicker.keypress(player.fire_key)

            if jump:
                clicker.keypress(player.force_forward_key)

            clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось
            clicker.dblclick(0, 0)  # Чтобы убрать курсор с радара и ускориться

        else:
            self.in_combat = True
            if self.smart_targeting:
                enemy_pixels = self.locate_enemies()
                if not enemy_pixels or math.dist(enemy_pixels[0], self.center) < 30:
                    clicker.keypress(player.fire_key)
            else:
                clicker.keypress(player.fire_key)

        return locked_on_enemy or target_enemy

    def loot(self):
        loot_replace_radius = 4
        clicker.screen_lookup(window=(-225, 15, -40, 200))
        replace_color = (0, 0, 0)
        # locate loot
        loot_pixel = clicker.find_pixel(color=(255, 229, 0))
        looting = loot_pixel is not None
        while loot_pixel:
            coord_to_click = (loot_pixel[0], loot_pixel[1] + 2)
            if math.dist(coord_to_click, self.center) < 30:
                clicker.move(*coord_to_click)
                time.sleep(.01)
                clicker.dblclick(*coord_to_click)
                time.sleep(.01)
            clicker.fill(
                window=(coord_to_click[0] - loot_replace_radius, coord_to_click[1] - loot_replace_radius,
                        coord_to_click[0] + loot_replace_radius, coord_to_click[1] + loot_replace_radius),
                color=replace_color
            )
            loot_pixel = clicker.find_pixel(color=(255, 229, 0))

        if looting:
            clicker.screen_lookup()
            take_all_coord = clicker.find_image(take_all_button, threshold=.99)
            if take_all_coord:
                print(datetime.datetime.now(), 'Взять всё')
                clicker.click(*take_all_coord[0])
                time.sleep(.3)
                self.break_target()

            clicker.move(0, 0)  # Чтобы убрать курсор с радара

        clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось
        return looting

    def lookup_coords(self):
        clicker.screen_lookup(binary=True, window=(-149, 209, -117, 213))
        result_coords = list()
        for key, image in coord_imgs.items():
            result_coords.extend((coord[0], key) for coord in clicker.find_image(image, threshold=.99))
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
        clicker.screen_lookup(window=(-141, 99, -126, 114))
        # cv2.imwrite('screen.png', clicker.screen)
        coords_index_offset = 5
        coords_to_check = [(1793, 106), (1793, 107), (1793, 108), (1793, 109), (1793, 110), (1792, 110), (1792, 111), (1791, 111), (1791, 112), (1790, 112), (1790, 113), (1789, 113), (1788, 113), (1787, 113), (1786, 113), (1785, 113), (1784, 113), (1783, 113), (1783, 112), (1782, 112), (1782, 111), (1781, 111), (1781, 110), (1780, 110), (1780, 109), (1780, 108), (1780, 107), (1780, 106), (1780, 105), (1780, 104), (1780, 103), (1781, 103), (1781, 102), (1782, 102), (1782, 101), (1783, 101), (1783, 100), (1784, 100), (1785, 100), (1786, 100), (1787, 100), (1788, 100), (1789, 100), (1790, 100), (1790, 101), (1791, 101), (1791, 102), (1792, 102), (1792, 103), (1793, 103), (1793, 104), (1793, 105)]
        coords_to_check = coords_to_check[-coords_index_offset:] + coords_to_check
        person_borders = []
        skip_on_find = 12
        do_skip = 0
        for i in range(len(coords_to_check)):
            if do_skip:
                do_skip -= 1
                continue

            pixel = clicker.pixel(*coords_to_check[i])
            if pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]:
                continues_pixels = [i]
                for j in range(i + 1, min(i + coords_index_offset, len(coords_to_check))):
                    coord = coords_to_check[j]
                    pixel = clicker.pixel(*coord)
                    if pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]:
                        continues_pixels.append(j)
                        # clicker.fill(window=(coord[0], coord[1], coord[0], coord[1]), color=(0, 0, 255))
                if continues_pixels[-1] > coords_index_offset:
                    pixel_index = continues_pixels[int(len(continues_pixels) / 2)]
                    coord = coords_to_check[pixel_index]
                    clicker.fill(window=(coord[0] - self.wr, coord[1] - self.wr, coord[0] + self.wr, coord[1] + self.wr), color=(0, 0, 0))
                    clicker.fill(window=(coord[0], coord[1], coord[0], coord[1]), color=(0, 0, 255))
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
            #     cv2.imwrite('screen.png', clicker.screen)
            #     clicker.keypress(player.fire_key)
            #     raise SystemExit(0)
        else:
            self.player_direction_certain = False
            # print(person_borders)
            # cv2.imwrite('screen.png', clicker.screen)
            # clicker.keypress(player.fire_key)
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
                clicker.keyup(win32con.VK_LEFT)
                clicker.keydown(win32con.VK_RIGHT)
                rotate_to = 'right'
                if self.player_direction != last_player_direction:
                    last_player_direction = self.player_direction
                    rotation_time = time.time()
            else:
                if rotate_to == 'right':
                    break
                clicker.keyup(win32con.VK_RIGHT)
                clicker.keydown(win32con.VK_LEFT)
                rotate_to = 'left'
                if self.player_direction != last_player_direction:
                    last_player_direction = self.player_direction
                    rotation_time = time.time()
            time.sleep(0.05)
            self.lookup_direction()

        if time.time() - rotation_time >= rotation_timeout:
            print(datetime.datetime.now(), 'Залип поворот')
            clicker.reset_keyboard()

        clicker.keyup(win32con.VK_RIGHT)
        clicker.keyup(win32con.VK_LEFT)

    def fly_to(self, x, y,
               rotate_first=False,
               speed_up=True, loot=True):
        self.break_target()  # Снимаем цель, чтобы случайно не развернуться
        clicker.keypress(win32con.VK_LEFT)  # Залипает поворот после снятия цели.
        clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось

        self.target_coords = (x, y)
        self.calculate_target_angle()

        # Если уже находимся в точке назначения, то выходим
        if self.target_distance <= self.target_bias:
            return True

        if rotate_first:
            self.rotate_to_target()

        last_distance_to_target = self.target_distance
        last_distance_to_target_time = time.time()
        last_player_coord = self.radar_coords

        while self.target_distance > self.target_bias:
            clicker.keypress(player.force_key if speed_up else player.forward_key)
            if loot:
                self.loot()
            time.sleep(0.05)
            self.calculate_target_angle()

            # Если залетели куда-то, то выходим, считая, что место назначения достигнуто
            if math.dist(last_player_coord, self.radar_coords) >= self.warp_bias:
                clicker.keypress(win32con.VK_DOWN)
                return True
            last_player_coord = self.radar_coords

            # Корректируем направление движения
            self.rotate_to_target()

            if self.stop_if_enemy_in_front_of_ship:
                # Если мы не находимся за границей области, и враг напротив, то выходим
                if self.distance_to_area < self.max_distance_away_from_area:
                    enemy_pixels = self.locate_enemies()
                    for enemy_coord in enemy_pixels:
                        to_enemy_distance = math.dist(self.center, enemy_coord)
                        to_enemy_direction = (
                            (enemy_coord[0] - self.center[0]) / to_enemy_distance,
                            (enemy_coord[1] - self.center[1]) / to_enemy_distance
                        )
                        if np.dot(self.player_direction, to_enemy_direction) > 0 and self.is_enemy_valid(enemy_coord):
                            return False

            # Если застряли где-то, то пробуем случайно ускориться влево/вправо
            if time.time() - last_distance_to_target_time > self.stuck_delay:
                if abs(last_distance_to_target - self.target_distance) <= self.stuck_difference:
                    if random.randint(0, 1):
                        clicker.keypress(player.force_left_key)
                    else:
                        clicker.keypress(player.force_right_key)

                last_distance_to_target_time = time.time()
                last_distance_to_target = self.target_distance

        if self.stop_at_destination:
            clicker.keypress(win32con.VK_DOWN)

        return True


clicker = Clicker()
clicker.hwnd = 0x1040668
player = Player()


# Медузяки
target_coords_range = [
    (42, 44),
    (30, 30),
]
city_coord = (49, 51)

repeat_cycle_forever = False

# player.target_coords = (50, 50)
# player.calculate_target_angle()
# player.rotate_to_target()
# raise SystemExit(0)
# player.lookup_coords()
# player.lookup_direction()
# enemies = player.locate_enemies()
# # enemies = filter(player.is_enemy_valid, enemies)
# valid_count = 0
# for index, enemy in enumerate(enemies):
#     if player.is_enemy_valid(enemy):
#         clicker.fill(window=(*enemy, *enemy), color=(0, 255 - (valid_count / len(enemy)) * 64, 0))
#         valid_count += 1
#     else:
#         clicker.fill(window=(*enemy, *enemy), color=(255, 0, 0))
#
# cv2.imwrite('screen.png', clicker.screen)
# raise SystemExit(0)




s2f_hwnd_set = set()

presets = list(filter(lambda x: x.endswith('.preset'), os.listdir(os.getcwd())))
print("Доступные пресеты:")
print('\n'.join(f'{i}) {preset[:-len(".preset")]}' for i, preset in enumerate(presets, 1)))

preset_number = '2'
while not preset_number.isdigit() or preset_number == '0' or int(preset_number) > len(presets):
    preset_number = input('Укажите номер пресета: ')

with open(presets[int(preset_number) - 1], 'r') as f:
    exec(f.read())

print('Наведите курсор мыши на игру и нажмите Ctrl.')
# Collect windows to operate
while True:
    with keyboard.Events() as events:
        event = events.get(.1)
        if isinstance(event, keyboard.Events.Press) and event.key == keyboard.Key.ctrl_l:
            current_hwnd = clicker.get_hwnd_from_mouse_position()
            if current_hwnd == clicker.hwnd:
                beep()
                break
            clicker.hwnd = current_hwnd
            if current_hwnd in s2f_hwnd_set:
                print('Окно', current_hwnd, 'уже добавлено')
            else:
                s2f_hwnd_set.add(current_hwnd)
                print('Добавлено новое окно:', current_hwnd)
                break
            beep(500)

print(datetime.datetime.now(), 'Процесс запущен.')
beep()
if s2f_hwnd_set:
    clicker.hwnd = next(iter(s2f_hwnd_set))

# def click_task():
#     while True:
#         clicker.keypress(player.fire_key)
#         time.sleep(.6)
#
#
# # Thread(target=click_task, daemon=True).start()
# attack_delay = .6
# last_attack_time = time.time()
# while True:
#     if time.time() - last_attack_time > attack_delay:
#         clicker.keypress(player.fire_key)
#         last_attack_time = time.time()
#     clicker.screen_lookup(window=(-225, 15, -40, 200))
#     player.loot()
#     time.sleep(min(.1, max(0, time.time() - last_attack_time)))

while True:
    try:
        player.lookup_coords()
    except ValueError:
        coords_to_undock = [
            (1789, 33),
            (1740, 55),
            (1722, 106),
            (1742, 159),
            (1787, 177),
            (1843, 155),
            (1862, 104),
            (1841, 58),
        ]
        clicker.click(*random.choice(coords_to_undock))
        time.sleep(10)

    if player.is_overweight():
        print(datetime.datetime.now(), 'Вылет с перегрузом.')
    else:
        # Активируем умения
        for ability in player.abilities:
            clicker.keypress(f'^{ability}')
            time.sleep(.5)

    clicker.reset_keyboard()
    last_closest_target = None
    player.farm_start_time = time.time()
    origin_target_bias = player.target_bias
    player.in_combat = True
    try:
        while player.is_farming():
            # Убиваем
            player.target_and_kill()

            time.sleep(.01)
            player.loot()  # Лутаем

            # Летим к следующей точке, если мобы кончились
            if not player.in_combat:
                player.loot()  # На всякий случай лутаем ещё
                closest_target = min(target_coords_range, key=lambda coords: math.dist(coords, player.radar_coords))
                # Чтобы не возвращаться в ту же самую точку каждый раз - меняем точку на следующую
                # если ближайшая точка посещалась в прошлый раз как отсутствовали цели.
                if closest_target == last_closest_target:
                    next_target_index = target_coords_range.index(closest_target) + 1
                    next_target_index = next_target_index if next_target_index < len(target_coords_range) else 0
                    closest_target = target_coords_range[next_target_index]

                if player.fly_to(*closest_target):
                    last_closest_target = closest_target
                player.in_combat = True
            else:
                time.sleep(.3)

        if player.is_overweight():
            print(datetime.datetime.now(), 'Перегруз')
        print(datetime.datetime.now(), 'Фарм окончен, летим в город.')
        # Летим в центр (город)
        player.target_bias = -1
        player.stop_if_enemy_in_front_of_ship = False
        player.fly_to(*city_coord, rotate_first=False)
    except ValueError:
        print(datetime.datetime.now(), 'В городе')
        player.target_bias = origin_target_bias

        time.sleep(1)
        clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
        clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
        clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
        time.sleep(1)
        player.store_resources_and_service()
        time.sleep(1)

    if not repeat_cycle_forever:
        beep(1000)
        time.sleep(1)
        beep(1100)
        time.sleep(1)
        beep(1200)
        break

# # Кружится вокруг небесной канцелярии)
# radius = 9
# target_coords_range = [(50 + int(math.cos(x * math.pi / 180) * radius), 50 + int(math.sin(x * math.pi / 180) * radius)) for x in range(10, 360, 50)]
# print(target_coords_range)
#
# player.target_bias = 4
# while True:
#     for target_coords in target_coords_range:
#         player.fly_to(*target_coords, stop_at_destination=False, rotate_first=False, speed_up=False)
