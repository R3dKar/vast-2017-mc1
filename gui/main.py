import dearpygui.dearpygui as dpg
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from typing import Any

# data parsing
@dataclass
class RouteData:
    timestamp: datetime
    car_id: str
    car_type: str
    gate_name: str

data: list[RouteData] = []

with open('./data/sensors.csv', 'r') as file:
    lines = file.readlines()[1:]

    for line in lines:
        timestamp, car_id, car_type, gate_name = line.strip().split(',')

        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        data.append(RouteData(timestamp, car_id, car_type, gate_name))

data = sorted(data, key=lambda x: x.timestamp)

map_points = {
    'entrance1': (17, 132),
    'general-gate0': (110, 190),
    'entrance0': (62, 186),
    'ranger-stop0': (89, 183),
    'general-gate1': (64, 174),
    'ranger-stop1': (19, 175),
    'gate0': (63, 166),
    'ranger-stop2': (80, 165),
    'general-gate2': (104, 167),
    'ranger-stop3': (148, 154),
    'camping8': (183, 151),
    'general-gate3': (186, 144),
    'gate3': (149, 139),
    'entrance2': (183, 112),
    'gate4': (164, 85),
    'ranger-stop5': (151, 81),
    'camping7': (181, 54),
    'general-gate6': (136, 62),
    'gate5': (131, 53),
    'ranger-stop6': (123, 52),
    'camping6': (150, 22),
    'gate8': (138, 18),
    'entrance4': (140, 15),
    'ranger-base': (128, 24),
    'entrance3': (115, 32),
    'gate6': (116, 48),
    'gate7': (97, 39),
    'ranger-stop7': (100, 47),
    'general-gate7': (65, 55),
    'camping5': (20, 78),
    'ranger-stop4': (18, 104),
    'camping4': (48, 110),
    'gate2': (24, 145),
    'camping2': (44, 135),
    'camping3': (45, 131),
    'camping4': (48, 110),
    'general-gate4': (69, 101),
    'general-gate5': (124, 88),
    'camping0': (52, 158),
    'camping1': (129, 149),
    'gate1': (58, 155),
}

# gui
dpg.create_context()
dpg.configure_app(docking=True, docking_space=True)

@dataclass
class Image:
    width: int
    height: int
    channels: int
    data: Any

map_image = Image(*dpg.load_image('./data/map.bmp'))
with dpg.texture_registry():
    dpg.add_static_texture(map_image.width, map_image.height, map_image.data, tag='map')

def car_changed(sender, selected_car_id: str, user_data):
    route = [map_points[entry.gate_name] for entry in data if entry.car_id == selected_car_id]
    route_x = [point[0] for point in route]
    route_y = [point[1] for point in route]

    dpg.delete_item('car_route')
    dpg.add_line_series(route_x, route_y, parent='map_plot_y', label='Car\'s route', tag='car_route')

with dpg.window(label='Map view', no_close=True):
    with dpg.plot(height=-1, width=-1, equal_aspects=True, no_title=True, tag='map_plot'):
        dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='map_plot_x')
        dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='map_plot_y')

        for point_name, coordinates in map_points.items():
            dpg.add_plot_annotation(label=point_name, default_value=coordinates, color=(255, 0, 0, 128), clamped=False)

        dpg.add_image_series(texture_tag='map', bounds_min=(0, 0), bounds_max=(200, 200), parent='map_plot_y')

with dpg.window(label='Cars', no_close=True):
    car_ids = list(set(item.car_id for item in data))

    # расскомментировать вместо строки выше, если нужно отобразить только 2P машины
    # cars_type_2p = [item for item in data if item.car_type == "2P"]
    # car_ids = list(set(item.car_id for item in cars_type_2p))

    dpg.add_text(f'Car ids ({len(car_ids)}):')
    dpg.add_listbox(items=car_ids, num_items=20, callback=car_changed)

dpg.create_viewport(title='Routes Preview', width=1600, height=900)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
