from bs4 import BeautifulSoup
from collections import namedtuple
from selenium import webdriver
from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager
import re
import requests
import json
import csv
import time
import datetime
import urllib.request

Video = namedtuple("Video", "video_id link title duration views age")

def get_videos(link):
    page = BeautifulSoup(download_page(link), "html.parser")
    print("Retrieved page.")
    driver.quit()
    videos = parse_videos_page(page)    
    print("Videos parsed.")
    return videos

def parse_videos_page(page):
    video_divs = page.find_all("div", "style-scope ytd-grid-video-renderer")
    num_video_divs = len(video_divs)
    full_video_divs = []
    for i in range(num_video_divs):
        if i % 11 == 0:
            full_video_divs.append(video_divs[i])
    return [parse_video_div(div) for div in full_video_divs]

def parse_video_div(div):
    try:
        video_id = div.find("a", "yt-simple-endpoint inline-block style-scope ytd-thumbnail")['href'].replace("/watch?v=", "")
        link = "https://www.youtube.com/watch?v=" + video_id
        title = div.find("a", "yt-simple-endpoint style-scope ytd-grid-video-renderer")['title']
        # <a id="video-title" class="yt-simple-endpoint style-scope ytd-grid-video-renderer" aria-label="The Galaxy Brain Garbage of Gaia by Ordinary Things 2 weeks ago 23 minutes 326,453 views" title="The Galaxy Brain Garbage of Gaia" href="/watch?v=fiqLzPBBGTk">The Galaxy Brain Garbage of Gaia</a>
        #in case a stream comes through without a duration tag
        if hasattr(div.find("span", "style-scope ytd-thumbnail-overlay-time-status-renderer"), 'contents'):
            duration = div.find("span", "style-scope ytd-thumbnail-overlay-time-status-renderer").text.replace('\n', '').replace(' ', '')
        else:
            duration = '00:00'
        views = 0
        full_label = div.find("a", "yt-simple-endpoint style-scope ytd-grid-video-renderer")['aria-label']
        views = full_label[len(full_label)-(full_label[::-1].find(' ', full_label.find('sweiv ')+7)):]
        age = 0
        age = div.find_all("span", "style-scope ytd-grid-video-renderer")[1].text
    except:
        print("Something got skipped. Don't worry about it. It probably wasn't important anyway.")
        pass
    return Video(video_id, link, title, duration, views, age)

def download_page(page_url):
    print("Downloading page...")
    try:
        global driver
        driver = webdriver.Chrome(ChromeDriverManager().install())
        time.sleep(1)
        #wait = WebDriverWait(driver, 8)
        driver.get(page_url)
        time.sleep(3)
        lastHeight = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            newHeight = driver.execute_script("return document.documentElement.scrollHeight")
            if newHeight == lastHeight:
                print("Page fully developed.")
                break
            lastHeight = newHeight
    except (KeyboardInterrupt, SystemExit):
        print("Program Stopped")
        raise
    except Exception as e:
        print(e)
        print("Some kind of exception occurred. You should probably try again.")
        pass
    return driver.page_source.encode('utf-8')

def request_until_succeed(url):
	req = urllib.request.Request(url)
	success = False
	while success is False:
		try:
			response = urllib.request.urlopen(req)
			if response.getcode() == 200:
				success = True
		except Exception as e:
			print(e)
			print("Error for URL {}: {}".format(url, datetime.datetime.now()))
			print("retrying.")
			time.sleep(5)
	return response.read().decode('utf-8')

def scrape_videos(page_url):
    if page_url.find("channel") > 0:
        youtube_name = page_url[page_url.find("channel")+8:page_url.find("videos")-1]
    else:
        youtube_name = page_url.replace('https://www.youtube.com','').replace('/c/','').replace('/channel/','').replace('/videos','')
    folder_path = str(Path.home() / "Downloads")
    with open ('{}\\{}_YouTube.csv'.format(folder_path, youtube_name), 'w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(["Video Id","Watch URL","Title","Video Length","View Count","Age","Thumbnail URL",
            "Description","Published","Tags","Comment Count","Like Count","Dislike Count"])
        scrape_starttime = datetime.datetime.now()
        print("Scraping {} Youtube: {} \n Pay attention to the messages below.".format(youtube_name, scrape_starttime))
        videos = get_videos(page_url)
        num_processed = 0
        num_errors = 0
        for video in videos:
            attempts = 0
            while attempts < 3:
                try:
                    video_url = video[1]
                    page_source = request_until_succeed(video_url)
                    page = BeautifulSoup(page_source, 'html.parser')
                    image_url = page.find("meta", property="og:image")["content"]
                    description = page.find("meta", property="og:description")["content"]
                    published = page.find("meta", itemprop="datePublished")["content"]     
                    tags = page.find("meta", {"name": "keywords"})["content"].replace(",",";")

                    # comments
                    json_string=page.find('script',string=re.compile('ytInitialData'))
                    
                    
                    # comment_count = ""
                    # for c in comment_section.findChildren():
                    #     comment_count += c

                    # comment_count = header_section.find("span", "style-scope yt-formatted-string").text.replace(",", "")
                    
                    # video_divs = page.find_all("div", "style-scope ytd-grid-video-renderer")
                    # num_video_divs = len(video_divs)
                    # full_video_divs = []
                    # for i in range(num_video_divs):
                    #     if i % 11 == 0:
                    #         full_video_divs.append(video_divs[i])
                    # return [parse_video_div(div) for div in full_video_divs]

                   # comment_count = ""
                    like_count = "20"
                    dislike_count = "1"    

                    video = video + (image_url, description, published, tags, comment_count, like_count, dislike_count)
                    csv.writer(file).writerow(video)
                    num_processed += 1
                    if num_processed % 100 == 0:
                        print("{} videos processed: {}".format(num_processed, datetime.datetime.now()))
                except Exception as e:
                    print(e)
                    print(video[1])
                    print("Error retrieving data for this video. Retrying")
                    attempts += 1
                    num_errors += 1
                    continue
                except (KeyboardInterrupt, SystemExit):
                    print("Program Stopped")
                    raise
                break

            # page = BeautifulSoup(page_source, 'html.parser')
            # #likes = json.loads(page.find("button", "style-scope yt-icon-button").text.replace(",",""))
            # # likebutton = page.find(attrs={"class": "like-button-renderer-like-button"})
            # # #likes = likebutton.span.text
            # # likes = page.find("yt-formatted-string", class="style-scope ytd-toggle-button-renderer style-default-active")["aria-label"]
            # # # dislikebutton = page.find(attrs={"class": "like-button-renderer-dislike-button"})
            # # # dislikes = dislikebutton.span.text
            # # #dislikes = json.loads(page.find("button", "style-scope yt-icon-button").text.replace(",",""))
            # # published = page.find("strong", "watch-time-text").text
            # # video = video + (published,)
    file.close()
    print("Done! {} videos scraped in {}".format(len(videos), datetime.datetime.now() - scrape_starttime))
    print("{} errors.".format(num_errors))

def __main__():
    videos = scrape_videos("https://www.youtube.com/c/OrdinaryThings/videos")

if __name__ == "__main__":
    __main__()