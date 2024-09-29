from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
import time

from dotenv import load_dotenv
import os
import json

load_dotenv()


def waitForVideoPlayerEC(chrome: WebDriver):
    adLen = 60

    # Wait for video player to show up
    videoPlayer = WebDriverWait(chrome, 20).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, "div[id='videoPlayer']"
        ))
    )
    # Wait for ad to finish
    WebDriverWait(chrome, adLen).until(
        lambda _: "vjs-live" in videoPlayer.get_attribute("class") and "vjs-playing" in videoPlayer.get_attribute("class") 
    )

def removeCamInfoEC(chrome: WebDriver):
    try:
        camInfoElement = WebDriverWait(chrome, 20).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div[class='display_camera_info_container']"
            ))
        )
        chrome.execute_script("arguments[0].style.display='none'", camInfoElement)
    except TimeoutException:
        pass

def removeLogoEC(chrome: WebDriver):
    try:
        logoElement = WebDriverWait(chrome, 20).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, "img[class='ecLogo']"
            ))
        )
        chrome.execute_script("arguments[0].style.display='none'", logoElement)
    except TimeoutException:
        pass

def screenshotEC(chrome: WebDriver, filename):
    chrome.find_element(
        By.CSS_SELECTOR, "video[id='videoPlayer_html5_api']"
    ).screenshot(filename)

def captureImageEC(chrome: WebDriver, link, path):
    chrome.get(link)
    waitForVideoPlayerEC(chrome)
    removeCamInfoEC(chrome)
    removeLogoEC(chrome)
    time.sleep(7)   # Top left live logo disappers!
    screenshotEC(chrome, path)


chrome = webdriver.Chrome(service = Service(os.environ.get("chromedriver_path")))
chrome.set_window_size(width = 1080, height = 1920)
chrome.implicitly_wait(7)

with open(os.environ.get("source_path"), mode = "r", encoding = "utf-8") as source:
    data = json.load(source)
    for city in data["cities"]:
        for link in city["images"]:
            if(city["name"] == "St. John's"):
                pass
            else:
                cityPath = f"./dataset/{city['name']}"
                if(not os.path.isdir(cityPath)):
                    os.makedirs(cityPath)
                captureImageEC(chrome, link, cityPath + f"/{len(os.listdir(cityPath)) + 1}.png")

chrome.close()