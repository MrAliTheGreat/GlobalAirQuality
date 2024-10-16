from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time, datetime, signal

from dotenv import load_dotenv
from random import randint
import os, json
import pandas as pd

load_dotenv()


def timeoutHandler(signum, frame):
    print(f"{datetime.datetime.now()}: ! Link froze - reloading!")
    raise TimeoutException

def resetBrowser(chrome, options, pageLoadTimeOut = 20):
    chrome.close()
    chrome = webdriver.Chrome(
        service = Service(os.environ.get("chromedriver_path")),
        options = options
    )
    chrome.set_page_load_timeout(pageLoadTimeOut)
    chrome.implicitly_wait(7)
    return chrome

def waitForVideoPlayerEC(chrome: WebDriver):
    adLen = 60

    # Wait for video player to show up
    videoPlayer = WebDriverWait(chrome, 20).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, "div[id='videoPlayer']"
        ))
    )

    try:
        # Wait for possible ad to show up
        WebDriverWait(chrome, 10).until(
            lambda _: "vjs-ad-playing" in videoPlayer.get_attribute("class")
        )
        # Wait for ad to finish
        WebDriverWait(chrome, adLen).until(
            lambda _: "vjs-live" in videoPlayer.get_attribute("class") and "vjs-playing" in videoPlayer.get_attribute("class")
        )
    except TimeoutException:
        pass

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

def captureImageEC(chrome: WebDriver, link, path, options):
    while(True):
        try:
            chrome.get(link)
        except TimeoutException:
            print(f"{datetime.datetime.now()}: ! timeout in EC - waiting & reloading!")
            time.sleep(randint(1, 3) * 60)
            chrome = resetBrowser(chrome, options)
            continue
        else:
            break
    
    waitForVideoPlayerEC(chrome)
    time.sleep(2)
    removeCamInfoEC(chrome)
    removeLogoEC(chrome)
    time.sleep(5)   # Top left live logo disappers!
    screenshotEC(chrome, path)
    print(f"{datetime.datetime.now()}: {path} created")
    return chrome

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
    try:
        chrome.get(link)
    except TimeoutException:
        pass

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

def fetchAQI(chrome: WebDriver, link, options):
    info = {
        "AQI": "",
        "AQI-PM2.5": "",
        "AQI-PM10": "",
        "AQI-NO2": "",
        "AQI-O3": "",
        "Amount-PM2.5": "",
        "Amount-PM10": "",
        "Amount-NO2": "",
        "Amount-O3": "",
    }
    
    while(True):
        try:            
            chrome.get(link)
            
            info["AQI"] = WebDriverWait(chrome, 20).until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR, "div[class='report__pi-number']"
                ))
            ).find_element(
                By.CSS_SELECTOR, "span[data-role='current-pi']"
            ).text

            aqi, pollutants = WebDriverWait(chrome, 20).until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR, "div[class='pollutants-desktop']"
                ))
            ).find_elements(
                By.CSS_SELECTOR, "ul[class=pollutants-desktop__list]"
            )            
        except TimeoutException:
            print(f"{datetime.datetime.now()}: ! timeout in AQI - waiting & reloading!")
            time.sleep(randint(1, 3) * 60)
            chrome = resetBrowser(chrome, options)
            continue
        else:
            break

    for val in aqi.text.split("\n"):
        val = val.strip()
        if(("AQI-" + val) in info.keys()):
            info["AQI-" + val] = prev
        else:
            prev = val

    for val in pollutants.text.split("\n"):
        val = val.strip()
        if(("Amount-" + val) in info.keys()):
            info["Amount-" + val] = prev
        else:
            prev = val

    return info, chrome

def writeTabular(city, filenames, weather, aqi, path = "./dataset/tabular/"):
    if(not os.path.isdir(path)):
        os.makedirs(path)

    info = {**weather, **aqi}
    for filename in filenames:
        info["Filename"] = filename
        if(not os.path.exists(path + f"{city}.csv")):
            pd.DataFrame(columns = list(info.keys())).to_csv(path + f"{city}.csv" , index = False, header = True)
        pd.DataFrame(info , index = [0]).to_csv(path + f"{city}.csv", mode = "a", index = False, header = False)
    print(f"{datetime.datetime.now()}: {path + city}.csv updated - {len(filenames)} new")



options = Options()
# options.add_argument('--headless=new')
# options.add_argument("--user-agent=Chrome/121.0.6105.0")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1080,1920")

startTime = time.time()
waitPeriodInMinutes = 60

signal.signal(signal.SIGALRM, timeoutHandler)
alarmLenInMinutes = 5

while(True):
    print(f"{datetime.datetime.now()}: cycle started!")
    
    chrome = webdriver.Chrome(service = Service(os.environ.get("chromedriver_path")), options = options)
    chrome.set_page_load_timeout(20)
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

                    signal.alarm(alarmLenInMinutes * 60)
                    try:
                        chrome = captureImageEC(chrome, link, cityPath + imgFilename, options)
                    except TimeoutException:
                        chrome = resetBrowser(chrome, options)
                        chrome = captureImageEC(chrome, link, cityPath + imgFilename, options)
                    else:
                        signal.alarm(0)
                
                signal.alarm(alarmLenInMinutes * 60)
                try:
                    infoWeather = fetchWeather(chrome, city["weather"])
                    infoAQI, chrome = fetchAQI(chrome, city["aqi"], options)
                    writeTabular(city = city["name"], filenames = imgFilenames, weather = infoWeather, aqi = infoAQI)
                except TimeoutException:
                    chrome = resetBrowser(chrome, options)
                    infoWeather = fetchWeather(chrome, city["weather"])
                    infoAQI, chrome = fetchAQI(chrome, city["aqi"], options)                    
                    writeTabular(city = city["name"], filenames = imgFilenames, weather = infoWeather, aqi = infoAQI)
                else:
                    signal.alarm(0)

    chrome.close()
    print(f"{datetime.datetime.now()}: cycle finished!")
    time.sleep( (waitPeriodInMinutes * 60.0) - ((time.time() - startTime) % (waitPeriodInMinutes * 60.0)) )
