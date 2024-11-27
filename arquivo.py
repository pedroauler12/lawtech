from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

chrome_driver_path = os.getenv("chrome_path")
service = Service(chrome_driver_path)
options = Options()
options.add_argument("--start-maximized") 


driver = webdriver.Chrome(service=service, options=options)

url = 'https://www.youtube.com/@JohnWatsonRooney/videos'

driver.get(url)

#div id="content" class="style-scope ytd-rich-item-renderer
#id="dismissible" class="style-scope ytd-rich-grid-media

videos = driver.find_elements(By.CLASS_NAME, "style-scope ytd-rich-grid-media")

video_list = []


for video in videos:
    title = video.find_element(By.XPATH, ".//*[@id='video-title']")
    views = video.find_element(By.XPATH, ".//*[@id='metadata-line']/span[1]").text
    when = video.find_element(By.XPATH, ".//*[@id='metadata-line']/span[2]").text
    print(f'Título: {title.text}\nViews: {views}\nQuando: {when}\n\n')
    
    vid_list = {
        'title': title.text,
        'views': views,
        'posted': when
    }
    
    video_list.append(vid_list)

df = pd.DataFrame(video_list)
print(df)
