import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def run_task(url: str) -> dict:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")

    with webdriver.Chrome(options=opts) as driver:
        driver.get(url)
        time.sleep(1)
        return {"title": driver.title}
