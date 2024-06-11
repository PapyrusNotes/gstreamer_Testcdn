import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
from gi.repository import Gst, GstRtsp

import sys

from pipeline.callbacks.callbacks import on_emit_frame, on_start_feed


class HLSConstructor:
    def __init__(self, rtsp_src, index):
        self.rtsp_src = rtsp_src
        self.local_time = 0
        self.index = index

    def compose_bin(self):
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

        tee = Gst.ElementFactory.make("tee", "tee")

        # Original video sinking branch
        video_queue = Gst.ElementFactory.make("queue", "video_queue")
        video_queue.set_property("max-size-buffers", 10)

        mpegtsmux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")
        hlssink = Gst.ElementFactory.make("hlssink", "hlssink")

        hlssink.set_property("max-files", 10)
        hlssink.set_property("playlist-length", 5)
        hlssink.set_property("location", f"/home/infer1/hls/output_{self.index}%05d.ts")
        hlssink.set_property("playlist-location", f"/home/infer1/hls/output_{self.index}.m3u8")
        hlssink.set_property("target-duration", 5)

        # Extracting tensors branch
        tensor_queue = Gst.ElementFactory.make("queue", "tensor_queue")
        tensor_queue.set_property("max-size-buffers", 10)

        avdec = Gst.ElementFactory.make("avdec_h264", "decode")
        convert = Gst.ElementFactory.make("videoconvert", "convert")
        videoscale = Gst.ElementFactory.make("videoscale")
        videorate = Gst.ElementFactory.make("videorate", f"videorate-{self.index}")
        videorate.set_property("drop-only", True)
        videorate.set_property("max-rate", 5)
        videorate.set_property("silent", True)
        caps = Gst.Caps.from_string(f"video/x-raw, format=(string)RGB, width=(int)1920, height=(int)1080")

        appsink = Gst.ElementFactory.make("appsink", f"rtspsink-{self.index}")
        appsink.set_property("emit-signals", True)
        appsink.set_property("max-buffers", 10)
        appsink.set_property("drop", True)
        appsink.set_property("sync", True)

        Gst.Bin.add(new_bin, src)
        Gst.Bin.add(new_bin, depay)
        Gst.Bin.add(new_bin, parse)

        Gst.Bin.add(new_bin, tee)

        Gst.Bin.add(new_bin, video_queue)
        Gst.Bin.add(new_bin, mpegtsmux)
        Gst.Bin.add(new_bin, hlssink)

        Gst.Bin.add(new_bin, tensor_queue)
        Gst.Bin.add(new_bin, avdec)
        Gst.Bin.add(new_bin, convert)
        Gst.Bin.add(new_bin, videoscale)
        Gst.Bin.add(new_bin, videorate)
        Gst.Bin.add(new_bin, appsink)

        def on_pad_added(element1, pad, element2):
            string = pad.query_caps(None).to_string()
            print("********pad.name********", pad.name)
            element1.link(element2)

        src.connect("pad-added", on_pad_added, depay)

        ret = depay.link(parse)
        if ret:
            print("parse linked")

        ret = ret and parse.link(tee)
        if ret:
            print("tee linked")

        # Link Original video sinking branch
        ret = ret and tee.link(video_queue)
        if ret:
            print("video_queue linked")

        ret = ret and video_queue.link(mpegtsmux)
        if ret:
            print("mpegtsmux linked")

        ret = ret and mpegtsmux.link(hlssink)
        if ret:
            print("hlssink linked")

        # Extracting tensors branch
        ret = ret and tee.link(tensor_queue)
        if ret:
            print("tensor_queue linked")

        ret = ret and tensor_queue.link(avdec)
        if ret:
            print("avdec linked")

        ret = ret and avdec.link(convert)
        if ret:
            print("convert linked")

        ret = ret and convert.link(videoscale)
        if ret:
            print("videscale linked")

        ret = ret and videoscale.link(videorate)
        if ret:
            print("videorate linked")

        ret = ret and videorate.link_filtered(appsink, caps)
        if ret:
            print("appsink linked")

        if not ret:
            print("ERROR: Elements could not be linked")
            sys.exit(1)
        else:
            print("DONE: All elements linked")

        appsink.connect("new-sample", on_emit_frame, self.index)
        print("appsink on_emit_Frame connected")

        return new_bin


class SinkBinConstructor:
    def __init__(self, index, pipeline):
        self.index = index
        self.src = 'RTSP'
        self.pipeline = pipeline

    def compose_bin(self):
        new_bin = Gst.Bin.new(f"HLS_Inference-{self.index}")

        appsrc = Gst.ElementFactory.make("appsrc", "appsrc")
        appsrc.set_property("format", Gst.Format.TIME)
        appsrc.set_property("is-live", True)
        appsrc.set_property("block", False)
        appsrc.set_property("do-timestamp", True)
        appsrc.connect("need-data", on_start_feed, self.index)
        caps = Gst.Caps.from_string(f"video/x-raw, format=(string)RGB, width=(int)1920, height=(int)1080")
        appsrc.set_property("caps", caps)

        convert = Gst.ElementFactory.make("videoconvert", "convert")
        overlay = Gst.ElementFactory.make("cairooverlay", "overlay")
        convert2 = Gst.ElementFactory.make("videoconvert", "convert2")
        x264enc = Gst.ElementFactory.make("x264enc", "x264enc")

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
        Gst.Bin.add(new_bin, mpegtsmux)
        Gst.Bin.add(new_bin, hlssink)

        ret = appsrc.link(convert)
        if ret:
            print("convert linked")

        ret = convert.link(overlay)
        if ret:
            print("overlay linked")

        ret = overlay.link(convert2)
        if ret:
            print("convert2 linked")

        ret = ret and convert2.link(x264enc)
        if ret:
            print("avenc linked")

        ret = ret and x264enc.link(mpegtsmux)
        if ret:
            print("mpegtsmux linked")

        ret = ret and mpegtsmux.link(hlssink)
        if ret:
            print("hlssink linked")

        return new_bin
