import json
import requests
# Загружаем TLE-данные
url = "https://celestrak.org/NORAD/elements/gp.php?SPECIAL=gpz&FORMAT=tle"
#  "https://celestrak.org/NORAD/elements/debris.txt"
data = requests.get(url).text.splitlines()
with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file)
print("---")
