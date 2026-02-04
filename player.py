import datetime
import json
import math
import random
import time
import os
import sys
from threading import Thread, Lock, Event

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

# Координаты радара
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
# Картинка с крестиком в залоченной цели
enemy_locked_on = cv2.imread(resource_path(os.path.join('images', 'enemy_locked_on.bmp')))

# Город/сервис/склад
service_button = cv2.imread(resource_path(os.path.join('images', 'service.bmp')))
service_title = cv2.imread(resource_path(os.path.join('images', 'service_title.png')))
service_all_button = cv2.imread(resource_path(os.path.join('images', 'service_all.bmp')))
service_tech_button = cv2.imread(resource_path(os.path.join('images', 'service_tech.png')))
service_quit_button = cv2.imread(resource_path(os.path.join('images', 'service_quit.png')))
take_all_button = cv2.imread(resource_path(os.path.join('images', 'take_all.bmp')))
storage_button = cv2.imread(resource_path(os.path.join('images', 'storage.bmp')))
all_to_storage_button = cv2.imread(resource_path(os.path.join('images', 'all_to_storage.bmp')))
storage_tab = cv2.imread(resource_path(os.path.join('images', 'storage_tab.png')))
storage_search_box = cv2.imread(resource_path(os.path.join('images', 'storage_search_box.PNG')))
buying_up_opened_button = cv2.imread(resource_path(os.path.join('images', 'buying_up_opened_button.PNG')))
buying_up_closed_button = cv2.imread(resource_path(os.path.join('images', 'buying_up_closed_button.PNG')))

# Тоннель
# tunnel_img = cv2.imread(resource_path(os.path.join('images', 'tunnel.bmp')))
tunnel_img = cv2.imread(resource_path(os.path.join('images', 'tunnel.png')), cv2.IMREAD_UNCHANGED)
tunnel_window_title = cv2.imread(resource_path(os.path.join('images', 'tunnel_window_title.bmp')))
tunnel_window_base_title = cv2.imread(resource_path(os.path.join('images', 'tunnel_window_base_title.bmp')))

# Диалоги
dialog_button = cv2.imread(resource_path(os.path.join('images', 'dialog_button.PNG')))
dialog_option = cv2.imread(resource_path(os.path.join('images', 'dialog_option.png')))
quest_dialog_option = cv2.imread(resource_path(os.path.join('images', 'quest_dialog_option.png')))
question_dialog_option = cv2.imread(resource_path(os.path.join('images', 'question_dialog_option.png')))
complete_dialog_option = cv2.imread(resource_path(os.path.join('images', 'complete_dialog_option.png')))
close_dialog_option = cv2.imread(resource_path(os.path.join('images', 'close_dialog_option.png')))

# Корабль/трюм
ship_tab = cv2.imread(resource_path(os.path.join('images', 'ship_tab.PNG')))
cargo_tab = cv2.imread(resource_path(os.path.join('images', 'cargo_tab.PNG')))
equipment_tab = cv2.imread(resource_path(os.path.join('images', 'equipment_tab.bmp')))
crew_title = cv2.imread(resource_path(os.path.join('images', 'crew_title.png')))
tech_title = cv2.imread(resource_path(os.path.join('images', 'tech_title.png')))
items_from_storage_title = cv2.imread(resource_path(os.path.join('images', 'items_from_storage_title.png')))
equipment_search_box = cv2.imread(resource_path(os.path.join('images', 'equipment_search_box.png')))
gasholder_low_charge_img = cv2.imread(resource_path(os.path.join('images', 'gasholder_low_charge.bmp')))
gasholder_full_charge_img = cv2.imread(resource_path(os.path.join('images', 'gasholder_full_charge.png')))
reload_button = cv2.imread(resource_path(os.path.join('images', 'reload.PNG')))
chest_icon = cv2.imread(resource_path(os.path.join('images', 'chest.PNG')))
black_chest_icon = cv2.imread(resource_path(os.path.join('images', 'black_chest.PNG')))
drop_button = cv2.imread(resource_path(os.path.join('images', 'drop_button.PNG')))

# Оружие
properties_tab = cv2.imread(resource_path(os.path.join('images', 'properties_tab.PNG')))
change_tab = cv2.imread(resource_path(os.path.join('images', 'change_tab.PNG')))
manufacture_tab = cv2.imread(resource_path(os.path.join('images', 'manufacture_tab.PNG')))
description_tab = cv2.imread(resource_path(os.path.join('images', 'description_tab.PNG')))

# Техи
tech_slot_saw = cv2.imread(resource_path(os.path.join('images', 'tech_slot_saw.PNG')), cv2.IMREAD_UNCHANGED)

# Действия с смертью и приглашением в группу
to_city_button = cv2.imread(resource_path(os.path.join('images', 'to_city_button.PNG')))
dead_title = cv2.imread(resource_path(os.path.join('images', 'your_ship_down.PNG')))
pay_button = cv2.imread(resource_path(os.path.join('images', 'pay.png')))
invite_button = cv2.imread(resource_path(os.path.join('images', 'invite_button.PNG')))
party_request = cv2.imread(resource_path(os.path.join('images', 'party_request.PNG')))
accept_button = cv2.imread(resource_path(os.path.join('images', 'accept_button.PNG')))

# Одуванчики
pink_dandelion = cv2.imread(resource_path(os.path.join('images', 'pink_dandelion.png')))
green_dandelion = cv2.imread(resource_path(os.path.join('images', 'green_dandelion.png')))
orange_dandelion = cv2.imread(resource_path(os.path.join('images', 'orange_dandelion.png')))

# Вихрь для пролета в небе
vortex_img = cv2.imread(resource_path(os.path.join('images', 'vortex.PNG')))

# Рыбалка
fishing_spot = cv2.imread(resource_path(os.path.join('images', 'fishing_spot.png')))
fishing_spot_eels = cv2.imread(resource_path(os.path.join('images', 'fishing_spot_eels.png')))
catching_img = cv2.imread(resource_path(os.path.join('images', 'catching.png')))
start_catch_img = cv2.imread(resource_path(os.path.join('images', 'start_fishing.png')))
pickup_img = cv2.imread(resource_path(os.path.join('images', 'pickup.png')))
continue_img = cv2.imread(resource_path(os.path.join('images', 'continue_catching.png')))
full_net_img = cv2.imread(resource_path(os.path.join('images', 'full_net.png')))

# Дровосекорубство
tree_image_base = cv2.imread(resource_path(os.path.join('images', 'tree_spot.png')))
tree_image_orange = cv2.imread(resource_path(os.path.join('images', 'tree_spot_orange.png')))
launch_saw_inactive_image = cv2.imread(resource_path(os.path.join('images', 'launch_saw_inactive_button.png')))
launch_saw_active_image = cv2.imread(resource_path(os.path.join('images', 'launch_saw_active_button.png')))
broken_saw_big_image = cv2.imread(resource_path(os.path.join('images', 'broken_saw_big.png')))
not_broken_saw_big_image = cv2.imread(resource_path(os.path.join('images', 'not_broken_saw_big.png')))
broken_saw_big_storage_image = cv2.imread(resource_path(os.path.join('images', 'broken_saw_big_storage.bmp')))

# Вход в док и пролёт/залёт во что-то
dock_button = cv2.imread(resource_path(os.path.join('images', 'dock_button.bmp')))
fly_in_button = cv2.imread(resource_path(os.path.join('images', 'fly_in_button.PNG')))

# Магазин
buy_for_button = cv2.imread(resource_path(os.path.join('images', 'buy_for_button.bmp')))
buy_saw_big_button = cv2.imread(resource_path(os.path.join('images', 'buy_saw_big_button.bmp')))
shop_button = cv2.imread(resource_path(os.path.join('images', 'shop_button.bmp')))
shop_equipment_button = cv2.imread(resource_path(os.path.join('images', 'shop_equipment_button.bmp')))
exit_button = cv2.imread(resource_path(os.path.join('images', 'exit_button.bmp')))

# Иконка босса
boss = cv2.imread(resource_path(os.path.join('images', 'boss.png')))


