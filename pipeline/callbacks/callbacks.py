import queue

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import cairo

import time
import os

from graphic.drawer import draw_bbox
from pipeline.gresource.gframe import GstFrameWrapper
from app_worker.app_worker import infer_queue, save_queues, frame_queue


def on_emit_frame(appsink, index):
    print("on_emit_frame callback")
    gst_sample = appsink.emit("pull-sample")
    new_frame = GstFrameWrapper(gst_sample, index)
    infer_queue.put(new_frame)
    return True


def on_start_feed(appsrc, length, save_queue_index):
    print("<on_start_Feed callback>")
    # 이미지 저장 큐 지정
    save_queue = save_queues[save_queue_index]
    if save_queue is None:
        print("Invalid save_queue")
        return False

    try:
        frame = save_queue.get(timeout=0)  # detection log socket stream에 쓰임
        print("on_start_feed, frame hit")
        _obj_tensor = frame.get_obj_result()  # detection log socket stream에 쓰임
        # _hv_zone_tensor = frame.get_hv_radius_result()  # detection log socket stream에 쓰임
        # _danger_zone_tensor = frame.get_danger_zone_result()  # detection log socket stream에 쓰임
        gst_buffer = frame.get_buffer()
        print("gst_buffer : ", gst_buffer)
        appsrc.emit("push-buffer", gst_buffer)
    except queue.Empty:
        print("save_queue empty")
        return True


def on_stop_feed():
    print("stop feed")
    return True


def on_draw(_overlay, context, _timestamp, _duration, stream_code):
    print("on_draw callback")
    context.select_font_face('Open Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(24)
    draw_bbox(context, stream_code, _timestamp)
    # draw_hv_radius(context, stream_code)
    # _danger_zone(obj_tensor, stream_code)
    return True


def on_prepare_overlay(_overlay, _caps):
    # print("*_overlay = ", _overlay, "context = ",
    #      context, "*_timestamp = ", _timestamp)
    return


def on_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
    if message.type == Gst.MessageType.EOS:
        print(f"on_message : End Of Stream")
        return True

    if message.type == Gst.MessageType.ERROR:
        try:
            err, debug = message.parse_error()
            print(f"on_message : Error - {err} - {debug}")
        except UnicodeDecodeError:
            pass
        return True

    if message.type == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print(f"on_message : Warning - {err} - {debug}")
        return True

    if message.type == Gst.MessageType.INFO:
        err, debug = message.parse_info()
        print(f"on_message : Info - {err} - {debug}")
        return True

    return True



