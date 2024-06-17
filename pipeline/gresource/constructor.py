import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
from gi.repository import Gst, GstRtsp

import sys

from pipeline.callbacks.callbacks import on_emit_frame, on_start_feed, on_halt_feed
from pipeline.callbacks.callbacks import on_draw


class HLSConstructor:
    def __init__(self, rtsp_src, index):
        self.rtsp_src = rtsp_src
        self.local_time = 0
        self.index = index

    def compose_bin(self):
        new_bin = Gst.Bin.new(f"HLSBin_{self.index}")
        rtsp_src = Gst.ElementFactory.make("rtspsrc", f"rtsp_hls_src={self.index}")
        rtsp_src.set_property("latency", 2000)
        rtsp_src.set_property("drop-on-latency", True)
        rtsp_src.set_property("do-rtsp-keep-alive", True)
        rtsp_src.set_property("udp-reconnect", True)
        rtsp_src.set_property("location", self.rtsp_src)
        rtsp_src.set_property("do-retransmission", False)
        rtsp_src.set_property("protocols", GstRtsp.RTSPLowerTrans.UDP)

        depay = Gst.ElementFactory.make("rtph264depay", "depay")
        parse = Gst.ElementFactory.make("h264parse", "parse")
        mpegtsmux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")

        hlssink = Gst.ElementFactory.make("hlssink", "hlssink")
        hlssink.set_property("max-files", 10)
        hlssink.set_property("playlist-length", 5)
        hlssink.set_property("location", f"/home/infer1/hls/output_{self.index}%05d.ts")
        hlssink.set_property("playlist-location", f"/home/infer1/hls/output_{self.index}.m3u8")
        hlssink.set_property("target-duration", 5)

        Gst.Bin.add(new_bin, rtsp_src)
        Gst.Bin.add(new_bin, depay)
        Gst.Bin.add(new_bin, parse)
        Gst.Bin.add(new_bin, mpegtsmux)
        Gst.Bin.add(new_bin, hlssink)

        def on_pad_added(element1, pad, element2):
            string = pad.query_caps(None).to_string()
            print("********pad.name********", pad.name)
            element1.link(element2)

        rtsp_src.connect("pad-added", on_pad_added, depay)
        print("HLS Bin : rtsp - depay connected")

        ret = depay.link(parse)
        if ret:
            print("HLS Bin : depay - parse connected")

        ret = ret and parse.link(mpegtsmux)
        if ret:
            print("HLS Bin : parse - mpegtsmux connected")

        ret = ret and mpegtsmux.link(hlssink)
        if ret:
            print("HLS Bin : mpegtsmux - hlssink connected")

        return new_bin


class AppSinkConstructor:
    def __init__(self, rtsp_src, index):
        self.rtsp_src = rtsp_src
        self.index = index

    def compose_bin(self):
        new_bin = Gst.Bin.new(f"AppSink-{self.index}")

        rtsp_infer_src = Gst.ElementFactory.make("rtspsrc", f"rtsp_infer_src-{self.index}")
        rtsp_infer_src.set_property("latency", 2000)
        rtsp_infer_src.set_property("drop-on-latency", True)
        rtsp_infer_src.set_property("do-rtsp-keep-alive", True)
        rtsp_infer_src.set_property("udp-reconnect", True)
        rtsp_infer_src.set_property("location", self.rtsp_src)
        rtsp_infer_src.set_property("do-retransmission", False)
        rtsp_infer_src.set_property("protocols", GstRtsp.RTSPLowerTrans.UDP)

        depay = Gst.ElementFactory.make("rtph264depay", "depay2")
        parse = Gst.ElementFactory.make("h264parse", "parse2")
        avdec = Gst.ElementFactory.make("avdec_h264", "decode")  # x-264 to x-raw
        convert = Gst.ElementFactory.make("videoconvert", "convert")
        videoscale = Gst.ElementFactory.make("videoscale", "videoscale")
        videorate = Gst.ElementFactory.make("videorate", "videorate")
        videorate.set_property("drop-only", True)
        videorate.set_property("max-rate", 20)
        videorate.set_property("silent", True)

        caps = Gst.Caps.from_string(f"video/x-raw, format=(string)RGB, width=(int)1280, height=(int)720")

        appsink = Gst.ElementFactory.make("appsink", f"appsink-{self.index}")
        appsink.set_property("emit-signals", True)
        appsink.set_property("max-buffers", 0)
        appsink.set_property("drop", True)
        appsink.set_property("sync", False)
        appsink.connect("new-sample", on_emit_frame, self.index)

        Gst.Bin.add(new_bin, rtsp_infer_src)
        Gst.Bin.add(new_bin, depay)
        Gst.Bin.add(new_bin, parse)
        Gst.Bin.add(new_bin, avdec)
        Gst.Bin.add(new_bin, convert)
        Gst.Bin.add(new_bin, videoscale)
        Gst.Bin.add(new_bin, videorate)
        Gst.Bin.add(new_bin, appsink)

        def on_pad_added(element1, pad, element2):
            string = pad.query_caps(None).to_string()
            print("********pad.name********", pad.name)
            element1.link(element2)

        rtsp_infer_src.connect("pad-added", on_pad_added, depay)
        print("AppSink Bin : rtsp - depay connected")

        ret = depay.link(parse)
        if ret:
            print("AppSink Bin : depay - parse connected")

        ret = parse.link(avdec)
        if ret:
            print("AppSink Bin : parse - avdec connected")

        ret = avdec.link(convert)
        if ret:
            print("AppSink Bin : avdec - convert connected")

        ret = ret and convert.link(videoscale)
        if ret:
            print("AppSink Bin : convert - videoscale connected")

        ret = ret and videoscale.link(videorate)
        if ret:
            print("AppSink Bin : videoscale - videorate connected")

        ret = ret and videorate.link_filtered(appsink, caps)
        if ret:
            print("AppSink Bin : convert - videoscale connected")

        '''
        ret = ret and convert.link_filtered(appsink, caps)
        if ret:
            print("AppSink Bin : convert - caps - appsink connected")
        '''
        if not ret:
            print("AppSink Bin ERROR: Elements could not be linked")
            sys.exit(1)
        else:
            print("AppSink Bin DONE: All elements linked")

        return new_bin