class Player:
    mode = 'Убийство мобов в зоне'
    next_preset = None
    on_error_save_image = False
    check_state_in_city_before_farm = False
    warp_bias = 7
    target_bias = 3
    stuck_delay = 3
    stuck_difference = 1.5
    rotating = False
    rotation_direction = None
    rotation_angle = None
    rotating_to = None
    rotation_button_pressed = False
    update_rotation_lock = Lock()
    stop_rotate_event = Event()
    rotation_stopped_event = Event()
    rotation_thread = None
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
    delay_between_farm_attempts = 0.3

    abilities = []
    kill_enemies = True
    spam_attack = False
    spam_attack_stop_event = None
    spam_attack_interval = 0.17
    last_attack_time = 0
    enemy_types = []  # ['neutral', 'agressive', 'special']
    smart_targeting = True
    fire_when_smart_targeting = True
    do_drop_chests = True
    loot_on_fly = True
    do_looting = True
    last_looting_time = 0
    loot_distance = 30
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

    action_timeout = 5
    scale_in_out_radar_delay = 1
    scaled_radar = False
    scaled_value = 3
    radar_to_global_ratio = 10 / 90
    # cx = 1786.5
    cx = 1786.5 - 1920
    cy = 106.5
    _center = (cx, cy)
    r = 7.5
    w = 2.75
    wr = round(w + 2, 0)
    green_buff = 1.07
    radar_window = (-225, 15, -40, 200)
    action_window = (-70, 360, -1, -1)
    action_detection_precision = .8
    tech_window = (-600, -100, -265, -1)
    tech_detection_precision = .4

    storage_filters_window = (-450, -170, -1, -100)
    city_services_window = (-600, -80, -1, -1)

    press_esc_after_radar_action = False
    fly_to_object_key = 'Клик левой кнопкой мыши'
    force_key = 'f'
    force_forward_key = 'q'
    force_left_key = 'x'
    force_right_key = 'c'
    forward_key = 'w'
    break_target_key = 'z'
    fire_key = ' '
    inventory_key = 'i'
    auto_use_all_key = '~'
    radar_in_key = '[Ctrl]+'
    radar_out_key = '[Ctrl]-'
    activate_ability_1_key = '[Ctrl]1'
    activate_ability_2_key = '[Ctrl]2'
    activate_ability_3_key = '[Ctrl]3'
    activate_ability_4_key = '[Ctrl]4'
    activate_ability_5_key = '[Ctrl]5'
    activate_ability_6_key = '[Ctrl]6'
    activate_ability_7_key = '[Ctrl]7'
    activate_ability_8_key = '[Ctrl]8'
    activate_ability_9_key = '[Ctrl]9'
    esc_key = win32con.VK_ESCAPE
    enter_key = '\r'

    _ocr_reader = None

    positioning_to_the_center = False

    tunnel_detection_precision = .7
    tunnel_approach_distance = 10

    fishing_spot_detection_precision = .65
    fishing_spot_approach_distance = 4
    fishing_spot_max_bad_fishing_tries = 1

    tree_spot_detection_precision = .65
    tree_spot_approach_distance = 4
    tree_spot_max_bad_cutting_tries = 1
    change_saw_after_no_looting_time = 30
    additional_saw_amount = 3

    dandelion_detection_precision = .85
    dandelion_approach_distance = 10

    vortex_detection_precision = .2
    vortex_approach_distance = 10

    attribute_cross_naming_en_ru = {
        "mode": "режим работы",
        "next_preset": "следующий пресет",
        "on_error_save_image": "в случае ошибки сохранять изображение",
        "check_state_in_city_before_farm": "выполнять проверку в начале перед вылетом",
        "warp_bias": "изменение координат, считающееся перелетом в другую локацию",
        "target_bias": "отклонение от координат перелетов",
        "stuck_delay": "задержка, после которой считается, что корабль застрял",
        "stuck_difference": "разница координат, считающаяся застреванием",
        # "rotating": "",
        # "rotation_direction": "",
        # "rotation_angle": "",
        # "rotating_to": "",
        # "rotation_button_pressed": "",
        # "update_rotation_lock": "",
        # "stop_rotate_event": "",
        # "rotation_stopped_event": "",
        # "rotation_thread": "",
        "direction_bias": "отклонение от заданного направления/точность поворота",
        # "radar_coords": "",
        # "target_coords": "",
        # "target_direction": "",
        # "target_angle": "",
        # "target_distance": "",
        # "player_direction": "",
        # "player_angle": "",
        # "player_direction_certain": "",
        "circle_area": "зона фарма является кругом/бубликом",
        "area_points": "точки зоны фарма в случае, если зона не является кругом, а многоугольником",
        # "area_edges": "",
        "area_coords": "центр зоны фарма",
        # "area_direction": "",
        # "distance_to_area": "",
        "min_distance_from_area": "минимальное расстояние зоны от её центра",
        "max_distance_away_from_area": "максимальное расстояние зоны от её центра",
        
        "to_farm_path": "путь к месту фарма",
        "to_base_path": "путь в док",
        "target_coords_range": "список координат, по которым будет осуществляться пермещение в процессе фарма",
        "repeat_cycle_forever": "повторять цикл фарма бесконечно",
        
        # "farm_start_time": "",
        "max_farm_time": "максимальное время фарма",
        "delay_between_farm_attempts": "задержка между циклами процесса фарма",
        
        "abilities": "способности для активации",
        "kill_enemies": "убивать врагов",
        "spam_attack_interval": "интервал атак при спаме",
        "spam_attack": "спамить атаку",
        # "spam_attack_stop_event": "",
        # "last_attack_time": "",
        "enemy_types": "типы врагов для убийства",
        "fire_when_smart_targeting": "спамить атаку, когда цель выделена",
        "smart_targeting": "умное выделение цели",
        "do_drop_chests": "выкидывать сундуки",
        "loot_on_fly": "собирать ресурсы, когда летишь куда-то",
        "do_looting": "собирать ресурсы",
        # "last_looting_time": "",
        "loot_distance": "дистанция подбора",
        "ignore_overweight": "игнорировать перегруз",
        "stop_if_enemy_in_front_of_ship": "останавливаться, если перед кораблем враг",
        "stop_at_destination": "останавливаться при достижении точки(-ек) назначения",
        "jump_forward_on_lose_target": "ускоряться вперед, когда цель потеряна",
        # "enemy_focused": "",
        # "last_time_enemy_focused": "",
        "enemy_focusing_max_time": "максимальное время на захват/поиск цели",
        # "enemy_focused_at": "",
        "enemy_kill_timeout": "максимальное время на убийство цели",
        
        "death_check_delay": "задержка между проверками подбит ли корабль",
        # "death_check_last_time": "",
        "after_death_wait_time_range": "диапазон времени в секундах, сколько ждать после смерти игрока перед началом нового цикла",
        
        "available_directions_to_undock": "доступные для вылета направления",
        # "coords_to_undock": "",
        "fly_trough_tunnel_tries_amount": "количество попыток воспользоваться тоннелем",
        
        "action_timeout": "таймаут на ожидание открытия окон",
        "scale_in_out_radar_delay": "задержка после масштабирования радара",
        # "scaled_radar": "",
        # "scaled_value": "",
        # "radar_to_global_ratio": "",
        # "cx": "",
        # "cy": "",
        # "_center": "",
        # "r": "",
        # "w": "",
        # "wr": "",
        # "green_buff": "",
        # "action_window": "",
        "action_detection_precision": "точность определения действий",
        # "tech_window": "",
        "tech_detection_precision": "точность определения техов",
        
        # "storage_filters_window": "",
        # "city_services_window": "",
        
        "press_esc_after_radar_action": "нажимать клавишу esc после взаимодействия с радаром",
        "fly_to_object_key": "лететь к объекту",
        "force_key": "форсаж вперед (расходуется охладитель)",
        "force_forward_key": "ускорение вперед",
        "force_left_key": "ускорение влево",
        "force_right_key": "ускорение вправо",
        "forward_key": "лететь вперед",
        "break_target_key": "сбросить цель",
        "fire_key": "залп из всех орудий",
        "inventory_key": "трюм/корабль",
        "auto_use_all_key": "вкл. автоиспользование всех техустройств",
        "radar_in_key": "масштаб радара крупнее",
        "radar_out_key": "масштаб радара мельче",
        "activate_ability_1_key": "активное умение 1",
        "activate_ability_2_key": "активное умение 2",
        "activate_ability_3_key": "активное умение 3",
        "activate_ability_4_key": "активное умение 4",
        "activate_ability_5_key": "активное умение 5",
        "activate_ability_6_key": "активное умение 6",
        "activate_ability_7_key": "активное умение 7",
        "activate_ability_8_key": "активное умение 8",
        "activate_ability_9_key": "активное умение 9",
        # "esc_key": "",
        # "enter_key": "",
        
        # "_ocr_reader": "",
        
        "positioning_to_the_center": "располагать корабль в центре области фарма",
        
        "tunnel_detection_precision": "точность определения тоннеля",
        "tunnel_approach_distance": "дистанция приближения тоннелю",
        
        "fishing_spot_detection_precision": "точность определения рыболовного места",
        "fishing_spot_approach_distance": "дистанция приближения к рыболовному месту",
        "fishing_spot_max_bad_fishing_tries": "количество попыток вернуться на рыболовное место",
        
        "tree_spot_detection_precision": "точность определения дерева",
        "tree_spot_approach_distance": "дистанция приближения к дереву",
        "tree_spot_max_bad_cutting_tries": "количество попыток вернуться на дерево",
        "change_saw_after_no_looting_time": "таймаут на замену дровосека, если не замечено ресурсов для подбора",
        "additional_saw_amount": "количество дровосеков, которые берутся в трюм перед вылетом",
        
        "dandelion_detection_precision": "точность определения одуванчика",
        "dandelion_approach_distance": "дистанция приближения к одуванчику",
        
        "vortex_detection_precision": "точность определения вихря",
        "vortex_approach_distance": "дистанция приближения к вихрю",
    }
    attribute_cross_naming_ru_en = {value: key for key, value in attribute_cross_naming_en_ru.items()}

    def __init__(self, clicker):
        self.clicker = clicker

    def log_message(self, text):
        print(str(datetime.datetime.now()), text)

    def log_error(self, text):
        print(str(datetime.datetime.now()), text)
        if self.on_error_save_image:
            self.clicker.save_dump(text)

    def force_left(self):
        self.clicker.keypress(self.force_left_key)

    def force_right(self):
        self.clicker.keypress(self.force_right_key)

    def force_forward(self):
        self.clicker.keypress(self.force_forward_key)

    def move_forward(self, force=False):
        if force:
            self.clicker.keypress(self.force_key)
        else:
            self.clicker.keypress(self.forward_key)

    def activate_ability(self, ability: int):
        if type(ability) is int and 0 < ability < 10:
            self.clicker.keypress(eval(f'self.activate_ability_{ability}_key'))
            return True
        return False

    def activate_abilities(self):
        for ability in self.abilities:
            if self.activate_ability(ability):
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
            self.log_message(f'Вылет в направлении "{direction}".')
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
        screen, offset = self.clicker.screen_lookup(window=(-12, -42, -12, -42))
        return all(self.clicker.pixel(-12, -42, screen=screen, offset=offset) == (255, 226, 229))

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

    def service_all_for_dl(self):
        service_coord = self.clicker.wait_for_image(
            image=service_button, window=self.city_services_window, centers=True, timeout=self.action_timeout)
        if service_coord:
            self.log_message('Сервис.')
            self.clicker.click(*service_coord)
            service_title_coord = self.clicker.wait_for_image(image=service_title, threshold=.8,
                                                              timeout=self.action_timeout)
            if service_title_coord:
                screen, offset = self.clicker.screen_lookup(window=(service_title_coord[0] - 20, service_title_coord[1], -1, -1))
                service_all_coord = self.clicker.find_image(image=service_all_button, threshold=.8, centers=True,
                                                            screen=screen, offset=offset)
                if service_all_coord:
                    self.log_message('Зарядить всё.')
                    self.clicker.click(*service_all_coord)
                    return True
                else:
                    service_tech_coord = self.clicker.find_image(image=service_tech_button, threshold=.8, centers=True,
                                                                 screen=screen, offset=offset)
                    if service_tech_coord:
                        self.log_message('Зарядить техустройства.')
                        self.clicker.click(*service_tech_coord)
                        return True
                    else:
                        service_quit_coord = self.clicker.find_image(image=service_quit_button, threshold=.8,
                                                                     centers=True,
                                                                     screen=screen, offset=offset)
                        if service_quit_coord:
                            self.log_message('Выйти из сервиса.')
                            self.clicker.click(*service_quit_coord)
                            return True
                        else:
                            self.log_error('Кнопка зарядки сервиса не была найдена!')
                            self.clicker.click(*service_coord)
                            return False
            else:
                self.log_error('Окно сервиса не открылось за отведенное время!')
                return False
        else:
            self.log_error('Кнопка "Сервис" не обнаружена!')
            return False

    def open_storage(self):
        screen, offset = self.clicker.screen_lookup(window=self.city_services_window)
        storage_coord = self.clicker.find_image(storage_button, centers=True, screen=screen, offset=offset)
        if storage_coord:
            self.clicker.click(*storage_coord)
            storage_search_box_coord = self.clicker.wait_for_image(
                image=storage_search_box, window=self.storage_filters_window, centers=True, timeout=self.action_timeout)
            if storage_search_box_coord:
                self.log_message('Склад открыт.')
                return True
            else:
                self.log_error('Склад не открыт!')
                return False
        else:
            screen, offset = self.clicker.screen_lookup(window=self.storage_filters_window)
            storage_search_box_coord = self.clicker.find_image(
                image=storage_search_box, centers=True, screen=screen, offset=offset)
            if storage_search_box_coord:
                self.log_message('Склад открыт.')
                return True

            self.log_error('Кнопка "Склад" не обнаружена!')
            return False

    def toggle_buying_up(self, state):
        screen, offset = self.clicker.screen_lookup(window=self.city_services_window)
        buying_up_opened_button_coord = self.clicker.find_image(buying_up_opened_button, centers=True, threshold=0.99,
                                                                screen=screen, offset=offset)
        buying_up_closed_button_coord = self.clicker.find_image(buying_up_closed_button, centers=True, threshold=0.99,
                                                                screen=screen, offset=offset)
        if (buying_up_opened_button_coord and state) or (buying_up_opened_button_coord is None and not state):
            return True

        if state and buying_up_closed_button_coord:
            self.clicker.click(*buying_up_closed_button_coord)
            self.log_message("Открыта скупка.")
            return True
        elif not state and buying_up_opened_button_coord:
            self.clicker.click(*buying_up_opened_button_coord)
            self.log_message("Закрыта скупка.")
            return True
        else:
            self.log_error("Кнопка скупки не найдена!")
            return False

    def exit(self):
        screen, offset = self.clicker.screen_lookup(window=self.city_services_window)
        exit_coord = self.clicker.find_image(exit_button, centers=True, screen=screen, offset=offset)
        if exit_coord is not None:
            self.clicker.move_and_click(*exit_coord)
            return True
        return False

    def store_resources_to_storage(self):
        if not self.open_storage():
            return False

        screen, offset = self.clicker.screen_lookup()
        store_all = self.clicker.find_image(image=all_to_storage_button, threshold=.99, centers=True,
                                            screen=screen, offset=offset)
        if store_all:
            self.log_message('Всё на склад.')
            self.clicker.click(*store_all)
            time.sleep(1)
            self.exit()
            return True
        else:
            self.log_error('Кнопка "Всё на склад" не обнаружена!')
            self.exit()
            return False

    def store_resources_and_service(self):
        # Сервис
        if self.service_all_for_dl():
            time.sleep(2)
        # Склад
        self.store_resources_to_storage()

    def reload_gasholders(self):
        self.log_message("Зарядка газгольдеров.")
        if not self.open_ship():
            return False

        screen, offset = self.clicker.screen_lookup()
        gasholders_to_reload_window = self.clicker.find_image(equipment_tab, screen=screen, offset=offset)
        gasholders_to_reload_window = (0, gasholders_to_reload_window[1], gasholders_to_reload_window[0], -1)
        gasholder_low_charge_coord = self.clicker.find_image(gasholder_low_charge_img, window=gasholders_to_reload_window,
                                                             screen=screen, offset=offset)
        while gasholder_low_charge_coord is not None:
            self.clicker.click(gasholder_low_charge_coord[0] + 20, gasholder_low_charge_coord[1] - 20)
            properties_tab_coord = self.clicker.wait_for_image(properties_tab, timeout=self.action_timeout)
            # screen, offset = self.clicker.screen_lookup()
            # gasholder_low_charge_coord = self.clicker.find_image(gasholder_low_charge_img, screen=screen, offset=offset)
            # self.clicker.click(gasholder_low_charge_coord[0] + 20, gasholder_low_charge_coord[1] + 70)  # Открыть окно газгольдера
            self.clicker.click(properties_tab_coord[0] + 35, properties_tab_coord[1] + 180)  # Открыть окно газгольдера
            reload_coord = self.clicker.wait_for_image(reload_button, threshold=.8, timeout=self.action_timeout)
            self.clicker.click(*reload_coord)  # Перезарядить
            self.log_message("Заряжен газгольдер.")
            time.sleep(1)
            self.clicker.click(reload_coord[0] + 183, reload_coord[1] - 318)  # Закрытие окна газгольдера
            self.clicker.keypress(win32con.VK_ESCAPE)  # Закрытие окна оружия
            time.sleep(1)
            screen, offset = self.clicker.screen_lookup(window=gasholders_to_reload_window)
            gasholder_low_charge_coord = self.clicker.find_image(gasholder_low_charge_img, screen=screen, offset=offset)

        self.log_message("Газгольдеры заряжены.")

        return True

    def break_target(self):
        self.clicker.keypress(self.break_target_key)
        self.enemy_focused = False

    def is_locked_on_enemy(self):
        screen, offset = self.clicker.screen_lookup(window=(400, 0, -325, 100))
        if self.clicker.find_image(enemy_locked_on, threshold=.99, screen=screen, offset=offset):
            self.enemy_focused = True
            return self.enemy_focused
        else:
            self.enemy_focused = False
            return self.enemy_focused

    def locate_enemies(self):
        if not self.enemy_types:
            return []
        # start = time.time()
        screen, offset = self.clicker.screen_lookup(window=self.radar_window)
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

            neutral_enemies = self.clicker.find_pixels(color=(221, 221, 221), min_dist=enemy_replace_pixels + 1, screen=screen, offset=offset)
            neutral_enemies = [(enemy_coord[0] + 1, enemy_coord[1] + 1) for enemy_coord in neutral_enemies]

        aggressive_enemies = []
        if 'agressive' in self.enemy_types:
            enemy_replace_pixels = 5
            aggressive_enemy = self.clicker.find_pixel(color=(255, 0, 0), screen=screen, offset=offset)
            while aggressive_enemy:
                if math.dist(aggressive_enemy, self.center) < 90:
                    pxl = self.clicker.pixel(aggressive_enemy[0] - 1, aggressive_enemy[1], screen=screen, offset=offset)
                    if pxl[1] == pxl[2] and abs(pxl[0] + pxl[1] * 5) % 255 < pxl[1]:
                        aggressive_enemies.append(aggressive_enemy)
                self.clicker.fill(
                    window=(aggressive_enemy[0] - enemy_replace_pixels, aggressive_enemy[1] - enemy_replace_pixels,
                            aggressive_enemy[0] + enemy_replace_pixels, aggressive_enemy[1] + enemy_replace_pixels),
                    color=(0, 0, 0),
                    screen=screen, offset=offset
                )
                aggressive_enemy = self.clicker.find_pixel(color=(255, 0, 0), screen=screen, offset=offset)

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

            special_enemies = self.clicker.find_pixels(color=(139, 0, 255), min_dist=enemy_replace_pixels + 1, screen=screen, offset=offset)
            special_enemies = [(enemy_coord[0] + 1, enemy_coord[1] + 2) for enemy_coord in special_enemies]

        bosses = []
        if 'boss' in self.enemy_types:
            screen, offset = self.clicker.screen_lookup(window=self.radar_window)
            bosses = self.clicker.find_images(boss, min_dist=10, threshold=.8, centers=True, screen=screen, offset=offset)

        enemies = neutral_enemies + aggressive_enemies + special_enemies + bosses

        directions = {coord: (coord[0] - self.center[0], coord[1] - self.center[1]) for coord in enemies}
        enemies = sorted(enemies, key=lambda coord: math.dist(coord, self.center) * (2 - np.dot(directions[coord] / np.linalg.norm(directions[coord]), self.player_direction)))
        # print(self.player_direction, [(enemy[0] - self.center[0], enemy[1] - self.center[1]) for enemy in enemies])
        # print(time.time() - start)
        # for index, enemy in enumerate(enemies):
        #     self.clicker.fill(window=(*enemy, *enemy),
        #                  color=(255 - int(255 / len(enemies)) * index, 0, 0), screen=screen, offset=offset)
        # cv2.imwrite('screen.png', screen)
        return enemies, screen, offset

    def is_enemy_valid(self, enemy_coord, screen=None, offset=None):
        # Проверка, что цель не находится за границей зоны фарма
        enemy_global_coord = (
            (enemy_coord[0] - self.center[0]) * self.radar_to_global_ratio / (self.scaled_value if self.scaled_radar else 1) + self.radar_coords[0],
            (enemy_coord[1] - self.center[1]) * self.radar_to_global_ratio / (self.scaled_value if self.scaled_radar else 1) + self.radar_coords[1]
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
            if screen is None or offset is None:
                screen, offset = self.clicker.screen_lookup(window=self.radar_window)

            for pixel_index in range(4, int(distance_to_enemy) - 10, 1):
                outer_target_pixel = self.clicker.pixel(
                    enemy_coord[0] - int(enemy_direction[0] * pixel_index),
                    enemy_coord[1] - int(enemy_direction[1] * pixel_index),
                    screen=screen, offset=offset
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

    def start_spam_attack(self):
        def spam_attack(stop_event):
            while not stop_event.is_set():
                self.clicker.keypress(self.fire_key)
                time.sleep(self.spam_attack_interval)

        if self.spam_attack and self.spam_attack_stop_event is None:
            self.spam_attack_stop_event = Event()
            Thread(target=spam_attack, args=(self.spam_attack_stop_event, ), daemon=True).start()

    def stop_spam_attack(self):
        if self.spam_attack and self.spam_attack_stop_event is not None:
            self.spam_attack_stop_event.set()
            self.spam_attack_stop_event = None

    def target_and_kill(self):
        if not self.kill_enemies or self.spam_attack:
            return False

        last_focus_state = self.enemy_focused
        locked_on_enemy = self.is_locked_on_enemy()

        if not last_focus_state and locked_on_enemy:
            self.enemy_focused_at = time.time()
        elif locked_on_enemy and time.time() - self.enemy_focused_at > self.enemy_kill_timeout:
            self.log_error('Превышено время на убийство цели!')
            self.break_target()
            time.sleep(.3)
            locked_on_enemy = False

        jump = last_focus_state and not locked_on_enemy and self.jump_forward_on_lose_target
        # locate closest enemy (neutral)
        target_enemy = False
        if not locked_on_enemy:
            self.lookup_coords()
            self.lookup_direction()
            enemy_coords, screen, offset = self.locate_enemies()
            for enemy_coord in enemy_coords:
                if self.is_enemy_valid(enemy_coord, screen=screen, offset=offset):
                    target_enemy = True
                    if self.smart_targeting:
                        self.clicker.move(*enemy_coord)
                        time.sleep(.01)
                        self.clicker.dblclick(*enemy_coord)
                        time.sleep(.01)
                        if self.press_esc_after_radar_action:
                            self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось
                    else:
                        self.clicker.keypress(self.fire_key)
                        self.last_attack_time = time.time()
                    break

            if jump:
                self.clicker.keypress(self.force_forward_key)

            self.clicker.dblclick(0, 0)  # Чтобы убрать курсор с радара и ускориться
        else:
            self.in_combat = True
            if self.smart_targeting:
                if self.fire_when_smart_targeting:
                    enemy_coords, screen, offset = self.locate_enemies()
                    if not enemy_coords or math.dist(enemy_coords[0], self.center) < 30:
                        self.clicker.keypress(self.fire_key)
                        self.last_attack_time = time.time()
            else:
                self.clicker.keypress(self.fire_key)
                self.last_attack_time = time.time()

        return locked_on_enemy or target_enemy

    def locate_loot(self):
        loot = []
        loot_replace_radius = 4
        screen, offset = self.clicker.screen_lookup(window=self.radar_window)
        replace_color = (0, 0, 0)
        # locate loot
        loot_pixel = self.clicker.find_pixel(color=(255, 229, 0), screen=screen, offset=offset)
        while loot_pixel:
            coord_to_click = (loot_pixel[0], loot_pixel[1] + 2)
            loot.append(coord_to_click)
            self.clicker.fill(
                window=(coord_to_click[0] - loot_replace_radius, coord_to_click[1] - loot_replace_radius,
                        coord_to_click[0] + loot_replace_radius, coord_to_click[1] + loot_replace_radius),
                color=replace_color,
                screen=screen, offset=offset
            )
            loot_pixel = self.clicker.find_pixel(color=(255, 229, 0), screen=screen, offset=offset)

        return loot

    def loot(self):
        if not self.do_looting:
            return False

        # locate loot
        looting = False  # loot_pixel is not None
        for coord_to_click in self.locate_loot():
            if math.dist(coord_to_click, self.center) < self.loot_distance:
                looting = True
                self.clicker.move(*coord_to_click)
                time.sleep(.01)
                self.clicker.dblclick(*coord_to_click)
                time.sleep(.01)
                if self.press_esc_after_radar_action:
                    self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось

        if looting:
            screen, offset = self.clicker.screen_lookup()
            take_all_coord = self.clicker.find_image(take_all_button, threshold=.99, screen=screen, offset=offset)
            if take_all_coord:
                self.log_message('Взять всё.')
                self.clicker.click(*take_all_coord)
                time.sleep(.3)
                if self.is_locked_on_enemy():
                    self.in_combat = True
                self.break_target()

            self.clicker.move(0, 0)  # Чтобы убрать курсор с радара

            self.last_looting_time = time.time()

        return looting

    def lookup_coords(self):
        screen, offset = self.clicker.screen_lookup(binary=True, window=(-149, 209, -117, 213))
        result_coords = list()
        for key, image in coord_imgs.items():
            result_coords.extend((coord[0], key) for coord in self.clicker.find_images(image, threshold=.99, screen=screen, offset=offset))
        coords_str = ''.join(map(lambda coord_value: coord_value[1], sorted(result_coords, key=lambda x: x[0])))
        try:
            self.radar_coords = tuple(map(int, coords_str.split(':')))
        except ValueError:
            self.log_error("Координаты радара не обнаружены, возможно корабль не в небе!")
            raise
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
        screen, offset = self.clicker.screen_lookup(window=(-135, 105, -132, 108))
        dir_view = screen#[6:10, 6:10]
        dir_view[1:-1, 1:-1] = np.array([0, 0, 0])
        dir_idx = np.unravel_index(np.argmax(dir_view[:, :, 1]), dir_view[:, :, 1].shape)
        left_idx, right_idx = {
            (0, 0): lambda: ((1, 0), (0, 1)),
            (0, 1): lambda: ((0, 0), (0, 2)),
            (0, 2): lambda: ((0, 1), (0, 3)),
            (0, 3): lambda: ((0, 2), (1, 3)),
            (1, 3): lambda: ((0, 3), (2, 3)),
            (2, 3): lambda: ((1, 3), (3, 3)),
            (3, 3): lambda: ((2, 3), (3, 2)),
            (3, 2): lambda: ((3, 3), (3, 1)),
            (3, 1): lambda: ((3, 2), (3, 0)),
            (3, 0): lambda: ((3, 1), (2, 0)),
            (2, 0): lambda: ((3, 0), (1, 0)),
            (1, 0): lambda: ((2, 0), (0, 0)),
        }[dir_idx]()
        left_pixel = dir_view[left_idx]
        dir_pixel = dir_view[dir_idx]
        right_pixel = dir_view[right_idx]

        left_border = [float((int(a) + int(b) - 3)) for a, b in zip(left_idx, dir_idx)]
        right_border = [float((int(a) + int(b) - 3)) for a, b in zip(dir_idx, right_idx)]

        left_value = int(dir_pixel[1]) - int(left_pixel[1])
        right_value = int(dir_pixel[1]) - int(right_pixel[1])
        total_value = left_value + right_value
        tdir = (
            (left_border[0] * (total_value - left_value) + right_border[0] * (total_value - right_value)) / total_value,
            (left_border[1] * (total_value - left_value) + right_border[1] * (total_value - right_value)) / total_value
        )
        tdir_len = pow(tdir[0] ** 2 + tdir[1] ** 2, .5)
        tdir = (tdir[0] / tdir_len, tdir[1] / tdir_len)[::-1]

        asin = math.asin(tdir[1])
        if asin == 0:
            asin_coef = -1
        else:
            asin_coef = asin / abs(asin)

        t_angle = (math.acos(tdir[0]) * 180 / math.pi) * -asin_coef + 180 * (1 + asin_coef)

        self.player_direction = tdir
        self.player_angle = t_angle
        self.player_direction_certain = True

        # dir_view[left_idx] = np.array([0, 0, 255])
        # dir_view[dir_idx] = np.array([255, 0, 0])
        # dir_view[right_idx] = np.array([255, 0, 255])
        # self.shower.display(dir_view)
        return
        screen, offset = self.clicker.screen_lookup(window=(-141, 99, -126, 114))

        # cv2.imwrite('screen.png', screen)
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

            pixel = self.clicker.pixel(*coords_to_check[i], screen=screen, offset=offset)
            if (pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]
                    and math.dist(pixel, (223, 247, 180)) > 30):
                continues_pixels = [i]
                for j in range(i + 1, min(i + coords_index_offset, len(coords_to_check))):
                    coord = coords_to_check[j]
                    pixel = self.clicker.pixel(*coord, screen=screen, offset=offset)
                    if (pixel[1] > pixel[0] * self.green_buff and pixel[1] > pixel[2]
                            and math.dist(pixel, (223, 247, 180)) > 30):
                        continues_pixels.append(j)
                        # self.clicker.fill(window=(coord[0], coord[1], coord[0], coord[1]), color=(0, 0, 255), screen=screen, offset=offset)
                if continues_pixels[-1] > coords_index_offset:
                    pixel_index = continues_pixels[int(len(continues_pixels) / 2)]
                    coord = coords_to_check[pixel_index]
                    self.clicker.fill(window=(coord[0] - self.wr, coord[1] - self.wr, coord[0] + self.wr, coord[1] + self.wr), color=(0, 0, 0), screen=screen, offset=offset)
                    self.clicker.fill(window=(coord[0], coord[1], coord[0], coord[1]), color=(0, 0, 255), screen=screen, offset=offset)
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
            #     cv2.imwrite('screen.png', screen)
            #     self.clicker.keypress(self.fire_key)
            #     raise SystemExit(0)
        else:
            self.player_direction_certain = False
            # print(person_borders)
            # cv2.imwrite('screen.png', screen)
            # self.clicker.keypress(self.fire_key)
            # raise SystemExit(0)

    def rotate_to_direction(self, direction, angle=None, sync=True):
        def rotate():
            try:
                self.lookup_direction()
            except Exception:
                self.rotating = False
                return

            rotation_timeout = 1
            last_player_direction = self.player_direction

            rotation_time = time.time()

            while self.rotating:
                with self.update_rotation_lock:
                    self.rotating = (not self.stop_rotate_event.is_set()
                                     and math.dist(self.player_direction, self.rotation_direction) > self.direction_bias
                                     and self.player_direction_certain
                                     and time.time() - rotation_time < rotation_timeout)

                    if not self.rotating:
                        if time.time() - rotation_time >= rotation_timeout:
                            self.log_error('Залип поворот!')
                            self.clicker.reset_keyboard()
                        #     self.clicker.keypress(win32con.VK_LEFT)
                        #     self.clicker.keypress(win32con.VK_RIGHT)
                        # else:
                        #     self.clicker.keyup(win32con.VK_LEFT)
                        #     self.clicker.keyup(win32con.VK_RIGHT)
                        if self.rotation_button_pressed:
                            self.clicker.keypress(win32con.VK_LEFT)
                            self.clicker.keypress(win32con.VK_RIGHT)

                        self.rotation_button_pressed = False
                        self.rotating_to = None
                        self.stop_rotate_event.clear()
                        self.rotation_stopped_event.set()
                        break

                    if ((0 < self.player_angle - self.rotation_angle < 180)
                            or (0 < self.player_angle + 360 - self.rotation_angle < 180)):
                        if self.rotating_to == 'left':
                            # self.clicker.keyup(win32con.VK_LEFT)
                            # self.clicker.keyup(win32con.VK_RIGHT)
                            self.clicker.keypress(win32con.VK_LEFT)
                            self.clicker.keypress(win32con.VK_RIGHT)
                            self.rotation_button_pressed = False
                            self.rotating_to = None
                            self.rotating = False
                            self.stop_rotate_event.clear()
                            self.rotation_stopped_event.set()
                            break
                        self.clicker.keyup(win32con.VK_LEFT)
                        self.clicker.keydown(win32con.VK_RIGHT)
                        self.rotation_button_pressed = True
                        self.rotating_to = 'right'
                    else:
                        if self.rotating_to == 'right':
                            # self.clicker.keyup(win32con.VK_LEFT)
                            # self.clicker.keyup(win32con.VK_RIGHT)
                            self.clicker.keypress(win32con.VK_LEFT)
                            self.clicker.keypress(win32con.VK_RIGHT)
                            self.rotation_button_pressed = False
                            self.rotating_to = None
                            self.rotating = False
                            self.stop_rotate_event.clear()
                            self.rotation_stopped_event.set()
                            break
                        self.clicker.keyup(win32con.VK_RIGHT)
                        self.clicker.keydown(win32con.VK_LEFT)
                        self.rotation_button_pressed = True
                        self.rotating_to = 'left'

                if self.player_direction != last_player_direction:
                    last_player_direction = self.player_direction
                    rotation_time = time.time()

                time.sleep(0.05)
                try:
                    self.lookup_direction()
                except Exception:
                    self.clicker.keypress(win32con.VK_LEFT)
                    self.clicker.keypress(win32con.VK_RIGHT)
                    self.rotation_button_pressed = False
                    self.rotating_to = None
                    self.rotating = False
                    self.stop_rotate_event.clear()
                    self.rotation_stopped_event.set()
                    break

        with self.update_rotation_lock:
            self.rotating_to = None
            self.rotation_direction = direction
            if angle is None:
                asin = math.asin(direction[1])
                if asin == 0:
                    asin_coef = -1
                else:
                    asin_coef = asin / abs(asin)
                angle = (math.acos(direction[0]) * 180 / math.pi) * -asin_coef + 180 * (1 + asin_coef)
            self.rotation_angle = angle
            self.stop_rotate_event.clear()
            self.rotation_stopped_event.clear()

        if not self.rotating:
            self.rotating = True
            self.rotation_thread = Thread(target=rotate, daemon=True)
            self.rotation_thread.start()

        if sync:
            self.rotation_thread.join()

    def stop_rotation(self):
        if not self.rotation_stopped_event.is_set():
            self.stop_rotate_event.set()
            self.rotation_stopped_event.wait()

    def rotate_to_radar(self, point=None, image=None, threshold=.85, sync=True):
        if image is not None:
            coords = self.locate(image=image, threshold=threshold)
            if not coords:
                return False
            point = min(coords, key=lambda x: math.dist(x, self.center))

        point_distance = math.dist(self.center, point)
        point_direction = ((point[0] - self.center[0]) / point_distance,
                           (point[1] - self.center[1]) / point_distance)
        self.rotate_to_direction(direction=point_direction, sync=sync)

    def rotate_to_target(self, sync=True):
        self.rotate_to_direction(self.target_direction, angle=self.target_angle, sync=sync)

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

    def fly_through_vortex(self):
        if not self.approach(vortex_img, threshold=self.vortex_detection_precision,
                             # stop_action_image=fly_in_button,
                             stop_distance_diff=4,
                             distance=self.vortex_approach_distance):
            return False

        screen, offset = self.clicker.screen_lookup()
        fly_in_button_coord = self.clicker.find_image(fly_in_button, screen=screen, offset=offset, centers=True)
        if fly_in_button_coord is not None:
            self.log_message("Перелет через вихрь.")
            self.clicker.click(*fly_in_button_coord)
            return True
        else:
            self.log_error("Кнопка перелета через вихрь не была найдена!")
            vortex_coord = self.locate(vortex_img, threshold=self.vortex_detection_precision)
            vortex_coord = min(vortex_coord, key=lambda x: math.dist(x, self.center)) if vortex_coord else None
            if vortex_coord is not None:
                self.clicker.click(*vortex_coord)
                if self.press_esc_after_radar_action:
                    self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось
                return True
            else:
                self.log_error("Вихрь не был найден!")
                return False

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
                stop_at_destination = stop_at_destination if stop_at_destination is not None else True
                stop_if_enemy_in_front_of_ship = False
            if mode == 'Быстро лететь к цели':
                stop_at_destination = stop_at_destination if stop_at_destination is not None else True
                stop_if_enemy_in_front_of_ship = False
                speed_up = True
            if mode == 'Лететь к цели':
                stop_at_destination = stop_at_destination if stop_at_destination is not None else True
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
            self.rotate_to_target(sync=True)

        last_distance_to_target = self.target_distance
        last_distance_to_target_time = time.time()
        last_player_coord = self.radar_coords

        while self.target_distance > target_bias:
            if self.is_dead():
                self.stop_rotation()
                raise ValueError

            self.clicker.keypress(self.force_key if speed_up else self.forward_key)
            if loot:
                self.loot()
            time.sleep(0.05)
            self.calculate_target_angle()

            # Если залетели куда-то, то выходим, считая, что место назначения достигнуто
            if math.dist(last_player_coord, self.radar_coords) >= self.warp_bias:
                if target_bias == -1:
                    self.log_message('Прыжок в другой лабиринт.')
                    self.clicker.keypress(win32con.VK_DOWN)
                    self.stop_rotation()
                    return True
                else:
                    self.log_error('Прыжок в другой лабиринт (ошибка)!')
                    self.clicker.keypress(win32con.VK_DOWN)
                    self.stop_rotation()
                    return False

            last_player_coord = self.radar_coords

            # Корректируем направление движения
            self.rotate_to_target(sync=False)

            # Если мы не находимся за границей области, и враг напротив, то выходим
            if stop_if_enemy_in_front_of_ship and self.in_area():
                enemy_coords, screen, offset = self.locate_enemies()
                for enemy_coord in enemy_coords:
                    to_enemy_distance = math.dist(self.center, enemy_coord)
                    to_enemy_direction = (
                        (enemy_coord[0] - self.center[0]) / to_enemy_distance,
                        (enemy_coord[1] - self.center[1]) / to_enemy_distance
                    )
                    enemy_in_front_of_player = np.dot(self.player_direction, to_enemy_direction) > 0
                    if enemy_in_front_of_player and self.is_enemy_valid(enemy_coord, screen=screen, offset=offset):
                        self.stop_rotation()
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

        self.stop_rotation()

        return True

    def scale_in_radar(self):
        for i in range(7):
            self.clicker.keypress(self.radar_in_key)

        if self.scale_in_out_radar_delay > 0:
            time.sleep(self.scale_in_out_radar_delay)

        self.scaled_radar = True

    def scale_out_radar(self):
        for i in range(7):
            self.clicker.keypress(self.radar_out_key)

        if self.scale_in_out_radar_delay > 0:
            time.sleep(self.scale_in_out_radar_delay)

        self.scaled_radar = False

    def fly_to_base_trough_tunnel(self, tries=None):
        tries = tries if tries is not None else self.fly_trough_tunnel_tries_amount
        result = False

        self.close_all_windows()

        self.approach(tunnel_img, threshold=self.tunnel_detection_precision, distance=self.tunnel_approach_distance)

        self.scale_in_radar()

        for i in range(tries):
            screen, offset = self.clicker.screen_lookup(window=self.radar_window)
            tunnel_coord = self.clicker.find_image(tunnel_img, threshold=self.tunnel_detection_precision,
                                                   centers=True, screen=screen, offset=offset)

            if tunnel_coord is None:
                self.log_error('Тоннель не обнаружен!')
            else:
                self.clicker.move(*tunnel_coord)
                time.sleep(.1)
                self.clicker.dblclick(*tunnel_coord)
                time.sleep(.1)

                if self.press_esc_after_radar_action:
                    self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось

                tunnel_window_coord = self.clicker.wait_for_image(tunnel_window_title, timeout=2)
                if tunnel_window_coord is None:
                    self.log_error('Окно воздушных течений не было найдено!')
                else:
                    screen, offset = self.clicker.screen_lookup(
                        window=(*tunnel_window_coord, tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400))
                    base_option_coord = self.clicker.find_image(tunnel_window_base_title, screen=screen, offset=offset)
                    if base_option_coord is None:
                        self.log_error('База клана не найдена в списке воздушных течений!')
                    else:
                        result = True
                        self.clicker.move(*base_option_coord)
                        self.clicker.click(base_option_coord[0] + 1, base_option_coord[1] + 1)
                        self.log_message(f'Выбран переход "База клана".')
                        time.sleep(1)
                        break

            self.clicker.move(0, 0)
            if i != tries - 1:
                time.sleep(1)

        self.scale_out_radar()

        return result

    def fly_from_tunnel_to(self, destination_name, tries=None):
        tries = tries if tries is not None else self.fly_trough_tunnel_tries_amount
        result = False

        self.close_all_windows()

        self.approach(tunnel_img, threshold=self.tunnel_detection_precision, distance=self.tunnel_approach_distance)

        self.scale_in_radar()

        for i in range(tries):
            screen, offset = self.clicker.screen_lookup(window=self.radar_window)
            tunnel_coord = self.clicker.find_image(tunnel_img, threshold=self.tunnel_detection_precision,
                                                   centers=True, screen=screen, offset=offset)

            if tunnel_coord is None:
                self.log_error('Тоннель не обнаружен!')
            else:
                self.clicker.move(*tunnel_coord)
                time.sleep(.1)
                self.clicker.dblclick(*tunnel_coord)
                time.sleep(.1)

                if self.press_esc_after_radar_action:
                    self.clicker.keypress(win32con.VK_ESCAPE)  # Esc, чтобы убрать меню взаимодействия, если вывелось

                tunnel_window_coord = self.clicker.wait_for_image(tunnel_window_title, timeout=2)
                if tunnel_window_coord is None:
                    self.log_error('Окно воздушных течений не было найдено!')
                else:
                    window = (
                        tunnel_window_coord[0], tunnel_window_coord[1],
                        tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400
                    )
                    screen, offset = self.clicker.screen_lookup(window=window)

                    last_texts = ['']
                    texts = []

                    while not result and last_texts != texts:
                        last_texts = texts
                        texts = []
                        for bbox, text, accuracy in self.ocr_reader.readtext(screen):
                            texts.append(text)
                            if text == destination_name:
                                result = True
                                x, y = bbox[0]
                                x += window[0]
                                y += window[1]
                                self.clicker.move(x, y)
                                self.clicker.click(x + 1, y + 1)
                                self.log_message(f'Выбран переход "{destination_name}".')
                                break

                        # Скроллим дальше, если возможно
                        if not result and last_texts != texts:
                            self.clicker.scroll(delta=-1000, x=tunnel_window_coord[0] + 100, y=tunnel_window_coord[1] + 100)
                            time.sleep(.5)
                            screen, offset = self.clicker.screen_lookup(window=window)

                    if not result:
                        self.log_error(f'Переход "{destination_name}" не найден!')

            self.clicker.move(0, 0)
            if result:
                break
            if i != tries - 1:
                time.sleep(1)

        time.sleep(1)
        self.scale_out_radar()

        return result

    def fly_from_base_to(self, destination_name):
        result = False

        self.close_all_windows()

        self.clicker.click(-130, 100)
        tunnel_window_coord = self.clicker.wait_for_image(tunnel_window_title, timeout=2)
        if tunnel_window_coord is None:
            self.log_error('Окно воздушных течений не было найдено!')
        else:
            # [[b0, b1, b2, b3], str, float] window = (*b0, *b2)
            window = (
                tunnel_window_coord[0], tunnel_window_coord[1],
                tunnel_window_coord[0] + 300, tunnel_window_coord[1] + 400
            )
            screen, offset = self.clicker.screen_lookup(window=window)

            last_texts = ['']
            texts = []

            while not result and last_texts != texts:
                last_texts = texts
                texts = []
                for bbox, text, accuracy in self.ocr_reader.readtext(screen):
                    texts.append(text)
                    print(text)
                    if text == destination_name:
                        result = True
                        x, y = bbox[0]
                        x += window[0]
                        y += window[1]
                        self.clicker.move(x, y)
                        self.clicker.click(x + 1, y + 1)
                        self.log_message(f'Выбран переход "{destination_name}".')
                        break

                # Скроллим дальше, если возможно
                if not result and last_texts != texts:
                    self.clicker.scroll(delta=-1000, x=tunnel_window_coord[0] + 100, y=tunnel_window_coord[1] + 100)
                    time.sleep(.5)
                    screen, offset = self.clicker.screen_lookup(window=window)

            if not result:
                self.log_error(f'Переход "{destination_name}" не найден!')

        return result

    def fly_route(self, route: list[((int, int), str)]):
        def act(action, attribute, stop_at_route_point=False):
            if action == 'Вылет':
                return self.undock(available_directions_to_undock=attribute)
            elif action == 'Перелететь':
                return self.fly_from_base_to(destination_name=attribute)
            elif action == 'В туннель':
                return self.fly_from_tunnel_to(destination_name=attribute)
            elif action == 'В тоннель':
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
            elif action == 'Выбрать опцию диалога':
                return self.select_dialog_option(*attribute if type(attribute) in [tuple, list] else [attribute])
            elif action == 'Пролететь через вихрь':
                return self.fly_through_vortex()
            elif type(action) in [tuple, list]:
                return self.fly_to(*action, mode=attribute, stop_at_destination=stop_at_route_point)

        def delay(action):
            if action == 'Вылет':
                return time.sleep(5)
            elif action == 'Перелететь':
                return time.sleep(3)
            elif action == 'В туннель':
                return time.sleep(15)
            elif action == 'В тоннель':
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
            elif action == 'Выбрать опцию диалога':
                return time.sleep(1)
            elif action == 'Пролететь через вихрь':
                return time.sleep(5)
            elif type(action) in [tuple, list]:
                return time.sleep(1)

        for index, route_point in enumerate(route):
            if self.is_dead():
                raise ValueError

            action, attribute = route_point
            stop_at_route_point = type(route[index + 1]) not in [tuple, list] if index + 1 < len(route) else True
            while not act(action, attribute, stop_at_route_point=stop_at_route_point):
                delay(action)
                backup_action, backup_attribute = route[index - 1]
                act(backup_action, backup_attribute, stop_at_route_point=type(action) not in [tuple, list])

            delay(action)

    def load_preset(self, file_path):
        with open(file_path, 'r', encoding='utf8') as f:
            data = json.loads(f.read())
            for attribute, value in data.items():
                if attribute.lower() in self.attribute_cross_naming_ru_en:
                    setattr(self, self.attribute_cross_naming_ru_en[attribute.lower()], value)
                elif attribute.lower() in self.attribute_cross_naming_en_ru:
                    setattr(self, attribute.lower(), value)
                else:
                    self.log_error(f"Внимание! Параметр \"{attribute}\" не поддерживается!")

    def find_text(self, text, window=None):
        screen, offset = self.clicker.screen_lookup(window=window)
        for bbox, ocr_text, accuracy in self.ocr_reader.readtext(screen):
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
            screen, offset = self.clicker.screen_lookup(window=(0, 0, -1, 200))
            dead_title_coord = self.clicker.find_image(dead_title, screen=screen, offset=offset)
            if dead_title_coord is not None:
                self.log_error(f'Корабль подбит!')
                screen, offset = self.clicker.screen_lookup(
                    window=(*dead_title_coord, dead_title_coord[0] + 200, dead_title_coord[1] + 200))
                pay_button_coord = self.clicker.find_image(pay_button, screen=screen, offset=offset)
                if pay_button_coord is not None:
                    self.clicker.click(*pay_button_coord)
                    time.sleep(1)
                self.clicker.click(dead_title_coord[0] + 20, dead_title_coord[1] + 65)
                if do_wait:
                    time.sleep(random.randint(*self.after_death_wait_time_range))
                return True
        return False

    def open_ship(self):
        screen, offset = self.clicker.screen_lookup()
        ship_tab_coord = self.clicker.find_image(ship_tab, screen=screen, offset=offset)
        if ship_tab_coord is not None:
            self.clicker.click(*ship_tab_coord)
        else:
            self.clicker.keypress(self.inventory_key)
            ship_tab_coord = self.clicker.wait_for_image(ship_tab, timeout=self.action_timeout)
            wait_result = False
            if ship_tab_coord is not None:
                self.clicker.click(*ship_tab_coord)
                wait_result = self.clicker.wait_for_image(equipment_tab, timeout=self.action_timeout)

            if not wait_result:
                self.log_error("Окно корабля не открылось!")
                return False

        return True

    def open_cargo(self):
        if not self.open_ship():
            return False

        cargo_tab_coord = self.clicker.wait_for_image(cargo_tab, timeout=self.action_timeout)
        if cargo_tab_coord is not None:
            self.clicker.click(*cargo_tab_coord)
            return True
        else:
            self.log_error("Вкладка трюма не была найдена!")
            return False

    def open_equipment(self):
        if not self.open_ship():
            return False

        equipment_tab_coord = self.clicker.wait_for_image(equipment_tab, timeout=self.action_timeout)
        if equipment_tab_coord is not None:
            self.clicker.click(*equipment_tab_coord)
            if self.clicker.wait_for_image(crew_title, timeout=self.action_timeout):
                self.log_message("Открыта вкладка снаряжения.")
                return True
            else:
                self.log_error("Вкладка снаряжения не была открыта!")
                return False
        else:
            self.log_error("Вкладка снаряжения не была найдена!")
            return False

    def drop_chests(self):
        self.open_cargo()
        screen, offset = self.clicker.screen_lookup()
        for chest_type in [chest_icon, black_chest_icon]:
            chest_coord = self.clicker.find_image(chest_type, screen=screen, offset=offset)
            while chest_coord is not None:
                self.clicker.ldown(*chest_coord)
                time.sleep(.5)
                self.clicker.move(10, 10)
                time.sleep(.5)
                self.clicker.lup(10, 10)
                drop_button_coord = self.clicker.wait_for_image(drop_button, timeout=6)
                if drop_button_coord is not None:
                    self.clicker.click(*drop_button_coord)
                self.log_message("Выброшен сундук.")
                time.sleep(1)
                screen, offset = self.clicker.screen_lookup()
                chest_coord = self.clicker.find_image(chest_type, screen=screen, offset=offset)

    def locate(self, image, threshold=.85, min_dist=10):
        screen, offset = self.clicker.screen_lookup(window=self.radar_window)
        coords = self.clicker.find_images(image, threshold=threshold, centers=True, min_dist=min_dist, screen=screen, offset=offset)
        return coords

    def get_speed_arm_value(self):
        arm_window = (-204, -137, -199, -109)
        screen, offset = self.clicker.screen_lookup(arm_window)
        self.clicker.fill(window=(-200, -137, -199, -133), color=(0, 0, 0), screen=screen, offset=offset)

        coord = self.clicker.find_pixel(color=(227, 227, 227), threshold=0.9, screen=screen, offset=offset)
        value = None
        if coord is not None:
            # self.clicker.fill(window=(*coord, *coord), color=(255, 0, 0))
            left, top, right, bottom = self.clicker._resolve_window(arm_window)
            zero_x, zero_y = self.clicker._resolve_coord(-199, -115)
            coord_x, coord_y = coord
            value = 0
            if coord_y < zero_y:
                value = (coord_y - zero_y) / (top - zero_y)
            elif coord_y > zero_y:
                value = -((coord_y - zero_y) / (bottom - zero_y))

        return value

    def set_speed_arm_value(self, value):
        arm_window = (-204, -137, -199, -109)
        screen, offset = self.clicker.screen_lookup(arm_window)
        self.clicker.fill(window=(-200, -137, -199, -133), color=(0, 0, 0), screen=screen, offset=offset)

        coord = self.clicker.find_pixel(color=(227, 227, 227), threshold=0.9, screen=screen, offset=offset)
        if coord is not None:

            left, top, right, bottom = self.clicker._resolve_window(arm_window)
            zero_x, zero_y = self.clicker._resolve_coord(-199, -115)

            coord_x, coord_y = coord
            current_value = 0
            initial_handle_offset = 17 + 3
            if coord_y < zero_y:
                current_value = (coord_y - zero_y) / (top - zero_y)
                initial_handle_offset = 17 + int((27 - 17) * current_value) + 3
            elif coord_y > zero_y:
                current_value = -((coord_y - zero_y) / (bottom - zero_y))
                initial_handle_offset = 17 + int((14 - 17) * abs(current_value)) + 3

            target_y = zero_y
            target_handle_offset = 17 + 3
            value = min(max(-1, value), 1)
            if value < 0:
                target_y = zero_y + int((bottom - zero_y) * abs(value))
                target_handle_offset = 17 + int((14 - 17) * abs(value)) + 3
            elif value > 0:
                target_y = zero_y + int((top - zero_y) * value)
                target_handle_offset = 17 + int((27 - 17) * value) + 3

            # print(current_value, value)
            # print(coord[1], target_y)
            # print(coord[1] - initial_handle_offset, target_y - target_handle_offset)
            from_y = coord[1] - initial_handle_offset
            to_y = target_y - target_handle_offset
            if abs(from_y - to_y) > 3:
                self.clicker.ldown(coord[0], from_y)
                time.sleep(.5)
                self.clicker.move(coord[0], to_y)
                time.sleep(.5)
                self.clicker.lup(coord[0], to_y)
            return True
        else:
            return False

    def set_low_speed(self):
        return self.set_speed_arm_value(0.28)

    def approach(self, image, threshold=.85, distance=0,
                 stop_action_image=None, very_slow=False, correct_rotation=True, stop_distance_diff=2):
        coords = self.locate(image=image, threshold=threshold)
        if not coords:
            self.log_error('Объект не найден!')
            return False

        closest_coord = min(coords, key=lambda x: math.dist(x, self.center))

        last_closest_distance = math.dist(closest_coord, self.center)
        if stop_action_image is not None:
            stop_action_present = self.find_action(stop_action_image)
        else:
            stop_action_present = False

        if last_closest_distance <= distance or stop_action_present:
            self.log_message('Уже на месте.')
            return True

        self.rotate_to_radar(closest_coord, sync=True)

        if very_slow:
            self.set_low_speed()
        else:
            self.clicker.keypress(self.forward_key)

        while last_closest_distance > distance and not stop_action_present:
            # Обработка смерти
            if self.is_dead():
                raise ValueError

            time.sleep(.1)
            coords = self.locate(image=image, threshold=threshold)
            if not coords:
                self.stop_rotation()
                break

            closest_coord = min(coords, key=lambda x: math.dist(x, self.center))
            closest_distance = math.dist(closest_coord, self.center)
            if closest_distance > last_closest_distance + stop_distance_diff:
                self.stop_rotation()
                break

            if correct_rotation:
                self.rotate_to_radar(closest_coord, sync=False)
            last_closest_distance = closest_distance

            if stop_action_image is not None:
                stop_action_present = self.find_action(stop_action_image)

        self.clicker.keypress(win32con.VK_DOWN)
        self.stop_rotation()

        # self.scale_in_radar()
        # dandelions = self.locate_dandelions()
        # if not dandelions:
        #     self.scale_out_radar()
        #     return False
        # closest_dandelion = min(dandelions, key=lambda x: math.dist(x, self.center))
        # self.rotate_to_radar(closest_dandelion)
        # time.sleep(.5)
        #
        # self.scale_out_radar()
        return True

    def locate_dandelions(self, return_dandelion_image=False):
        screen, offset = self.clicker.screen_lookup(window=self.radar_window)
        dandelions = []
        for dandelion_type in [pink_dandelion, green_dandelion, orange_dandelion]:
            dandelions_of_type = self.clicker.find_images(dandelion_type, min_dist=10,
                                                          threshold=self.dandelion_detection_precision,
                                                          centers=True, screen=screen, offset=offset)
            if return_dandelion_image:
                dandelions.extend(list(zip(dandelions_of_type, [dandelion_type] * len(dandelions_of_type))))
            else:
                dandelions.extend(dandelions_of_type)

        # for i, dandelion in enumerate(dandelions):
        #     dandelions[i] = (dandelion[0] + 6, dandelion[1] + 6)

        # for dandelion in dandelions:
        #     self.clicker.fill(window=(*dandelion, *dandelion), color=(0, 255, 0), screen=screen, offset=offset)

        # cv2.imwrite('screen.png', screen)

        return dandelions

    def move_to_dandelion(self):
        dandelions = self.locate_dandelions(return_dandelion_image=True)
        if not dandelions:
            self.lookup_coords()
            radar_coord = str(self.radar_coords).replace(', ', ':')
            self.log_error(f"Одуванчиков не найдено {radar_coord}!")
            return False

        # closest_dandelion_coord = min(dandelions_coord, key=lambda x: math.dist(x, self.center))
        # self.rotate_to_radar(closest_dandelion_coord, sync=True)
        # self.clicker.keypress(self.forward_key)
        #
        # last_closest_distance = math.dist(closest_dandelion_coord, self.center)
        # while last_closest_distance > 10:
        #     # Обработка смерти
        #     if self.is_dead():
        #         raise ValueError
        #
        #     dandelions_coord = self.locate_dandelions()
        #     if not dandelions_coord:
        #         break
        #     closest_dandelion_coord = min(dandelions_coord, key=lambda x: math.dist(x, self.center))
        #     closest_dandelion_distance = math.dist(closest_dandelion_coord, self.center)
        #     if closest_dandelion_distance > last_closest_distance + 2:
        #         break
        #     last_closest_distance = closest_dandelion_distance
        #     time.sleep(.1)
        #
        # self.clicker.keypress(win32con.VK_DOWN)

        dandelion_image = min(dandelions, key=lambda x: math.dist(x[0], self.center))[1]
        self.approach(image=dandelion_image, distance=self.dandelion_approach_distance,
                      threshold=self.dandelion_detection_precision)

        # Корректировка направления к одуванчику
        self.scale_in_radar()
        dandelions_coord = self.locate_dandelions()
        if not dandelions_coord:
            self.scale_out_radar()
            self.lookup_coords()
            radar_coord = str(self.radar_coords).replace(', ', ':')
            self.log_error(f"Потерян одуванчик после подлёта к нему {radar_coord}!")
            return False
        closest_dandelion_coord = min(dandelions_coord, key=lambda x: math.dist(x, self.center))
        self.rotate_to_radar(closest_dandelion_coord, sync=True)
        time.sleep(.5)

        self.scale_out_radar()
        return True

    def loot_dandelion(self):
        click_coord = (int(self.clicker.screen_width / 2), int(self.clicker.screen_height / 2) - 30)
        for i in range(10):
            if self.fly_to_object_key.lower() == 'клик правой кнопкой мыши':
                self.clicker.clickr(*click_coord)
            elif self.fly_to_object_key.lower() == 'клик левой кнопкой мыши':
                self.clicker.click(*click_coord)
            else:
                self.clicker.click(*click_coord)
            time.sleep(.1)

        self.clicker.keypress(self.force_right_key)
        time.sleep(.5)
        self.clicker.keypress(self.force_forward_key)
        time.sleep(1)
        self.clicker.keypress(self.force_forward_key)

        for i in range(3):
            self.loot()
            time.sleep(.3)

    def start_dialog(self):
        screen, offset = self.clicker.screen_lookup(window=self.action_window)
        dialog_button_coord = self.clicker.find_image(dialog_button, centers=True, screen=screen, offset=offset)
        if dialog_button_coord is not None:
            self.clicker.click(*dialog_button_coord)
            self.log_message("Начат диалог.")
            return True
        else:
            self.log_error("Кнопка начала диалога не была найдена!")
            return False

    def select_dialog_option(self, option, index=1):
        index = index - 1
        option_image = {
            'стандарт': dialog_option,
            'закрыть': close_dialog_option,
            'квест': quest_dialog_option,
            'сдать': complete_dialog_option,
            'вопрос': question_dialog_option
        }.get(option.lower(), None)

        if option_image is None:
            return False
        else:
            screen, offset = self.clicker.screen_lookup()
            options = self.clicker.find_images(option_image, min_dist=5, centers=True, screen=screen, offset=offset)
            if index < len(options):
                selected_option = options[index]
                self.clicker.click(*selected_option)
                self.log_message(f"Выбрана опция диалога \"{option.capitalize()} {index + 1}\".")
                return True
            else:
                self.log_error(f"Опция диалога \"{option.capitalize()} {index + 1}\" недоступна для выбора!")
                return False

    def send_message_to_chat(self, message, key_delay=.1):
        self.clicker.keypress(self.enter_key)
        time.sleep(.5)
        self.clicker.send_chars(message, key_delay=key_delay)
        self.clicker.keypress(self.enter_key)
        self.log_message(f"Отправлено сообщение в чат \"{message}\".")

    def invite_to_party(self, name):
        self.send_message_to_chat(f'/invite {name}')
        invite_button_coord = self.clicker.wait_for_image(invite_button, centers=True, timeout=self.action_timeout)
        if invite_button_coord is not None:
            self.clicker.click(*invite_button_coord)
            self.log_message(f"Отправлено приглашение в группу игроку {name}.")
            return True
        else:
            self.log_error(f"Не удалось отправить приглашение в группу игроку {name}!")
            return False

    def wait_for_party_request(self):
        screen, offset = self.clicker.screen_lookup(window=self.action_window)
        party_request_coord = self.clicker.find_image(party_request, screen=screen, offset=offset)
        while party_request_coord is None:
            if self.is_dead():
                raise ValueError
            time.sleep(1)
            screen, offset = self.clicker.screen_lookup(window=self.action_window)
            party_request_coord = self.clicker.find_image(party_request, screen=screen, offset=offset)
        self.log_message("Получено приглашение в группу.")
        return True

    def accept_party_request(self):
        screen, offset = self.clicker.screen_lookup(window=self.action_window)
        party_request_coord = self.clicker.find_image(party_request, centers=True, screen=screen, offset=offset)
        if party_request_coord is not None:
            self.clicker.click(*party_request_coord)
            accept_coord = self.clicker.wait_for_image(accept_button, centers=True, timeout=self.action_timeout)
            if accept_coord is not None:
                self.clicker.click(*accept_coord)
                self.log_message("Принято приглашение в группу.")
                return True
            else:
                self.log_error("Кнопка принятия приглашения в группу не была найдена!")
                return False
        else:
            self.log_error("Кнопка приглашения в группу не была найдена!")
            return False

    def suicide(self):
        self.send_message_to_chat('/die')
        to_city_coord = self.clicker.wait_for_image(to_city_button, centers=True, timeout=self.action_timeout)
        if to_city_coord is not None:
            self.clicker.click(*to_city_coord)
            time.sleep(21)
            if self.is_dead(do_wait=False):
                self.log_message("Совершен суицид.")
                return True
            else:
                self.log_error("Не удалось совершить суицид!")
                return False
        else:
            self.log_error("Не найдена кнопка \"В город\" (суицид)!")
            return False

    def start_new_game(self):
        pass

    def farm(self, mode=None):
        self.farm_start_time = time.time()
        return {
            "Убийство мобов в зоне": self.fly_in_zone_and_kill_mobs,
            "Рыбалка": self.fishing,
            "Одуванчики": self.dandelion_cycle,
            "Дерево": self.woodcutting,
        }[self.mode if mode is None else mode]()

    def in_city_actions(self, mode=None):
        action_list = {
            "Убийство мобов в зоне": (self.store_resources_and_service, self.reload_gasholders),
            "Рыбалка": (self.store_resources_and_service, self.reload_gasholders),
            "Одуванчики": (self.store_resources_and_service, self.reload_gasholders),
            "Дерево": (self.store_resources_and_service, self.reload_gasholders, self.saw_prep_in_dock),
        }[self.mode if mode is None else mode]

        self.close_all_windows()
        time.sleep(1)
        for action in action_list:
            action()
            self.close_all_windows()
            time.sleep(1)

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
                time.sleep(self.delay_between_farm_attempts)

    def fishing(self):
        bad_fishing_tries = 0
        max_bad_fishing_tries = self.fishing_spot_max_bad_fishing_tries
        catching_window_coord = (0, 0, -1, -1)
        fishing_in_progress = False
        last_continue_click_coord = None

        fishing_image = {
            True: fishing_spot,
            False: fishing_spot_eels
        }[len(self.locate(image=fishing_spot, threshold=self.fishing_spot_detection_precision)) > 0]
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

                screen, offset = self.clicker.screen_lookup()
                # cv2.imwrite('screen.png', self.clicker.screen)
                continue_coord = self.clicker.find_image(continue_img, window=catching_window_coord, screen=screen, offset=offset)
                if continue_coord:
                    bad_fishing_tries = 0
                    full_net_coord = self.clicker.find_image(full_net_img, window=catching_window_coord, screen=screen, offset=offset)
                    if full_net_coord or not is_farm_not_ended:
                        # self.log_message('Сеть заполнилась.')
                        pickup_coord = self.clicker.find_image(pickup_img, centers=True, window=catching_window_coord,
                                                               screen=screen, offset=offset)
                        if pickup_coord:
                            self.log_message('Поднять сеть.')
                            fishing_in_progress = False
                            self.clicker.click(*pickup_coord)
                            time.sleep(3)
                            continue
                    else:
                        self.log_message('Продолжить ловить.')
                        fishing_in_progress = True
                        continue_click_coord = (
                            continue_coord[0] + random.randint(1, 5),
                            continue_coord[1] + random.randint(1, 5)
                        )
                        while continue_click_coord == last_continue_click_coord:
                            continue_click_coord = (
                                continue_coord[0] + random.randint(1, 5),
                                continue_coord[1] + random.randint(1, 5)
                            )

                        self.clicker.click(*continue_click_coord)
                        last_continue_click_coord = continue_click_coord
                else:
                    catching_coord = self.clicker.find_image(catching_img, catching_window_coord, screen=screen, offset=offset)
                    # Возможно было перемещено пользователем
                    if catching_coord is None:
                        catching_coord = self.clicker.find_image(catching_img, screen=screen, offset=offset)

                    if catching_coord:
                        # self.log_message('Ловля в прогрессе.')
                        # bad_fishing_tries = 0
                        catching_window_coord = (
                        catching_coord[0] - 10, catching_coord[1], catching_coord[0] + 400, catching_coord[1] + 600)
                    else:
                        start_catch_coord = self.find_action(start_catch_img, screen=screen, offset=offset)
                        if start_catch_coord:
                            self.log_message('Начало рыбалки.')
                            fishing_in_progress = True
                            # bad_fishing_tries = 0
                            self.clicker.click(*start_catch_coord)
                        else:
                            self.log_error('Кнопка начала рыбалки не была найдена!')
                            bad_fishing_tries += 1
                            fishing_in_progress = False
                            if bad_fishing_tries > max_bad_fishing_tries:
                                # beep(sync=True)
                                break

                            if self.approach(fishing_image,
                                             distance=self.fishing_spot_approach_distance if not self.positioning_to_the_center else 0,
                                             threshold=self.fishing_spot_detection_precision,
                                             stop_action_image=start_catch_img if not self.positioning_to_the_center else None):
                                time.sleep(3)
                                continue

                time.sleep(self.delay_between_farm_attempts)
            except win32ui.error:
                self.log_error(
                      f'Случилась внутренняя ошибка windows при определении окна, '
                      f'будет произведена повторная попытка получить окно {self.clicker.hwnd}.')
                continue
            except ValueError:
                self.log_error(f"Разверните окно {self.clicker.hwnd}!")
                beep(sync=True)

    def dandelion_cycle(self):
        dandelions_global_coord = [
            [53, 32],
            [52, 28],
            [56, 25],
            [62, 25],
            [60, 28],
            [59, 31],
            [62, 34],
            [65, 33],
            [62, 38],
            [66, 39],
            [63, 41],
            [62, 42],
            [66, 45],
            [63, 47],
            [61, 45],
            [58, 44],
            [57, 48],
            [57, 48],
            [60, 50],
            [55, 50],
            [52, 48],
            [53, 42],
            [51, 39],
            [48, 38],
            [49, 32],
            [52, 36],
        ]

        farming = self.is_farming()
        while farming:
            for dandelion_coord in self.target_coords_range:
                self.fly_to(*dandelion_coord, stop_at_destination=self.stop_at_destination, target_bias=self.target_bias,
                            stop_if_enemy_in_front_of_ship=self.stop_if_enemy_in_front_of_ship)
                time.sleep(1)
                if self.move_to_dandelion():
                    time.sleep(.5)
                    self.loot_dandelion()

                # Заканчиваем цикл, если после сбора пушинки фарм окончен
                farming = self.is_farming()
                if not farming:
                    break

                time.sleep(self.delay_between_farm_attempts)

            # except win32ui.error:
            #     print(datetime.datetime.now(),
            #           f'Случилась внутренняя ошибка windows при определении окна, '
            #           f'будет произведена повторная попытка получить окно {self.clicker.hwnd}.')
            #     continue
            # except ValueError:
            #     self.log_error(f"Разверните окно {self.clicker.hwnd}!")
            #     beep(sync=True)

    def woodcutting(self):
        bad_cutting_tries = 0

        tree_spot_image = {
            False: tree_image_base,
            True: tree_image_orange,
        }[len(self.locate(image=tree_image_orange, threshold=self.tree_spot_detection_precision)) > 0]
        broken_saw_image = broken_saw_big_image
        not_broken_saw_image = not_broken_saw_big_image

        self.log_message("Поиск дровосека среди техустройств...")
        tech_saw_found = self.clicker.wait_for_image(tech_slot_saw, window=self.tech_window, threshold=self.tech_detection_precision, timeout=30)
        if not tech_saw_found:
            self.log_error("Не удалось найти дровосека среди техустройств!")
            return False

        tech_saw_slot_number = self.get_tech_slot_number(tech_slot_saw)
        self.log_message(f"Найден дровосек среди техустройств: {tech_saw_slot_number}.")

        # if self.approach(tree_spot_image, distance=self.fishing_spot_approach_distance, threshold=self.fishing_spot_detection_precision):
        #     time.sleep(3)

        # Если при запуске мы уже на дереве
        start_cutting_button = self.find_action(launch_saw_active_image)
        if start_cutting_button:
            if self.do_looting:
                self.scale_in_radar()
            self.clicker.keypress(self.auto_use_all_key)
            self.start_spam_attack()

        # self.last_looting_time = time.time()

        while True:
            # Обработка смерти
            if self.is_dead():
                self.stop_spam_attack()

                if self.do_looting:
                    self.scale_out_radar()

                raise ValueError

            try:
                if not self.is_farming():
                    self.stop_spam_attack()

                    if self.do_looting:
                        self.scale_out_radar()

                    break

                start_cutting_button = self.find_action(launch_saw_active_image)
                if start_cutting_button:
                    bad_cutting_tries = 0

                    self.target_and_kill()

                    time.sleep(.01)
                    if self.do_looting:
                        self.loot()
                    # else:
                    #     if len(self.locate_loot()) > 0:
                    #         self.last_looting_time = time.time()

                    # if time.time() - self.last_looting_time > self.change_saw_after_no_looting_time:
                    if not self.get_auto_use(tech_saw_slot_number):
                        self.log_error("Не включено автоиспользование дровосека!")
                        self.stop_spam_attack()
                        if not self.change_saw():
                            self.log_error("Дровосеки закончились!")
                            if self.do_looting:
                                self.scale_out_radar()
                            break
                        self.start_spam_attack()
                        # self.last_looting_time = time.time() + 30
                else:
                    self.log_error('Кнопка запуска дровосека не была найдена!')

                    self.stop_spam_attack()

                    if self.do_looting:
                        self.scale_out_radar()

                    bad_cutting_tries += 1
                    if bad_cutting_tries > self.tree_spot_max_bad_cutting_tries:
                        # beep(sync=True)
                        break

                    # Подлететь к дереву
                    self.approach(tree_spot_image, distance=self.tree_spot_approach_distance,
                                  threshold=self.tree_spot_detection_precision,
                                  stop_action_image=launch_saw_active_image,
                                  very_slow=True if not self.positioning_to_the_center else False)

                    # После приближения по идее надо пару секунд подождать, чтобы кнопка остановилась
                    on_tree_start_time = time.time()

                    self.scale_in_radar()
                    if self.positioning_to_the_center:
                        # Подлететь к дереву
                        self.approach(tree_spot_image,
                                      distance=self.tree_spot_approach_distance if not self.positioning_to_the_center else 0,
                                      threshold=self.tree_spot_detection_precision,
                                      stop_action_image=launch_saw_active_image if not self.positioning_to_the_center else None,
                                      very_slow=True)
                    else:
                        # Повернуться к центру дерева
                        self.rotate_to_radar(image=tree_spot_image, threshold=self.tree_spot_detection_precision)
                    if not self.do_looting:
                        self.scale_out_radar()

                    self.clicker.keypress(self.auto_use_all_key)

                    self.start_spam_attack()
                    # self.last_looting_time = time.time()

                    # После приближения по идее надо пару секунд подождать, чтобы кнопка остановилась
                    actions_time = time.time() - on_tree_start_time
                    if actions_time < 3:
                        time.sleep(3 - actions_time)

                time.sleep(self.delay_between_farm_attempts)
            except win32ui.error:
                self.log_error(
                      f'Случилась внутренняя ошибка windows при определении окна, '
                      f'будет произведена повторная попытка получить окно {self.clicker.hwnd}.')
                continue
            except ValueError:
                self.log_error(f"Разверните окно {self.clicker.hwnd}!")
                beep(sync=True)

    def find_tech(self, tech_image, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup(self.tech_window)
        return self.clicker.find_image(tech_image, window=self.tech_window, centers=True,
                                       threshold=self.tech_detection_precision,
                                       screen=screen, offset=offset)

    def get_tech_slot_number(self, tech_image, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup(self.tech_window)
        tech_coord = self.clicker.find_image(tech_image, window=self.tech_window, centers=True,
                                             threshold=self.tech_detection_precision,
                                             screen=screen, offset=offset)
        if tech_coord is None:
            return None

        tech_coord_local = (tech_coord[0] - offset[0], tech_coord[1] - offset[1])
        return int(tech_coord_local[0] // 47 + (tech_coord_local[1] // 49) * 7)

    def get_auto_use(self, slot, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup(self.tech_window)

        xi = slot % 7
        yi = slot // 7
        for xo, yo in [(2, 1), (-1, 2)]:
            auto_use_tech_offset = (1360 + xo - 1920, 1018 + yo - 1080)
            dx = 47
            dy = 49
            pixel = self.clicker.pixel(
                auto_use_tech_offset[0] + xi * dx,
                auto_use_tech_offset[1] + yi * dy,
                screen=screen, offset=offset
            )
            if all(pixel == (255, 255, 255)) or all(pixel == (119, 123, 109)):
                return True

        return False

    def check_auto_use(self, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup(self.tech_window)

        auto = []

        for xo, yo in [(2, 1), (-1, 2)]:
            auto_use_tech_offset = (1360 + xo - 1920, 1018 + yo - 1080)
            dx = 47
            dy = 49
            for yi in range(2):
                for xi in range(7):
                    if xi + yi * 7 in auto:
                        continue

                    pixel = self.clicker.pixel(
                        auto_use_tech_offset[0] + xi * dx,
                        auto_use_tech_offset[1] + yi * dy,
                        screen=screen, offset=offset
                    )
                    if all(pixel == (255, 255, 255)) or all(pixel == (119, 123, 109)):
                        auto.append(xi + yi * 7)
                        # print("auto", xi, yi)

                        self.clicker.fill((auto_use_tech_offset[0] + xi * dx, auto_use_tech_offset[1] + yi * dy, auto_use_tech_offset[0] + xi * dx, auto_use_tech_offset[1] + yi * dy),
                                          (255, 0, 0), screen=screen, offset=offset)

        return auto

    def find_action(self, action_image, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup(self.action_window)
        return self.clicker.find_image(action_image, window=self.action_window, centers=True,
                                       threshold=self.action_detection_precision,
                                       screen=screen, offset=offset)

    def find_equipped_slot(self, equipment_image, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup()

        tech_title_coord = self.clicker.find_image(tech_title, screen=screen, offset=offset)
        if tech_title_coord is None:
            return None

        items_from_storage_title_coord = self.clicker.find_image(
            items_from_storage_title, screen=screen, offset=offset,
            window=(tech_title_coord[0] - 10, tech_title_coord[1] - 10, -1, -1))
        if items_from_storage_title_coord is None:
            return None

        return self.clicker.find_image(
            equipment_image, screen=screen, offset=offset, centers=True,
            window=(tech_title_coord[0] - 10, tech_title_coord[1] - 10, -1, items_from_storage_title_coord[1]))

    def find_slot_in_items(self, slot_image, screen=None, offset=None):
        if screen is None or offset is None:
            screen, offset = self.clicker.screen_lookup()

        items_from_storage_title_coord = self.clicker.find_image(items_from_storage_title, screen=screen, offset=offset)
        if items_from_storage_title_coord is None:
            return None

        return self.clicker.find_image(
            slot_image, screen=screen, offset=offset, centers=True,
            window=(items_from_storage_title_coord[0] - 10, items_from_storage_title_coord[1] - 10, -1, -1))

    def change_saw(self):
        self.log_message("Замена дровосека.")

        self.close_all_windows()
        self.open_equipment()

        screen, offset = self.clicker.screen_lookup()
        broken_saw_coord = self.find_equipped_slot(broken_saw_big_image, screen=screen, offset=offset)
        if broken_saw_coord is not None:
            not_broken_saw_coord = self.find_slot_in_items(not_broken_saw_big_image, screen=screen, offset=offset)
            if not_broken_saw_coord is not None:
                self.clicker.drag_and_drop(*not_broken_saw_coord, *broken_saw_coord)
                self.log_message("Дровосек заменен.")
                time.sleep(1)
                self.clicker.keypress(self.auto_use_all_key)
                # time.sleep(30)
            else:
                self.log_error("Дровосек для замены не был найден!")
                self.close_all_windows()
                return False
        else:
            not_broken_saw_coord = self.find_equipped_slot(not_broken_saw_big_image, screen=screen, offset=offset)
            if not_broken_saw_coord is None:
                self.log_error("Дровосек не экипирован, чтобы его можно было заменить!")
                self.close_all_windows()
                return False
            else:
                self.log_message("Замена дровосека не требуется.")

            self.clicker.keypress(self.auto_use_all_key)

        self.close_all_windows()
        return True

    def close_all_windows(self):
        for i in range(5):
            self.clicker.keypress(self.esc_key)

    def buy_in_shop(self, image_list, amount=1, wait_shop=True):
        if wait_shop:
            shop_coord = self.clicker.wait_for_image(shop_button, window=self.city_services_window,
                                                     centers=True, timeout=self.action_timeout)
        else:
            screen, offset = self.clicker.screen_lookup(window=self.city_services_window)
            shop_coord = self.clicker.find_image(shop_button, centers=True, screen=screen, offset=offset)
        if shop_coord is not None:
            self.clicker.click(*shop_coord)
        else:
            self.log_error("Кнопка магазина не была найдена!")
            return False

        shop_item_coord = None
        for image in image_list:
            shop_item_coord = self.clicker.wait_for_image(image, centers=True, timeout=self.action_timeout)
            if shop_item_coord is not None:
                self.clicker.click(*shop_item_coord)
            else:
                self.log_error("Не найден пункт в магазине!")
                self.exit()
                return False

        for i in range(amount):
            buy_for_coord = self.clicker.wait_for_image(buy_for_button, centers=True, timeout=self.action_timeout)
            if buy_for_coord is not None:
                self.clicker.click(*buy_for_coord)
                self.log_message("Куплен предмет в магазине.")
                time.sleep(1)
            else:
                self.log_error("Не найдена кнопка \"Купить за\" предмета в магазине!")
                self.exit()
                return False

            if i < amount - 1:
                self.clicker.click(*shop_item_coord)

        self.exit()
        return True

    def saw_prep_in_dock(self):
        self.open_equipment()

        screen, offset = self.clicker.screen_lookup()

        # Проверяем, экипированна ли дровосек в целом
        broken_saw_coord = self.find_equipped_slot(broken_saw_big_image, screen=screen, offset=offset)
        not_broken_saw_coord = self.find_equipped_slot(not_broken_saw_big_image, screen=screen, offset=offset)
        if broken_saw_coord is None and not_broken_saw_coord is None:
            self.log_error("Дровосек не экипирован, фарм будет завершен!")
            self.repeat_cycle_forever = False
            self.close_all_windows()
            return False

        # Если дровосек уже экипирован, то пропускаем экипировку
        saw_equipped_successful = bool(not_broken_saw_coord)

        # Фильтруем по дровосекам
        if not saw_equipped_successful:
            equipment_search_box_coord = self.clicker.find_image(equipment_search_box, centers=True,
                                                                 screen=screen, offset=offset)
            self.clicker.click(*equipment_search_box_coord)
            time.sleep(1)
            self.clicker.send_chars("Дровосек СДА-2")
            time.sleep(1)

            # Покупка целой пилы (при необходимости) и её установка
            not_broken_saw_coord = self.find_slot_in_items(not_broken_saw_big_image)
            if not_broken_saw_coord is not None:
                self.clicker.drag_and_drop(*not_broken_saw_coord, *broken_saw_coord)
                self.log_message("Сломанный дровосек заменен на новый.")
                saw_equipped_successful = True
            else:
                self.close_all_windows()

                if not self.buy_in_shop([shop_equipment_button, buy_saw_big_button],
                                        amount=self.additional_saw_amount + 1,
                                        wait_shop=True):
                    self.log_error("Фарм будет завершен!")
                    self.repeat_cycle_forever = False
                    return False

                time.sleep(1)

                self.open_equipment()

                screen, offset = self.clicker.screen_lookup()
                equipment_search_box_coord = self.clicker.find_image(equipment_search_box, centers=True,
                                                                     screen=screen, offset=offset)
                self.clicker.click(*equipment_search_box_coord)
                time.sleep(1)
                self.clicker.send_chars("Дровосек СДА-2")
                time.sleep(1)

                screen, offset = self.clicker.screen_lookup()
                broken_saw_coord = self.find_equipped_slot(broken_saw_big_image, screen=screen, offset=offset)
                not_broken_saw_coord = self.find_slot_in_items(not_broken_saw_big_image, screen=screen, offset=offset)
                if not_broken_saw_coord is None:
                    self.log_error("Не найден дровосек в снаряжении!")
                    saw_equipped_successful = False
                elif broken_saw_coord is None:
                    self.log_error("Не найден сломанный дровосек в техустройствах!")
                    saw_equipped_successful = False
                else:
                    self.clicker.drag_and_drop(*not_broken_saw_coord, *broken_saw_coord)
                    self.log_message("Сломанный дровосек заменен на новый.")
                    saw_equipped_successful = True

        self.close_all_windows()

        if not saw_equipped_successful:
            self.log_error("Не удалось экипировать дровосек, фарм будет завершен!")
            self.repeat_cycle_forever = False
            return False

        # Далее работа со складом
        self.open_storage()
        # Надо закрыть скупку, а то может загораживать при работе со складом
        self.toggle_buying_up(False)

        # Фильтруем склад на наличие дровосеков
        storage_search_box_coord = (-150, -115)
        self.clicker.move_and_click(*storage_search_box_coord)
        time.sleep(1)
        self.clicker.send_chars("Дровосек СДА-2")
        time.sleep(1)

        # Ищем окно со складом
        screen, offset = self.clicker.screen_lookup()
        storage_tabs_coord = self.clicker.find_images(storage_tab, screen=screen, offset=offset, min_dist=10)
        main_storage_tab_coord = max(storage_tabs_coord, key=lambda x: x[0])
        storage_window = (main_storage_tab_coord[0] - 10, main_storage_tab_coord[1] - 10, -1, self.storage_filters_window[1])

        # Цикл выкидывания сломанных дровосеков
        thrown_away_saw_count = 0
        screen, offset = self.clicker.screen_lookup(window=storage_window)
        broken_saw_storage_coord = self.clicker.find_image(broken_saw_big_storage_image, centers=True,
                                                           screen=screen, offset=offset)
        while broken_saw_storage_coord is not None:
            self.clicker.drag_and_drop(*broken_saw_storage_coord, *(10, 10))
            drop_button_coord = self.clicker.wait_for_image(drop_button, centers=True, timeout=self.action_timeout)
            if drop_button_coord is not None:
                self.clicker.move_and_click(*drop_button_coord)
                thrown_away_saw_count += 1

            time.sleep(1)
            screen, offset = self.clicker.screen_lookup(window=storage_window)
            broken_saw_storage_coord = self.clicker.find_image(broken_saw_big_storage_image, centers=True,
                                                               screen=screen, offset=offset)
        if thrown_away_saw_count > 0:
            self.log_message(f"Выкинуто {thrown_away_saw_count} сломанных дровосеков.")
        else:
            self.log_message("Сломанных дровосеков не обнаружено.")

        # Цикл закидывания в трюм целых пил
        if self.additional_saw_amount > 0:
            # screen, offset = self.clicker.screen_lookup(window=storage_window)
            not_broken_saw_storage_coord = self.clicker.find_image(not_broken_saw_big_image, centers=True,
                                                                   screen=screen, offset=offset)
            in_cargo_saw_count = 0
            for i in range(in_cargo_saw_count, self.additional_saw_amount):
                if not_broken_saw_storage_coord is None:
                    self.log_error(f"Не найдено {self.additional_saw_amount - i} дровосеков для перекладывания в трюм!")
                    break

                self.clicker.drag_and_drop(*not_broken_saw_storage_coord,
                                           not_broken_saw_storage_coord[0] - 100, not_broken_saw_storage_coord[1])
                in_cargo_saw_count += 1

                if i != self.additional_saw_amount - 1:
                    time.sleep(1)
                    screen, offset = self.clicker.screen_lookup(window=storage_window)
                    not_broken_saw_storage_coord = self.clicker.find_image(not_broken_saw_big_image, centers=True,
                                                                           screen=screen, offset=offset)

            # Если недоложили - идем покупаем
            if in_cargo_saw_count < self.additional_saw_amount:
                self.exit()

                if not self.buy_in_shop([shop_equipment_button, buy_saw_big_button],
                                        amount=self.additional_saw_amount - in_cargo_saw_count,
                                        wait_shop=True):
                    self.log_error("Фарм будет завершен!")
                    self.repeat_cycle_forever = False
                    return False

                time.sleep(1)

                self.open_storage()

                # Надо закрыть скупку, а то может загораживать при работе со складом
                self.toggle_buying_up(False)

                # Фильтруем склад на наличие дровосеков
                storage_search_box_coord = (-150, -115)
                self.clicker.move_and_click(*storage_search_box_coord)
                time.sleep(1)
                self.clicker.send_chars("Дровосек СДА-2")
                time.sleep(1)

                screen, offset = self.clicker.screen_lookup(window=storage_window)
                not_broken_saw_storage_coord = self.clicker.find_image(not_broken_saw_big_image, centers=True,
                                                                       screen=screen, offset=offset)
                for i in range(in_cargo_saw_count, self.additional_saw_amount):
                    if not_broken_saw_storage_coord is None:
                        self.log_error(f"Не найдено {self.additional_saw_amount - i} дровосеков для перекладывания в трюм, фарм будет завершен!")
                        self.repeat_cycle_forever = False
                        self.exit()
                        return False

                    self.clicker.drag_and_drop(*not_broken_saw_storage_coord,
                                               not_broken_saw_storage_coord[0] - 100, not_broken_saw_storage_coord[1])
                    in_cargo_saw_count += 1

                    if i != self.additional_saw_amount - 1:
                        time.sleep(1)
                        screen, offset = self.clicker.screen_lookup(window=storage_window)
                        not_broken_saw_storage_coord = self.clicker.find_image(not_broken_saw_big_image, centers=True,
                                                                               screen=screen, offset=offset)

            if in_cargo_saw_count == self.additional_saw_amount:
                self.log_message("Дровосеки переложены в трюм.")

        self.exit()

        return True

