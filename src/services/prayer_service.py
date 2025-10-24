import asyncio
from datetime import datetime, timedelta
from hijri_converter import Gregorian
from timezonefinder import TimezoneFinder
import pytz, os, time
from praytimes import PrayTimes

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

BASE_DIR = os.path.dirname(__file__)
ADHAN_AUDIO_PATH = os.path.join(BASE_DIR, "static", "audio", "azan1.mp3")
CACHE = {}
DEFAULT_METHOD = "ISNA"
DEFAULT_LAT = 7.3775
DEFAULT_LON = 3.9470
CALC_METHODS = ["MWL", "ISNA", "Egypt", "Makkah", "Karachi", "Tehran", "Jafari"]
PRAYER_ORDER = ["imsak", "fajr", "dhuhr", "asr", "maghrib", "isha"]
REMINDER_MINUTES = 10
PRAYER_CACHE = {}
PRAYER_CACHE_TTL = 30

def get_timezone(lat, lon):
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=lat, lng=lon) or "Africa/Lagos"
    return pytz.timezone(tz_str)

def get_timezone_offset(lat, lon):
    tz = get_timezone(lat, lon)
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_time = now_utc.astimezone(tz)
    offset = local_time.utcoffset()
    return offset.total_seconds() / 3600 if offset else 1.0

def format_time_12h(time_str):
    try:
        hour, minute = map(int, time_str.split(":"))
    except:
        return "--:--"
    suffix = "AM" if hour < 12 else "PM"
    hour = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)
    return f"{hour}:{minute:02d} {suffix}"

def precompute_weekly_cache(lat, lon, method=DEFAULT_METHOD):
    key = f"{lat}:{lon}:{method}"
    if key in CACHE:
        return CACHE[key]
    pt = PrayTimes(method)
    tz = get_timezone(lat, lon)
    week = {}
    for i in range(7):
        day = datetime.now(tz) + timedelta(days=i)
        times = pt.getTimes(
            date=(day.year, day.month, day.day),
            coords=(lat, lon),
            timezone=get_timezone_offset(lat, lon)
        )
        if "isha" in times:
            h, m = map(int, times["isha"].split(":"))
            isha_dt = datetime(day.year, day.month, day.day, h, m) + timedelta(minutes=15)
            times["isha"] = isha_dt.strftime("%H:%M")
        hijri = Gregorian(day.year, day.month, day.day).to_hijri()
        formatted = {
            k: {"24h": v, "12h": format_time_12h(v)}
            for k, v in times.items()
            if v and k.lower() != "sunrise"
        }
        week[day.strftime("%Y-%m-%d")] = {
            "hijri_date": f"{hijri.day}-{hijri.month}-{hijri.year}",
            "prayer_times": formatted
        }
    CACHE[key] = week
    return week

def play_audio_file(path):
    if not PYGAME_AVAILABLE:
        return
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except:
        pass

async def play_adhan():
    await asyncio.to_thread(play_audio_file, ADHAN_AUDIO_PATH)

def _get_prayer_times_cached(lat, lon, method, day):
    key = f"{lat}:{lon}:{method}:{day.year}-{day.month}-{day.day}"
    entry = PRAYER_CACHE.get(key)
    now_ts = time.time()
    if entry and now_ts - entry["ts"] < PRAYER_CACHE_TTL:
        return entry["data"]
    pt = PrayTimes(method)
    tz = get_timezone(lat, lon)
    times = pt.getTimes(
        date=(day.year, day.month, day.day),
        coords=(lat, lon),
        timezone=get_timezone_offset(lat, lon)
    )
    if "isha" in times:
        h, m = map(int, times["isha"].split(":"))
        isha_dt = datetime(day.year, day.month, day.day, h, m) + timedelta(minutes=15)
        times["isha"] = isha_dt.strftime("%H:%M")
    PRAYER_CACHE[key] = {"ts": now_ts, "data": times}
    return times

async def get_prayer_times(lat=None, lon=None, method=DEFAULT_METHOD):
    if method not in CALC_METHODS:
        method = DEFAULT_METHOD
    if lat is None or lon is None:
        lat, lon = DEFAULT_LAT, DEFAULT_LON
    tz = get_timezone(lat, lon)
    pt = PrayTimes(method)
    now = datetime.now(tz)
    today_times = _get_prayer_times_cached(lat, lon, method, now)
    prayers = {}
    for k, v in today_times.items():
        if v and k.lower() != "sunrise":
            h, m = map(int, v.split(":"))
            dt = tz.localize(datetime(now.year, now.month, now.day, h, m))
            prayers[k] = {
                "time": dt.strftime("%H:%M:%S"),
                "time_12h": format_time_12h(dt.strftime("%H:%M"))
            }
    next_name, next_dt = None, None
    for name in PRAYER_ORDER:
        t = prayers.get(name, {}).get("time")
        if not t:
            continue
        h, m, s = map(int, t.split(":"))
        dt = tz.localize(datetime(now.year, now.month, now.day, h, m, s))
        if dt > now:
            next_name, next_dt = name, dt
            break
    if not next_name:
        tomorrow = now + timedelta(days=1)
        tom_times = _get_prayer_times_cached(lat, lon, method, tomorrow)
        if "isha" in tom_times:
            h, m = map(int, tom_times["isha"].split(":"))
            isha_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, h, m) + timedelta(minutes=15)
            tom_times["isha"] = isha_dt.strftime("%H:%M")
        h, m = map(int, tom_times.get("fajr", "05:00").split(":"))
        next_name = "fajr"
        next_dt = tz.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, h, m))
    minutes_until = int((next_dt - now).total_seconds() // 60)
    hijri = Gregorian(now.year, now.month, now.day).to_hijri()
    weekly = precompute_weekly_cache(lat, lon, method)
    return {
        "prayer_times": prayers,
        "next_prayer": {
            "name": next_name,
            "time": next_dt.strftime("%H:%M:%S"),
            "time_12h": format_time_12h(next_dt.strftime("%H:%M")),
            "minutes_until": minutes_until,
            "timestamp": next_dt.timestamp()
        },
        "hijri_date": f"{hijri.day}-{hijri.month}-{hijri.year}",
        "gregorian_date": now.strftime("%d-%m-%Y"),
        "weekly_prayer_times": weekly
    }

class Scheduler:
    def __init__(self):
        self.users = {}

    def add_user(self, user_id, lat, lon, method="ISNA"):
        if user_id not in self.users:
            self.users[user_id] = {
                "lat": lat,
                "lon": lon,
                "method": method,
                "last_played": {}
            }

    async def run(self):
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        for user_id, info in list(self.users.items()):
            tz = get_timezone(info["lat"], info["lon"])
            now = now_utc.astimezone(tz)
            today_times = _get_prayer_times_cached(info["lat"], info["lon"], info["method"], now)
            prayers = {}
            for k, v in today_times.items():
                if v and k.lower() != "sunrise":
                    h, m = map(int, v.split(":"))
                    dt = tz.localize(datetime(now.year, now.month, now.day, h, m))
                    prayers[k] = {"time": dt.strftime("%H:%M:%S")}
            for pname, pinfo in prayers.items():
                ph, pm, ps = map(int, pinfo["time"].split(":"))
                pdt = tz.localize(datetime(now.year, now.month, now.day, ph, pm, ps))
                reminder_window_start = pdt - timedelta(minutes=1)
                reminder_window_end = pdt + timedelta(seconds=30)
                last_played = info["last_played"].get(pname)
                if reminder_window_start <= now <= reminder_window_end and last_played != pdt.date():
                    info["last_played"][pname] = pdt.date()
                    asyncio.create_task(play_adhan())
