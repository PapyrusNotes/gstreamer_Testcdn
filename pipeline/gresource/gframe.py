class GstFrameWrapper:
    def __init__(self, gst_sample, index):
        self.sample = gst_sample
        self.stream_code = index
        self.save_queue_index = index
        self.index = index

        self.object_result = None

    def get_sample(self):
        return self.sample

    def set_obj_result(self, prediction_tensor):
        self.object_result = prediction_tensor

    def get_buffer(self):
        return self.sample.get_buffer()

