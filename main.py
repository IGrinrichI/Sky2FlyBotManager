import os
import random
import sys
import time

import numpy as np

from licence import get_trial_time

if getattr(sys, 'frozen', False):
    if not os.path.exists('key'):
        input('Отсутствует ключ доступа, обратитесь к разработчику.')
        raise SystemExit(0)

    with open('key', 'rb') as f:
        hash_key = f.read()
    # trial_time = get_trial_time(input('Введите ключ доступа: '))
    trial_time = get_trial_time(hash_key)
    if trial_time <= time.time():
        input('Триал окончен, обратитесь к разработчику ;)')
        raise SystemExit(0)
else:
    trial_time = 99999999999999999

import datetime
from threading import Thread

import math

import winsound
from pynput import keyboard

from clicker import Clicker
from player import Player, tunnel_img, vortex_img, fly_in_button, launch_saw_active_image, properties_tab, \
    reload_button, not_broken_saw_big_image, tech_slot_saw, tech_slot_auto_use
import win32con
import win32gui


def beep(freq=1000, sync=False):
    def _beep():
        dur = 1000
        winsound.Beep(freq, dur)

    if sync:
        _beep()
    else:
        Thread(target=_beep, daemon=True).start()


def get_s2f_hwnds():
    app_list = find_windows(window_name='Sky2Fly')
    s2f_actual_windows = [
        win32gui.FindWindowEx(
            win32gui.FindWindowEx(parent_hwnd, None, 'AtlAxWin100', None),
            None, 'MacromediaFlashPlayerActiveX', None
        )
        for parent_hwnd in app_list
    ]
    return s2f_actual_windows


def find_windows(window_name=None, window_class=None):
    """Finds all windows with a title matching the given name."""
    if window_name is None and window_class is None:
        return []

    def enum_windows_callback(hwnd, window_list):
        name = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        # print(name, class_name, win32gui.GetWindowRect(hwnd), visible)
        if ((window_name is None or window_name == name)
                and (window_class is None or window_class == class_name)
                and visible):
            window_list.append(hwnd)
        return True

    result = []
    win32gui.EnumWindows(enum_windows_callback, result)
    return result


clicker = Clicker(retry_color=np.array([118, 105, 86], dtype=np.uint8))
# clicker.hwnd = 0x3006E
clicker.hwnd = get_s2f_hwnds()[0]
player = Player(clicker=clicker)
autofire = False
quest = False

if autofire:
    def click_task():
        while True:
            with keyboard.Events() as events:
                event = events.get(.1)
                if isinstance(event, keyboard.Events.Press) and event.key == keyboard.Key.ctrl_l:
                    if attack:
                        attack.pop()
                    else:
                        attack.append(True)

    Thread(target=click_task, daemon=True).start()
    attack_delay = .6
    attack = []
    last_attack_time = time.time()
    while True:
        if time.time() - last_attack_time > attack_delay and attack:
            clicker.keypress(player.fire_key)
            last_attack_time = time.time()
            # clicker.screen_lookup(window=(-225, 15, -40, 200))
            player.loot()
        time.sleep(min(.1, max(0, time.time() - last_attack_time)))

