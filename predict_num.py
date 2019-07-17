import tensorflow as tf
import numpy as np
from PIL import Image
from train_license_number import num_h_fc1_drop, num_W_fc2, num_b_fc2, num_x, num_keep_prob
from train_license_char import char_h_fc1_drop, char_W_fc2, char_b_fc2, char_x, char_keep_prob
from predict_char import license_num


SIZE = 1280
NUM_LABELS = 34
CHAR_LABELS = 31

SAVER_NUM_DIR = './models/num_model/' # 模型保存目录
# strs = './exam_data/exam_images/' # 验证集目录


NUM_DIGITS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
              "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M",
              "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
# CHAR_DIGITS = ("京", "闽", "粤", "苏", "沪", "浙")

# license_num = []

def predict_num(strs):
    with tf.Session() as sess2:
        saver2 = tf.train.import_meta_graph("%smodel.ckpt.meta" % (SAVER_NUM_DIR))
        sess2.run(tf.global_variables_initializer())
        # 加载已经保存的模型
        saver2.restore(sess2, "%smodel.ckpt" % (SAVER_NUM_DIR))

        for n in range(2, 9):
            if n == 3:
                continue
            path = "result/num_bord_save/%s/num_detail/bmp/%s.bmp" % (strs, n)
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
            soft_max = tf.nn.softmax(tf.matmul(num_h_fc1_drop, num_W_fc2) + num_b_fc2)
            result = sess2.run(soft_max, feed_dict={num_x: np.array(img_data), num_keep_prob: 1.0})
            max1 = 0.3
            max2 = 0
            max3 = 0
            max1_index = 0
            max2_index = 0
            max3_index = 0
            for j in range(NUM_LABELS):
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
            license_num.append(NUM_DIGITS[max1_index])
            print("softmax结果前三位概率：%s: %.2f%%    %s: %.2f%%   %s: %.2f%%"
                  % (NUM_DIGITS[max1_index], max1 * 100, NUM_DIGITS[max2_index], max2 * 100, NUM_DIGITS[max3_index], max3 * 100))
    return license_num

# predict_num()
# print(license_num)