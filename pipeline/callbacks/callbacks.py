import queue

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import cairo

from calculator.extractor import extract_detection_from_tensors
from graphic.drawer import draw_bbox
from pipeline.gresource.gframe import GstFrameWrapper
from app_worker.app_worker import infer_queue, save_queues
import time


def on_emit_frame(appsink, index):
    print("on_emit_frame callback triggerd")
    gst_sample = appsink.emit("pull-sample")
    print("Returned gst sample : ", gst_sample)
    new_frame = GstFrameWrapper(gst_sample, index)
    infer_queue.put(new_frame)
    print("put frame into infer queue")
    return True


def on_start_feed(appsrc, length, save_queue_index):
    # Frame 저장 큐 지정
    print("call back on_start_feed reacehd")
    save_queue = save_queues[save_queue_index]
    if save_queue is None:
        print(f"save_queue {save_queue_index} is None")
        return False

    if save_queue.qsize() < 1 or infer_queue.qsize() < 5:
        print("queue sparse reacehd")
        time.sleep(1)
        buffer_size = 1920 * 1080 * 3
        gst_buffer = Gst.Buffer.new_allocate(None, buffer_size, None)
        appsrc.emit("push-buffer", gst_buffer)
        for _ in (0, len(save_queues)):
            appsrc.emit("push-buffer", gst_buffer)

    try:
        frame = save_queue.get(timeout=0)  # detection log socket stream에 쓰임
        print("on_start_feed, frame hit")
        _obj_tensor = frame.get_obj_result()  # detection log socket stream에 쓰임
        # _hv_zone_tensor = frame.get_hv_radius_result()  # detection log socket stream에 쓰임
        # _danger_zone_tensor = frame.get_danger_zone_result()  # detection log socket stream에 쓰임
        print("pushing gst Buffer reached")
        gst_buffer = frame.get_buffer()
        appsrc.emit("push-buffer", gst_buffer)  # App pushes to data to gpipeline
    except queue.Empty:
        print("save_Queue is empty")
        time.sleep(1)
        return True


def on_stop_feed():
    print("stop feed")
    return True


def on_draw(_overlay, context, _timestamp, _duration, stream_code):
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



