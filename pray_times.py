#!/bin/python3 python
# compatible with python 3.x

import math
import re

"""
--------------------- Copyright Block ----------------------

praytimes.py: Prayer Times Calculator (ver 2.4)
Copyright (C) 2007-2025 PrayTimes.org

Python Code: Saleem Shafi, Hamid Zarrabi-Zadeh, Mohammad Rahimi
Original js Code: Hamid Zarrabi-Zadeh

License: GNU LGPL v3.0

TERMS OF USE:
	Permission is granted to use this code, with or
	without modification, in any website or application
	provided that credit is given to the original work
	with a link back to PrayTimes.org.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY.

PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.


--------------------- Help and Manual ----------------------

User's Manual:
http://praytimes.org/manual

Calculation Formulas:
http://praytimes.org/calculation

Github Repo:
https://gitbub.com/zamoosh/pray_times/


------------------------ User Interface -------------------------

	get_times (date, coordinates, timeZone [, dst [, timeFormat]])

	set_method (method)       // set calculation method
	adjust (parameters)      // adjust calculation parameters
	tune (offsets)           // tune times by given offsets

	get_method ()             // get calculation method
	get_setting ()            // get current calculation parameters
	get_offsets ()            // get current time offsets


------------------------- Sample Usage --------------------------

	>>> PT = PrayTimes('Tehran')
	>>> times = PT.get_times((2024, 12, 22), (50, 34), 3.5)
	>>> times['sunrise']
	07:26
	
"""


# ----------------------- PrayTimes Class ------------------------


