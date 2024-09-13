import re
import string
import sys
import jieba
import os
from line_profiler import LineProfiler


def read_clean_file(file_path):       #读取文件并且清洗文本
    if not os.path.exists(file_path):           #若路径不存在，则报错并结束程序
        print(f"Error: The path {file_path} does not exist.")
        exit(0)
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    chinese_punctuation = re.compile(r'[，。？！；：、“”‘’《》【】（）—…、%s]' % re.escape(string.punctuation))   #清洗文本
    return chinese_punctuation.sub('', text)

def merge_keywords(text_x, text_y):    #将两个词典的关键词提取合并在同一个集合中
    keyword_list=[]
    times_x = times_y = 0           #次数限制,限制高频词的数量
    for key  in text_x.keys():
        keyword_list.append(key)        #将关键词加入队列当中
        times_x+=1
        if times_x == 20:           #若次数到达限制，则退出循环
            break
    for key  in text_y.keys():
        keyword_list.append(key)
        times_y+=1
        if times_y == 20:       # #若次数到达限制，则退出循环
            break
    keyword_list = set(keyword_list)        #使用列表去掉相同项
    return keyword_list

def sort_keywords(text_x, text_y, keyword_list):      #将两个词典的内容按照集合进行排序,使两个字典的关键词顺序相同，方便使用余弦定理
    x_sort = {}
    y_sort = {}
    for i in keyword_list:
        if not (i in text_x):           #若这个字典中不存在该关键词，则添加进去，其键值为‘0’
            x_sort[i] = 0
        else:
            x_sort[i] = text_x[i]
        if not (i in text_y):           #若这个字典中不存在该关键词，则添加进去，其键值为‘0’
            y_sort[i] = 0
        else:
            y_sort[i] = text_y[i]
    return x_sort,y_sort
def word_frequency(text):           #jieba分词并且将高频词排序出来
    text= jieba.lcut(text)
    count = {}
    for text in text:
        if len(text) == 1:          #筛选掉不合理的词
            continue
        else:
            count[text] = count.get(text, 0) + 1
    items = list(count.items())
    items.sort(key=lambda x: x[1], reverse=True)            #对列表排序，按照键值从高到低
    items = dict(items)             #转化为字典
    return items

def cosine_similarity(x, y, z):      #计算余弦相似值
    x_sort,y_sort=sort_keywords(x,y,z)          #将两个字典按照相同顺序进行排序
    multiply_each_other = multiply_self_x = multiply_self_y =0
    for value1,value2 in zip(x_sort.values(),y_sort.values()):      #余弦定理
        multiply_each_other = value2 *value1 + multiply_each_other
        multiply_self_x = value1**2 + multiply_self_x
        multiply_self_y = value2**2 + multiply_self_y
    if multiply_each_other != 0:
        return multiply_each_other / (multiply_self_y * multiply_self_x)**(1/2)
    if multiply_each_other == 0:            #防止分母为‘0’
        return 0




def main():         #总程序

    if len(sys.argv) != 4:       #确保输入正确的地址
        print("请输入正确的地址：[原文文件] [抄袭版论文的文件] [答案文件]")
        exit(0)

    text_standard = ""  #   原文文件的地址 C:/Users/唔知/Desktop/学习/软件过程/第二次作业/样例/orig.txt
    text_plagiarize = ""  #  抄袭文件的地址 C:/Users/唔知/Desktop/学习/软件过程/第二次作业/样例/orig_0.8_add.txt

    text = [text_standard, text_plagiarize]

    for i in range(0, 2):
        text[i] = sys.argv[i + 1]       #分别将地址赋予变量
    text_answer = sys.argv[3]             #储存答案的地址

    if not os.path.exists(text_answer):           #检查答案文件路径是否存在，若不存在，则报错并结束程序
        print(f"Error: The path {text_answer} does not exist.")
        exit(0)

    text_clean = []  # 用于储存读取出来并清洗的文件
    for i in text:
        text_clean.append(read_clean_file(i))

    text_word = []  # 用于储存文件中的高频词
    for i in text_clean:
        text_word.append(word_frequency(i))

    text_keyword = []  # 用于储存用于比较的文档的关键词
    for i in range(1, len(text_word)):
        text_keyword.append(merge_keywords(text_word[0], text_word[i]))

    f = open(text_answer, 'w', encoding='utf-8')
    for i in range(1, len(text_word)):
        print(text[0], 'vs', text[i] + ":", end=' ')
        f.write(text[0] + ' vs ' + text[i] + ': ')      #写入文件
        result = cosine_similarity(text_word[0], text_word[i], text_keyword[i - 1])         #返回结果并打印
        print(result)
        f.write(str(result) + '\n')
    f.close()




if __name__ == "__main__":          #用与代码的分析，并且是程序的入口
    lp = LineProfiler()  # 构造分析对象
    """如果想分析多个函数，可以使用add_function进行添加"""
    lp.add_function(read_clean_file)        #添加需要分析的函数
    lp.add_function(merge_keywords)
    lp.add_function(sort_keywords)
    lp.add_function(word_frequency)
    lp.add_function(cosine_similarity)
    test_func = lp(main)  # 添加程序执行的第一个函数
    test_func()  # 执行主函数
    lp.print_stats()  # 打印分析结果
