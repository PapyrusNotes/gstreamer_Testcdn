class GstFrameWrapper:
    def __init__(self, gst_sample, index):
        self.sample = gst_sample
        self.stream_code = index
        self.save_queue_index = index
        self.index = index

    def get_sample(self):
        return self.sample

