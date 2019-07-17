import cv2
import numpy as np


# 1.对图像做预处理
def img_process(path):
    # 读取图片
    img = cv2.imread(path)
    # 1.1.统一规定大小为640 * 480
    img = cv2.resize(img, (640, 480))
    # 1.2.高斯模糊
    img_gas = cv2.GaussianBlur(img, (5, 5), 0)
    # 1.3.RGB通道分离
    img_B = cv2.split(img_gas)[0]
    img_G = cv2.split(img_gas)[1]
    img_R = cv2.split(img_gas)[2]
    # 1.4.读取灰度图与HSV空间图
    img_grey = cv2.cvtColor(img_gas, cv2.COLOR_BGR2GRAY)
    img_HSV = cv2.cvtColor(img_gas, cv2.COLOR_BGR2HSV)
    return img, img_gas, img_B, img_G, img_R, img_grey, img_HSV


# 2.初步识别,通过车牌颜色来定位车牌位置
def first_distinguish(img_grey, img_HSV, img_B, img_G, img_R):
    for i in range(480):
        for j in range(640):
            # 蓝色车牌
            if ((img_HSV[:, :, 0][i, j] - 115) ** 2 < 15 ** 2) and (img_B[i, j] > 70) and (img_R[i, j] < 40):
                img_grey[i, j] = 255
            # 黄色车牌
            # elif ((img_HSV[:, :, 0][i, j] - 22) ** 2 < 11 ** 2) and (img_B[i, j] < 70) and (img_R[i, j] > 190):
            elif ((img_HSV[:, :, 0][i, j] - 22) ** 2 < 11 ** 2) and (img_B[i, j] < 70) and (img_R[i, j] > 120) and (
                    img_G[i, j] > 100):
                img_grey[i, j] = 255
            else:
                img_grey[i, j] = 0
    # 3.进一步对图像进行处理
    # 3.1.定义核
    kernel_small = np.ones((3, 3))
    kernel_big = np.ones((7, 7))
    # 3.2.进行高斯平滑
    img_grey = cv2.GaussianBlur(img_grey, (5, 5), 0)
    # 3.3.进行腐蚀操作5次
    img_dilate = cv2.dilate(img_grey, kernel_small, iterations=5)
    # 3.4.进行闭操作
    img_close = cv2.morphologyEx(img_dilate, cv2.MORPH_CLOSE, kernel_big)
    # 3.5.再次进行高斯平滑
    img_close = cv2.GaussianBlur(img_close, (5, 5), 0)
    # 3.6.二值化处理
    ret, img_binary = cv2.threshold(img_close, 100, 255, cv2.THRESH_BINARY)
    return img_binary


# 4.车牌定位
def locate(img_binary):
    # 4.1.检测所有外轮廓，只留矩形的四个顶点
    contours, hierarchy = cv2.findContours(img_binary,
                                           cv2.RETR_LIST,
                                           cv2.CHAIN_APPROX_SIMPLE)
    # 4.2.形状和大小筛选校验
    det_x_max = 0
    der_y_max = 0
    num = 0
    for i in range(len(contours)):
        x_min = np.min(contours[i][:, :, 0])
        x_max = np.max(contours[i][:, :, 0])
        y_min = np.min(contours[i][:, :, 1])
        y_max = np.max(contours[i][:, :, 1])
        det_x = x_max - x_min
        det_y = y_max - y_min
        if (det_x / det_y > 1.8) and (det_x > det_x_max) and (det_y > der_y_max):
            det_x_max = det_x
            der_y_max = det_y
            num = i
    # 4.3.获取最可疑区域轮廓点集
    points = np.array(contours[num][:, 0])
    return points


def find_vertices(points):
    # 4.4.获取最小外接矩阵，中心点坐标，宽高，旋转角度
    rect = cv2.minAreaRect(points)
    # 4.5.获取矩形四个顶点
    box = cv2.boxPoints(rect)
    # 4.6.取整
    box = np.int0(box)
    # 4.7.获取四个顶点坐标
    left_point_x = np.min(box[:, 0])
    right_point_x = np.max(box[:, 0])
    top_point_y = np.min(box[:, 1])
    bottom_point_y = np.max(box[:, 1])

    left_point_y = box[:, 1][np.where(box[:, 0] == left_point_x)][0]
    right_point_y = box[:, 1][np.where(box[:, 0] == right_point_x)][0]
    top_point_x = box[:, 0][np.where(box[:, 1] == top_point_y)][0]
    bottom_point_x = box[:, 0][np.where(box[:, 1] == bottom_point_y)][0]
    # 4.8.封装坐标
    vertices = np.array([[top_point_x, top_point_y],
                         [bottom_point_x, bottom_point_y],
                         [left_point_x, left_point_y],
                         [right_point_x, right_point_y]])
    return vertices, rect, box