class PrayTimes:
    # === TIME NAMES === #
    TIME_NAMES = {
        "imsak": "Imsak",
        "fajr": "Fajr",
        "sunrise": "Sunrise",
        "dhuhr": "Dhuhr",
        "asr": "Asr",
        "sunset": "Sunset",
        "maghrib": "Maghrib",
        "isha": "Isha",
        "midnight": "Midnight",
    }

    # === CALCULATION METHOD === #
    METHODS = {
        "MWL": {
            "name": "Muslim World League",
            "params": {"fajr": 18, "isha": 17},
        },
        "ISNA": {
            "name": "Islamic Society of North America",
            "params": {"fajr": 15, "isha": 15},
        },
        "Egypt": {
            "name": "Egyptian General Authority of Survey",
            "params": {"fajr": 19.5, "isha": 17.5},
        },
        "Makkah": {
            "name": "Umm Al-Qura University, Makkah",
            "params": {"fajr": 18.5, "isha": "90 min"},
        },  # fajr was 19 degrees before 1430 hijri
        "Karachi": {
            "name": "University of Islamic Sciences, Karachi",
            "params": {"fajr": 18, "isha": 18},
        },
        "Tehran": {
            "name": "Institute of Geophysics, University of Tehran",
            "params": {"fajr": 17.7, "isha": 14, "maghrib": 4.5, "midnight": "Jafari"},
        },  # isha is not explicitly specified in this method
        "Jafari": {
            "name": "Shia Ithna-Ashari, Leva Institute, Qom",
            "params": {"fajr": 16, "isha": 14, "maghrib": 4, "midnight": "Jafari"},
        },
    }

    # === DEFAULT PARAMETERS IN CALCULATION METHODS === #
    DEFAULT_PARAMS = {
        "maghrib": "0 min",
        "midnight": "Standard",
    }

    # ---------------------- Default Settings --------------------

    CALC_METHOD = "Tehran"

    # do not change anything here; use adjust method instead
    SETTINGS = {
        "imsak": "10 min",
        "dhuhr": "0 min",
        "asr": "Standard",
        "highLats": "NightMiddle",
    }

    TIME_FORMAT = "24h"
    TIME_SUFFIXES = ["am", "pm"]
    INVALID_TIME = "-----"

    numIterations = 1
    offset = {}

    # ---------------------- Initialization -----------------------

    def __init__(self, calc_method="MWL"):

        # set methods defaults
        self.j_date = None
        self.time_zone = None
        self.elv = None
        self.lng = None
        self.lat = None
        for method, config in self.METHODS.items():
            for name, value in self.DEFAULT_PARAMS.items():
                if not name in config["params"] or config["params"][name] is None:
                    config["params"][name] = value

        # initialize settings
        self.CALC_METHOD = calc_method if calc_method in self.METHODS else "MWL"
        params = self.METHODS[self.CALC_METHOD]["params"]
        for name, value in params.items():
            self.SETTINGS[name] = value

        # init time offsets
        for name in self.TIME_NAMES:
            self.offset[name] = 0

    # -------------------- Interface Functions --------------------

    def set_method(self, method):
        if method in self.METHODS:
            self.adjust(self.METHODS[method]["params"])
            self.CALC_METHOD = method

    def adjust(self, params: dict):
        self.SETTINGS.update(params)

    def get_method(self):
        return self.CALC_METHOD

    def get_settings(self) -> dict[str, str]:
        return self.SETTINGS

    def get_offsets(self):
        return self.offset

    def get_defaults(self):
        return self.METHODS

    # return prayer times for a given date
    def get_times(self, date, coords, timezone, dst=0, format=None):
        self.lat = coords[0]
        self.lng = coords[1]
        self.elv = coords[2] if len(coords) > 2 else 0
        if format != None:
            self.TIME_FORMAT = format
        if type(date).__name__ == "date":
            date = (date.year, date.month, date.day)
        self.time_zone = timezone + (1 if dst else 0)
        self.j_date = self.julian(date[0], date[1], date[2]) - self.lng / (15 * 24.0)
        return self.compute_times()

    # convert float time to the given format (see timeFormats)
    def get_formatted_time(self, time, format, suffixes=None):
        if math.isnan(time):
            return self.INVALID_TIME
        if format == "Float":
            return time
        if suffixes == None:
            suffixes = self.TIME_SUFFIXES

        time = self.fix_hour(time + 0.5 / 60)  # add 0.5 minutes to round
        hours = math.floor(time)

        minutes = math.floor((time - hours) * 60)
        suffix = suffixes[0 if hours < 12 else 1] if format == "12h" else ""
        formatted_time = (
            "%02d:%02d" % (hours, minutes)
            if format == "24h"
            else "%d:%02d" % ((hours + 11) % 12 + 1, minutes)
        )
        return formatted_time + suffix

    # ---------------------- Calculation Functions -----------------------

    # compute midday time
    def midday(self, time):
        eqt = self.sun_position(self.j_date + time)[1]
        return self.fix_hour(12 - eqt)

    # compute the time at which sun reaches a specific angle below horizon
    def sun_angle_time(self, angle, time, direction=None):
        try:
            decl = self.sun_position(self.j_date + time)[0]
            noon = self.midday(time)
            t = (
                    1
                    / 15.0
                    * self.arccos(
                (-self.sin(angle) - self.sin(decl) * self.sin(self.lat))
                / (self.cos(decl) * self.cos(self.lat))
            )
            )
            return noon + (-t if direction == "ccw" else t)
        except ValueError:
            return float("nan")

    # compute asr time
    def asr_time(self, factor, time):
        decl = self.sun_position(self.j_date + time)[0]
        angle = -self.arccot(factor + self.tan(abs(self.lat - decl)))
        return self.sun_angle_time(angle, time)

    # compute declination angle of sun and equation of time
    # Ref: http://aa.usno.navy.mil/faq/docs/SunApprox.php
    def sun_position(self, jd):
        D = jd - 2451545.0
        g = self.fix_angle(357.529 + 0.98560028 * D)
        q = self.fix_angle(280.459 + 0.98564736 * D)
        L = self.fix_angle(q + 1.915 * self.sin(g) + 0.020 * self.sin(2 * g))

        R = 1.00014 - 0.01671 * self.cos(g) - 0.00014 * self.cos(2 * g)
        e = 23.439 - 0.00000036 * D

        RA = self.arctan2(self.cos(e) * self.sin(L), self.cos(L)) / 15.0
        eqt = q / 15.0 - self.fix_hour(RA)
        decl = self.arcsin(self.sin(e) * self.sin(L))

        return (decl, eqt)

    # convert Gregorian date to Julian day
    # Ref: Astronomical Algorithms by Jean Meeus
    @staticmethod
    def julian(year, month, day):
        if month <= 2:
            year -= 1
            month += 12
        A = math.floor(year / 100)
        B = 2 - A + math.floor(A / 4)
        return (
                math.floor(365.25 * (year + 4716))
                + math.floor(30.6001 * (month + 1))
                + day
                + B
                - 1524.5
        )

    # ---------------------- Compute Prayer Times -----------------------

    # compute prayer times at given julian date
    def compute_prayer_times(self, times):
        times = self.day_portion(times)
        params = self.SETTINGS

        imsak = self.sun_angle_time(self.eval(params["imsak"]), times["imsak"], "ccw")
        fajr = self.sun_angle_time(self.eval(params["fajr"]), times["fajr"], "ccw")
        sunrise = self.sun_angle_time(
            self.rise_set_angle(self.elv), times["sunrise"], "ccw"
        )
        dhuhr = self.midday(times["dhuhr"])
        asr = self.asr_time(self.asr_factor(params["asr"]), times["asr"])
        sunset = self.sun_angle_time(self.rise_set_angle(self.elv), times["sunset"])
        maghrib = self.sun_angle_time(self.eval(params["maghrib"]), times["maghrib"])
        isha = self.sun_angle_time(self.eval(params["isha"]), times["isha"])
        return {
            "imsak": imsak,
            "fajr": fajr,
            "sunrise": sunrise,
            "dhuhr": dhuhr,
            "asr": asr,
            "sunset": sunset,
            "maghrib": maghrib,
            "isha": isha,
        }

    # compute prayer times
    def compute_times(self):
        times = {
            "imsak": 5,
            "fajr": 5,
            "sunrise": 6,
            "dhuhr": 12,
            "asr": 13,
            "sunset": 18,
            "maghrib": 18,
            "isha": 18,
        }
        # main iterations
        for i in range(self.numIterations):
            times = self.compute_prayer_times(times)
        times = self.adjust_times(times)
        # add midnight time
        if self.SETTINGS["midnight"] == "Jafari":
            times["midnight"] = (
                    times["sunset"] + self.time_diff(times["sunset"], times["fajr"]) / 2
            )
        else:
            times["midnight"] = (
                    times["sunset"] + self.time_diff(times["sunset"], times["sunrise"]) / 2
            )

        times = self.tune_times(times)
        return self.modify_formats(times)

    # adjust times in a prayer time array
    def adjust_times(self, times):
        params = self.SETTINGS
        tzAdjust = self.time_zone - self.lng / 15.0
        for t, v in times.items():
            times[t] += tzAdjust

        if params["highLats"] != "None":
            times = self.adjust_high_lats(times)

        if self.is_min(params["imsak"]):
            times["imsak"] = times["fajr"] - self.eval(params["imsak"]) / 60.0
        # need to ask about 'min' settings
        if self.is_min(params["maghrib"]):
            times["maghrib"] = times["sunset"] - self.eval(params["maghrib"]) / 60.0

        if self.is_min(params["isha"]):
            times["isha"] = times["maghrib"] - self.eval(params["isha"]) / 60.0
        times["dhuhr"] += self.eval(params["dhuhr"]) / 60.0

        return times

    # get asr shadow factor
    def asr_factor(self, asr_param):
        methods = {"Standard": 1, "Hanafi": 2}
        return methods[asr_param] if asr_param in methods else self.eval(asr_param)

    # return sun angle for sunset/sunrise
    @staticmethod
    def rise_set_angle(elevation=0):
        elevation = 0 if elevation is None else elevation
        return 0.833 + 0.0347 * math.sqrt(elevation)  # an approximation

    # apply offsets to the times
    def tune_times(self, times):
        for name, value in times.items():
            times[name] += self.offset[name] / 60.0
        return times

    # convert times to given time format
    def modify_formats(self, times):
        for name, value in times.items():
            times[name] = self.get_formatted_time(times[name], self.TIME_FORMAT)
        return times

    # adjust times for locations in higher latitudes
    def adjust_high_lats(self, times):
        params = self.SETTINGS
        night_time = self.time_diff(
            times["sunset"], times["sunrise"]
        )  # sunset to sunrise
        times["imsak"] = self.adjust_high_lat_time(
            times["imsak"],
            times["sunrise"],
            self.eval(params["imsak"]),
            night_time,
            "ccw",
        )
        times["fajr"] = self.adjust_high_lat_time(
            times["fajr"], times["sunrise"], self.eval(params["fajr"]), night_time, "ccw"
        )
        times["isha"] = self.adjust_high_lat_time(
            times["isha"], times["sunset"], self.eval(params["isha"]), night_time
        )
        times["maghrib"] = self.adjust_high_lat_time(
            times["maghrib"], times["sunset"], self.eval(params["maghrib"]), night_time
        )
        return times

    # adjust a time for higher latitudes
    def adjust_high_lat_time(self, time, base, angle, night, direction=None):
        portion = self.night_portion(angle, night)
        diff = (
            self.time_diff(time, base)
            if direction == "ccw"
            else self.time_diff(base, time)
        )
        if math.isnan(time) or diff > portion:
            time = base + (-portion if direction == "ccw" else portion)
        return time

    # the night portion used for adjusting times in higher latitudes
    def night_portion(self, angle, night):
        method = self.SETTINGS["highLats"]
        portion = 1 / 2.0  # midnight
        if method == "AngleBased":
            portion = 1 / 60.0 * angle
        if method == "OneSeventh":
            portion = 1 / 7.0
        return portion * night

    # convert hours to day portions
    @staticmethod
    def day_portion(times):
        for i in times:
            times[i] /= 24.0
        return times

    # ---------------------- Misc Functions -----------------------

    # compute the difference between two times
    def time_diff(self, time1, time2):
        return self.fix_hour(time2 - time1)

    # convert given string into a number
    @staticmethod
    def eval(st):
        val = re.split("[^0-9.+-]", str(st), 1)[0]
        return float(val) if val else 0

    # detect if input contains 'min'
    @staticmethod
    def is_min(arg):
        return isinstance(arg, str) and arg.find("min") > -1

    # ----------------- Degree-Based Math Functions -------------------

    @staticmethod
    def sin(d):
        return math.sin(math.radians(d))

    @staticmethod
    def cos(d):
        return math.cos(math.radians(d))

    @staticmethod
    def tan(d):
        return math.tan(math.radians(d))

    @staticmethod
    def arcsin(x):
        return math.degrees(math.asin(x))

    @staticmethod
    def arccos(x):
        return math.degrees(math.acos(x))

    @staticmethod
    def arctan(x):
        return math.degrees(math.atan(x))

    @staticmethod
    def arccot(x):
        return math.degrees(math.atan(1.0 / x))

    @staticmethod
    def arctan2(y, x):
        return math.degrees(math.atan2(y, x))

    def fix_angle(self, angle):
        return self.fix(angle, 360.0)

    def fix_hour(self, hour):
        return self.fix(hour, 24.0)

    @staticmethod
    def fix(a, mode):
        if math.isnan(a):
            return a
        a = a - mode * (math.floor(a / mode))
        return a + mode if a < 0 else a
