import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst
import numpy as np


def get_ndarray(sample):
    buf = sample.get_buffer()
    caps = sample.get_caps()  # get meta data from gst sample
    format = caps.get_structure(0).get_value("format")
    height = caps.get_structure(0).get_value("height")
    width = caps.get_structure(0).get_value("width")
    _, map_info = buf.map(Gst.MapFlags.READ)
    array = np.ndarray(
        (height, width, 3),
        buffer=buf.extract_dup(0, buf.get_size()),
        dtype=np.uint8)
    buf.unmap(map_info)
    array = array[..., ::-1]
    return array


def extract_detection_from_tensors(_obj_tensor, _hv_zone_tensor):
    detections_in_frame = {'obj_risk': [], 'hv_boundary': []}
    for i in range(_obj_tensor[0].shape[0]):
        class_value = int(_obj_tensor[0][i][5])
        if class_value == 0 or class_value == 5:  # Leave only detected objects whose risk is itself.(Fire, Non-helmet)
            detections_in_frame['obj_risk'].append(class_value)
    hv_boundary_in = int(sum(_hv_zone_tensor['res'].values()))
    if hv_boundary_in > 0:
        detections_in_frame['hv_boundary'].append(hv_boundary_in)
    # TODO: extract danger area values
    return detections_in_frame
