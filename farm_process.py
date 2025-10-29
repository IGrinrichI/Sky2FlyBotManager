import sys
import time
import datetime
import traceback
from multiprocessing import Process, Pipe
from threading import Thread
import math
import winsound
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


def farm_process(hwnd, preset, trial_time, child_conn):
    child_conn.write = child_conn.send
    child_conn.flush = lambda : None
    sys.stdout = child_conn
    sys.stderr = child_conn

    clicker = Clicker(retry_color=[118, 105, 86])
    clicker.hwnd = hwnd
    player = Player(clicker=clicker)

    # Выставляем пресет
    player.load_preset(preset)

    print(datetime.datetime.now(), 'Процесс запущен.')

    # Вычисляем границы поля фарма
    player.calc_edges()

    while True:
        undock_with_overweight = False
        player.loot_on_fly = player.do_looting
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
            # Отдаляем радар
            for i in range(7):
                clicker.keypress('^-')
            time.sleep(2)
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


def get_farm_process(hwnd, preset, trial_time):
    from multiprocessing import freeze_support
    freeze_support()
    parent_conn, child_conn = Pipe()
    return Process(target=farm_process, args=(hwnd, preset, trial_time, child_conn)), parent_conn
