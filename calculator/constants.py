# get circle coord()
CIRCLE_Y_COEFFICIENT = 0.55
HEIGHT = 1080

# hv_radius()
OBJECT_COEFFICIENT = 600
N_POINTS = 500
DISTANCE_THRESHOLD = 175
CONFIDENCE_THRESHOLD = 0.7
Y_CENTER_DICT = {
    2: 0.9,
    3: 0.9,
    7: 0.95
}  # 타원 y 좌표 중심점 비율, 낮을 수록 바운딩 박스 위쪽 부분이 타원의 중심이 됨
DIST_DICT = {
    2: 175,
    3: 175,
    7: 50
}  # 작업 반경 안에 사람이 들어왔을 때, 바운딩 박스 중심점으로부터 얼마 이상 떨어져야 카운트할지 정한 수치
ELLIPSE_DICT = {
    2: 0.5,
    3: 0.5,
    7: 0.25,
}  # 타원의 찌그러진 정도, 1에가까울수록 원, 0에 가까울수록 많이 찌그러짐. 카메라 각도에 영향 있어서 추후에 카메라 기준으로 바꿀 예정

OBJECT_COEFFICIENT_DICT = {
    2: 400 / 1920 * 1920,
    3: 500 / 1920 * 1920,
    7: 700 / 1920 * 1920,
}  # 1920 * 1080, 영상 가장 아랫부분에 바운딩 박스 생겼을 때 기준 반지름
