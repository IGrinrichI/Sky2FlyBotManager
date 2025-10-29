import datetime
import json
import math
import random
import time
import os
import sys
from threading import Thread

import cv2
import numpy as np
import win32con
import win32ui
import winsound


def resource_path(relative_path) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def beep(freq=1000, sync=False):
    def _beep():
        dur = 1000
        winsound.Beep(freq, dur)

    if sync:
        _beep()
    else:
        Thread(target=_beep, daemon=True).start()


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

dialog_button = cv2.imread(resource_path(os.path.join('images', 'dialog_button.PNG')))
dialog_option = cv2.imread(resource_path(os.path.join('images', 'dialog_option.png')))
quest_dialog_option = cv2.imread(resource_path(os.path.join('images', 'quest_dialog_option.png')))
question_dialog_option = cv2.imread(resource_path(os.path.join('images', 'question_dialog_option.png')))
complete_dialog_option = cv2.imread(resource_path(os.path.join('images', 'complete_dialog_option.png')))
close_dialog_option = cv2.imread(resource_path(os.path.join('images', 'close_dialog_option.png')))

ship_tab = cv2.imread(resource_path(os.path.join('images', 'ship_tab.PNG')))
cargo_tab = cv2.imread(resource_path(os.path.join('images', 'cargo_tab.PNG')))
gasholder_low_charge_img = cv2.imread(resource_path(os.path.join('images', 'gasholder_low_charge.bmp')))
reload_button = cv2.imread(resource_path(os.path.join('images', 'reload.PNG')))
chest_icon = cv2.imread(resource_path(os.path.join('images', 'chest.PNG')))
black_chest_icon = cv2.imread(resource_path(os.path.join('images', 'black_chest.PNG')))
drop_button = cv2.imread(resource_path(os.path.join('images', 'drop_button.PNG')))

to_city_button = cv2.imread(resource_path(os.path.join('images', 'to_city_button.PNG')))
dead_title = cv2.imread(resource_path(os.path.join('images', 'your_ship_down.PNG')))
pay_button = cv2.imread(resource_path(os.path.join('images', 'pay.png')))
invite_button = cv2.imread(resource_path(os.path.join('images', 'invite_button.PNG')))
party_request = cv2.imread(resource_path(os.path.join('images', 'party_request.PNG')))
accept_button = cv2.imread(resource_path(os.path.join('images', 'accept_button.PNG')))

pink_dandelion = cv2.imread(resource_path(os.path.join('images', 'pink_dandelion.png')))
green_dandelion = cv2.imread(resource_path(os.path.join('images', 'green_dandelion.png')))
orange_dandelion = cv2.imread(resource_path(os.path.join('images', 'orange_dandelion.png')))

fishing_spot = cv2.imread(resource_path(os.path.join('images', 'fishing_spot.png')))
fishing_spot_eels = cv2.imread(resource_path(os.path.join('images', 'fishing_spot_eels.png')))
catching_img = cv2.imread(resource_path(os.path.join('images', 'catching.png')))
start_catch_img = cv2.imread(resource_path(os.path.join('images', 'start_fishing.png')))
pickup_img = cv2.imread(resource_path(os.path.join('images', 'pickup.png')))
continue_img = cv2.imread(resource_path(os.path.join('images', 'continue_catching.png')))
full_net_img = cv2.imread(resource_path(os.path.join('images', 'full_net.png')))

boss = cv2.imread(resource_path(os.path.join('images', 'boss.png')))


