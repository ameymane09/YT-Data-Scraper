import time
from scraper_advanced import scraper_advanced

URL = "https://www.youtube.com/@undercitypodcast/videos"
channel = "Undercity_Podcast"

if __name__ == '__main__':

    loop_start = time.time()

    # Put the link of the videos page of the channel
    scraper_advanced(URL, channel)

    loop_end = time.time()
    print(f"\n\nTotal time for the program to execute: {round(loop_end - loop_start, 2)}s")
