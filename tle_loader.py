import json
import requests

URL = "https://celestrak.org/NORAD/elements/gp.php?SPECIAL=gpz&FORMAT=tle"


def save_tle():
    data = requests.get(URL, timeout=10).text.splitlines()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f)


def dataset_sat(number_sat):
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    max_sat_index = (len(data) // 3) - 1
    if number_sat < 0 or number_sat > max_sat_index:
        raise IndexError(f"Satellite index out of range. Max allowed: {max_sat_index}")

    index = number_sat * 3
    return data[index], data[index + 1], data[index + 2]



def parse_tle_fields(line1, line2):
    return {
        "norad_id": line1[2:7].strip(),
        "designator": line1[9:17].strip(),
        "epoch": line1[18:32].strip(),
        "inclination": line2[8:16].strip(),
        "raan": line2[17:25].strip(),
        "eccentricity": line2[26:33].strip(),
        "perigee": line2[34:42].strip(),
        "mean_anomaly": line2[43:51].strip(),
        "mean_motion": line2[52:63].strip(),
        "ballistic": line1[53:61].strip(),
        "derivative2": line1[44:52].strip(),
        "pressure": line1[53:61].strip(),
        "ephemeris": line1[62:63].strip(),
        "element": line1[64:68].strip(),
        "revolution": line2[63:68].strip(),  # <-- правильное место
    }
