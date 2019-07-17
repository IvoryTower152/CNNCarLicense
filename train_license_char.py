# python3.7.3
# -*- coding: utf-8 -*-

import tensorflow as tf

from train_license_number import fetch_data, conv_layer, fully_connected_layer


SIZE = 1280
WIDTH = 32
HEIGHT = 40
# CHAR_LABELS = 6
CHAR_LABELS = 31

SAVER_CHAR_DIR = './models/char_model/' # 模型保存目录
TRAIN_CHAR_DIR = './train_data/train_char_images/' # 训练集目录
VALIDATION_CHAR_DIR = './validation_data/validation_char_images/' # 测试集目录

# 获取训练数据集
input_count = 0
input_index = 0

input_count, input_index, input_images, input_labels = fetch_data(input_count, input_index, TRAIN_CHAR_DIR, CHAR_LABELS)

# 获取测试数据集
vali_count = 0
vali_index = 0

vali_count, vali_index, vali_images, vali_labels = fetch_data(vali_count, vali_index, VALIDATION_CHAR_DIR, CHAR_LABELS)

# 定义输入节点，对应于图片像素值矩阵集合和图片标签(即所代表的数字)
char_x = tf.placeholder(tf.float32, shape=[None, SIZE])
char_y_ = tf.placeholder(tf.float32, shape=[None, CHAR_LABELS])

x_image = tf.reshape(char_x, [-1, WIDTH, HEIGHT, 1])

# 定义第一个卷积层的variables和ops
W_conv1 = tf.Variable(tf.truncated_normal([3, 3, 1, 32], stddev=0.1))
b_conv1 = tf.Variable(tf.constant(0.1, shape=[32]))

conv_strides = [1, 1, 1, 1]
kernel_size = [1, 2, 2, 1]
pool_strides = [1, 2, 2, 1]

L1_pool = conv_layer(x_image, W_conv1, b_conv1, conv_strides, kernel_size, pool_strides, padding='SAME')

# 定义第二个卷积层的variables和ops
W_conv2 = tf.Variable(tf.truncated_normal([3, 3, 32, 64], stddev=0.1))
b_conv2 = tf.Variable(tf.constant(0.1, shape=[64]))

conv_strides = [1, 1, 1, 1]
kernel_size = [1, 2, 2, 1]
pool_strides = [1, 2, 2, 1]

L2_pool = conv_layer(L1_pool, W_conv2, b_conv2, conv_strides, kernel_size, pool_strides, padding='SAME')

char_h_fc1_drop, char_W_fc2, char_b_fc2, char_keep_prob, char_y_conv = fully_connected_layer(8, 10, L2_pool, CHAR_LABELS)

# 定义优化器和训练op
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=char_y_, logits=char_y_conv))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(char_y_conv, 1), tf.argmax(char_y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# 初始化saver
saver = tf.train.Saver()

if __name__ == '__main__':

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 加载已经保存的模型
        saver.restore(sess, "%smodel.ckpt" % (SAVER_CHAR_DIR))

        print("一共读取了 %s 个输入图像， %s 个标签" % (input_count, input_count))

        # 设置每次训练op的输入个数和迭代次数，这里为了支持任意图片总数，定义了一个余数remainder，譬如，如果每次训练op的输入个数为60，图片总数为150张，则前面两次各输入60张，最后一次输入30张（余数30）
        batch_size = 10
        iterations = 100
        batches_count = int(input_count / batch_size)
        remainder = input_count % batch_size
        print("数据集分成 %s 批, 前面每批 %s 个数据，最后一批 %s 个数据" % (batches_count + 1, batch_size, remainder))

        # 执行训练迭代
        for it in range(iterations):
            # 这里的关键是要把输入数组转为np.array
            for n in range(batches_count):
                train_step.run(feed_dict={char_x: input_images[n * batch_size:(n + 1) * batch_size],
                                          char_y_: input_labels[n * batch_size:(n + 1) * batch_size], char_keep_prob: 0.5})
            if remainder > 0:
                start_index = batches_count * batch_size;
                train_step.run(
                    feed_dict={char_x: input_images[start_index:input_count - 1], char_y_: input_labels[start_index:input_count - 1],
                               char_keep_prob: 0.5})

            # 每完成五次迭代，判断准确度是否已达到100%，达到则退出迭代循环
            iterate_accuracy = 0
            if it % 5 == 0:
                iterate_accuracy = accuracy.eval(feed_dict={char_x: vali_images, char_y_: vali_labels, char_keep_prob: 1.0})
                iterate_loss = cross_entropy.eval(feed_dict={char_x: vali_images, char_y_: vali_labels, char_keep_prob: 1.0})
                print('iteration %d: accuracy %s, loss %s' % (it, iterate_accuracy, iterate_loss))
                if iterate_accuracy >= 1:
                    break;

        print('完成训练!')

        # 保存训练结果
        saver.save(sess, "%smodel.ckpt" % (SAVER_CHAR_DIR))
        print('模型保存成功!')