import math
import time
import os

import supervision as sv
import numpy as np
import torch
import cv2

# from calculator.constants import CIRCLE_Y_COEFFICIENT, HEIGHT  # get circle coord()
# from calculator.constants import OBJECT_COEFFICIENT, N_POINTS, DISTANCE_THRESHOLD, CONFIDENCE_THRESHOLD  # hv_radius()
from calculator.constants import Y_CENTER_DICT, DIST_DICT, ELLIPSE_DICT, OBJECT_COEFFICIENT_DICT  # hv_radius()


def get_circle_coord(theta, x_center, y_center, radius, class_label):
    x = x_center + radius * math.cos(theta)
    y = y_center + radius * math.sin(theta) * max(0.3, y_center / 1080) * ELLIPSE_DICT[class_label]
    return [x, y]


def get_all_circle_coords(x_center, y_center, radius, n_points, class_label):
    thetas = [i / n_points * 2 * math.pi for i in range(n_points)]
    circle_coords = [get_circle_coord(theta, x_center, y_center, radius, class_label) for theta in thetas]
    return circle_coords


def hv_radius(object_result):
    radius_zone = dict(coords=dict(), res=dict())

    total_detections = sv.Detections.from_ultralytics(object_result[0])

    workers_classes = [4, 5]
    workers = total_detections[np.isin(total_detections.class_id, workers_classes)]
    workers_zone = total_detections[np.isin(total_detections.class_id, workers_classes)]

    selected_classes = [2, 3, 7]
    heavy_equipment = total_detections[np.isin(total_detections.class_id, selected_classes)]
    equipment_list = list(heavy_equipment)

    # heavy_vehicles = []  # = obj2draw_radius
    # detection_objects = []  # = obj2det_in_zone

    for i, equipment in enumerate(equipment_list):
        bbox = equipment[0]
        class_label = equipment[3]
        x_center = bbox[0] + (bbox[2] - bbox[0]) // 2
        y_center = bbox[3] * Y_CENTER_DICT[class_label]
        radius = OBJECT_COEFFICIENT_DICT[class_label] * bbox[3] / 1080
        n_points = 500
        poly = get_all_circle_coords(
            x_center=x_center,
            y_center=y_center,
            radius=radius,
            n_points=n_points,
            class_label=class_label)
        poly = np.array(poly).astype(int)
        radius_zone['coords'][f'poly{i}'] = poly

        equipment_center = [x_center, y_center]
        for j in range(len(workers)):
            worker_center = [
                (workers[j].xyxy[0][0] + workers[j].xyxy[0][2]) / 2,
                (workers[j].xyxy[0][1] + workers[j].xyxy[0][3]) / 2
            ]
            dist = np.sqrt(
                (equipment_center[0] - worker_center[0]) ** 2 + (equipment_center[0] - worker_center[0]) ** 2)
            if dist < DIST_DICT[class_label]:
                workers.confidence[j] = 0
        workers = workers[workers.confidence > 0.7]

        obj_zone = sv.PolygonZone(polygon=radius_zone['coords'][f'poly{i}'],
                                  frame_resolution_wh=(1920, 1080))
        radius_zone['res'][f'poly{i}'] = sum(obj_zone.trigger(detections=workers))

    return radius_zone

    # 사용자 지정 위험 구역 진입 계산


def danger_zone():
    """
    poly_data =
    if poly.size == 0 or poly == []:
        return False
    poly_zones = [sv.PolygonZone(polygon=polygon,frame_resolution_wh=(1920, 1080)) for polygon in [poly_data]]
    for poly_zone in poly_zones:
        zone_detection = poly_zone.trigger(detections=obj2det_in_zone)
        zone_res += (zone_detection)
    
    return danger_zone
    """""
