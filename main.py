import os
import sys, time
from threading import Thread

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib, GObject

from pipeline.gresource.gpipeline import GPipeline, RTSP_SRC
from mlmodel.manager import ModelManager
from app_worker.app_worker import AppWorker
from app_worker.global_tensors import initialize_global_tensors


def main():

    # App Task 초기화
    mlmodel_manager = ModelManager()
    mlmodel = mlmodel_manager.load_model()
    app_worker = AppWorker(mlmodel=mlmodel)

    Gst.init(sys.argv)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)
    # main_loop = GLib.MainLoop()

    # Gstreamer Main Loop Task를 Python Thread에 할당
    # thread = Thread(target=main_loop.run)
    # thread.start()

    initialize_global_tensors(RTSP_SRC)
    gpipeline = GPipeline()
    gpipeline.add_bin()
    # gpipeline.start()
    pipeline = gpipeline.pipeline
    gthread = Thread(target=gpipeline.start, daemon=True)
    gthread.start()

    while True:
        try:
            app_worker.process_imaging()
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT")
            pipeline.set_state(Gst.State.NULL)
            # main_loop.quit()
            sys.exit(1)


if __name__ == '__main__':
    main()
