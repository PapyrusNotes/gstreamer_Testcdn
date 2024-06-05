class GPUNotFound(Exception):
    def __init__(self):
        self.message = "Graphic Processor Unit Not found"
        super().__init__(self.message)


class ModelNotFound(Exception):
    def __init__(self):
        self.message = "Model file Not found"
        super().__init__(self.message)
