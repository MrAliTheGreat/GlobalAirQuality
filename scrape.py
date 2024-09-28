from dotenv import load_dotenv
import os
import json

load_dotenv()


with open(os.environ.get("source_path"), mode = "r", encoding = "utf-8") as source:
    data = json.load(source)
    for city in data["cities"]:
        print(city["name"])