class InferHLSConstructor:
    def __init__(self, index, pipeline):
        self.index = index
        self.pipeline = pipeline

    def compose_bin(self):
        new_bin = Gst.Bin.new(f"HLS_Inference-{self.index}")

        appsrc = Gst.ElementFactory.make("appsrc", f"appsrc-{self.index}")
        appsrc.set_property("format", Gst.Format.TIME)
        appsrc.set_property("is-live", True)
        appsrc.set_property("do-timestamp", True)
        appsrc.set_property("max-bytes", 0)
        appsrc.set_property("block", False)
        appsrc.set_property("emit-signals", True)
        appsrc.connect("need-data", on_start_feed, self.index)
        appsrc.connect("enough-data", on_halt_feed, self.index)
        caps = Gst.Caps.from_string(f"video/x-raw, format=(string)RGB, width=(int)1280, height=(int)720")
        caps2 = Gst.Caps.from_string(f"video/x-raw, width=(int)1280, height=(int)720")
        appsrc.set_property("caps", caps)

        convert = Gst.ElementFactory.make("videoconvert", "convert")
        overlay = Gst.ElementFactory.make("cairooverlay", "overlay")
        overlay.connect('draw', on_draw, self.index)  # video/x-raw

        convert2 = Gst.ElementFactory.make("videoconvert", "convert2")
        videoscale = Gst.ElementFactory.make("videoscale")
        videorate = Gst.ElementFactory.make("videorate")
        videorate.set_property("drop-only", True)
        videorate.set_property("max-rate", 20)
        videorate.set_property("silent", True)

        x264enc = Gst.ElementFactory.make("x264enc", "x264enc")  # video/x-264
        x264enc.set_property("tune", "zerolatency")
        x264enc.set_property("speed-preset", 4)
        x264enc.set_property("pass", 5)

        mpegtsmux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")
        hlssink = Gst.ElementFactory.make("hlssink", "hlssink")
        hlssink.set_property("max-files", 10)
        hlssink.set_property("playlist-length", 5)
        hlssink.set_property("location", f"/home/infer1/hls/infer/output_{self.index}%05d.ts")
        hlssink.set_property("playlist-location", f"/home/infer1/hls/infer/output_{self.index}.m3u8")
        hlssink.set_property("target-duration", 5)

        Gst.Bin.add(new_bin, appsrc)
        Gst.Bin.add(new_bin, convert)
        Gst.Bin.add(new_bin, overlay)
        Gst.Bin.add(new_bin, convert2)
        Gst.Bin.add(new_bin, x264enc)
        Gst.Bin.add(new_bin, videoscale)
        Gst.Bin.add(new_bin, videorate)
        Gst.Bin.add(new_bin, mpegtsmux)
        Gst.Bin.add(new_bin, hlssink)

        ret = appsrc.link(convert)
        if ret:
            print("InferHLS Bin : appsrc - convert connected")

        ret = convert.link(overlay)
        if ret:
            print("InferHLS Bin : convert - overlay connected")

        ret = overlay.link(convert2)
        if ret:
            print("InferHLS Bin : overlay - convert2 connected")
        '''
        ret = convert2.link(x264enc)
        if ret:
            print("InferHLS Bin : convert2 - x264enc connected")
        '''

        ret = convert2.link(videoscale)
        if ret:
            print("InferHLS Bin : convert2 - videoscale connected")

        ret = videoscale.link(videorate)
        if ret:
            print("InferHLS Bin : videoscale - videorate connected")

        ret = ret and videorate.link_filtered(x264enc, caps2)
        if ret:
            print("InferHLS Bin : videorate - x264enc connected")

        ret = x264enc.link(mpegtsmux)
        if ret:
            print("InferHLS Bin : x264enc - mpegtsmux connected")

        ret = ret and mpegtsmux.link(hlssink)
        if ret:
            print("InferHLS Bin : mpegtsmux - hlssink connected")

        if not ret:
            print("InferHLS Bin ERROR: Elements could not be linked")
            sys.exit(1)
        else:
            print("InferHLS Bin DONE: All elements linked")

        return new_bin
