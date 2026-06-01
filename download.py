import os
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

# ==================== 配置区域 ====================
CSV_FILE = "Fissidens adianthoides 可研究的证实级别.csv"  # 你从 iNaturalist 下载的表格文件名
SAVE_DIR = "Fissidens adianthoides 可研究的证实级别"  # 图片保存的文件夹名称
# ==================================================python3 download.py


def download_image(url_info):
    index, url = url_info
    if not isinstance(url, str) or not url.startswith("http"):
        return
    try:
        # 将缩略图链接替换为高清大图链接
        if "square" in url:
            url = url.replace("square", "large")
        elif "medium" in url:
            url = url.replace("medium", "large")

        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            ext = url.split("?")[0].split(".")[-1]
            if ext.lower() not in ["jpg", "jpeg", "png"]:
                ext = "jpg"
            filename = os.path.join(SAVE_DIR, f"img_{index:04d}.{ext}")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"成功下载: {filename}")
    except Exception as e:
        print(f"下载失败 (第 {index} 行): {e}")


def main():
    if not os.path.exists(CSV_FILE):
        print(
            f"❌ 错误：找不到表格文件 '{CSV_FILE}'，请确认它和本代码在同一个文件夹下！"
        )
        return

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # 读取 CSV，自动处理第一行是标题或网址的情况
    try:
        df = pd.read_csv(CSV_FILE, header=None)
        # 如果第一列里有带有网址特征的字符串，过滤出来
        urls = [url for url in df[0].tolist() if isinstance(url, str) and "http" in url]
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        return

    if not urls:
        print("ℹ️ 表格里没有找到有效的图片网址，请检查表格内容！")
        return

    print(f"📂 找到 {len(urls)} 个有效链接，开始多线程下载...")

    # 使用多线程加速下载
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_image, enumerate(urls, 1))

    print("\n🎉 下载完成！请检查文件夹:", SAVE_DIR)


if __name__ == "__main__":
    main()