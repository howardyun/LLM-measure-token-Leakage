from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import os
import chardet  # 用于检测文件编码

# 检测文件编码
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # 读取文件前 10KB 的内容用于检测编码
        result = chardet.detect(raw_data)
    return result['encoding'] or 'utf-8'  # 如果无法检测到编码，默认使用 'utf-8'

# 创建一个索引
def create_index(directory):
    schema = Schema(path=TEXT(stored=True), content=TEXT)
    if not os.path.exists("../../index"):
        os.mkdir("../../index")
    ix = create_in("index", schema)
    writer = ix.writer()

    # 遍历目录下的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # 检测文件编码
                encoding = detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    writer.add_document(path=file_path, content=content)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    writer.commit()
    print("Index creation done")

# 搜索文件内容
def search_index(query_str):
    ix = open_dir("index")
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query)
        for result in results:
            print(f"Found in {result['path']}")
    print("Index search done")


# 示例
create_index("C:/Users/ShaoxuanYun/Desktop")  # 将此路径替换为需要索引的文件夹路径
search_index("dga")  # 搜索包含 'dga' 的文件内容
