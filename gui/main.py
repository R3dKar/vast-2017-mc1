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

@dataclass
class Image:
    width: int
    height: int
    channels: int
    data: Any

map_image = Image(*dpg.load_image('./data/map.bmp'))
with dpg.texture_registry():
    dpg.add_static_texture(map_image.width, map_image.height, map_image.data, tag='map')

with dpg.window(label="Map view", no_close=True):
    with dpg.plot(label="Map", height=-1, width=-1, equal_aspects=True, no_title=True, tag='map_plot'):
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='map_plot_x')
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='map_plot_y')

        for point_name, coordinates in map_points.items():
            dpg.add_plot_annotation(label=point_name, default_value=coordinates, color=(255, 0, 0, 255), clamped=False)

        dpg.add_image_series(texture_tag='map', bounds_min=(0, 0), bounds_max=(200, 200), parent='map_plot_y')

dpg.create_viewport(title='Routes Preview', width=1600, height=900)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
