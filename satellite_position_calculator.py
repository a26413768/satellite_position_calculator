import requests
from bs4 import BeautifulSoup
import datetime
from datetime import timedelta

from sgp4.api import Satrec
from sgp4.api import jday
from skyfield.api import Distance, load, wgs84
from skyfield.positionlib import Geocentric

from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import ESRI_IMAGERY, get_provider
from pyproj import Proj, Transformer

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

delta = timedelta(
   seconds=5
)

lat_deg = []
lon_deg = []
height = []

for ii in range(0,1000):
    time_stampe = datetime.datetime.utcnow() + delta*ii
    UTC= (time_stampe.year, time_stampe.month,\
        time_stampe.day, time_stampe.hour,\
        time_stampe.minute, time_stampe.second)
    jd, fr= jday(UTC[0],UTC[1],UTC[2],UTC[3],UTC[4],UTC[5]) # julian day
    #calculate satalite position in ECI frame
    satellite = Satrec.twoline2rv(s, t)
    e, r, v = satellite.sgp4(jd, fr) # e=error, r=position vector, v=volecity vector 
    #transfer ECI frame position to latitude and longitude and height
    ts = load.timescale()
    t_utc = ts.utc(UTC[0],UTC[1],UTC[2],UTC[3],UTC[4],UTC[5])
    d = Distance(m=[r[0]*1000,r[1]*1000,r[2]*1000]) # "*1000" for km to m
    p = Geocentric(d.au, t=t_utc)
    g = wgs84.subpoint(p)
    lat_deg.append(g.latitude.degrees)
    lon_deg.append(g.longitude.degrees)
    height.append(g.elevation.m)

output_file("tile.html")

esri = get_provider(ESRI_IMAGERY)

transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
world_lon1, world_lat1 = transformer.transform(-80,-180)
world_lon2, world_lat2 = transformer.transform(80,180)
sat_lon, sat_lat = transformer.transform(lat_deg,lon_deg)

p = figure(plot_width=600, plot_height=600,
           x_range=(world_lon1, world_lon2), y_range=(world_lat1, world_lat2),
           x_axis_type="mercator", y_axis_type="mercator",
           tooltips=[
                    ("Source", "@Country_Orig"), ("Destination", "@Country_Dest"), ("Count", "@Count")
                    ],
           title="Position of FORMOSAT-5, latitude "+str("%0.2f" % (lat_deg[0],))+", longitude "+str("%0.2f" % (lon_deg[0],))+", Height "+str("%0.2f" % (height[0]/1000))+"km")

p.circle(sat_lon, sat_lat, size = 3, color='#e75480')
p.cross(sat_lon[0], sat_lat[0], size = 30,line_width=3, color="white")
p.add_tile(esri)

show(p)
