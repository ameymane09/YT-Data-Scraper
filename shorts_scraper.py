from selenium_setup import driver
from scroll_to_bottom import scroll_to_bottom
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def shorts_scraper(url, channel_name):
    driver.get(url)

    scroll_to_bottom()

    shorts_page_data = []
    data_list = []

    # Get every link on the page
    for div in BeautifulSoup(driver.page_source,
                             parser="lxml",
                             parse_only=SoupStrainer('div', id='details'),
                             features="lxml"):
        # if link.has_attr('href'):
        #
        #     # Add to list if link is for a video
        #     if "/shorts/" in link['href']:
        #         pprint(link)
        #         print("\n\n\n")

        shorts_link = div.find_next('a')['href']
        views = div.select_one('#metadata-line > span').text.strip()
        title = div.select_one('#video-title').text.strip()

        shorts_page_data.append((shorts_link, views, title))

    # Deleting duplicate values
    shorts_page_data = [*set(shorts_page_data)]

    print(f"There are {len(shorts_page_data)} shorts on this channel.")

    for link in shorts_page_data:
        # Open a new window
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://www.youtube.com" + link[0])

        # Wait till the short is loaded
        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.ID, "button-shape")))

        # Click the three dots
        more_actions_button = driver.find_element(By.CSS_SELECTOR, "#button-shape > button")
        more_actions_button.click()

        try:
            # Wait till the description button loads
            WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR,
                                                "#items > ytd-menu-service-item-renderer.style-scope.ytd-menu-popup-renderer.iron-selected > tp-yt-paper-item > yt-formatted-string")))

            # Click the description button
            desc_button = driver.find_element(By.CSS_SELECTOR,
                                              "#items > ytd-menu-service-item-renderer.style-scope.ytd-menu-popup-renderer.iron-selected > tp-yt-paper-item > yt-formatted-string")
            desc_button.click()

            # Wait till the description page loads
            WebDriverWait(driver, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "#shorts-title")))

            # Start scraping the data
            soup = BeautifulSoup(driver.page_source, 'lxml')

            # The title and views data have already been scraped during the links scraping from Shorts page
            title = link[2]
            views = link[1]

            # Scrape the rest of the data from the description page
            likes = soup.select_one(
                '#factoids > ytd-factoid-renderer:nth-child(1) > div > yt-formatted-string.factoid-value.style-scope.ytd-factoid-renderer').text.strip()
            date_month = soup.select_one(
                "#factoids > ytd-factoid-renderer:nth-child(2) > div > yt-formatted-string.factoid-value.style-scope.ytd-factoid-renderer").text.strip()
            year = soup.select_one(
                "#factoids > ytd-factoid-renderer:nth-child(2) > div > yt-formatted-string.factoid-label.style-scope.ytd-factoid-renderer").text.strip()

            data_dict = {
                "Title": title,
                "Likes": likes,
                "Views": views,
                "Date_Month": date_month,
                "Year": year,
            }
            data_list.append(data_dict)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except TimeoutException:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

    # Convert data to pandas df and store it in a csv file
    shorts_data = pd.DataFrame(data_list)
    shorts_data.to_csv(f"data/Shorts/{channel_name}_shorts_data_{date.today()}.csv",
                       index=False)

    driver.quit()
