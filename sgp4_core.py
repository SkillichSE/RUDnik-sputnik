import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timezone, timedelta
from math import atan2, sqrt, degrees, sin, cos

def gmst_from_jd(jd):
    T = (jd - 2451545.0) / 36525.0
    gmst_sec = (
        67310.54841
        + (876600 * 3600 + 8640184.812866) * T
        + 0.093104 * T**2
        - 6.2e-6 * T**3
    )
    return (gmst_sec % 86400) * (2 * np.pi / 86400)

def teme_to_ecef(r, jd):
    theta = gmst_from_jd(jd)
    R = np.array([
        [ cos(theta),  sin(theta), 0],
        [-sin(theta),  cos(theta), 0],
        [ 0,           0,          1]
    ])
    return R @ r

def ecef_to_latlon(r):
    x, y, z = r
    lon = atan2(y, x)
    lat = atan2(z, sqrt(x*x + y*y))
    return degrees(lat), degrees(lon)

def simulate(tle1, tle2, start_time, hours=1, step_min=10):
    sat = Satrec.twoline2rv(tle1, tle2)
    result = []

    t = start_time
    end = t + timedelta(hours=hours)

    while t <= end:
        jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
        err, r, _ = sat.sgp4(jd, fr)

        if err == 0:
            r = np.array(r)
            r_ecef = teme_to_ecef(r, jd + fr)
            lat, lon = ecef_to_latlon(r_ecef)
            rad = np.linalg.norm(r)

            result.append((t, lat, lon, rad))

        t += timedelta(minutes=step_min)

    return result
