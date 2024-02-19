# **v1.1** 2024-01-13

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
