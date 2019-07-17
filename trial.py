import os

import numpy as np
import tensorflow as tf

from PIL import Image
import cv2

SIZE = 1280
WIDTH = 32
HEIGHT = 40
CHAR_LABELS = 31

Den_dir = './train_data/train_char_images/'
TRAIN_CHAR_DIR = './train_data/train_char_images_ud/' # 训练集目录

for i in range(0, CHAR_LABELS):
    dir = '%s%s/' % (TRAIN_CHAR_DIR, i)  # 数据集的图片目录，i为分类标签
    dird = '%s%s/' % (Den_dir, i)
    for rt, dirs, files in os.walk(dir):
        for filename in files:
            filenames = dir + filename
            nimg = cv2.imread(filenames)
            img = cv2.cvtColor(nimg, cv2.COLOR_BGR2GRAY)
            filenamed = dird + filename
            cv2.imwrite(filenamed, img)