import undetected_chromedriver as uc


_driver = None

def get_driver():
    """
    Set up and return a single instance of the Selenium WebDriver (Chrome).
    """
    global _driver
    if _driver is None:
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        _driver = uc.Chrome(options=options, headless=False, use_subprocess=False, user_multi_procs=True)

    return _driver


def quit_driver():
    global _driver
    if _driver:
        _driver.quit()
        _driver = None

