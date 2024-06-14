from graphic.cfg.cfgs import CLASS, CLASS_RGBA
from app_worker.global_tensors import obj_tensor


def draw_bbox(context, stream_code, timestamp):
    obj_tensor_res = obj_tensor[f'{stream_code}']
    if not obj_tensor_res:
        return False
    if obj_tensor_res[0].shape == (0, 6):
        return False
    for i in range(obj_tensor_res[0].shape[0]):
        x1 = int(obj_tensor_res[0][i][0])
        y1 = int(obj_tensor_res[0][i][1])
        x2 = int(obj_tensor_res[0][i][2])
        y2 = int(obj_tensor_res[0][i][3])
        w = x2 - x1
        h = y2 - y1
        context.rectangle(x1, y1, w, h)
        context.set_line_width(8)
        context.set_source_rgba(*CLASS_RGBA[int(obj_tensor_res[0][i][5])])
        context.stroke()
        text = f'{CLASS[int(obj_tensor_res[0][i][5])]} | Conf[{round(float(obj_tensor_res[0][i][4]), 2)}]'
        (x, y, w, h, dx, dy) = context.text_extents(text)
        context.rectangle(x1, y1 - 36, w, 36)
        context.set_line_width(8)
        context.fill()
        context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        context.move_to(x1, y1 - 8)
        context.show_text(text)
    return True


'''
def danger_zone(context, stream_code):
    danger_zone_res = danger_zone_tensor[f'{stream_code}']
    poly = DataBase().selectDangerPolyByCam(camera)
    if poly.size == 0:
        pass
    else:
        len_poly = len(poly)
        context.move_to(poly[0][0], poly[0][1])
        for i in range(1, len_poly):
            context.line_to(poly[i][0], poly[i][1])
        context.close_path()
        context.set_source_rgba(255 / 255, 255 / 255, 0 / 255, 0.5)
        context.set_line_width(8)
        if zone_res > 0:
            context.fill()
        context.stroke()
'''

'''
def draw_hv_radius(context, stream_code):
    obj_zone_res = hv_zone_tensor[f'{stream_code}']
    if not obj_zone_res:
        return False
    for k in range(len(obj_zone_res['coords'])):
        try:
            poly = obj_zone_res['coords'][f'poly{k}']
            len_poly = len(poly)
            context.move_to(poly[0][0], poly[0][1])
            for i in range(1, len_poly):
                context.line_to(poly[i][0], poly[i][1])
            context.close_path()
            context.set_source_rgba(0 / 255, 0 / 255, 255 / 255, 0.3)
            context.set_line_width(8)
            if obj_zone_res['res'][f'poly{k}'] > 0:
                context.fill()
            context.stroke()
        except Exception as e:
            print(f"EXCEPTION on hv_radius on_draw callback\n{e}")
'''
