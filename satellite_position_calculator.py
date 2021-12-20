from sgp4.api import Satrec
from sgp4.api import jday
from skyfield.api import Distance, load, wgs84
from skyfield.positionlib import Geocentric
import requests
from bs4 import BeautifulSoup
import datetime

# Reminder:
# get two line elements from https://www.celestrak.com/NORAD/elements/active.txt
# UTC = local_time(Taiwan)-8hr
url = "https://www.celestrak.com/NORAD/elements/active.txt"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
result = soup.getText()
TLE_index = result.find('ISS (ZARYA)')  # satellite name, FS-8B should be "FORMOSAT 8-2"
# set two line elements and UTC time 
s = result[TLE_index+26:TLE_index+95]
t = result[TLE_index+97:TLE_index+166]
UTC= (datetime.datetime.utcnow().year, datetime.datetime.utcnow().month,\
    datetime.datetime.utcnow().day, datetime.datetime.utcnow().hour,\
    datetime.datetime.utcnow().minute, datetime.datetime.utcnow().second)
print(UTC)
#calculate satalite position in ECI frame
satellite = Satrec.twoline2rv(s, t)
jd, fr = jday(UTC[0],UTC[1],UTC[2],UTC[3],UTC[4],UTC[5]) # julian day
e, r, v = satellite.sgp4(jd, fr) # e=error, r=position vector, v=volecity vector 
#transfer ECI frame position to latitude and longitude and height
ts = load.timescale()
t = ts.utc(UTC[0],UTC[1],UTC[2],UTC[3],UTC[4],UTC[5])
d = Distance(m=[r[0]*1000,r[1]*1000,r[2]*1000]) # "*1000" for km to m
p = Geocentric(d.au, t=t)
g = wgs84.subpoint(p)
print(g.latitude.degrees, 'degrees latitude')
print(g.longitude.degrees, 'degrees longitude')
print(g.elevation.m, 'meters above WGS84 mean sea level')