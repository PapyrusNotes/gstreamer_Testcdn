import torch


class MLModel:
    def __init__(self, model, device):
        self.inference_model = model
        self.predict_result = None
        self.detection_tensor = None
        self.device = device
        self.cls = {
            0: 'FIRE',
            1: 'WORKER',
            2: 'EXCAVATOR',
            3: 'FORKLIFT',
            4: 'WORKER-SAFE',
            5: 'WORKER-DANGER',
            6: 'SPD',
            7: 'TRUCK'
        }
        self.cls_rgba = {
            0: (0.80, 0.16, 0.63, 1.0),  # Pink
            1: (0.98, 0.13, 0.13, 1.0),  # Red
            2: (0.80, 0.16, 0.63, 1.0),  # Pink
            3: (0.00, 0.74, 0.00, 1.0),  # Green
            4: (0.00, 0.74, 0.00, 1.0),  # Green
            5: (0.98, 0.13, 0.13, 1.0),  # Red
            6: (0.80, 0.16, 0.63, 1.0),  # Pink
            7: (0.80, 0.16, 0.63, 1.0),  # Pink
        }

    def predict(self, img_array, input_shape):
        self.predict_result = self.inference_model.predict(img_array, conf=0.7, imgsz=input_shape, show=False,
                                                           verbose=False,
                                                           device=self.device)

    def extract_tensor(self):
        obj_boxes = self.predict_result[0].boxes.xyxy
        obj_conf = self.predict_result[0].boxes.conf
        obj_classes = self.predict_result[0].boxes.cls

        if len(obj_classes) > 0:
            obj_classes = torch.tensor([int(c) for c in obj_classes.cpu().numpy()]).to('cuda:0')

        if obj_boxes.size()[0] == 0:
            detected_tensor = [obj_boxes.cpu()]
        else:
            detected_tensor = [torch.cat((obj_boxes,
                                          obj_conf.view(obj_boxes.shape[0], 1),
                                          obj_classes.view(obj_boxes.shape[0], 1),
                                          ), dim=1).cpu()]
        return detected_tensor
