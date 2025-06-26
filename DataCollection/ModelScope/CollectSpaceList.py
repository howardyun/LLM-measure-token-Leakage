from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json

# 配置 headless 模式（可选）
chrome_options = Options()
chrome_options.add_argument("--headless")  # 不打开浏览器窗口
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

base_url1 = "https://modelscope.cn/studios?page={}&type=programmatic"
page = 1
studio_links = set()

# 开始爬取
while True:
    url = base_url1.format(page)
    print(f"Visiting page {page}: {url}")
    driver.get(url)
    time.sleep(2)  # 等待页面加载

    # 获取所有 <a> 标签并提取以 /studios/ 开头的 href
    anchors = driver.find_elements(By.TAG_NAME, "a")
    new_links = 0
    for a in anchors:
        href = a.get_attribute("href")
        if href and "/studios/" in href and "modelscope.cn/studios/" in href:
            if href not in studio_links:
                studio_links.add(href)
                new_links += 1

    if new_links == 0:
        print("No new links found. Exiting.")
        break
    else:
        print(f"Found {new_links} new links.")

    page += 1
    time.sleep(1)
base_url2 = "https://modelscope.cn/studios?page={}&type=interactive"
page = 1
# 开始爬取
while True:
    url = base_url2.format(page)
    print(f"Visiting page {page}: {url}")
    driver.get(url)
    time.sleep(2)  # 等待页面加载

    # 获取所有 <a> 标签并提取以 /studios/ 开头的 href
    anchors = driver.find_elements(By.TAG_NAME, "a")
    new_links = 0
    for a in anchors:
        href = a.get_attribute("href")
        if href and "/studios/" in href and "modelscope.cn/studios/" in href:
            if href not in studio_links:
                studio_links.add(href)
                new_links += 1

    if new_links == 0:
        print("No new links found. Exiting.")
        break
    else:
        print(f"Found {new_links} new links.")

    page += 1
    time.sleep(1)




# 关闭浏览器
driver.quit()

# 打印结果
# print(f"\n共提取到 {len(studio_links)} 个 Studio 链接：\n")
# for link in sorted(studio_links):
#     print(link)

# 保存为 JSON 文件
studio_links_list = sorted(list(studio_links))
output_path = "output/modelscope_studios_links.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(studio_links_list, f, ensure_ascii=False, indent=2)

print(f"\n已保存链接到文件：{output_path}")
