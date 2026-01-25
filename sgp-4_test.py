import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
from math import sin, cos, atan2, sqrt, degrees
import time

# GMST (вращение Земли)

def gmst_from_jd(jd):
    T = (jd - 2451545.0) / 36525.0
    gmst_sec = (
        67310.54841
        + (876600 * 3600 + 8640184.812866) * T
        + 0.093104 * T**2
        - 6.2e-6 * T**3
    )
    gmst_rad = (gmst_sec % 86400.0) * (2 * np.pi / 86400.0)
    return gmst_rad


# TEME → ECEF

def teme_to_ecef(r_teme, jd):
    theta = gmst_from_jd(jd)

    R = np.array([
        [ cos(theta),  sin(theta), 0],
        [-sin(theta),  cos(theta), 0],
        [ 0,           0,          1]
    ])

    return R @ r_teme


# ECEF → географические координаты

def ecef_to_latlon(r_ecef):
    x, y, z = r_ecef

    lon = atan2(y, x)
    lat = atan2(z, sqrt(x**2 + y**2))

    return degrees(lat), degrees(lon)


# TLE геостационарного спутника


#tle_line1 ="1 38740U 12038A   24016.50000000  .00000025  00000-0  00000+0 0  9993"
#tle_line2 ="2 38740   0.0162  85.8234 0001812  96.2034 219.8264  1.00270000"
tle_line1 ="1 00634U 63031A   26022.80567956 -.00000086  00000+0  00000+0 0  9997"
tle_line2 ="2 00634  30.2947 302.5085 0006034 210.5743 336.0747  1.00251118228908"
sat = Satrec.twoline2rv(tle_line1, tle_line2)

#din tle:
import re

def parse_tle_line(line: str):
    """
    Разбирает строку TLE в массив токенов.
    Возвращает два массива:
      - tokens      -> массив токенов (пробелы и числа)
      - numbers_list -> массив всех числовых токенов по порядку
    """
    tokens = []
    numbers_list = []
    pattern = re.compile(r'\s+|[+-]?\d+(?:\.\d+)?')
    number_index = 0

    for m in pattern.finditer(line):
        text = m.group()

        if text.isspace():
            tokens.append(text)
        else:
            value = float(text) if "." in text else int(text)
            token = [value, text, number_index]
            tokens.append(token)
            numbers_list.append(token)  # добавляем в массив чисел по индексу
            number_index += 1

    return tokens, numbers_list


def update_number(token, new_value):
    """
    Обновляет значение числового токена,
    сохраняя исходный формат записи.
    """
    old_text = token[1]

    if "." in old_text:
        decimals = len(old_text.split(".")[1])
        token[1] = f"{new_value:.{decimals}f}"
        token[0] = float(new_value)
    else:
        width = len(old_text)
        token[1] = f"{int(new_value):0{width}d}"
        token[0] = int(new_value)


def build_tle_line(tokens):
    """
    Собирает строку обратно из массива токенов.
    Пробелы и формат чисел сохраняются полностью.
    """
    return "".join(
        t if isinstance(t, str) else t[1]
        for t in tokens
    )


import json
def dataset_sat(number_sat):
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    tle_text=[]
    tle_num=0
    DO_NOT_OPEN=data
    line_1=line_2=""
    line_0=""
    for i in range(number_sat, number_sat+3):
        if tle_num==0:
            line_0=DO_NOT_OPEN[i]
        if tle_num==1:
            line_1=DO_NOT_OPEN[i]
        if tle_num==2:
            line_2=DO_NOT_OPEN[i]
        tle_text.append(DO_NOT_OPEN[i])
        tle_num=tle_num+1
    return(line_0, line_1, line_2)
number_sat=(int(input("NUMBER: "))-1)*3
line0, line1, line2=dataset_sat(number_sat)

