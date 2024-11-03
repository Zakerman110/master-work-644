from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc


def get_driver():
    """
    Set up and return the Selenium WebDriver (Chrome) for headless scraping.
    """
    # chrome_options = Options()
    # # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    #
    # # Set the path to your ChromeDriver
    # service = Service(executable_path='E:\\Programming\\Selenium\\chromedriver.exe')
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = uc.Chrome(headless=False,use_subprocess=False)

    return driver