# 5.畸变矫正，对最小矩形旋转角度进行判断
def correct(vertices, rect):
    # 5.1.畸变情况一
    if rect[2] > -45:
        new_right_point_x = vertices[0, 0]
        new_right_point_y = int(vertices[1, 1] - (vertices[0, 0] - vertices[1, 0]) / (vertices[3, 0] - vertices[1, 0]) * (vertices[1, 1] - vertices[3, 1]))

        new_left_point_x = vertices[1, 0]
        new_left_point_y = int(vertices[0, 1] + (vertices[0, 0] - vertices[1, 0]) / (vertices[0, 0] - vertices[2, 0]) * (vertices[2, 1] - vertices[0, 1]))
        # 矫正后的四个顶点坐标
        point_set_1 = np.float32([[440, 0], [0, 0], [0, 140], [440, 140]])
    # 5.2.畸变情况二
    elif rect[2] < -45:
        new_right_point_x = vertices[1, 0]
        new_right_point_y = int(vertices[0, 1] + (vertices[1, 0] - vertices[0, 0]) / (vertices[3, 0] - vertices[0, 0]) * (vertices[3, 1] - vertices[0, 1]))

        new_left_point_x = vertices[0, 0]
        new_left_point_y = int(vertices[1, 1] - (vertices[1, 0] - vertices[0, 0]) / (vertices[1, 0] - vertices[2, 0]) * (vertices[1, 1] - vertices[2, 1]))
        # 矫正后的四个顶点坐标
        point_set_1 = np.float32([[0, 0], [0, 140], [440, 140], [440, 0]])
    # 5.3.矫正前平行四边形四个顶点坐标
    new_box = np.array([(vertices[0, 0], vertices[0, 1]), (new_left_point_x, new_left_point_y),
                        (vertices[1, 0], vertices[1, 1]), (new_right_point_x, new_right_point_y)])
    point_set_0 = np.float32(new_box)
    return point_set_0, point_set_1, new_box


# 6.变换
def transform(img, point_set_0, point_set_1):
    # 变换矩阵
    mat = cv2.getPerspectiveTransform(point_set_0, point_set_1)
    # 投影变换
    lic = cv2.warpPerspective(img, mat, (440, 140))
    return lic


# 切割出车牌
def cut_lic(img, vertices):
    lic = img[vertices[0, 1]: vertices[1, 1], vertices[2, 0]: vertices[3, 0]]
    lic = cv2.resize(lic, (440, 140))
    return lic


# 确认车牌颜色
def check_color(lic):
    img_HSV = cv2.cvtColor(lic, cv2.COLOR_BGR2HSV)
    yellow = 0
    blue = 0
    for i in range(140):
        for j in range(440):
            if (img_HSV[:, :, 0][i, j] - 115) ** 2 < 15 ** 2:
                blue += 1
            elif (img_HSV[:, :, 0][i, j] - 22) ** 2 < 11 ** 2:
                yellow += 1
    if blue > yellow:
        return '蓝'
    else:
        return '黄'


# 用于外部调用的封装方法
def find_car_license(path):
    img, img_gas, img_B, img_G, img_R, img_grey, img_HSV = img_process(path=path)
    img_binary = first_distinguish(img_grey, img_HSV, img_B, img_G, img_R)
    points = locate(img_binary)
    vertices, rect, box = find_vertices(points)
    # 若中心旋转角恰好为-0.0则不需要矫正
    if rect[2] == -0.0:
        lic = cut_lic(img, vertices)
    # 否则矫正车牌
    else:
        point_set_0, point_set_1, new_box = correct(vertices, rect)
        lic = transform(img, point_set_0, point_set_1)
    # 确认车牌颜色用于下一步
    str_color = check_color(lic)
    # 保存切割下来的车牌图片以及车的图片
    cv2.imwrite('result/num_bord/car.jpg', img)
    cv2.imwrite('result/num_bord/num_bord.jpg', lic)
    return str_color


if __name__ == '__main__':
    path = 'testimage/02.jpg'
    # img, img_gas, img_B, img_G, img_R, img_grey, img_HSV = img_process(path=path)
    # img_binary = first_distinguish(img_grey, img_HSV, img_B, img_G, img_R)
    # points = locate(img_binary)
    # vertices, rect, box = find_vertices(points)
    # # 若中心旋转角恰好为-0.0则不需要矫正
    # if rect[2] == -0.0:
    #     img_draw = cv2.drawContours(img.copy(), [box], -1, (0, 0, 255), 3)
    #     lic = cut_lic(img, vertices)
    # # 否则矫正车牌
    # else:
    #     point_set_0, point_set_1, new_box = correct(vertices, rect)
    #     img_draw = cv2.drawContours(img.copy(), [new_box], -1, (0, 0, 255), 3)
    #     lic = transform(img, point_set_0, point_set_1)
    # # cv2.imshow('TEST', img_draw)
    # # cv2.imshow('LIC', lic)
    # cv2.imwrite('result/num_bord/num_bord.jpg', lic)
    # cv2.imwrite('result/num_bord/car.jpg', img)
    # # cv2.waitKey(0)
    str_color = find_car_license(path)
    print(str_color)
