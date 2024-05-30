import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
from gi.repository import Gst, GstRtsp

import sys


class HLSConstructor:
    def __init__(self, rtsp_src, index):
        self.rtsp_src = rtsp_src
        self.local_time = 0
        self.index = index

    def compose_bin(self):
        print(f"HLS BIN {self.index} !")
        new_bin = Gst.Bin.new(f"HLSBin_{self.index}")
        src = Gst.ElementFactory.make("rtspsrc", "src")
        src.set_property("latency", 2000)
        src.set_property("drop-on-latency", True)
        src.set_property("do-rtsp-keep-alive", True)
        src.set_property("udp-reconnect", True)
        src.set_property("location", self.rtsp_src)
        src.set_property("do-retransmission", False)
        src.set_property("protocols", GstRtsp.RTSPLowerTrans.UDP)

        depay = Gst.ElementFactory.make("rtph264depay", "depay")

        parse = Gst.ElementFactory.make("h264parse", "parse")

        mpegtsmux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")

        hlssink = Gst.ElementFactory.make("hlssink", "hlssink")

        hlssink.set_property("max-files", 10)
        hlssink.set_property("playlist-length", 5)
        hlssink.set_property("location", f"/home/infer1/hls/output_{self.index}%05d.ts")
        hlssink.set_property("playlist-location", f"/home/infer1/hls/output_{self.index}.m3u8")
        hlssink.set_property("target-duration", 5)

        Gst.Bin.add(new_bin, src)
        Gst.Bin.add(new_bin, depay)
        Gst.Bin.add(new_bin, parse)
        Gst.Bin.add(new_bin, mpegtsmux)
        Gst.Bin.add(new_bin, hlssink)

        def on_pad_added(element1, pad, element2):
            string = pad.query_caps(None).to_string()
            print("********pad.name********", pad.name)
            if pad.name == "video_0" or pad.name.find("recv") == 0:
                element1.link(element2)

        src.connect("pad-added", on_pad_added, depay)
        ret = depay.link(parse)

        if ret:
            print("parse linked")
        ret = ret and parse.link(mpegtsmux)

        if ret:
            print("mpegtsmux linked")
        ret = ret and mpegtsmux.link(hlssink)
        if ret:
            print("hlssink linked")

        if not ret:
            print("ERROR: Elements could not be linked")
            sys.exit(1)
        else:
            print("DONE: All elements linked")

        return new_bin
