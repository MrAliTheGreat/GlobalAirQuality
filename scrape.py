from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
import time

from dotenv import load_dotenv
import os, json
import pandas as pd

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

def fetchLocalDate(chrome: WebDriver):
    return WebDriverWait(chrome, 20).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR, "div[class='content-module subnav-pagination']"
        ))
    ).find_element(
        By.TAG_NAME, "div"
    ).text

def fetchLocalTime(chrome: WebDriver):
    return chrome.find_element(
        By.CSS_SELECTOR, "div[class='card-header spaced-content']"
    ).find_element(
        By.TAG_NAME, "p"
    ).text

def fetchTemperature(chrome: WebDriver):
    return chrome.find_element(
        By.CSS_SELECTOR, "div[class='current-weather-info']"
    ).find_element(
        By.CSS_SELECTOR, "div[class='display-temp']"
    ).text[:-2]

def fetchRealFeel(chrome: WebDriver):
    return chrome.find_element(
        By.CSS_SELECTOR, "div[class='current-weather-extra no-realfeel-phrase']"
    ).find_element(
        By.TAG_NAME, "div"
    ).text.split(" ")[-1][:-1]

def fetchCurrentWeatherStatus(chrome: WebDriver):
    return chrome.find_element(
        By.CSS_SELECTOR, "div[class='phrase']"
    ).text

def fetchRemainingWeatherDetails(chrome: WebDriver, info):
    details = chrome.find_element(
        By.CSS_SELECTOR, "div[class='current-weather-details no-realfeel-phrase ']"
    ).find_elements(
        By.CSS_SELECTOR, "div[class='detail-item spaced-content']"
    )
    for detail in details:
        if(detail.text):
            tag, val = detail.text.split("\n")
            if(tag != "Max UV Index" and tag != "Wind"):
                if(tag == "Wind Gusts" or tag == "Visibility" or tag == "Cloud Ceiling"):
                    info[tag] = val.split(" ")[0]
                if(tag == "Indoor Humidity"):
                    h, status = val.split("(")
                    info["Indoor Humidity"] = int(h[:-2]) / 100
                    info["Humidity Status"] = status[:-1]
                if(tag == "Humidity" or tag == "Cloud Cover"):
                    info[tag] = int(val[:-1]) / 100
                if(tag == "Dew Point"):
                    info[tag] = val[:-3]
                if(tag == "Pressure"):
                    info["Pressure Direction"], info[tag], _ = val.split(" ")
    return info

def fetchWeather(chrome: WebDriver, link):
    chrome.get(link)
    info = {
        "Date": "",
        "Time": "",
        "Temperature": "",
        "Real Feel": "",
        "Weather Status": "",
        "Wind Gusts": "",
        "Humidity": "",
        "Indoor Humidity": "",
        "Humidity Status": "",
        "Dew Point": "",
        "Pressure": "",
        "Pressure Direction": "",
        "Cloud Cover": "",
        "Visibility": "",
        "Cloud Ceiling": ""
    }
    info["Date"] = fetchLocalDate(chrome)
    info["Time"] = fetchLocalTime(chrome)
    info["Temperature"]= fetchTemperature(chrome)
    info["Real Feel"] = fetchRealFeel(chrome)
    info["Weather Status"] = fetchCurrentWeatherStatus(chrome)
    return fetchRemainingWeatherDetails(chrome, info)

def fetchAQI(chrome: WebDriver, link):
    chrome.get(link)
    return WebDriverWait(chrome, 20).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, "div[class='report__pi-number']"
        ))
    ).find_element(
        By.TAG_NAME, "span"
    ).text

def writeTabular(city, filenames, weather, aqi, path = "./dataset/tabular/"):
    if(not os.path.isdir(path)):
        os.makedirs(path)    

    info = weather
    for filename in filenames:
        info["Filename"] = filename; info["AQI"] = aqi
        if(not os.path.exists(path + f"{city}.csv")):
            pd.DataFrame(columns = list(info.keys())).to_csv(path + f"{city}.csv" , index = False, header = True)
        pd.DataFrame(info , index = [0]).to_csv(path + f"{city}.csv", mode = "a", index = False, header = False)


chrome = webdriver.Chrome(service = Service(os.environ.get("chromedriver_path")))
chrome.set_window_size(width = 1080, height = 1920)
chrome.implicitly_wait(7)

with open(os.environ.get("source_path"), mode = "r", encoding = "utf-8") as source:
    data = json.load(source)
    for city in data["cities"]:
        if(city["name"] == "St. John's"):
            pass
        else:
            imgFilenames = []
            for link in city["images"]:
                cityPath = f"./dataset/{city['name']}/"
                if(not os.path.isdir(cityPath)):
                    os.makedirs(cityPath)
                imgFilename = f"{len(os.listdir(cityPath)) + 1}.png"
                imgFilenames.append(imgFilename)                
                captureImageEC(chrome, link, cityPath + imgFilename)
            writeTabular(
                city = city["name"],
                filenames = imgFilenames,
                weather = fetchWeather(chrome, city["weather"]),
                aqi = fetchAQI(chrome, city["aqi"])
            )

chrome.close()