# Prayer Times Calculator

This Python script calculates Islamic prayer times based on a user's location, the date, and a selected calculation method. Originally developed by Hamid Zarrabi-Zadeh, it was later adapted to Python by Saleem Shafi and Hamid Zarrabi-Zadeh.

---

## Features

- Calculates the times for Islamic prayers, including Fajr, Dhuhr, Asr, Maghrib, and Isha, for any geographic location.
- Supports multiple established calculation methods, such as MWL, ISNA, Umm Al-Qura, and Jafari.
- Includes settings tailored for high-latitude locations where the sun's behavior may vary significantly.
- Allows users to customize prayer time offsets.
- Offers output formats in both 12-hour and 24-hour clock styles.

---

## Requirements

To run this script, you will need:

- Python version 3.x or later.
- The built-in `math` and `re` modules, which come pre-installed with Python.

---

## How to Use

### 1. Initialize the `PrayTimes` Class

To begin, create an instance of the `PrayTimes` class, specifying your desired calculation method. For example:

```python
from praytimes import PrayTimes
PT = PrayTimes('MWL')
```

### 2. Calculate Prayer Times

To compute prayer times for a specific date and location, use the `get_times` method. This method requires the date, geographic coordinates (latitude, longitude, and optionally elevation), the time zone offset, daylight saving adjustment (if applicable), and the desired time format.

```python
from datetime import date

# Initialize PrayTimes
PT = PrayTimes('Tehran')

# Specify Coordinates (latitude, longitude)
coordinates = (34.641159, 50.877456)
timezone = 3.5  # Time zone offset from UTC

times = PT.get_times(date.today(), coordinates, timezone)
print(times)
```

**Example Output:**

```plaintext
{
  'imsak': '05:10',
  'fajr': '05:20',
  'sunrise': '06:50',
  'dhuhr': '12:15',
  'asr': '15:20',
  'sunset': '18:45',
  'maghrib': '18:55',
  'isha': '20:15',
  'midnight': '00:35'
}
```

---

## Key Methods and Functions

### `get_times(date, coordinates, timezone, dst=0, format=None)`

This method calculates prayer times for a given date and location.

- **`date`**: Accepts either a tuple `(year, month, day)` or a `datetime.date` object.
- **`coordinates`**: A tuple specifying `(latitude, longitude, [elevation])`.
- **`timezone`**: The time zone offset from UTC.
- **`dst`**: Optional daylight saving time adjustment (default is `0`).
- **`format`**: Optionally specify time output format (`12h` or `24h`).

### `set_method(method)`

This method sets the prayer time calculation method.

- Supported methods include `MWL`, `ISNA`, `Egypt`, `Makkah`, `Karachi`, `Tehran`, and `Jafari`.

### `adjust(parameters)`

Use this method to modify calculation parameters, such as those for Imsak or Maghrib.

### `tune(offsets)`

This function allows you to fine-tune computed prayer times by applying custom offsets in minutes.

### `get_method()` and `get_settings()`

These methods retrieve the currently selected calculation method and its associated parameters.

---

## Calculation Methods

Each supported method uses specific angle values to determine Fajr and Isha timings. For instance:

- **MWL (Muslim World League)**: Fajr at 18°, Isha at 17°
- **ISNA (Islamic Society of North America)**: Fajr at 15°, Isha at 15°
- **Tehran (Institute of Geophysics, University of Tehran)**: Fajr at 17.7°, Maghrib 4.5° after sunset, Isha at 14°

---

## Example Output

When run directly, the script outputs prayer times for today using a sample location:

```plaintext
Prayer Times for today in Waterloo/Canada
=========================================
imsak: 05:10
fajr: 05:20
sunrise: 06:50
dhuhr: 12:15
asr: 15:20
sunset: 18:45
maghrib: 18:55
isha: 20:15
midnight: 00:35
```

---

## License

This script is distributed under the GNU LGPL v3.0 license. Proper credit should be given to the original authors, with a link to [PrayTimes.org](http://praytimes.org).

---

## Acknowledgments

- Original JavaScript Code: Hamid Zarrabi-Zadeh
- Python Adaptation: Saleem Shafi and Hamid Zarrabi-Zadeh, Mohammad Rahimi

For more details about the calculations, see the [user manual](http://praytimes.org/manual) and [calculation formulas](http://praytimes.org/calculation).

Project [link](https://pypi.org/project/religious-times/) on **Pypi.org** 

Project on **GitHub**: [religious_times](https://github.com/zamoosh/religious_times)

