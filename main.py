import os
import sys
import time


if getattr(sys, 'frozen', False) and time.time() - os.path.getctime(sys.executable) > 3600 * 24:
    input('Триал окончен, обратитесь к разработчику ;)')
    raise SystemExit(0)

import datetime
from threading import Thread

import math

import winsound
from pynput import keyboard

from clicker import Clicker
from player import Player
import win32con


def beep(freq=1000, sync=False):
    def _beep():
        dur = 1000
        winsound.Beep(freq, dur)

    if sync:
        _beep()
    else:
        Thread(target=_beep, daemon=True).start()


clicker = Clicker()
clicker.hwnd = 0xC058E
player = Player(clicker=clicker)
autofire = False

# Задаем значения по умолчанию, они все равно будут переопределяться пресетом
# Путь к месту фарма
player.to_farm_path = [
    ('Перелететь', 'ФАРМ МЕДУЗ НЕ ТРОГАТЬ'),  # С базы в туннель
    ((29, 15), 'Переход между лабиринтами'),  # С 4 омута в 5
    ((45, 48), 'Быстро лететь к цели'),  # Прилет к медузкам
]
# Путь на базу
player.to_base_path = [
    ((49, 51), 'Переход между лабиринтами'),  # С 5 омута в 4
    ((34, 9), 'Лететь к цели'),  # Подлет к туннелю
    ('В туннель', 'База клана'),  # С туннеля на базу
]
player.target_coords_range = []
player.repeat_cycle_forever = False


def click_task():
    while True:
        with keyboard.Events() as events:
            event = events.get(.1)
            if isinstance(event, keyboard.Events.Press) and event.key == keyboard.Key.ctrl_l:
                if attack:
                    attack.pop()
                else:
                    attack.append(True)


if autofire:
    Thread(target=click_task, daemon=True).start()
    attack_delay = .6
    attack = []
    last_attack_time = time.time()
    while True:
        if time.time() - last_attack_time > attack_delay and attack:
            clicker.keypress(player.fire_key)
            last_attack_time = time.time()
        # clicker.screen_lookup(window=(-225, 15, -40, 200))
        # player.loot()
        time.sleep(min(.1, max(0, time.time() - last_attack_time)))

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
# tunnels = clicker.find_image(tunnel_img, threshold=.8)
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
presets = list(filter(lambda x: x.endswith('.preset'), os.listdir(os.getcwd())))
print("Доступные пресеты:")
print('\n'.join(f'{i}) {preset[:-len(".preset")]}' for i, preset in enumerate(presets, 1)))
preset_number = '2'
while not preset_number.isdigit() or preset_number == '0' or int(preset_number) > len(presets):
    preset_number = input('Укажите номер пресета: ')
# with open(presets[int(preset_number) - 1], 'r', encoding='utf-8') as f:
#     exec(f.read())

player.load_preset(presets[int(preset_number) - 1])

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
        player.fly_route(player.to_farm_path)

    if player.is_overweight():
        print(datetime.datetime.now(), 'Вылет с перегрузом.')
        undock_with_overweight = True
    else:
        # Активируем умения
        player.activate_abilities()

    # clicker.reset_keyboard()
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
        if undock_with_overweight:
            player.fly_route([player.to_base_path[-1]])
        else:
            player.fly_route(player.to_base_path)
    except ValueError:
        pass

    print(datetime.datetime.now(), 'В городе')
    player.target_bias = origin_target_bias

    time.sleep(1)
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы закрыть менюшки
    time.sleep(1)
    player.store_resources_and_service()
    time.sleep(1)

    if not player.repeat_cycle_forever:
        beep(1000, sync=True)
        beep(1100, sync=True)
        beep(1200, sync=True)
        break