if quest:
    import cv2


    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


    sushi_img = cv2.imread(resource_path(os.path.join('images', 'sushi.PNG')))
    decline_img = cv2.imread(resource_path(os.path.join('images', 'decline.PNG')))
    fiola_img = cv2.imread(resource_path(os.path.join('images', 'Fiola.PNG')))
    end_dialog_img = cv2.imread(resource_path(os.path.join('images', 'end_dialog.PNG')))
    continue_img = cv2.imread(resource_path(os.path.join('images', 'continue.PNG')))
    while True:
        clicker.screen_lookup()
        clicker.reset_keyboard()
        window = (850, 400, 1250, 750)

        clicker.click(int(clicker.screen_width / 2), int(clicker.screen_height * 2 / 5))
        time.sleep(1)

        clicker.screen_lookup(window=window)
        clicker.click(*clicker.find_image(sushi_img))
        time.sleep(1)

        clicker.screen_lookup(window=window)
        continue_coord = clicker.find_image(continue_img)
        if continue_coord:
            clicker.click(*continue_coord)
            time.sleep(1)
            clicker.screen_lookup(window=window)
            clicker.click(*clicker.find_image(sushi_img))
            time.sleep(1)

        target_npc = None
        while target_npc is None:
            clicker.screen_lookup(window=window)
            target_npc = clicker.find_image(fiola_img)
            if target_npc is None:
                clicker.screen_lookup(window=window)
                clicker.click(*clicker.find_image(decline_img))
                time.sleep(1)
                clicker.screen_lookup(window=window)
                clicker.click(*clicker.find_image(sushi_img))
                time.sleep(1)
            else:
                clicker.click(*clicker.find_image(sushi_img))
                time.sleep(1)

        clicker.screen_lookup(window=window)
        clicker.click(*clicker.find_image(end_dialog_img))

        player.fly_to(30, 62, "Быстро лететь к цели", target_bias=2)
        player.fly_to(31, 70, "Быстро лететь к цели", target_bias=0, stop_at_destination=True)
        time.sleep(1)

        clicker.click(int(clicker.screen_width / 2), int(clicker.screen_height * 2 / 5))
        time.sleep(1)
        clicker.screen_lookup(window=window)
        clicker.click(*clicker.find_image(sushi_img))
        time.sleep(1)
        clicker.screen_lookup(window=window)
        clicker.click(*clicker.find_image(sushi_img))
        time.sleep(1)
        clicker.screen_lookup(window=window)
        clicker.click(*clicker.find_image(end_dialog_img))

        player.fly_to(30, 62, "Быстро лететь к цели", target_bias=1)
        player.fly_to(40, 47, "Быстро лететь к цели", target_bias=0, stop_at_destination=True)
        time.sleep(1)

player.clicker.screen_lookup()

# player.clicker.keydown('[Shift]')
# time.sleep(.5)
player.clicker.click(960, 200)
# time.sleep(.5)
# player.clicker.keyup('[Shift]')
exit()
# player.check_auto_use()
# exit()
# print(player.find_tech(tech_slot_saw))
# print(player.find_slot_in_items(not_broken_saw_big_image))

# print(player.attribute_cross_naming_en_ru)
# print(player.attribute_cross_naming_ru_en)
#
#
# preset_dir = 'presets'
# preset_path_list = (os.path.join(preset_dir, preset_name) for preset_name in os.listdir(preset_dir))
#
# for preset_path in preset_path_list:
#     with open(preset_path, 'r', encoding='utf8') as f:
#         file_data = f.read()
#         for parameter, replacement in player.attribute_cross_naming_en_ru.items():
#             file_data = file_data.replace(parameter, replacement.capitalize(), 1)
#
#     with open(preset_path, 'w', encoding='utf8') as ff:
#         ff.write(file_data)

# with open("Инструкция по пресетам.txt", "r", encoding="utf8") as f:
#     file_data = f.read()
#     for parameter, replacement in player.attribute_cross_naming_en_ru.items():
#         index = file_data.find(parameter)
#         if index == -1:
#             continue
#
#         index += len(parameter) + len('" или "')
#         if file_data[index] == '"':
#             file_data = file_data[:index] + replacement.capitalize() + file_data[index:]
#
#     with open("Инструкция по пресетам_.txt", "w", encoding="utf8") as ff:
#         ff.write(file_data)

# coord = clicker.wait_for_image(reload_button, threshold=.8, timeout=1)
# print(coord[0] + 183 + 0, coord[1] - 318 + 23)
# print(player.saw_prep_in_dock())

