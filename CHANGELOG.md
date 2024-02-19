# v2.0.0 *2024-02-19*

## What's New?
- Added the Shorts Scraper and made it work in 2024.
    - Instead of scraping views and title from the description of the Short, I've scraped it from the initial Shorts page itself.
- Added a basic UI, but for testing reasons I've kept the UI non-functional for now.

## Future Additions
- Add the 'save to local cache file' function to the Shorts scraper also.

---

# v1.1.0 *2024-02-13*

The basic scraper code ported from a previous YT scraper I made in 2022, with the updated changes.

## What's New?
- Updated the scraper to work on the latest version of YouTube.
- Save to local cache file:
    - Added a function to save the data to a local text cache file if the program is interrupted for any reason.
    - The function is currently only added to the Video Scraper.

## Bug Fixes
- Fixed the comments traceback by using xpath instead of selector to find the number of comments.
- Added a sleep function when the scraper scrolls down to the bottom to help load the number of comments.

## Future Additions
- Add a Shorts scraper.
- Add UI to the program.
- Make an executable so that the program can run independently.

---

# v1.0.0

Ported the basic YouTube Sraper from a previous project.
