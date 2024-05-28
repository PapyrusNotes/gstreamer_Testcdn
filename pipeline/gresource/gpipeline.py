import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, GLib
from .constructor import HLSConstructor

from pipeline.cfg.cfgs import RTSP_SRC
from pipeline.callbacks.callbacks import on_message


class GPipeline:

    def __init__(self):
        self.pipeline = Gst.Pipeline()
        self.channels_registry = RTSP_SRC

    def add_bin(self):
        for i, camera in enumerate(self.channels_registry):
            hls_bin_constructor = HLSConstructor(camera)
            hls_bin = hls_bin_constructor.compose_bin()
            self.pipeline.add(hls_bin)

    def start(self, main_loop):
        self.pipeline.set_state(Gst.State.PLAYING)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", on_message, main_loop)
