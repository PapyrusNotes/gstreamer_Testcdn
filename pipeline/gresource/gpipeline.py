import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, GLib
from .constructor import HLSConstructor, InferHLSConstructor, AppSinkConstructor

from pipeline.cfg.cfgs import RTSP_SRC
from pipeline.callbacks.callbacks import on_message, on_emit_frame


class GPipeline:

    def __init__(self):
        self.pipeline = Gst.Pipeline()
        self.channels_registry = RTSP_SRC
        self.bus = None

    def add_bin(self):
        for i, camera in enumerate(self.channels_registry):
            hls_bin_constructor = HLSConstructor(camera, i)
            hls_bin = hls_bin_constructor.compose_bin()
            self.pipeline.add(hls_bin)

        for i, camera in enumerate(self.channels_registry):
            appsink_bin_constructor = AppSinkConstructor(camera, i)
            appsink_bin = appsink_bin_constructor .compose_bin()
            self.pipeline.add(appsink_bin)

        for i, camera in enumerate(self.channels_registry):
            infer_hls_bin_constructor = InferHLSConstructor(i, self.pipeline)
            infer_hls_bin = infer_hls_bin_constructor.compose_bin()
            self.pipeline.add(infer_hls_bin)

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        bus = self.pipeline.get_bus()
        self.bus = bus
        self.bus.add_signal_watch()
        # self.bus.connect("message", on_message, main_loop)
