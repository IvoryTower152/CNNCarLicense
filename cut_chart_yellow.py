import cv2
from PIL import Image
import numpy as np
from pip._vendor.distlib._backport import shutil
import os
import datetime


# 创建目录存放各个结果
def makedir():
    dateTime_p = datetime.datetime.now()
    str_p = datetime.datetime.strftime(dateTime_p, '%Y%m%d_%H%M%S')
    path = 'result/num_bord_save/' + str_p
    path_bord = 'result/num_bord_save/' + str_p + '/num_bord'
    path_detail = 'result/num_bord_save/' + str_p + '/num_detail'
    path_detail_jpg = 'result/num_bord_save/' + str_p + '/num_detail/jpg'
    path_detail_bmp = 'result/num_bord_save/' + str_p + '/num_detail/bmp'

    isExists = os.path.exists(path=path)
    if not isExists:
        os.mkdir(path)
    else:
        print('文件已存在')

    isExists = os.path.exists(path=path_bord)
    if not isExists:
        os.mkdir(path_bord)
    else:
        print('文件已存在')

    isExists = os.path.exists(path=path_detail)
    if not isExists:
        os.mkdir(path_detail)
    else:
        print('文件已存在')

    isExists = os.path.exists(path=path_detail_jpg)
    if not isExists:
        os.mkdir(path_detail_jpg)
    else:
        print('文件已存在')

    isExists = os.path.exists(path=path_detail_bmp)
    if not isExists:
        os.mkdir(path_detail_bmp)
    else:
        print('文件已存在')

    return str_p


# 对定位后的车牌进行预处理
def deal_bord_chart():
    # 读取图像
    img = cv2.imread('result/num_bord/num_bord.jpg')
    img_car = cv2.imread('result/num_bord/car.jpg')
    # 创建目录存储车牌的各个信息
    strs = makedir()
    cv2.imwrite('result/num_bord_save/' + strs + '/num_bord/car.jpg', img_car)
    cv2.imwrite('result/num_bord_save/' + strs + '/num_bord/num_bord.jpg', img)
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 切割掉车牌外围一圈以便后续操作
    # img_new = img_gray[23: 120, 5: 435]
    # 先将其变换为RGB三通道图像
    img_B = cv2.split(img)[0]
    img_G = cv2.split(img)[1]
    img_R = cv2.split(img)[2]
    # 寻找左部的切割边界
    cut_left = 0
    is_cut_left = False
    for i in range(440):
        for j in range(140):
            if (img_B[j, i] < 70) and (img_R[j, i] > 120) and (img_G[j, i] > 100):
                cut_left = i
                is_cut_left = True
                break
        if is_cut_left:
            break
    # 寻找右部的分割边界
    cut_right = 0
    is_cut_right = False
    for i in range(439, -1, -1):
        for j in range(140):
            if (img_B[j, i] < 70) and (img_R[j, i] > 120) and (img_G[j, i] > 100):
                cut_right = i
                is_cut_right = True
                break
        if is_cut_right:
            break
    # 寻找上部的分割边界
    cut_top = 0
    is_cut_top = False
    for i in range(140):
        for j in range(440):
            if (img_B[i, j] < 70) and (img_R[i, j] > 120) and (img_G[i, j] > 100):
                cut_top = i
                is_cut_top = True
                break
        if is_cut_top:
            break
    # 寻找下部的分割边界
    cut_buttom = 0
    is_cut_buttom = False
    for i in range(139, -1, -1):
        for j in range(440):
            if (img_B[i, j] < 70) and (img_R[i, j] > 120) and (img_G[i, j] > 100):
                cut_buttom = i
                is_cut_buttom = True
                break
        if is_cut_buttom:
            break
    # 切割
    img_new = img[cut_top: cut_buttom, cut_left: cut_right]
    # cv2.imshow('TEST', img_new)
    # cv2.imwrite('result/num_bord/test.jpg', img_new)
    # cv2.waitKey(0)
    # 重定大小
    img_new = cv2.resize(img_new, (440, 140))
    # 再切割
    img_new = img_new[20: 125, 0: 440]
    # 转换为灰度图
    img_gray = cv2.cvtColor(img_new, cv2.COLOR_BGR2GRAY)
    # 将车牌图像二值化
    # 先进行高斯滤波
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    ret, img_binary = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 由于黄牌车是黄底黑字，二值化之后会变成白底黑字，因此需要进行二值反转
    cv2.bitwise_not(img_binary, img_binary)
    cv2.imwrite('result/num_bord_save/' + strs + '/num_bord/num_bord_binary.jpg', img_binary)
    return strs


