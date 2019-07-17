# python3.7.3
# -*- coding: utf-8 -*-

import os

import numpy as np
import tensorflow as tf

from PIL import Image

SIZE = 1280
WIDTH = 32
HEIGHT = 40
NUM_LABELS = 34

SAVER_NUM_DIR = './models/num_model/' # 模型保存目录
TRAIN_NUM_DIR = './train_data/train_num_images/' # 训练集目录
VALIDATION_NUM_DIR = './validation_data/validation_num_images/' # 测试集目录

# 卷积神经网络
def conv_layer(inputs, W, b, conv_strides, kernel_size, pool_strides, padding):
    L_conv = tf.nn.conv2d(inputs, W, strides=conv_strides, padding=padding)
    L_relu = tf.nn.relu(L_conv+b)
    return tf.nn.max_pool(L_relu, ksize=kernel_size, strides=pool_strides, padding='SAME')

# 获得数据集
def fetch_data(count, index, DIR, LABELS):
    # 第一次遍历图片目录是为了获取图片总数
    for i in range(0, LABELS):
        dir = '%s%s/' % (DIR, i)  # 数据集的图片目录，i为分类标签
        for rt, dirs, files in os.walk(dir):
            for filename in files:
                count += 1

    # 定义对应维数和各维长度的数组
    images = np.array([[0] * SIZE for i in range(count)]) # 生成1087(input_count)行，1280(SIZE)列的二维数组
    labels = np.array([[0] * LABELS for i in range(count)]) # 生成1087行，10(LETTER_LABELS)列的二维数组

    # 第二次遍历图片目录是为了生成图片数据和标签
    for i in range(0, LABELS):
        dir = '%s%s/' % (DIR, i)  # 数据集的图片目录，i为分类标签
        for rt, dirs, files in os.walk(dir):
            for filename in files:
                filename = dir + filename
                img = Image.open(filename)
                width = img.size[0]
                height = img.size[1]
                for h in range(0, height):
                    for w in range(0, width):
                        # 通过这样的处理，使数字的线条变细，有利于提高识别准确率
                        # print(img.getpixel((w, h)))
                        if img.getpixel((w, h)) > 190:
                            images[index][w + h * width] = 0
                        else:
                            images[index][w + h * width] = 1
                labels[index][i] = 1
                index += 1

    # 打乱拿到的图片顺序，防止过拟合
    data_index = [i for i in range(len(images))]
    np.random.shuffle(data_index)
    images = images[data_index]
    labels = labels[data_index]

    return count, index, images, labels

# 全连接层
def fully_connected_layer(conv_width, conv_height, conv_pool, labels):
    # 全连接层
    W_fc1 = tf.Variable(tf.truncated_normal([conv_width * conv_height * 64, 1024], stddev=0.1))
    b_fc1 = tf.Variable(tf.constant(0.1, shape=[1024]))

    h_pool2_flat = tf.reshape(conv_pool, [-1, 8 * 10 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    # dropout
    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    # readout层
    W_fc2 = tf.Variable(tf.truncated_normal([1024, labels], stddev=0.1))
    b_fc2 = tf.Variable(tf.constant(0.1, shape=[labels]))

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

    return h_fc1_drop, W_fc2, b_fc2, keep_prob, y_conv

# 获取训练数据集
input_count = 0
input_index = 0

input_count, input_index, input_images, input_labels = fetch_data(input_count, input_index, TRAIN_NUM_DIR, NUM_LABELS)

# 获取测试数据集
vali_count = 0
vali_index = 0

vali_count, vali_index, vali_images, vali_labels = fetch_data(vali_count, vali_index, VALIDATION_NUM_DIR, NUM_LABELS)

# 定义输入节点，对应于图片像素值矩阵集合和图片标签(即所代表的数字)
num_x = tf.placeholder(tf.float32, shape=[None, SIZE])
num_y_ = tf.placeholder(tf.float32, shape=[None, NUM_LABELS])

x_image = tf.reshape(num_x, [-1, WIDTH, HEIGHT, 1])

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

num_h_fc1_drop, num_W_fc2, num_b_fc2, num_keep_prob, num_y_conv = fully_connected_layer(8, 10, L2_pool, NUM_LABELS)

# 定义优化器和训练op
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=num_y_, logits=num_y_conv))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(num_y_conv, 1), tf.argmax(num_y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# 初始化saver
saver = tf.train.Saver()

if __name__ == '__main__':

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 加载已经保存的模型
        saver.restore(sess, "%smodel.ckpt" % (SAVER_NUM_DIR))

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
                train_step.run(feed_dict={num_x: input_images[n * batch_size:(n + 1) * batch_size],
                                          num_y_: input_labels[n * batch_size:(n + 1) * batch_size], num_keep_prob: 0.5})
            if remainder > 0:
                start_index = batches_count * batch_size;
                train_step.run(
                    feed_dict={num_x: input_images[start_index:input_count - 1], num_y_: input_labels[start_index:input_count - 1],
                               num_keep_prob: 0.5})

            # 每完成五次迭代，判断准确度是否已达到100%，达到则退出迭代循环
            iterate_accuracy = 0
            if it % 5 == 0:
                iterate_accuracy = accuracy.eval(feed_dict={num_x: vali_images, num_y_: vali_labels, num_keep_prob: 1.0})
                iterate_loss = cross_entropy.eval(feed_dict={num_x: vali_images, num_y_: vali_labels, num_keep_prob: 1.0})
                print('iteration %d: accuracy %s, loss %s' % (it, iterate_accuracy, iterate_loss))
                if iterate_accuracy >= 1:
                    break;

        print('完成训练!')

        # 保存训练结果
        saver.save(sess, "%smodel.ckpt" % (SAVER_NUM_DIR))
        print('模型保存成功!')