from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取桌面路径
def get_desktop_path():
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    else:  # macOS 或 Linux
        return os.path.join(os.path.expanduser('~'), 'Desktop')

# 打开网站
def open_website(url):
    options = webdriver.ChromeOptions()
    # 注释掉无头模式
    # options.add_argument("--headless")  # 移除这行
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver



# 对部分区域截图
def capture_element_screenshot(driver, element, save_path):
    location = element.location
    size = element.size

    driver.save_screenshot("full_page.png")  # 保存整个页面截图

    full_image = Image.open("full_page.png")
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    cropped_image = full_image.crop((left, top, right, bottom))
    cropped_image.save(save_path)  # 保存裁剪后的图片
    print(f"截图已保存到: {save_path}")

# 主函数
def main():
    url = "https://www.gmgn.cc/kline/sol/C14UcJMfvGxLwkfBRnibL5NUpKC7S1mN3Nq8NhFvpump?interval=5"  # 目标网站
    save_name = "kline_chart.png"  # 截图文件名
    save_path = os.path.join(get_desktop_path(), save_name)  # 保存路径

    # 打开网站
    driver = open_website(url)

    try:
        # 等待 K 线图加载完成（根据元素的具体情况来调整）
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-container"))  # 根据 K 线图容器的 CSS 选择器定位
        )

        # 定位 K 线图元素
        element = driver.find_element(By.CSS_SELECTOR, ".chart-container")  # 修改为具体的 CSS 选择器

        # 对目标元素截图
        capture_element_screenshot(driver, element, save_path)

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        driver.quit()  # 关闭浏览器

if __name__ == "__main__":
    main()