# directions = []
# max_dist = 0
# last_max_dist = max_dist
# min_dist = 10
# last_min_dist = min_dist
# while True:
#     player.lookup_direction()
#     if player.player_direction not in directions:
#         directions.append((player.player_direction, player.player_angle))
#         directions.sort(key=lambda d: d[1])
#         # print(directions)
#         if len(directions) > 1:
#             max_dist = max(math.dist(a[0], b[0]) for a, b in zip(directions[1:], directions))
#             min_dist = min(math.dist(a[0], b[0]) for a, b in zip(directions[1:], directions))
#
#             # print_diff = False
#
#             # if max_dist > last_max_dist:
#             #     last_max_dist = max_dist
#             #     print_diff = True
#             #
#             # if min_dist < last_min_dist:
#             #     last_min_dist = min_dist
#             #     print_diff = True
#             #
#             # if print_diff:
#             print(min_dist, max_dist)
#
#     # print(player.player_angle)
#     time.sleep(.05)
# player.clicker.screen_lookup()
# player.clicker.scroll(x=516, y=238)
# player.clicker.scroll(-1000, x=900, y=400)
# player.fly_from_base_to("На платформу Фейра-ди-Сантана")
# exit()
# for i in range(10):
#     player.scale_in_radar()
#     player.scale_out_radar()
    # player.activate_ability(1)

# player.approach(vortex_img, threshold=.2, stop_action_image=fly_in_button, stop_distance_diff=4)
# player.fly_through_vortex()

# player.fly_route([
#     ["Вылет", ["ю"]],
#     [[86, 47], "Быстро лететь к цели"],
#     ["Пролететь через вихрь", ""],
#     [[84, 73], "Быстро лететь к цели"],
#     [[70, 92], "Быстро лететь к цели"],
#     [[40, 91], "Переход между лабиринтами"],
#     [[50, 50], "Переход между лабиринтами"],
# ])

# import cv2
# tree_image = cv2.imread(os.path.join('images', 'tree_spot.png'))
# # tree_image = cv2.imread(os.path.join('images', 'tree_spot_orange.png'))
# launch_saw_image = cv2.imread(os.path.join('images', 'launch_saw_inactive_button.png'))
# player.approach(image=tree_image,
#                 distance=player.fishing_spot_approach_distance,
#                 threshold=player.fishing_spot_detection_precision,
#                 stop_action_image=launch_saw_image,
#                 very_slow=True,
#                 # correct_rotation=False
#                 )

# exit()
from image_finder import find_template_on_image
# origin_image = imread('pht.jpg')
# centers = np.array(find_template_on_image(origin_image, tunnel_img, circle_mask=False, centers=True, threshold=.7, min_dist=None))
# print(centers)
# origin_image = np.array(origin_image[:, :, ::-1])
# origin_image[centers[:, 1], centers[:, 0]] = [255, 0, 0]
# from imaginary import ImageShower
# shower = ImageShower()
# shower.display(origin_image)
# input()
# exit()
# player.fly_to_base_trough_tunnel(1)
# exit()
# player.approach(tunnel_img, threshold=player.tunnel_detection_precision, distance=5)
#
# exit()

# player.lookup_direction()
# exit()
from imaginary import ImageShower
shower = ImageShower()
hashes = dict()


