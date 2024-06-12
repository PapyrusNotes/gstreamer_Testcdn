import queue
from queue import Queue
import time
from multiprocessing import Queue as mpQueue

from calculator.extractor import get_ndarray
# from calculator.zone import hv_radius
from app_worker.global_tensors import obj_tensor

infer_queue = Queue(32)
save_queues = [Queue(32) for _ in range(30)]
infer_queues = [Queue(32) for _ in range(30)]
frame_queue = mpQueue(100)


class AppWorker:
    def __init__(self, mlmodel):
        self.mlmodel = mlmodel
        self.save_queues = []
        self.infer_queues = []

    def process_imaging(self):
        try:
            frame = infer_queue.get()
            print("infer queue frame hit")
            sample = frame.get_sample()
            stream_code = frame.stream_code
            save_queue_index = frame.save_queue_index

            img_array = get_ndarray(sample)

            self.mlmodel.predict(img_array=img_array, input_shape=(960, 960))
            print(self.mlmodel.predict_result)

            obj_tensor_result = self.mlmodel.extract_tensor()
            frame.set_obj_result(obj_tensor_result)
            obj_tensor[f'{stream_code}'] = obj_tensor_result

            save_queues[save_queue_index].put(frame)
        except queue.Empty:
            print("infer queue is empty")
            pass
