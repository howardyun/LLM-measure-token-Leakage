import pandas as pd
import matplotlib.pyplot as plt
import os

path="C:/Users/szk/Desktop/code/new/LLM-measure-token-Leakage/Analysis/result/"
file_names =[]
for a in os.listdir(path):
    b=path+a
    file_names.append(b)

dataframes = [pd.read_csv(file,encoding='latin1') for file in file_names]

combined_df = pd.read_csv("all_result1.csv",encoding='latin1', dtype=str)


def counts_valid():
    # 计算valid列中1和0的数量
    valid_counts = combined_df['valid'].value_counts()

    # 绘制饼图
    plt.figure(figsize=(6, 6))
    plt.pie(valid_counts, labels=valid_counts.index, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
    plt.title('Valid == 1 vs Valid == 0')
    plt.show()

def valid_available():
    # 过滤出 valid == 1 并且 available == 1 的数据
    filtered_df = combined_df[(combined_df['valid'] == "1") & (combined_df['available'] == "1")]

    # 计算符合条件的比例
    valid_available_count = len(filtered_df)
    total_count = len(combined_df['valid'] == 1)
    other_count=total_count-valid_available_count
    # 创建饼图的数据
    labels = ['Valid & Available', 'Valid not Available']
    sizes = [valid_available_count, other_count]
    colors = ['#66b3ff', '#99ff99']
    explode = (0.1, 0)  # 突出显示第一块

    # 绘制饼图
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Proportion of Valid == 1 and Available == 1')
    plt.axis('equal')  # 保持饼图为圆形

    # 显示图表
    plt.show()

def test():
    # huggingface permission
    valid_counts = combined_df['permissions'].value_counts()

    # 绘制饼图
    plt.figure(figsize=(6, 6))
    plt.pie(valid_counts, labels=valid_counts.index, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
    plt.title('huggingface_permission')
    plt.show()

def openai():
    filtered_df = combined_df[(combined_df['organization'] == "openai") & (combined_df['valid'] == "1")]
    languages = ['valid', "unvalid"]
    popularity = [len(filtered_df),len(combined_df[(combined_df['organization'] == "openai")])-len(filtered_df)]

    plt.pie(popularity, labels=languages, autopct='%1.1f%%', counterclock=False, startangle=90)

    plt.title('openai api')
    plt.tight_layout()
    plt.show()


def all():
    # all
    valid_counts = combined_df['organization'].value_counts()
    valid_counts=valid_counts[valid_counts>50]
    

    # 绘柱状图
    valid_counts.plot(kind='bar')
    plt.title('Number of Organizations')
    plt.xlabel('Organization')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    openai()

