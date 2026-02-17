import os
import sys
import time
import datetime
import traceback
from multiprocessing import Process, Pipe
from threading import Thread
import math
import winsound
from clicker import Clicker
from exceptions import StopFarmException
from player import Player
import win32con

from ram_cleaner import start_ram_cleaner


def beep(freq=1000, sync=False):
    def _beep():
        dur = 1000
        winsound.Beep(freq, dur)

    if sync:
        _beep()
    else:
        Thread(target=_beep, daemon=True).start()


def farm_process(hwnd, preset, trial_time, child_conn, screen_lookup_lock):
    try:
        child_conn.write = child_conn.send
        child_conn.flush = lambda : None
        sys.stdout = child_conn
        sys.stderr = child_conn

        clicker = Clicker(retry_color=[118, 105, 86], screen_lookup_lock=screen_lookup_lock)
        clicker.hwnd = hwnd
        player = Player(clicker=clicker)

        # Выставляем пресет
        player.load_preset(preset)

        # Запускаем периодическую очистку RAM
        if player.clean_ram_periodically:
            start_ram_cleaner(hwnd=hwnd, max_ram=player.min_ram_to_clean)

        print(datetime.datetime.now(), 'Процесс запущен.')

        # Вычисляем границы поля фарма
        player.calc_edges()

        while True:
            try:
                undock_with_overweight = False
                player.loot_on_fly = player.do_looting
                clicker.reset_keyboard()
                # Если запустили с места фарма, то незачем лететь
                try:
                    player.lookup_coords()
                except ValueError:
                    if player.check_state_in_city_before_farm:
                        player.in_city_actions()

                    try:
                        player.fly_route(player.to_farm_path)
                    except ValueError:
                        continue

                if player.is_overweight():
                    print(datetime.datetime.now(), 'Вылет с перегрузом.')
                    undock_with_overweight = True
                else:
                    time.sleep(1)
                    # Отдаляем радар
                    player.scale_out_radar()
                    # Активируем умения
                    player.activate_abilities()

                # clicker.reset_keyboard()
                try:
                    # Процесс фарма
                    player.farm()

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

                player.in_city_actions()
            except StopFarmException:
                player.log_error("Фарм будет окончен!")
                player.repeat_cycle_forever = False

            if (not player.repeat_cycle_forever and not player.next_preset) or trial_time <= time.time():
                beep(1000, sync=True)
                beep(1100, sync=True)
                beep(1200, sync=True)
                break

            if not player.repeat_cycle_forever and player.next_preset:
                next_preset = player.next_preset + ('.preset' if not player.next_preset.endswith('.preset') else '')
                if not hasattr(sys, '_MEIPASS'):
                    next_preset = os.path.join('presets', next_preset)
                # Не знаю как лучше перетирать данные с прошлых пресетов, поэтому пересоздаем игрока
                player = Player(clicker=clicker)
                # Выставляем пресет
                player.load_preset(next_preset)
                # Вычисляем границы поля фарма
                player.calc_edges()
    except Exception:
        print(traceback.format_exc())


def get_farm_process(hwnd, preset, trial_time, screen_lookup_lock):
    from multiprocessing import freeze_support
    freeze_support()
    parent_conn, child_conn = Pipe()
    return Process(target=farm_process, args=(hwnd, preset, trial_time, child_conn, screen_lookup_lock), daemon=True), parent_conn
