import os
import time
from datetime import date
import json
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium_setup import driver
from scroll_to_bottom import scroll_to_bottom

data_list = []


def get_data_from_link(links, channel_name):
    folder_path = f'data/Videos/{channel_name}'

    for link in links:
        # Open a new window
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://www.youtube.com" + link)

        # Wait till the YT video page is loaded
        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.ID, "above-the-fold")))

        # Expand the description
        show_more_button = driver.find_element(By.CSS_SELECTOR, "#expand")
        show_more_button.click()

        # Wait till the description page has expanded
        WebDriverWait(driver, 5).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "#collapse")))

        # Move to the bottom of the description to make the comments section unhidden
        html = driver.find_element(By.TAG_NAME, 'html')
        comments_counter = 0
        while True:
            html.send_keys(Keys.END)

            # Only break the loop once the comments section is visible
            try:
                time.sleep(2)
                driver.find_element(By.XPATH,
                                    '//*[@id="count"]/yt-formatted-string/span[1]').get_attribute("textContent")
            except NoSuchElementException:
                continue
            else:
                break
            finally:
                comments_counter += 1
                if comments_counter > 2:
                    break

        # Extract the YT video data
        soup = BeautifulSoup(driver.page_source, 'lxml')

        title = soup.select_one("#title > h1 > yt-formatted-string").text.strip()
        views = soup.select_one("#info > span:nth-child(1)").text.strip()
        date_uploaded = soup.select_one("#info > span:nth-child(3)").text.strip()
        likes = soup.select_one('#top-level-buttons-computed > segmented-like-dislike-button-view-model > '
                                'yt-smartimation > div > div > like-button-view-model > toggle-button-view-model > '
                                'button-view-model > button > '
                                'div.yt-spec-button-shape-next__button-text-content').text.strip()
        dislikes = soup.select_one("#top-level-buttons-computed > segmented-like-dislike-button-view-model > "
                                   "yt-smartimation > div > div > dislike-button-view-model > "
                                   "toggle-button-view-model > button-view-model > button > "
                                   "div.yt-spec-button-shape-next__button-text-content").text.strip()

        # Change formatting of the date
        if "Premiered" in date_uploaded:
            date_uploaded = date_uploaded[10:]
        elif "Sept" in date_uploaded:
            date_uploaded.replace("t", "")

        # If comments are turned off, skip it.
        if soup.find("a",
                     href="https://support.google.com/youtube/answer/9706180?hl=en",
                     text="Learn more"
                     ) is None:
            comments = driver.find_element(by='xpath',
                                           value='/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div['
                                                 '5]/div[1]/div/div[2]/ytd-comments/ytd-item-section-renderer/div['
                                                 '1]/ytd-comments-header-renderer/div[1]/h2/yt-formatted-string/span['
                                                 '1]').text.strip()

        else:
            comments = "N/A"
            print("Age Restricted Video: https://www.youtube.com" + link + " " + title)

        # For age restricted video, description is not available. Hence, skip it.
        if soup.find("a",
                     href="http://www.youtube.com/t/community_guidelines",
                     text="Age-restricted video (based on Community Guidelines)") is None:
            description = soup.select_one("#description-inline-expander").text.strip()
        else:
            description = "Age Restricted Video"
            print("https://www.youtube.com" + link + " " + title)

        data_dict = {
            "Link": link,
            "Content ID": link[9:],
            "Title": title,
            "Views": views[:-5],
            "Upload Date": date_uploaded,
            "Likes": likes,
            "Dislikes": dislikes,
            "No. of Comments": comments,
            "Description": description,
        }
        data_list.append(data_dict)

        # Write the data to the local cache file also.
        with open(f'{folder_path}/local_cache.json', 'a', encoding='utf-8') as file:
            json.dump(data_dict, file)
            file.write('\n')
            print(f'Scraped the data for the video titled "{title}" successfully!')

        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def get_video_links():
    links = []

    # Get every link on the page
    for link in BeautifulSoup(driver.page_source,
                              parser='lxml',
                              parse_only=SoupStrainer('a'),
                              features="lxml"):
        if link.has_attr('href'):

            # Add to list if link is for a video
            if "/watch?v=" in link['href']:
                links.append(link['href'])

    # Deleting duplicate values
    links = [*set(links)]

    return links


def scraper_advanced(url, channel_name):
    """Get the full data for every video on the channel including its title, views, exact upload date, number of
    comments and first paragraph of the description. """

    driver.get(url)

    scroll_to_bottom()

    folder_path = f'data/Videos/{channel_name}'

    """In case the program is interrupted because of any error, write the data to a local cache file and read from 
    it so that the entire program doesn't have to be run again. If no local cache file is detected, run the program as 
    intended. It also deletes the cache file once all the data has been scraped successfully."""
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

        links = get_video_links()
        get_data_from_link(links, channel_name)

    else:
        links = get_video_links()

        # Convert the lines (list of strings of dictionaries) to cache (list of dictionaries)
        cache = [json.loads(line) for line in lines]

        # Read the links from the cache and make a final_links variable which has links for videos yet to be scraped
        links_already_present = [data["Link"] for data in cache]
        final_links = list(set(links).symmetric_difference(set(links_already_present)))

        # Append the already existing data to the data list and then run the scraper on the final links
        for line in cache:
            data_list.append(line)

        get_data_from_link(final_links, channel_name)

    finally:
        if len(links) == len(data_list):
            os.remove(f'{folder_path}/local_cache.json')
            print("File 'local_cache.json' deleted successfully.")

            # Convert data to pandas df and store it in a csv file
            video_data = pd.DataFrame(data_list)
            video_data.to_csv(f"{folder_path}/{channel_name}_Youtube_Video_Data_Advanced_{date.today()}.csv",
                              index=False)

        else:
            print("Program ended abruptly. Saved the data to the local cache. Please run the program again.\n")

        # driver.quit()
