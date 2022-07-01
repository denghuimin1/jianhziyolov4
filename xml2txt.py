import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join

#数据集
sets=[("2020", "train"), ("2020", "val"), ("2020", "test"), ("2020","trainval")]
#要检测的类别
classes = ['ore carrier', 'bulk cargo carrier', 'general cargo ship', 'container ship', 'fishing boat','passenger ship']

def convert(size, box):
    #box中存的是框的xmin,xmax,ymin,ymax
    dw = 1./(size[0])#size[0]是图片的宽度
    dh = 1./(size[1])#size[1]是图片的高度
    #x,y框的中心坐标
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    #w,h框的宽度和高度
    w = box[1] - box[0]
    h = box[3] - box[2]
    #把相关值进行等比例转换，或者说归一化
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(year, image_id):#从XML文件中读出数据，到上面的函数中归一化，然后将信息写到txt标注文件中
    in_file = open('VOCdevkit/VOC%s/Annotations/%s.xml'%(year, image_id),'rb')#要读取的数据集中的注释文件，是XML格式
    out_file = open('VOCdevkit/VOC%s/labels/%s.txt'%(year, image_id), 'w')#要生成的标注文件，是txt格式
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')#图片大小的节点
    w = int(size.find('width').text)#从注释文件中获得图片的“宽”和“高”
    h = int(size.find('height').text)

    for obj in root.iter('object'):#检测到的对象节点
        #difficult = obj.find('difficult').text#从注释文件中获得difficult
        cls = obj.find('name').text#从注释文件中获得“类别名”
        if cls not in classes==1:  # or int(difficult)==1
            continue
        cls_id = classes.index(cls)#获得这个类别名，在上面的classes中的位置序号
        xmlbox = obj.find('bndbox')#检测框节点
        #b中是框的xmin,xmax,ymin,ymax
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)#bb中是归一化后的，框的中心坐标，宽，高
        #[fun(a) for a in [...]] 
        #>>> [a+1 for a in [2,3,4,5,6]]
        #[3, 4, 5, 6, 7]
        #'内容'.join([string array])
        #>>> '.'.join(['2','3','4','5','6']) 
        #'2.3.4.5.6'
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')#向标注文件中写入：类别序号 框中心坐标x 框中心坐标y 框宽 框高
wd = getcwd()
 #sets=[('2012', 'train'), ('2012', 'val'), ('2007', 'train'), ('2007', 'val'), ('2007', 'test')]
for year, image_set in sets:
    if not os.path.exists('VOCdevkit/VOC%s/labels/'%(year)):#不存在labels路径，就新建这个路径
        os.makedirs('VOCdevkit/VOC%s/labels/'%(year))
    #.read() 每次读取整个文件，它通常将读取到底文件内容放到一个字符串变量中，也就是说 .read() 生成文件内容是一个字符串类型
    #.readline()每只读取文件的一行，通常也是读取到的一行内容放到一个字符串变量中，返回str类型
    #.readlines()每次按行读取整个文件内容，将读取到的内容放到一个列表中，返回list类型
    #strip（'a'）会把前后两端的字符a删除，而不会删除中间的a。括号没东西时，删除转义字符和空白字符
    #split('a')就是将字符串中包含a的部分，将a删除，并从此处分割字符串为多个字符串。无参数时，以空格分
    image_ids = open('VOCdevkit/VOC%s/ImageSets/Main/%s.txt'%(year, image_set)).read().strip().split()#这个Main文件夹中的：train.txt;val.txt;test.txt三个文件，看了一下都是数据图片文件名
    list_file = open('%s_%s.txt'%(year, image_set), 'w')#生成一个txt文件
    for image_id in image_ids:
        list_file.write('%s/VOCdevkit/VOC%s/JPEGImages/%s.jpg\n'%(wd, year, image_id))#向txt文件中写入：当前目录/VOCdevkit/VOC年/JPEGImages/（Main文件夹中各文件读出的图片文件名）.jpg\n
        convert_annotation(year, image_id)#调用函数生成对应图片的，标注文件
    list_file.close()

#os.system("cat 2020_train.txt 2020_val.txt  2020_trainval.txt> train.txt")#将多个文件内容写入一个文件中
#os.system("cat 2007_train.txt 2007_val.txt 2007_test.txt 2012_train.txt 2012_val.txt > train.all.txt")
