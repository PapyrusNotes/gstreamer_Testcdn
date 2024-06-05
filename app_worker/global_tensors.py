obj_tensor = dict()


def initialize_global_tensors(initial_channels):
    for i, channel in enumerate(initial_channels):
        obj_tensor[f'{i}'] = None
    return True
