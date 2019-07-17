import tensorflow as tf
import numpy as np
from PIL import Image
from train_license_number import num_h_fc1_drop, num_W_fc2, num_b_fc2, num_x, num_keep_prob
from train_license_char import char_h_fc1_drop, char_W_fc2, char_b_fc2, char_x, char_keep_prob



SIZE = 1280
NUM_LABELS = 34
CHAR_LABELS = 31

SAVER_CHAR_DIR = './models/char_model/' # 模型保存目录
# strs = './exam_data/exam_images/' # 验证集目录


# NUM_DIGITS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
#               "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M",
#               "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
CHAR_DIGITS = ("藏", "川", "鄂", "甘", "赣", "贵", "桂", "黑", "沪", "吉",
               "冀", "津", "晋", "京", "辽", "鲁", "蒙", "闽", "宁", "青",
               "琼", "陕", "苏", "皖", "湘", "新", "渝", "豫", "粤", "云", "浙")
license_num = []

def predict_char(strs):
    with tf.Session() as sess1:
        saver1 = tf.train.import_meta_graph("%smodel.ckpt.meta" % (SAVER_CHAR_DIR))
        sess1.run(tf.global_variables_initializer())
        # 加载已经保存的模型
        saver1.restore(sess1, "%smodel.ckpt" % (SAVER_CHAR_DIR))

        path = "result/num_bord_save/%s/num_detail/bmp/1.bmp" % (strs)
        img = Image.open(path)
        width = img.size[0]
        height = img.size[1]

        img_data = [[0] * SIZE for i in range(1)]
        for h in range(0, height):
            for w in range(0, width):
                if img.getpixel((w, h)) > 190:
                    img_data[0][w + h * width] = 0
                else:
                    img_data[0][w + h * width] = 1

        # 获取softmax结果前三位的index和概率值
        soft_max = tf.nn.softmax(tf.matmul(char_h_fc1_drop, char_W_fc2) + char_b_fc2)
        result = sess1.run(soft_max, feed_dict={char_x: np.array(img_data), char_keep_prob: 1.0})
        max1 = 0.3
        max2 = 0
        max3 = 0
        max1_index = 0
        max2_index = 0
        max3_index = 0
        for j in range(CHAR_LABELS):
            if result[0][j] > max1:
                max1 = result[0][j]
                max1_index = j
                continue
            if (result[0][j] > max2) and (result[0][j] <= max1):
                max2 = result[0][j]
                max2_index = j
                continue
            if (result[0][j] > max3) and (result[0][j] <= max2):
                max3 = result[0][j]
                max3_index = j
                continue
        license_num.clear()
        license_num.append(CHAR_DIGITS[max1_index])
        print("softmax结果前三位概率：%s: %.2f%%    %s: %.2f%%   %s: %.2f%%"
              % (
              CHAR_DIGITS[max1_index], max1 * 100, CHAR_DIGITS[max2_index], max2 * 100, CHAR_DIGITS[max3_index], max3 * 100))

# predict_char()

