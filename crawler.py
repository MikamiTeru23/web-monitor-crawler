# 导入需要的第三方库
import requests
from bs4 import BeautifulSoup
import time

def get_all_page_text(url):
    """
    通用静态网页抓取函数
    功能：访问目标网页，提取网页标题 + 页面所有可见正文文本
    注意：仅支持静态HTML网站，JS动态加载的网站需要Selenium
    """
    # 伪装成浏览器访问，降低被网站拦截概率
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # 发送网络请求，超时10秒自动断开
        resp = requests.get(url, headers=headers, timeout=10)
        # 自动识别网页编码，避免中文乱码
        resp.encoding = resp.apparent_encoding
        # 用BeautifulSoup解析网页源码
        soup = BeautifulSoup(resp.text, "html.parser")

        # 删掉不需要的脚本、样式标签，避免抓到JS/CSS代码
        for useless_tag in soup(["script", "style"]):
            useless_tag.decompose()

        # 提取网页标题
        page_title = soup.find("title").get_text(strip=True) if soup.find("title") else "无标题"
        # 提取页面所有可见文字，清理多余空行
        raw_text = soup.get_text()
        line_list = [line.strip() for line in raw_text.splitlines()]
        line_list = [line for line in line_list if line]
        page_text = "\n".join(line_list)

        return page_title, page_text

    except Exception as err:
        # 网络错误、链接失效时返回错误信息，不让程序崩溃
        return "访问失败", f"请求异常：{str(err)}"


if __name__ == "__main__":
    # ========== 这里改你要监控的网页地址 ==========
    target_url = "https://quotes.toscrape.com/"
    # 抓取间隔，单位秒，不要设太小，避免给网站造成压力
    check_interval = 10
    # ===============================================

    # 保存上一次抓取的内容，用来对比网页有没有更新
    last_page_content = ""

    print("===== 网页监控爬虫启动 =====")
    print(f"监控地址：{target_url}")
    print(f"每 {check_interval} 秒检测一次，网页更新才会打印内容，按 Ctrl+C 停止\n")

    # 无限循环持续监控
    while True:
        title, current_content = get_all_page_text(target_url)

        # 对比两次内容，不一样就打印更新提示
        if current_content != last_page_content:
            print("=" * 70)
            print(f"🔔 检测到网页更新｜{time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📑 网页标题：{title}")
            print("📃 网页内容：")
            print(current_content)
            print("=" * 70)
            # 更新缓存的内容
            last_page_content = current_content

        # 等待指定时间后，再抓下一次
        time.sleep(check_interval)
