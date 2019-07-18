# CNNCarLicense

## 1.界面设计部分

**work.py**负责最终页面的显示，以及相关功能的实现

**style.css**负责界面与组件的样式的设计

**images**文件夹下存储界面设计部分所用到的图片

**image.qrc**存储样式文件和图片的引用路径

**image.qrc**资源文件转换为.py文件，在work.py界面实现中引用

---

## 2.图像处理部分

**locate_and_cut_lic.py**文件中的程序用于实现对车牌的定位和分割；

**cut_chart_blue.py**与**cut_chart_yellow.py**文件中的程序用于分别实现对于蓝色车牌以及黄色车牌的字符分割；

**result**文件夹下用于存储相关的图片，其中**num_bord**文件夹存储当前输入的图片以及分割出的车牌图片，**num_bord_save**文件夹中存在复数文件夹，其命名规则使用车牌识别时的时间，其中存放相应的车牌图片以及过程相关材料和分割完成的车牌字符图片，一个文件夹中存在一组；

---

## 3.字符识别部分

**train_license_num.py**用于训练识别数字和英文字母的模型

**train_license_char.py**用于训练识别汉字的模型

**predict_num.py**识别目标文件夹中的数字和英文字母

**predict_char.py**识别目标文件夹中的汉字

**train_data**文件夹中的是训练集，其中**train_char_images**文件夹中的是汉字数据，**train_num_images**文件夹中的是数字和英文字母的数据，**validation_data**文件夹中的是测试集，其中**validatinon_char_images**文件夹中的是汉字数据，**validation_num_images**文件夹中的是数字和英文字母的数据，**models**文件夹中存放保存的模型，其中**char_model**文件夹保存识别识别汉字的模型，**num_model**文件夹中保存识别数字和英文字母的模型。

(其中，**models**文件夹下文件已打包成压缩包，请解压后再使用)

---

## 4.数据库操作部分

**dbbase.py**文件中的程序用于在数据库中创建数据表以及提供相关的类和数据库引擎给其他程序使用；

**dbmanage.py**文件中的程序用于进行数据库操作，实现高速车辆的出入管理与计费；

---

## 5.数据集下载地址

**百度网盘链接**：https://pan.baidu.com/s/1Hu-h5PIDCqb6c5dshBlqnA 

**提取码**：hyl1

---