player.shower = shower
while True:
    if not player.get_auto_use(13):
        print('FUCK')
    shower.display(player.clicker.screen[:,:,::-1])
    continue
    # print(player.set_speed_arm_value(-1))
    # print(player.set_low_speed())
    # start = time.time()
    # player.lookup_direction()

    # screen, offset = clicker.screen_lookup(window=(-225, 15, -40, 200))
    screen, offset = clicker.screen_lookup(window=player.tech_window)

    radar = screen
    # centers = np.array(find_template_on_image(radar, vortex_img, circle_mask=False, centers=True, threshold=.2, min_dist=None))
    (119, 123, 109)
    (255, 255, 255)
    (1642, 1018)
    (1595, 1067)
    dx = 47
    dy = 49
    (1360, 1067)
    centers = np.array(find_template_on_image(radar, tech_slot_saw, circle_mask=False, centers=True, threshold=.4, min_dist=None))
    radar = radar[:, :, ::-1]
    if len(centers) > 0:
        radar[centers[:, 1], centers[:, 0]] = [255, 0, 0]
    else:
        print('FUCK')

    # player.check_auto_use()
    # tech_slot = player.get_tech_slot_number(tech_slot_saw, screen=screen, offset=offset)
    # print(tech_slot)
    # print(player.get_auto_use(tech_slot))
    # shower.display(clicker.screen[:, :, ::-1])

    # print(clicker._resolve_coord(1362 + 2, 1018 - 23 + 1))
    # print(clicker._resolve_coord(1362 + 2 - 1920, 1018 - 23 + 1 - 1080))
    #
    # for x in range(1360 + 2, 1643 + 2, 47):
    #     for y in range(1018 - 23 + 1, 1068 - 23 + 1, 49):
    #         if ((radar[y - offset[1], x - offset[0]] == (255, 255, 255)).all()
    #                 or (radar[y - offset[1], x - offset[0]] == (119, 123, 109)).all()):
    #             radar[y - offset[1], x - offset[0]] = [255, 0, 0]
    #
    # for x in range(1360 + -1, 1643 + -1, 47):
    #     for y in range(1018 - 23 + 2, 1068 - 23 + 2, 49):
    #         if ((radar[y - offset[1], x - offset[0]] == (255, 255, 255)).all()
    #                 or (radar[y - offset[1], x - offset[0]] == (119, 123, 109)).all()):
    #             radar[y - offset[1], x - offset[0]] = [255, 0, 0]



    shower.display(radar)
    # ld_time = time.time() - start
    # print('ld', ld_time)
    # coords = [
    #     (-136, 104), (-135, 104), (-134, 104), (-133, 104), (-132, 104), (-131, 104),
    #     (-136, 105),                                                     (-131, 105),
    #     (-136, 106),                                                     (-131, 106),
    #     (-136, 107),                                                     (-131, 107),
    #     (-136, 108),                                                     (-131, 108),
    #     (-136, 109), (-135, 109), (-134, 109), (-133, 109), (-132, 109), (-131, 109),
    # ]
    # start = time.time()
    # clicker.screen_lookup(window=(-141, 99, -126, 114))
    # clicker.screen_lookup(window=(-134, 106, -133, 107))


    # print(hashes[angle_hash], hashes[angle_hash] == player.player_angle)
    # clicker.fill(window=(-135, 105, -132, 108), color=(0, 0, 0))
    # pixel_values = np.array([clicker.pixel(*pxl) for pxl in pixels])
    # pixel = pixels[np.argmax(pixel_values[:, 1])]
    # target_pixel = (30, 190, 25)
    # diff = 25
    # for coord in coords:
    #     pixel = clicker.pixel(*coord)
    #     if all(abs(pixel - target_pixel) < diff):
    #         pixel = clicker._resolve_coord(*coord)
    #         break
    # clicker.fill(window=(*pixel, *pixel), color=(255, 0, 0))


    # pixels = np.array(clicker.find_pixels(window=(-136, 104, -131, 109), color=target_pixel, threshold=0.87))
    # print(np.polyfit(pixels[:, 0], pixels[:, 1], 1)[0])
    # exit()
    # pixels = clicker.find_pixels(window=(-136, 104, -131, 109), color=target_pixel, threshold=0.9)
    # pixel_window = (min(p[0] for p in pixels) - 1, min(p[1] for p in pixels) - 1, max(p[0] for p in pixels) + 1, max(p[1] for p in pixels) + 1)
    # pixels.extend(clicker.find_pixels(window=pixel_window, color=target_pixel, threshold=0.9))
    # # print(clicker.pixel(*pixel))
    #
    # for pixel in pixels:
    #     clicker.fill(window=(*pixel, *pixel), color=(255, 0, 0))
    #
    # print({p: math.dist(p, player.center) for p in set(pixels)})
    # pixel = max(set(pixels), key=lambda x: math.dist(player.center, x))
    # clicker.fill(window=(*pixel, *pixel), color=(0, 0, 255))

    # nld_time = time.time() - start
    # print('nld', nld_time)
    # print(nld_time / ld_time)
    # clicker.fill(window=(*pixel, *pixel), color=(255, 0, 0))
    # pxl = clicker.find_pixel(window=(-136, 104, -131, 109), color=())
    # for pxl in clicker.find_pixels(window=(-136, 104, -131, 109), color=):
    #     clicker.fill(window=(*pxl, *pxl), color=(0, 0, 0))
    # clicker.fill(window=(-136, 104, -131, 109), color=(0, 0, 0))
    # shower.display(clicker.screen[:,:,::-1])
    time.sleep(.1)
