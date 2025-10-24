from math import radians, degrees, sin, cos, atan2

KAABA_LAT = radians(21.422487)
KAABA_LON = radians(39.826206)

def calculate_qibla(latitude: float, longitude: float):
    lat1 = radians(latitude)
    lon1 = radians(longitude)

    dlon = KAABA_LON - lon1
    x = sin(dlon) * cos(KAABA_LAT)
    y = cos(lat1) * sin(KAABA_LAT) - sin(lat1) * cos(KAABA_LAT) * cos(dlon)
    bearing = (degrees(atan2(x, y)) + 360) % 360

    R = 6371.0
    dlat = KAABA_LAT - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(KAABA_LAT) * sin(dlon/2)**2
    c = 2 * atan2(a**0.5, (1-a)**0.5)
    distance = R * c
    return bearing, distance
