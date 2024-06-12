import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, GLib
from .constructor import HLSConstructor, SinkBinConstructor

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
            sink_bin_constructor = SinkBinConstructor(i, self.pipeline)
            sink_bin = sink_bin_constructor.compose_bin()
            self.pipeline.add(sink_bin)

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        bus = self.pipeline.get_bus()
        self.bus = bus
        self.bus.add_signal_watch()
        # self.bus.connect("message", on_message, main_loop)
        self.bus.connect("sample-emit", on_emit_frame, 0)
