import math
import sys


def waypoints_to_file(lat, lon, outfile=sys.stdout):
    print("QGC WPL 110", file=outfile)
    print("0\t1\t0\t16\t0\t0\t0\t0\t{}\t{}\t20\t1".format(lat[0],lon[0]), file=outfile)
    for i,lat_ in enumerate(lat):
        print("{}\t0\t3\t16\t0\t0\t0\t0\t{}\t{}\t1\t1".format(i+1, lat_, lon[i]), file=outfile)


# meters_per_deg borrowed from swiftnav's piksi_tools/console/solution_view.py
def meters_per_deg(lat):
    m1 = 111132.92  # latitude calculation term 1
    m2 = -559.82    # latitude calculation term 2
    m3 = 1.175      # latitude calculation term 3
    m4 = -0.0023    # latitude calculation term 4
    p1 = 111412.84  # longitude calculation term 1
    p2 = -93.5      # longitude calculation term 2
    p3 = 0.118      # longitude calculation term 3

    # Calculate the length of a degree of latitude and longitude in meters
    latlen = m1 + (m2 * math.cos(2 * lat * math.pi / 180)) + (
        m3 * math.cos(4 * lat * math.pi / 180)) + \
        (m4 * math.cos(6 * lat * math.pi / 180))
    longlen = (p1 * math.cos(lat * math.pi / 180)) + (
        p2 * math.cos(3 * lat * math.pi / 180)) + \
        (p3 * math.cos(5 * lat * math.pi / 180))
    return (latlen, longlen)


def meters_to_latlon(xy, lat, lon):
    x,y = xy
    latlen, lonlen = meters_per_deg(lat)
    lon = lon + x/lonlen
    lat = lat + y/latlen
    return lat, lon


if __name__ == '__main__':
	for filename in sys.argv[1:]:
		lat = []
		lon = []
		with open(filename) as file:
			for line in file:
				lat_, lon_ = line.split(',')
				lat.append(float(lat_))
				lon.append(float(lon_))
		with open(filename + '.waypoints', 'w') as outfile:
			waypoints_to_file(lat, lon, outfile)
