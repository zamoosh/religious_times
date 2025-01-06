from datetime import date
from religious_times import PrayTimes

if __name__ == '__main__':
    pt = PrayTimes('MWL')
    pt.set_method("Tehran")
    coordinates = (34.641159, 50.877456)
    timezone = 3.5  # Time zone offset from UTC

    times = pt.get_times(date.today(), coordinates, timezone)
    for k, v in times.items():
        print(k, v)
