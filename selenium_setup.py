from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()

# To stop YouTube from detecting Selenium use and blocking us For more info,
# visit: https://newbedev.com/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detection
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_experimental_option('detach', True)

options.set_capability('pageLoadStrategy', 'normal')

# Mute audio
options.add_argument("--mute-audio")

# Add extensions to chrome
options.add_extension(r'D:\Amey\Python\Freelance Work\Youtube Scraper\return_YT_Dislikes_Chrome_extension.crx')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
