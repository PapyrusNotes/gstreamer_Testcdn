from ultralytics import YOLO
import torch

import os
from pathlib import Path

from mlmodel.errors.custom_errors import GPUNotFound, ModelNotFound
from mlmodel.yolomodel.YOLOmodel import MLModel


def is_model_available(tsr_engine_dir, trt_engine_dir):
    return os.path.isfile(tsr_engine_dir) and os.path.isfile(trt_engine_dir)


def is_gpu_available():
    print('gpu available : ', torch.cuda.is_available())
    print('available gpus : ', torch.cuda.device_count())
    print('current gpu : ', torch.cuda.current_device())
    print('gpu name : ', torch.cuda.get_device_name(0))
    return torch.cuda.is_available()


class ModelManager:
    def __init__(self):
        self.tsr_engine_dir = './pretrained/safety-0225-epoch87.pt'
        self.trt_engine_dir = './pretrained/safety-0225-epoch87.engine'
        self.devices = []
        self.show_conf = False
        self.input_shape = (960, 960)
        self.output_shape = (1, 7, 18900)  # (batch, 1, class+4, dividend)

    def build_trt_engine(self):
        """
        TODO : Move building model function to 'Toolkit' project
        """
        tsr_model = YOLO(f"{self.tsr_engine_dir}")
        tsr_model.export(format="tensorrt", device="0", half=True)
        trt_model = YOLO(f"{self.trt_engine_dir}")
        return True

    def set_config(self):
        self.tsr_engine_dir = Path(os.getenv('PYTORCH_MODEL'))
        self.trt_engine_dir = Path(os.getenv('TENSORRT_MODEL'))
        self.show_conf = Path(os.getenv('SHOW_CONF'))
        self.input_shape = Path(os.getenv('INPUT_SHAPE'))
        self.output_shape = Path(os.getenv('OUTPUT_SHAPE'))

    def load_model(self):
        """
        TODO : Search torch API iterating all available gpu devices.
        """
        if is_gpu_available():
            self.devices.append('cuda:0')
        else:
            raise GPUNotFound

        if not is_model_available(self.tsr_engine_dir, self.trt_engine_dir):
            self.build_trt_engine()

        if not is_model_available(self.tsr_engine_dir, self.trt_engine_dir):
            raise ModelNotFound

        return MLModel(model=YOLO(f"{self.trt_engine_dir}", task="detect"), device=self.devices[0])