class Player:
    mode = 'Убийство мобов в зоне'
    warp_bias = 7
    target_bias = 3
    stuck_delay = 3
    stuck_difference = 1.5
    rotation_thread = None
    stop_rotation_event = None
    rotating = False
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

    to_farm_path = []
    to_base_path = []
    target_coords_range = []
    repeat_cycle_forever = False

    farm_start_time = time.time()
    max_farm_time = 300

    abilities = []
    enemy_types = []  # ['neutral', 'agressive', 'special']
    smart_targeting = True
    fire_when_smart_targeting = True
    do_drop_chests = True
    loot_on_fly = True
    do_looting = True
    ignore_overweight = False
    stop_if_enemy_in_front_of_ship = True
    stop_at_destination = False
    jump_forward_on_lose_target = True
    enemy_focused = False
    last_time_enemy_focused = 0
    enemy_focusing_max_time = 1
    enemy_focused_at = 0
    enemy_kill_timeout = 10

    death_check_delay = 10
    death_check_last_time = 0
    after_death_wait_time_range = [300, 3600]

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

    fishing_spot_detection_precision = .65
    fishing_spot_approach_distance = 4
    fishing_spot_max_bad_fishing_tries = 1

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
            time.sleep(.2)
            self.clicker.move(0, 0)
        return True

    @property
    def center(self):
        return (
            self.clicker.screen_width + self.cx if self.cx < 0 else self.cx,
            self.clicker.screen_height + self.cy if self.cy < 0 else self.cy
        )

    def is_overweight(self):
        self.clicker.screen_lookup(window=(-12, -42, -12, -42))
        return all(self.clicker.pixel(-12, -42) == (255, 226, 229))

    def is_farming(self):
        return time.time() - self.farm_start_time < self.max_farm_time and (self.ignore_overweight or not self.is_overweight())

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

    def reload_gasholders(self):
        self.clicker.screen_lookup()
        ship_tab_coord = next(iter(self.clicker.find_image(ship_tab)), None)
        if ship_tab_coord is not None:
            self.clicker.click(*ship_tab_coord)
        else:
            self.clicker.keypress('i')
            time.sleep(1)

            self.clicker.screen_lookup()
            ship_tab_coord = next(iter(self.clicker.find_image(ship_tab)), None)
            if ship_tab_coord is not None:
                self.clicker.click(*ship_tab_coord)
                time.sleep(1)
                self.clicker.screen_lookup()
            else:
                return False

        gasholder_low_charge = next(iter(self.clicker.find_image(gasholder_low_charge_img)), None)
        while gasholder_low_charge is not None:
            self.clicker.click(*gasholder_low_charge)
            time.sleep(1)
            self.clicker.screen_lookup()
            gasholder_low_charge = next(iter(self.clicker.find_image(gasholder_low_charge_img)), None)
            self.clicker.click(gasholder_low_charge[0] + 20, gasholder_low_charge[1] + 70)  # Открыть окно газгольдера
            time.sleep(1)
            self.clicker.screen_lookup()
            reload_coord = self.clicker.find_image(reload_button, threshold=.8)[0]
            self.clicker.click(*reload_coord)  # Перезарядить
            time.sleep(1)
            self.clicker.click(reload_coord[0] + 180, reload_coord[1] - 320)  # Закрытие окна газгольдера
            self.clicker.keypress(win32con.VK_ESCAPE)  # Закрытие окна оружия
            time.sleep(1)
            self.clicker.screen_lookup()
            gasholder_low_charge = next(iter(self.clicker.find_image(gasholder_low_charge_img)), None)

        return True

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
            # neutral_enemy = self.clicker.find_pixel(color=(221, 221, 221))
            # while neutral_enemy:
            #     neutral_enemies.append(neutral_enemy)
            #     self.clicker.fill(
            #         window=(neutral_enemy[0] - enemy_replace_pixels, neutral_enemy[1] - enemy_replace_pixels,
            #                 neutral_enemy[0] + enemy_replace_pixels, neutral_enemy[1] + enemy_replace_pixels),
            #         color=(0, 0, 0)
            #     )
            #     neutral_enemy = self.clicker.find_pixel(color=(221, 221, 221))

            neutral_enemies = self.clicker.find_pixels(color=(221, 221, 221), min_dist=enemy_replace_pixels + 1)
            neutral_enemies = [(enemy_coord[0] + 1, enemy_coord[1] + 1) for enemy_coord in neutral_enemies]

        aggressive_enemies = []
        if 'agressive' in self.enemy_types:
            enemy_replace_pixels = 5
            aggressive_enemy = self.clicker.find_pixel(color=(255, 0, 0))
            while aggressive_enemy:
                if math.dist(aggressive_enemy, self.center) < 90:
                    pxl = self.clicker.pixel(aggressive_enemy[0] - 1, aggressive_enemy[1])
                    if pxl[1] == pxl[2] and abs(pxl[0] + pxl[1] * 5) % 255 < pxl[1]:
                        aggressive_enemies.append(aggressive_enemy)
                self.clicker.fill(
                    window=(aggressive_enemy[0] - enemy_replace_pixels, aggressive_enemy[1] - enemy_replace_pixels,
                            aggressive_enemy[0] + enemy_replace_pixels, aggressive_enemy[1] + enemy_replace_pixels),
                    color=(0, 0, 0)
                )
                aggressive_enemy = self.clicker.find_pixel(color=(255, 0, 0))

            aggressive_enemies = [(enemy_coord[0], enemy_coord[1] + 2) for enemy_coord in aggressive_enemies]

        special_enemies = []
        if 'special' in self.enemy_types:
            enemy_replace_pixels = 7
            # special_enemy = self.clicker.find_pixel(color=(139, 0, 255))
            # while special_enemy:
            #     special_enemies.append(special_enemy)
            #     self.clicker.fill(
            #         window=(special_enemy[0] - enemy_replace_pixels, special_enemy[1] - enemy_replace_pixels,
            #                 special_enemy[0] + enemy_replace_pixels, special_enemy[1] + enemy_replace_pixels),
            #         color=(0, 0, 0)
            #     )
            #     special_enemy = self.clicker.find_pixel(color=(139, 0, 255))

            special_enemies = self.clicker.find_pixels(color=(139, 0, 255), min_dist=enemy_replace_pixels + 1)
            special_enemies = [(enemy_coord[0] + 1, enemy_coord[1] + 2) for enemy_coord in special_enemies]

        bosses = []
        if 'boss' in self.enemy_types:
            self.clicker.screen_lookup(window=(-225, 15, -40, 200))
            bosses = self.clicker.find_image(boss, min_dist=10, threshold=.8, centers=True)

        enemies = neutral_enemies + aggressive_enemies + special_enemies + bosses

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
            enemy_coords = self.locate_enemies()
            for enemy_coord in enemy_coords:
                if self.is_enemy_valid(enemy_coord):
                    target_enemy = True
                    if self.smart_targeting:
                        self.clicker.move(*enemy_coord)
                        time.sleep(.01)
                        self.clicker.dblclick(*enemy_coord)
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

    def locate_loot(self):
        loot = []
        loot_replace_radius = 4
        self.clicker.screen_lookup(window=(-225, 15, -40, 200))
        replace_color = (0, 0, 0)
        # locate loot
        loot_pixel = self.clicker.find_pixel(color=(255, 229, 0))
        while loot_pixel:
            coord_to_click = (loot_pixel[0], loot_pixel[1] + 2)
            loot.append(coord_to_click)
            self.clicker.fill(
                window=(coord_to_click[0] - loot_replace_radius, coord_to_click[1] - loot_replace_radius,
                        coord_to_click[0] + loot_replace_radius, coord_to_click[1] + loot_replace_radius),
                color=replace_color
            )
            loot_pixel = self.clicker.find_pixel(color=(255, 229, 0))

        return loot

    def loot(self):
        # locate loot
        looting = False  # loot_pixel is not None
        for coord_to_click in self.locate_loot():
            if math.dist(coord_to_click, self.center) < 30:
                looting = True
                self.clicker.move(*coord_to_click)
                time.sleep(.01)
                self.clicker.dblclick(*coord_to_click)
                time.sleep(.01)

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
            if (pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]
                    and math.dist(pixel, (223, 247, 180)) > 30):
                continues_pixels = [i]
                for j in range(i + 1, min(i + coords_index_offset, len(coords_to_check))):
                    coord = coords_to_check[j]
                    pixel = self.clicker.pixel(*coord)
                    if (pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]
                            and math.dist(pixel, (223, 247, 180)) > 30):
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

    def rotate_to_radar(self, point, sync=True):
        def rotate():
            self.lookup_direction()
            rotate_to = None
            rotation_timeout = 1
            last_player_direction = self.player_direction

            point_distance = math.dist(self.center, point)
            point_direction = ((point[0] - self.center[0]) / point_distance,
                               (point[1] - self.center[1]) / point_distance)
            asin = math.asin(point_direction[1])
            if asin == 0:
                asin_coef = -1
            else:
                asin_coef = asin / abs(asin)
            point_angle = (math.acos(point_direction[0]) * 180 / math.pi) * -asin_coef + 180 * (1 + asin_coef)

            rotation_time = time.time()

            while (math.dist(self.player_direction, point_direction) > self.direction_bias
                   and self.player_direction_certain and time.time() - rotation_time < rotation_timeout):
                if ((0 < self.player_angle - point_angle < 180)
                        or (0 < self.player_angle + 360 - point_angle < 180)):
                    if rotate_to == 'left':
                        break
                    self.rotating = True
                    self.clicker.keyup(win32con.VK_LEFT)
                    self.clicker.keydown(win32con.VK_RIGHT)
                    rotate_to = 'right'
                    if self.player_direction != last_player_direction:
                        last_player_direction = self.player_direction
                        rotation_time = time.time()
                else:
                    if rotate_to == 'right':
                        break
                    self.rotating = True
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

            self.rotating = False
            self.stop_rotation_event = None
            self.rotation_thread = None

        self.rotation_thread = Thread(target=rotate)
        self.rotation_thread.start()
        self.rotation_thread.join()

    def rotate_to_target(self, sync=True):
        def rotate():
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
                    self.rotating = True
                    self.clicker.keyup(win32con.VK_LEFT)
                    self.clicker.keydown(win32con.VK_RIGHT)
                    rotate_to = 'right'
                    if self.player_direction != last_player_direction:
                        last_player_direction = self.player_direction
                        rotation_time = time.time()
                else:
                    if rotate_to == 'right':
                        break
                    self.rotating = True
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

            self.rotating = False
            self.stop_rotation_event = None
            self.rotation_thread = None

        self.rotation_thread = Thread(target=rotate)
        self.rotation_thread.start()
        self.rotation_thread.join()

    def wait_for_warp(self):
        self.lookup_coords()
        initial_player_coord = self.radar_coords
        last_player_coord = initial_player_coord
        while True:
            if self.is_dead():
                raise ValueError

            self.calculate_target_angle()

            # Если залетели куда-то, то выходим, считая, что место назначения достигнуто
            if math.dist(last_player_coord, self.radar_coords) >= self.warp_bias:
                return True
            elif initial_player_coord != self.radar_coords:
                return False

            last_player_coord = self.radar_coords
            time.sleep(1)

    def fly_to(self, x, y,
               mode=None,
               rotate_first=False,
               speed_up=True, loot=None,
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

        loot = loot if loot is not None else self.loot_on_fly
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
            if self.is_dead():
                raise ValueError

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
            self.rotate_to_target(sync=False)

            # Если мы не находимся за границей области, и враг напротив, то выходим
            if stop_if_enemy_in_front_of_ship and self.in_area():
                enemy_coords = self.locate_enemies()
                for enemy_coord in enemy_coords:
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
                h, w, _ = tunnel_img.shape
                click_coord = tunnel[0] + int(w / 2), tunnel[1] + int(h / 2)
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
                h, w, _ = tunnel_img.shape
                click_coord = tunnel[0] + int(w / 2), tunnel[1] + int(h / 2)
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

                    last_texts = ['']
                    texts = []

                    while not result and last_texts != texts:
                        last_texts = texts
                        texts = []
                        for bbox, text, accuracy in self.ocr_reader.readtext(
                                self.clicker.screen[window[1]:window[3], window[0]:window[2]]):
                            texts.append(text)
                            if text == destination_name:
                                result = True
                                x, y = bbox[0]
                                x += window[0]
                                y += window[1]
                                self.clicker.move(x, y)
                                self.clicker.click(x + 1, y + 1)
                                print(datetime.datetime.now(), f'Выбран переход "{destination_name}"')
                                break

                        # Скроллим дальше, если возможно
                        if not result and last_texts != texts:
                            self.clicker.scroll(delta=-1000, x=tunnel_window_coord[0] + 100, y=tunnel_window_coord[1] + 100)
                            time.sleep(.5)
                            self.clicker.screen_lookup()

                    if not result:
                        print(datetime.datetime.now(), f'Переход "{destination_name}" не найден')

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

            last_texts = ['']
            texts = []

            while not result and last_texts != texts:
                last_texts = texts
                texts = []
                for bbox, text, accuracy in self.ocr_reader.readtext(self.clicker.screen[window[1]:window[3], window[0]:window[2]]):
                    texts.append(text)
                    if text == destination_name:
                        result = True
                        x, y = bbox[0]
                        x += window[0]
                        y += window[1]
                        self.clicker.move(x, y)
                        self.clicker.click(x + 1, y + 1)
                        print(datetime.datetime.now(), f'Выбран переход "{destination_name}"')
                        break
                    print(text)

                # Скроллим дальше, если возможно
                if not result and last_texts != texts:
                    self.clicker.scroll(delta=-1000, x=tunnel_window_coord[0] + 100, y=tunnel_window_coord[1] + 100)
                    time.sleep(.5)
                    self.clicker.screen_lookup()

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
            elif action == 'Ожидание перелета':
                return self.wait_for_warp()
            elif action == 'Пригласить в пати':
                return self.invite_to_party(attribute)
            elif action == 'Ожидание пати':
                return self.wait_for_party_request()
            elif action == 'Принять пати':
                return self.accept_party_request()
            elif action == 'Суицид':
                return self.suicide()
            elif action == 'Начать диалог':
                return self.start_dialog()
            elif type(action) in [tuple, list]:
                return self.fly_to(*action, mode=attribute)

        def delay(action):
            if action == 'Вылет':
                return time.sleep(10)
            elif action == 'Перелететь':
                return time.sleep(3)
            elif action == 'В туннель':
                return time.sleep(15)
            elif action == 'Ожидание перелета':
                return time.sleep(1)
            elif action == 'Пригласить в пати':
                return time.sleep(1)
            elif action == 'Ожидание пати':
                return time.sleep(1)
            elif action == 'Принять пати':
                return time.sleep(1)
            elif action == 'Суицид':
                return time.sleep(1)
            elif action == 'Начать диалог':
                return time.sleep(1)
            elif type(action) in [tuple, list]:
                return time.sleep(1)

        for index, route_point in enumerate(route):
            if self.is_dead():
                raise ValueError

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

    def find_text(self, text, window=None):
        self.clicker.screen_lookup(window=window)
        for bbox, ocr_text, accuracy in self.ocr_reader.readtext(
                self.clicker.screen):
            # print(ocr_text)
            if text in ocr_text:
                x, y = bbox[0]
                x += window[0]
                y += window[1]
                # self.clicker.move(x, y)
                # self.clicker.click(x + 1, y + 1)
                return x, y

        return None

    def is_dead(self, do_wait=True):
        current_time = time.time()
        if current_time - self.death_check_last_time > self.death_check_delay:
            self.death_check_last_time = current_time
            self.clicker.screen_lookup(window=(0, 0, -1, 200))
            dead_title_coord = next(iter(self.clicker.find_image(dead_title)), None)
            if dead_title_coord is not None:
                print(datetime.datetime.now(), f'Корабль подбит!')
                self.clicker.screen_lookup(
                    window=(*dead_title_coord, dead_title_coord[0] + 200, dead_title_coord[1] + 200))
                pay_button_coord = next(iter(self.clicker.find_image(pay_button)), None)
                if pay_button_coord is not None:
                    self.clicker.click(*pay_button_coord)
                    time.sleep(1)
                self.clicker.click(dead_title_coord[0] + 20, dead_title_coord[1] + 65)
                if do_wait:
                    time.sleep(random.randint(*self.after_death_wait_time_range))
                return True
        return False

    def open_cargo(self):
        self.clicker.screen_lookup()
        ship_tab_coord = next(iter(self.clicker.find_image(ship_tab)), None)
        if ship_tab_coord is not None:
            self.clicker.click(*ship_tab_coord)
        else:
            self.clicker.keypress('i')
            time.sleep(1)

            self.clicker.screen_lookup()
            ship_tab_coord = next(iter(self.clicker.find_image(ship_tab)), None)
            if ship_tab_coord is not None:
                self.clicker.click(*ship_tab_coord)
                time.sleep(1)
                self.clicker.screen_lookup()
            else:
                return False

        cargo_tab_coord = next(iter(self.clicker.find_image(cargo_tab)), None)
        if cargo_tab_coord is not None:
            self.clicker.click(*cargo_tab_coord)
            return True
        return False

    def drop_chests(self):
        self.open_cargo()
        self.clicker.screen_lookup()
        for chest_type in [chest_icon, black_chest_icon]:
            chest_coord = next(iter(self.clicker.find_image(chest_type)), None)
            while chest_coord is not None:
                self.clicker.ldown(*chest_coord)
                time.sleep(.5)
                self.clicker.move(10, 10)
                time.sleep(.5)
                self.clicker.lup(10, 10)
                time.sleep(4)
                self.clicker.screen_lookup()
                drop_button_coord = next(iter(self.clicker.find_image(drop_button)), None)
                if drop_button_coord is not None:
                    self.clicker.click(*drop_button_coord)
                time.sleep(1)
                self.clicker.screen_lookup()
                chest_coord = next(iter(self.clicker.find_image(chest_type)), None)

    def locate(self, image, threshold=.85, min_dist=10):
        self.clicker.screen_lookup(window=(-225, 15, -40, 200))
        coords = self.clicker.find_image(image, threshold=threshold, centers=True, min_dist=min_dist)
        return coords

    def approach(self, image, threshold=.85, distance=0):
        coords = self.locate(image=image, threshold=threshold)
        if not coords:
            return False

        closest_coord = min(coords, key=lambda x: math.dist(x, self.center))

        self.rotate_to_radar(closest_coord)

        last_closest_distance = math.dist(closest_coord, self.center)
        while last_closest_distance > distance:
            self.clicker.keypress(self.forward_key)
            coords = self.locate(image=image, threshold=threshold)
            if not coords:
                break

            closest_coord = min(coords, key=lambda x: math.dist(x, self.center))
            closest_distance = math.dist(closest_coord, self.center)
            if closest_distance > last_closest_distance + 2:
                break
            self.rotate_to_radar(closest_coord)
            last_closest_distance = closest_distance
            time.sleep(.1)

        self.clicker.keypress(win32con.VK_DOWN)

        # for i in range(7):
        #     self.clicker.keypress('^+')
        #
        # time.sleep(.5)
        # dandelions = self.locate_dandelions()
        # if not dandelions:
        #     for i in range(7):
        #         self.clicker.keypress('^-')
        #
        #     time.sleep(.5)
        #     return False
        # closest_dandelion = min(dandelions, key=lambda x: math.dist(x, self.center))
        # self.rotate_to_radar(closest_dandelion)
        # time.sleep(.5)
        #
        # for i in range(7):
        #     self.clicker.keypress('^-')
        #
        # time.sleep(.5)
        return True

    def locate_dandelions(self):
        self.clicker.screen_lookup(window=(-225, 15, -40, 200))
        dandelions = []
        for dandelion_type in [pink_dandelion, green_dandelion, orange_dandelion]:
            dandelions_of_type = self.clicker.find_image(dandelion_type, min_dist=10, threshold=.85)
            dandelions.extend(dandelions_of_type)

        for i, dandelion in enumerate(dandelions):
            dandelions[i] = (dandelion[0] + 6, dandelion[1] + 6)

        # for dandelion in dandelions:
        #     self.clicker.fill(window=(*dandelion, *dandelion), color=(0, 255, 0))

        # cv2.imwrite('screen.png', self.clicker.screen)

        return dandelions

    def move_to_dandelion(self):
        dandelions = self.locate_dandelions()
        if not dandelions:
            return False

        closest_dandelion = min(dandelions, key=lambda x: math.dist(x, self.center))
        self.rotate_to_radar(closest_dandelion)
        self.clicker.keypress(self.forward_key)

        last_closest_distance = math.dist(closest_dandelion, self.center)
        while last_closest_distance > 10:
            dandelions = self.locate_dandelions()
            if not dandelions:
                break
            closest_dandelion = min(dandelions, key=lambda x: math.dist(x, self.center))
            closest_dandelion_distance = math.dist(closest_dandelion, self.center)
            if closest_dandelion_distance > last_closest_distance + 2:
                break
            last_closest_distance = closest_dandelion_distance
            time.sleep(.1)

        self.clicker.keypress(win32con.VK_DOWN)

        for i in range(7):
            self.clicker.keypress('^+')

        time.sleep(.5)
        dandelions = self.locate_dandelions()
        if not dandelions:
            for i in range(7):
                self.clicker.keypress('^-')

            time.sleep(.5)
            return False
        closest_dandelion = min(dandelions, key=lambda x: math.dist(x, self.center))
        self.rotate_to_radar(closest_dandelion)
        time.sleep(.5)

        for i in range(7):
            self.clicker.keypress('^-')

        time.sleep(.5)
        return True

    def loot_dandelion(self):
        click_coord = (int(self.clicker.screen_width / 2), int(self.clicker.screen_height / 2) - 30)
        for i in range(10):
            self.clicker.clickr(*click_coord)
            time.sleep(.1)

        self.clicker.keypress(self.force_right_key)
        time.sleep(.5)
        self.clicker.keypress(self.force_forward_key)
        time.sleep(1)
        self.clicker.keypress(self.force_forward_key)

        for i in range(3):
            self.loot()
            time.sleep(.3)

    def dandelion_cycle(self):
        dandelions_global_coords = [
            (53, 32),
            (52, 28),
            (56, 25),
            (62, 25),
            (60, 28),
            (59, 31),
            (62, 34),
            (65, 33),
            (62, 38),
            (66, 39),
            (63, 41),
            (62, 42),
            (66, 45),
            (63, 47),
            (61, 45),
            (58, 44),
            (57, 48),
            (57, 48),
            (60, 50),
            (55, 50),
            (52, 48),
            (53, 42),
            (51, 39),
            (48, 38),
            (49, 32),
            (52, 36),
        ]

        for point in dandelions_global_coords:
            self.fly_to(*point, stop_at_destination=True, target_bias=1.5, stop_if_enemy_in_front_of_ship=False)
            time.sleep(1)
            if self.move_to_dandelion():
                time.sleep(.5)
                self.loot_dandelion()

    def start_dialog(self):
        self.clicker.screen_lookup()
        dialog_button_coord = next(iter(self.clicker.find_image(dialog_button)), None)
        if dialog_button_coord is not None:
            self.clicker.click(*dialog_button_coord)
            return True
        else:
            return False

    def select_dialog_option(self, option, index=1):
        index = index - 1
        option_image = {
            'стандарт': dialog_option,
            'закрыть': close_dialog_option,
            'квест': quest_dialog_option,
            'сдать': complete_dialog_option,
            'вопрос': question_dialog_option
        }.get(option, None)

        if option_image is None:
            return False
        else:
            self.clicker.screen_lookup()
            options = self.clicker.find_image(option_image, min_dist=5)
            if index < len(options):
                selected_option = options[index]
                h, w, _ = option_image.shape
                selected_option = (
                    selected_option[0] + int(w / 2),
                    selected_option[1] + int(h / 2)
                )
                self.clicker.click(*selected_option)
                return True
            else:
                return False

    def send_message_to_chat(self, message, key_delay=.1):
        self.clicker.keypress('\r')
        time.sleep(.5)
        for key in message:
            self.clicker.send_char(key)
            time.sleep(key_delay)
        self.clicker.keypress('\r')

    def invite_to_party(self, name):
        self.send_message_to_chat(f'/invite {name}')
        time.sleep(1)
        self.clicker.screen_lookup()
        invite_button_coord = next(iter(self.clicker.find_image(invite_button)), None)
        if invite_button_coord is not None:
            h, w, _ = invite_button.shape
            invite_button_coord = (
                invite_button_coord[0] + int(w / 2),
                invite_button_coord[1] + int(h / 2)
            )
            self.clicker.click(*invite_button_coord)
            return True
        else:
            return False

    def wait_for_party_request(self):
        self.clicker.screen_lookup()
        party_request_coord = next(iter(self.clicker.find_image(party_request)), None)
        while party_request_coord is None:
            if self.is_dead():
                raise ValueError
            time.sleep(1)
            self.clicker.screen_lookup()
            party_request_coord = next(iter(self.clicker.find_image(party_request)), None)
        return True

    def accept_party_request(self):
        self.clicker.screen_lookup()
        party_request_coord = next(iter(self.clicker.find_image(party_request)), None)
        if party_request_coord is not None:
            h, w, _ = party_request.shape
            party_request_coord = (
                party_request_coord[0] + int(w / 2),
                party_request_coord[1] + int(h / 2),
            )
            self.clicker.click(*party_request_coord)
            time.sleep(1)
            self.clicker.screen_lookup()
            accept_coord = next(iter(self.clicker.find_image(accept_button)), None)
            if accept_coord is not None:
                h, w, _ = accept_button.shape
                accept_coord = (
                    accept_coord[0] + int(w / 2),
                    accept_coord[1] + int(h / 2)
                )
                self.clicker.click(*accept_coord)
                return True
            else:
                return False
        else:
            return False

    def suicide(self):
        self.send_message_to_chat('/die')
        time.sleep(1)
        self.clicker.screen_lookup()
        to_city_coord = next(iter(self.clicker.find_image(to_city_button)), None)
        if to_city_coord is not None:
            h, w, _ = to_city_button.shape
            to_city_coord = (
                to_city_coord[0] + int(w / 2),
                to_city_coord[1] + int(h / 2)
            )
            self.clicker.click(*to_city_coord)
            time.sleep(21)
            if self.is_dead(do_wait=False):
                return True
            else:
                return False
        else:
            return False

    def start_new_game(self):
        pass

    def farm(self, mode=None):
        self.farm_start_time = time.time()
        return {
            "Убийство мобов в зоне": self.fly_in_zone_and_kill_mobs,
            "Рыбалка": self.fishing
        }[self.mode if mode is None else mode]()

    def fly_in_zone_and_kill_mobs(self):
        self.in_combat = True
        last_closest_target = None
        while self.is_farming():
            # Обработка смерти
            if self.is_dead():
                raise ValueError
            # Убиваем
            self.target_and_kill()

            time.sleep(.01)
            self.loot()  # Лутаем

            # Летим к следующей точке, если мобы кончились, или мы улетели за границу зоны
            if not self.in_combat or not self.in_area():
                self.loot()  # На всякий случай лутаем ещё
                closest_target = min(self.target_coords_range,
                                     key=lambda coords: math.dist(coords, self.radar_coords))
                # Чтобы не возвращаться в ту же самую точку каждый раз - меняем точку на следующую
                # если ближайшая точка посещалась в прошлый раз как отсутствовали цели.
                if closest_target == last_closest_target:
                    next_target_index = self.target_coords_range.index(closest_target) + 1
                    next_target_index = next_target_index if next_target_index < len(self.target_coords_range) else 0
                    closest_target = self.target_coords_range[next_target_index]

                if self.fly_to(*closest_target):
                    last_closest_target = closest_target
                self.in_combat = True
            else:
                time.sleep(.3)

    def fishing(self):
        bad_fishing_tries = 0
        max_bad_fishing_tries = self.fishing_spot_max_bad_fishing_tries
        catching_window_coords = (0, 0, -1, -1)
        fishing_in_progress = False
        last_continue_click_coord = None

        fishing_image = {
            True: fishing_spot,
            False: fishing_spot_eels
        }[len(self.locate(image=fishing_spot)) > 0]
        # if self.approach(fishing_image, distance=self.fishing_spot_approach_distance, threshold=self.fishing_spot_detection_precision):
        #     time.sleep(3)

        while True:
            # Обработка смерти
            if self.is_dead():
                raise ValueError

            try:
                is_farm_not_ended = self.is_farming()
                if not (is_farm_not_ended or fishing_in_progress):
                    break

                self.clicker.screen_lookup()
                # cv2.imwrite('screen.png', self.clicker.screen)
                continue_coords = next(iter(self.clicker.find_image(continue_img, window=catching_window_coords)), None)
                if continue_coords:
                    bad_fishing_tries = 0
                    full_net_coords = next(iter(self.clicker.find_image(full_net_img, window=catching_window_coords)), None)
                    if full_net_coords or not is_farm_not_ended:
                        # print(datetime.datetime.now(), 'Сеть заполнилась.')
                        pickup_coords = next(iter(self.clicker.find_image(pickup_img, window=catching_window_coords)), None)
                        if pickup_coords:
                            print(datetime.datetime.now(), 'Поднять сеть.')
                            fishing_in_progress = False
                            self.clicker.click(*pickup_coords)
                            time.sleep(3)
                            continue
                    else:
                        print(datetime.datetime.now(), 'Продолжить ловить.')
                        fishing_in_progress = True
                        continue_click_coord = (
                            continue_coords[0] + random.randint(1, 5),
                            continue_coords[1] + random.randint(1, 5)
                        )
                        while continue_click_coord == last_continue_click_coord:
                            continue_click_coord = (
                                continue_coords[0] + random.randint(1, 5),
                                continue_coords[1] + random.randint(1, 5)
                            )

                        self.clicker.click(*continue_click_coord)
                        last_continue_click_coord = continue_click_coord
                else:
                    catching_coords = next(iter(self.clicker.find_image(catching_img, catching_window_coords)), None)
                    # Возможно было перемещено пользователем
                    if catching_coords is None:
                        catching_coords = next(iter(self.clicker.find_image(catching_img)), None)

                    if catching_coords:
                        # print(datetime.datetime.now(), 'Ловля в прогрессе.')
                        # bad_fishing_tries = 0
                        catching_window_coords = (
                        catching_coords[0] - 10, catching_coords[1], catching_coords[0] + 400, catching_coords[1] + 600)
                    else:
                        start_catch_coords = next(
                            iter(self.clicker.find_image(start_catch_img, window=(-70, 360, -1, -1))), None)
                        if start_catch_coords:
                            print(datetime.datetime.now(), 'Начало рыбалки.')
                            fishing_in_progress = True
                            # bad_fishing_tries = 0
                            self.clicker.click(*start_catch_coords)
                        else:
                            print(datetime.datetime.now(), 'Кнопка начала рыбалки не была найдена!')
                            bad_fishing_tries += 1
                            fishing_in_progress = False
                            if bad_fishing_tries > max_bad_fishing_tries:
                                # beep(sync=True)
                                break

                            if self.approach(fishing_image, distance=self.fishing_spot_approach_distance,
                                             threshold=self.fishing_spot_detection_precision):
                                time.sleep(3)


                time.sleep(5)
            except win32ui.error:
                print(datetime.datetime.now(),
                      f'Случилась внутренняя ошибка windows при определении окна, '
                      f'будет произведена повторная попытка получить окно {self.clicker.hwnd}.')
                continue
            except ValueError:
                print(datetime.datetime.now(), f"Разверните окно {self.clicker.hwnd}!")
                beep(sync=True)