# 对处理后的车牌进行字符分割
def cut_bord_chart(fstr):
    strs = fstr
    # 读取并处理图片
    img = cv2.imread('result/num_bord_save/' + strs + '/num_bord/num_bord_binary.jpg')
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 准备空白画布用于绘制白色像素直方图
    img_hist = np.zeros((105, 440), np.uint8)
    # 变量准备
    width = 440
    height = 105
    white_pixel = [0 for i in range(width)]
    # 统计每一列的白色像素数量
    for i in range(width):
        for j in range(height):
            if img_binary[j, i] > 0:
                white_pixel[i] += 1
    # 绘制直方图
    for i in range(len(white_pixel)):
        cv2.line(img_hist, (i, 105), (i, 105 - white_pixel[i]), 255)
    cv2.imwrite('result/num_bord_save/' + strs + '/num_bord/num_bord_hist.jpg', img_hist)
    # 利用直方图来进行分割
    temp = 1
    white_start = 0
    white_end = 0
    chuan_check = 0
    while temp <= 8:
        # 确认白像素开始点和结束点，以此来分割字符
        for i in range(white_start, len(white_pixel)):
            if white_pixel[i] > 0:
                white_start = i
                break
        for i in range(white_start, len(white_pixel)):
            if white_pixel[i] == 0 or i == len(white_pixel) - 1:
                white_end = i
                break
        # 第一个字符有存在干扰的可能，对其进行判断
        if temp == 1:
            length = white_end - white_start
            # 长度过短必定不是汉字，因此抛弃该选项
            if length < 25:
                # 追加对四川牌照的判断，'川'字可能会被误认为是干扰因素
                # 如果干扰因素出现在边界且较小，就认为它是真的干扰
                if white_start == 0 and length < 15:
                    white_start = white_end
                    continue
                # 否则其极有可能是'川'字的一个笔划，对其做出记录
                else:
                    chuan_check += 1
                    # 如果这样的因素存在三个，那么其极有可能就是'川'字，将其切割
                    if chuan_check == 3:
                        # 切割
                        img_chart = img_binary[0: 105, 0: white_end]
                        # 保存
                        cv2.imwrite('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg', img_chart)
                        # 保存为用于识别的位图
                        im = Image.open('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg')
                        size = 32, 40
                        imm = im.resize(size, Image.ANTIALIAS)
                        imm.save('result/num_bord_save/' + strs + '/num_detail/bmp/' + str(temp) + '.bmp', quality=95)
                        # 分割下一个字符
                        temp += 1
                        white_start = white_end
                    else:
                        white_start = white_end
                        continue
            # 否则就认为该字符确实为要寻找的第一个字符，将其切割保存
            else:
                # 切割
                if white_start <= 3:
                    img_chart = img_binary[0: 105, white_start: white_end]
                else:
                    img_chart = img_binary[0: 105, white_start - 3: white_end + 3]
                # 保存
                cv2.imwrite('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg', img_chart)
                # 保存为用于识别的位图
                im = Image.open('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg')
                size = 32, 40
                imm = im.resize(size, Image.ANTIALIAS)
                imm.save('result/num_bord_save/' + strs + '/num_detail/bmp/' + str(temp) + '.bmp', quality=95)
                # 分割下一个字符
                temp += 1
                white_start = white_end
        # 余下的字符
        else:
            # 需要对'1'注意，因为'1'比较小，若切割下来可能会出现问题
            # 在判定其为'1'之后，可以用自备的图像代替
            length = white_end - white_start
            if length < 30:
                # 有可能是'1'也有可能是车牌的那个点
                # 第三个字符一定是点
                if temp == 3:
                    # 切割
                    img_chart = img_binary[0: 105, white_start - 3: white_end + 3]
                    # 保存
                    cv2.imwrite('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg', img_chart)
                    # 保存为用于识别的位图
                    im = Image.open('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg')
                    size = 32, 40
                    imm = im.resize(size, Image.ANTIALIAS)
                    imm.save('result/num_bord_save/' + strs + '/num_detail/bmp/' + str(temp) + '.bmp', quality=95)
                    # 分割下一个字符
                    temp += 1
                    white_start = white_end
                # 认为是'1'
                else:
                    # 切割
                    img_chart = img_binary[0: 105, white_start - 3: white_end + 3]
                    cv2.imwrite('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg', img_chart)
                    # 使用准备好的位图替代
                    shutil.copy(os.path.join('result/num_bord_save/sample/', 'sample.bmp'),
                                os.path.join('result/num_bord_save/' + strs + '/num_detail/bmp/', str(temp) + '.bmp'))
                    # 分割下一个字符
                    temp += 1
                    white_start = white_end
            else:
                # 切割
                img_chart = img_binary[0: 105, white_start - 3: white_end + 3]
                # 保存
                cv2.imwrite('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg', img_chart)
                # 保存为用于识别的位图
                im = Image.open('result/num_bord_save/' + strs + '/num_detail/jpg/' + str(temp) + '.jpg')
                size = 32, 40
                imm = im.resize(size, Image.ANTIALIAS)
                imm.save('result/num_bord_save/' + strs + '/num_detail/bmp/' + str(temp) + '.bmp', quality=95)
                # 分割下一个字符
                temp += 1
                white_start = white_end


def yellow_temperance():
    strs = deal_bord_chart()
    cut_bord_chart(strs)
    return strs


if __name__ == '__main__':
    strs = deal_bord_chart()
    cut_bord_chart(strs)