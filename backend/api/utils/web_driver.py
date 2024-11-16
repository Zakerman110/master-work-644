import undetected_chromedriver as uc
import threading

# Thread-local storage for WebDriver instances
_thread_local = threading.local()


def get_driver():
    """
    Set up and return a thread-local instance of the Selenium WebDriver (Chrome).
    """
    if not hasattr(_thread_local, "driver"):
        options = uc.ChromeOptions()
        # options.add_argument("--headless=new")  # Uncomment for headless mode
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-blink-features=AutomationControlled')
        _thread_local.driver = uc.Chrome(options=options, headless=False, use_subprocess=False, user_multi_procs=True)
    return _thread_local.driver


def quit_driver():
    """
    Quit and clean up the thread-local instance of the WebDriver.
    """
    if hasattr(_thread_local, "driver"):
        _thread_local.driver.quit()
        del _thread_local.driver