exit()


# def broken(clicker):
#     for i in range(30):
#         clicker.screen_lookup()
#
# if __name__ == '__main__':
#     from multiprocessing import freeze_support
#     freeze_support()
#     from multiprocessing import Process
#     threads = [Process(target=broken, args=(Clicker(retry_color=np.array([118, 105, 86], dtype=np.uint8), hwnd=get_s2f_hwnds()[i]), )) for i in range(10)]
#     start = time.time()
#     for thread in threads:
#         thread.start()
#     for thread in threads:
#         thread.join()
#     print(time.time() - start)
#
# exit()


# fishing_spot = cv2.imread(os.path.join('images', 'fishing_spot.png'))
# start_catch_img = cv2.imread(os.path.join('images', 'start_fishing.png'))
# player.approach(image=fishing_spot,
#                 distance=player.fishing_spot_approach_distance,
#                 threshold=player.fishing_spot_detection_precision,
#                 stop_action_image=start_catch_img,
#                 # very_slow=True,
#                 # correct_rotation=False
#                 )
# while True:
# player.rotate_to_radar(image=tree_image)
# player.force_right()

exit()

# import cv2
# fishing_image = cv2.imread(os.path.join('images', 'fishing_spot.png'))
# player.approach(fishing_image, distance=4, threshold=.65)
# player.drop_chests()
# player.send_message_to_chat('/die')
# player.start_dialog()
# player.select_dialog_option('закрыть', 1)
# raise SystemExit(0)

# from imaginary import ImageShower
# shower = ImageShower()
# while True:
    # shower.display(clicker.screen[:,:,::-1])
    # time.sleep(.1)

# Задаем значения по умолчанию, они все равно будут переопределяться пресетом
# Путь к месту фарма
player.to_farm_path = [
    ('Перелететь', 'ФАРМ МЕДУЗ НЕ ТРОГАТЬ'),  # С базы в тоннель
    ((29, 15), 'Переход между лабиринтами'),  # С 4 омута в 5
    ((45, 48), 'Быстро лететь к цели'),  # Прилет к медузкам
]
# Путь на базу
player.to_base_path = [
    ((49, 51), 'Переход между лабиринтами'),  # С 5 омута в 4
    ((34, 9), 'Лететь к цели'),  # Подлет к туннелю
    ('В тоннель', 'База клана'),  # С туннеля на базу
]
player.target_coords_range = []
player.repeat_cycle_forever = False






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

# clicker.screen_lookup(window=(800, 300, 1200, 700))

# clicker.screen_lookup()
# print(player.fly_from_base_to('ФАРМ МЕДУЗ НЕ ТРОГАТЬ'))
# time.sleep(3)
# print(player.fly_to_base_trough_tunnel())
# player.fly_from_base_to('ФАРМ МЕДУЗ НЕ ТРОГАТЬ')
# time.sleep(3)

# Летим на фарм
# player.fly_route(route=player.to_farm_path)
# time.sleep(10)
# player.fly_route(route=player.to_base_path)
# for index, coord, mode in enumerate(player.to_farm_path):
#     while not player.fly_to(*coord, mode=mode):
#         time.sleep(1)
#         backup_coord, backup_mode = player.to_farm_path[index - 1]
#         player.fly_to(*backup_coord, mode=backup_mode)
#     time.sleep(1)

# time.sleep(20)

# Летим на базу
# for coord, mode in player.to_base_path:
#     player.fly_to(*coord, mode=mode)
#     time.sleep(1)

# player.fly_to_base_trough_tunnel()
# raise SystemExit(0)

# clicker.screen_lookup(window=(-225, 15, -40, 200))
# tunnel_img = cv2.imread('images/tunnel.bmp')
# tunnels = clicker.find_images(tunnel_img, threshold=.8)
# for tunnel in tunnels:
#     print(tunnel)
#     clicker.fill(window=(*tunnel, tunnel[0] + tunnel_img.shape[1], tunnel[1] + tunnel_img.shape[0]), color=(0, 255, 0))
#
# cv2.imwrite('screen.png', clicker.screen)
# raise SystemExit(0)


