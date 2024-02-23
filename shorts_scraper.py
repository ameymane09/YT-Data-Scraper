import os
import time

from selenium_setup import driver
from scroll_to_bottom import scroll_to_bottom
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import json


def get_shorts_links():
    shorts_page_data = []

    # Get every div with the Shorts details on the page
    for div in BeautifulSoup(driver.page_source,
                             parser="lxml",
                             parse_only=SoupStrainer('div', id='details'),
                             features="lxml"):
        # Get the Shorts link, views and title
        shorts_link = div.find_next('a')['href']
        views = div.select_one('#metadata-line > span').text.strip()
        title = div.select_one('#video-title').text.strip()
        shorts_page_data.append((shorts_link, views, title))

    # Deleting duplicate values
    shorts_page_data = [*set(shorts_page_data)]
    print(f"There are {len(shorts_page_data)} shorts on this channel.")

    return shorts_page_data


def get_data_from_link(shorts_page_data, channel_name):
    folder_path = f'data/Shorts/{channel_name}'
    data_list = []

    for link in shorts_page_data:
        # Open a new window with a new Short
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://www.youtube.com" + link[0])

        # Wait till the short is loaded
        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.ID, "button-shape")))

        # Click the three dots
        more_actions_button = driver.find_element(By.CSS_SELECTOR, "#button-shape > button")
        more_actions_button.click()

        # Wait till the description button loads
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR,
                                            "#items > ytd-menu-service-item-renderer.style-scope.ytd-menu-popup"
                                            "-renderer.iron-selected > tp-yt-paper-item > yt-formatted-string")))

        # Click the description button
        desc_button = driver.find_element(By.CSS_SELECTOR,
                                          "#items > ytd-menu-service-item-renderer.style-scope.ytd-menu-popup"
                                          "-renderer.iron-selected > tp-yt-paper-item > yt-formatted-string")
        desc_button.click()

        # Wait till the description page loads
        WebDriverWait(driver, 5).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "#shorts-title")))

        # The title and views data have already been scraped during the links scraping from Shorts page
        title = link[2]

        # Scrape the rest of the data from the description page
        soup = BeautifulSoup(driver.page_source, 'lxml')
        views = soup.select_one('#factoids > view-count-factoid-renderer > factoid-renderer > div > '
                                'span.YtwFactoidRendererValue > span').text.strip()
        likes = soup.select_one('#factoids > factoid-renderer:nth-child(1) > div > span.YtwFactoidRendererValue > span').text.strip()
        date_month = soup.select_one('#factoids > factoid-renderer:nth-child(3) > div > span.YtwFactoidRendererValue '
                                     '> span').text.strip()
        year = soup.select_one('#factoids > factoid-renderer:nth-child(3) > div > span.YtwFactoidRendererLabel > span').text.strip()

        data_dict = {
            "Link": link[0],
            "Title": title,
            "Likes": likes,
            "Views": views,
            "Date_Month": date_month,
            "Year": year,
        }
        data_list.append(data_dict)

        # Write the data to the local cache file also.
        with open(f'{folder_path}/local_cache.json', 'a', encoding='utf-8') as file:
            json.dump(data_dict, file)
            file.write('\n')
            print(f'Scraped the data for the Short titled "{title}" successfully!')

        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def shorts_scraper(url, channel_name):
    data_list = []
    folder_path = f'data/Shorts/{channel_name}'

    driver.get(url)

    # Close the return YT dislikes extension page
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    scroll_to_bottom()

    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        else:
            print(f"Folder '{folder_path}' already exists.")

        with open(f"{folder_path}/local_cache.json", "r") as file:
            lines = file.readlines()
            print("Cache file detected. Loading data from it.\n")

    except FileNotFoundError:
        # Create a local cache file
        with open(f'{folder_path}/local_cache.json', 'w'):
            print("No local cache file found. Created one successfully.\n")

        shorts_page_data = get_shorts_links()

        get_data_from_link(shorts_page_data, channel_name)

    else:
        shorts_page_data = get_shorts_links()

        # Convert the lines (list of strings of dictionaries) to cache (list of dictionaries)
        cache = [json.loads(line) for line in lines]

        # Read the links from the cache and make a final_links variable which has links for videos yet to be scraped
        links_already_present = [data["Link"] for data in cache]

        all_shorts_links = [data[0] for data in shorts_page_data]
        final_links = list(set(all_shorts_links).symmetric_difference(set(links_already_present)))

        # Delete the data for links not present in final_links
        final_shorts_page_data = [data for data in shorts_page_data if data[0] in final_links]

        # Append the already existing data to the data list and then run the scraper on the final links
        for line in cache:
            data_list.append(line)

        get_data_from_link(final_shorts_page_data, channel_name)

    finally:
        # If all the links in the cache file have been expanded, then write the data to a CSV file.
        if len(shorts_page_data) == len(data_list):
            os.remove(f'{folder_path}/local_cache.json')
            print("File 'local_cache.json' deleted successfully.")

            # Convert data to pandas df and store it in a csv file
            video_data = pd.DataFrame(data_list)
            video_data.to_csv(f"{folder_path}/{channel_name}_Youtube_Shorts_Data_{date.today()}.csv",
                              index=False)

        else:
            print("Program ended abruptly. Saved the data to the local cache. Please run the program again.\n")

        driver.quit()
