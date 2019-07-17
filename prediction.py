from predict_char import predict_char
from predict_num import predict_num

# SIZE = 1280
# NUM_LABELS = 40
# CHAR_LABELS = 31

# SAVER_CHAR_DIR = './models/char_model/' # 模型保存目录
# EXAM_DIR = './exam_data/exam_images/' # 验证集目录


NUM_DIGITS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
              "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M",
              "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
CHAR_DIGITS = ("藏", "川", "鄂", "甘", "赣", "贵", "桂", "黑", "沪", "吉",
               "冀", "津", "晋", "京", "辽", "鲁", "蒙", "闽", "宁", "青",
               "琼", "陕", "苏", "皖", "湘", "新", "渝", "豫", "粤", "云", "浙")

predict_char()
license = predict_num()

print("车牌号为: %s" % license)