tokens, numbers_list = parse_tle_line(line2)
print(line0)
print(line1)
print(line2)
# Теперь числа доступны напрямую по индексу в numbers_list
# Например, inclination = 2-й числовой токен (индекс 2)
# update_number(numbers_list[2], 52.0001)
#=========================================================
#вторая строка третье значение- наклонение орбиты line_2[2]
#вторая строка четвертое значение- долгота восходящего угла line_2[3]
#вторая строка пятое значение- эксцентриситет(числовая характеристика, определяющая форму орбиты и степень ее отличия от идеальной окружности, в идеале 0) line_2[4]
#вторая строка шестое значение- аргумент перигея(градус ближайшей точки орбиты к земле) line_2[5]
#вторая строка седьмое значение- средняя аномалия(угловая мера положения небесного тела на орбите, показывающая, сколько времени прошло с момента прохождения им перицентра) line_2[6]
#вторая строка восьмое значение- среднее движение(обороты в сутки) line_2[7]
Inclination=float(input("DELTA Inclination: ")) #Наклонение орбиты (в градусах).
RAAN=float(input("DELTA RAAN: ")) #Долгота восходящего узла (в градусах).
Eccentricity=float(input("DELTA Eccentricity: "))#Эксцентриситет орбиты.
Argument_of_Perigee=float(input("DELTA Argument_of_Perigee: "))#Аргумент перигея (в градусах).
#Mean_Anomaly=float(input("DELTA Mean_Anomaly: "))#Средняя аномалия (в градусах).
Mean_Motion=float(input("DELTA Mean_Motion: "))#Среднее число оборотов в сутки (витки/день).
#===============================
update_number(numbers_list[2], numbers_list[2][0]+Inclination)
update_number(numbers_list[3], numbers_list[3][0]+RAAN)
update_number(numbers_list[4], numbers_list[4][0]+Eccentricity)
update_number(numbers_list[5], numbers_list[5][0]+Argument_of_Perigee)
#update_number(numbers_list[6], numbers_list[6][0]+Mean_Anomaly)
update_number(numbers_list[7], numbers_list[7][0]+Mean_Motion)
# Собираем строку обратно
restored = build_tle_line(tokens)
#print(numbers_list)
print(line0)#название
print(line1)#первая строка
print(restored)#вторая строка
print("==================================================")
tle_line0, tle_line1, tle_line2=dataset_sat(number_sat)
tle_line0=line0
tle_line1=line1
tle_line2=restored

sat = Satrec.twoline2rv(tle_line1, tle_line2)
def time_now():
    import time
    from datetime import datetime
    date=time.ctime(time.time())
    date=list(map(str, date.split()))
    now = datetime.now()
    today=str(now.date())
    hours, minutes, seconds=[int(x) for x in date[3].split(":")]
    year, month, day=[int(x) for x in today.split("-")]
    return(year, month, day, hours, minutes, seconds)
year, month, day, hours, minutes, seconds=time_now()
start_time=datetime(year, month, day, hours, minutes, seconds)   #реальное время
#start_time = datetime(2024, 1, 16, 0, 0, 0) #фиксированное время
duration_hours = 24  #длительность суток
step_minutes = float(input("step_minutes: "))


# ============================================================
# Симуляция
# ============================================================
print("TLE: ")
print(tle_line0)
print(tle_line1)
print(tle_line2)
print("-" * 80)
print(f"{'UTC':>20} | {'X_TEME km':>10} {'Y_TEME km':>10} {'Z_TEME km':>10} | {'Lat °':>7} {'Lon °':>7}")
print("-" * 80)

current_time = start_time
while current_time <= start_time + timedelta(hours=duration_hours):

    jd, fr = jday(
        current_time.year,
        current_time.month,
        current_time.day,
        current_time.hour,
        current_time.minute,
        current_time.second
    )

    error, r_teme, v = sat.sgp4(jd, fr)
    if error!=0:
        print("error: ", error)
    if error == 0:
        r_teme = np.array(r_teme)

        r_ecef = teme_to_ecef(r_teme, jd + fr)
        lat, lon = ecef_to_latlon(r_ecef)
        rad=(r_teme[0]**2+r_teme[1]**2+r_teme[2]**2)**0.5
        print(
            f"{current_time} | "
            f"{r_teme[0]:10.1f} {r_teme[1]:10.1f} {r_teme[2]:10.1f} | "
            f"{lat:7.2f} {lon:7.2f}"
            "    RAD: ", rad
        )

    current_time += timedelta(minutes=step_minutes)
