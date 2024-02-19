import time
from scraper_advanced import scraper_advanced
from shorts_scraper import shorts_scraper

URL = "https://www.youtube.com/@undercitypodcast/shorts"
CHANNEL = "Undercity_Podcast"

if __name__ == '__main__':
    # Welcome Message
    print("Welcome to the Youtube Scraper. This is a UI based scraper which will fetch the video/shorts data for any "
          "given channel.\n\n\n")

    channel_url = input("What is the URL of the channel?: ")
    channel_name = input("What is the name of the channel?: ")

    if "videos" in URL:
        loop_start = time.time()

        # Scrape the videos from the channel
        scraper_advanced(URL, CHANNEL)

        loop_end = time.time()
        print(f"\n\nTotal time for the program to execute: {round(loop_end - loop_start, 2)}s")

    elif "shorts" in URL:
        loop_start = time.time()

        # Scrape the shorts from the channel
        shorts_scraper(URL, CHANNEL)

        loop_end = time.time()
        print(f"\n\nTotal time for the program to execute: {round(loop_end - loop_start, 2)}s")

    else:
        print("Bad URL. Closing the program.")