# # Кружится вокруг небесной канцелярии)
# radius = 9
# player.target_coords_range = [(50 + int(math.cos(x * math.pi / 180) * radius), 50 + int(math.sin(x * math.pi / 180) * radius)) for x in range(10, 360, 50)]
# print(player.target_coords_range)
#
# player.target_bias = 3
# while True:
#     for target_coords in player.target_coords_range:
#         player.fly_to(*target_coords, rotate_first=False, speed_up=False)


# Выставляем пресет
if hasattr(sys, '_MEIPASS'):
    preset_dir = os.getcwd()
else:
    preset_dir = os.path.join(os.getcwd(), 'presets')
presets = list(filter(lambda x: x.endswith('.preset'), os.listdir(preset_dir)))
print("Доступные пресеты:")
print('\n'.join(f'{i}) {preset[:-len(".preset")]}' for i, preset in enumerate(presets, 1)))
preset_number = ''
while not preset_number.isdigit() or preset_number == '0' or int(preset_number) > len(presets):
    preset_number = input('Укажите номер пресета: ')
# with open(presets[int(preset_number) - 1], 'r', encoding='utf-8') as f:
#     exec(f.read())

player.load_preset(os.path.join(preset_dir, presets[int(preset_number) - 1]))

print('Наведите курсор мыши на игру и нажмите Ctrl.')
s2f_hwnd_set = set()
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

# Вычисляем границы поля фарма
player.calc_edges()

while True:
    undock_with_overweight = False
    clicker.reset_keyboard()
    # Если запустили с места фарма, то незачем лететь
    try:
        player.lookup_coords()
    except ValueError:
        try:
            player.fly_route(player.to_farm_path)
        except ValueError:
            continue

    if player.is_overweight():
        print(datetime.datetime.now(), 'Вылет с перегрузом.')
        undock_with_overweight = True
    else:
        time.sleep(1)
        player.scale_out_radar()
        time.sleep(1)
        # Активируем умения
        player.activate_abilities()

    # clicker.reset_keyboard()
    last_closest_target = None
    player.farm_start_time = time.time()
    origin_target_bias = player.target_bias
    player.in_combat = True
    try:
        while player.is_farming():
            # Обработка смерти
            if player.is_dead():
                raise ValueError
            # Убиваем
            player.target_and_kill()

            time.sleep(.01)
            player.loot()  # Лутаем

            # Летим к следующей точке, если мобы кончились, или мы улетели за границу зоны
            if not player.in_combat or not player.in_area():
                player.loot()  # На всякий случай лутаем ещё
                closest_target = min(player.target_coords_range, key=lambda coords: math.dist(coords, player.radar_coords))
                # Чтобы не возвращаться в ту же самую точку каждый раз - меняем точку на следующую
                # если ближайшая точка посещалась в прошлый раз как отсутствовали цели.
                if closest_target == last_closest_target:
                    next_target_index = player.target_coords_range.index(closest_target) + 1
                    next_target_index = next_target_index if next_target_index < len(player.target_coords_range) else 0
                    closest_target = player.target_coords_range[next_target_index]

                if player.fly_to(*closest_target):
                    last_closest_target = closest_target
                player.in_combat = True
            else:
                time.sleep(.3)

        if player.is_overweight():
            print(datetime.datetime.now(), 'Перегруз')
        print(datetime.datetime.now(), 'Фарм окончен, летим в город.')
        # Летим в центр (город)
        player.loot_on_fly = False
        if undock_with_overweight:
            player.fly_route([player.to_base_path[-1]])
        else:
            # Выкидываем сундуки
            if player.do_drop_chests:
                player.drop_chests()
            player.fly_route(player.to_base_path)
    except ValueError:
        pass

    print(datetime.datetime.now(), 'В городе')
    player.target_bias = origin_target_bias
    player.loot_on_fly = True

    time.sleep(1)
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    time.sleep(1)
    player.store_resources_and_service()
    time.sleep(1)
    player.reload_gasholders()
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    time.sleep(1)

    if not player.repeat_cycle_forever or trial_time <= time.time():
        beep(1000, sync=True)
        beep(1100, sync=True)
        beep(1200, sync=True)
        break
